import subprocess
import sys
import types

import pytest


def findings(cc, text, tmp_path, name="doc.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    pairs, names = cc.load_bib()
    return cc.check_file(p, pairs, names)


# ---------------- fold ----------------
def test_fold_strips_accents_and_case(cc):
    assert cc.fold("Pástor") == "pastor" and cc.fold("ÉMILE") == "emile" and cc.fold("plain") == "plain"


# ---------------- bibliography ----------------
def test_bib_env_override_and_default(cc, tmp_path, monkeypatch):
    assert cc.BIB == cc.BIB_PATH
    monkeypatch.delenv("CITE_CHECK_BIB")
    import importlib.util
    spec = importlib.util.spec_from_file_location("cc_default", cc.__file__)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.BIB.name == "references.bib" and m.BIB.parent == __import__("pathlib").Path(cc.__file__).parent


def test_load_bib_pairs_and_names(cc):
    pairs, names = cc.load_bib()
    assert ("piotroski", "2000") in pairs and ("fama", "1993") in pairs and ("french", "1993") in pairs
    assert ("de bondt", "1985") in pairs and ("bondt", "1985") in pairs and ("thaler", "1985") in pairs   # full surname AND last token
    assert ("pastor", "2003") in pairs and ("stambaugh", "2003") in pairs                              # TeX accents and braces dropped
    assert ("novy-marx", "2013") in pairs and ("corwin", "2012") in pairs and ("schultz", "2012") in pairs
    assert "ghost" not in names                                                                        # entries without a year are ignored
    assert {"piotroski", "bondt", "de bondt"} <= names


def test_load_bib_skips_blank_surnames(cc):
    pairs, names = cc.load_bib()
    assert ("realname", "2010") in pairs and "" not in names and ("", "2010") not in pairs


def test_load_bib_resets_between_entries(cc):
    pairs, _ = cc.load_bib()
    assert ("ghost", "2000") not in pairs and ("ghost", "1993") not in pairs and ("piotroski", "1993") not in pairs


# ---------------- lead_candidates ----------------
def test_lead_candidates(cc):
    assert cc.lead_candidates("Piotroski") == {"piotroski"}
    assert cc.lead_candidates("Fama & French") == {"fama"}
    assert cc.lead_candidates("Bhute et al.") == {"bhute"}
    assert cc.lead_candidates("Novy-Marx") == {"novy-marx", "novy"}              # hyphen is ambiguous: both readings
    assert cc.lead_candidates("Amihud's") == {"amihud"}                          # possessive dropped
    assert cc.lead_candidates("Fama, French and Carhart") == {"fama"}
    assert cc.lead_candidates("Corwin–Schultz") == {"corwin", "corwin–schultz"} or "corwin" in cc.lead_candidates("Corwin–Schultz")
    assert cc.lead_candidates("Émile & X") == {"emile"}


def test_is_shouting(cc):
    assert cc._is_shouting("MSFT") and cc._is_shouting("ICICI") and cc._is_shouting("U.S.A")
    assert not cc._is_shouting("US") and not cc._is_shouting("Piotroski") and not cc._is_shouting("MS")
    assert cc._is_shouting("MUF-G") and not cc._is_shouting("Mufg")


# ---------------- check_file ----------------
def test_known_citation_is_clean(cc, tmp_path):
    assert findings(cc, "As Piotroski (2000) showed, and Fama & French (1993) too.\n", tmp_path) == []


def test_unknown_citation(cc, tmp_path):
    out = findings(cc, "line one\nBhute et al. (2024) claim this.\n", tmp_path)
    assert out == [("UNKNOWN", 2, "Bhute et al. (2024)", "no entry in references.bib — add one or fix the cite")]


def test_wrong_year_flags_year_with_known_years(cc, tmp_path):
    out = findings(cc, "Balvers & Wu (2005) found it.\n", tmp_path)
    assert out == [("YEAR?", 1, "Balvers & Wu (2005)", "'balvers' in bib but for year(s) 2006")]


def test_year_letter_suffix_and_citation_forms(cc, tmp_path):
    assert findings(cc, "Piotroski (2000a, p. 3) and Piotroski (2000, 2001) and Piotroski ( 2000 ).\n", tmp_path) == []
    out = findings(cc, "Fama, French and Carhart (1997) and Corwin-Schultz (2012) and Novy-Marx (2013).\n", tmp_path)
    # the bib holds Fama for 1993 only, so 1997 is a year problem rather than an unknown citation
    assert out == [("YEAR?", 1, "Fama, French and Carhart (1997)", "'fama' in bib but for year(s) 1993")]


def test_year_range_boundaries(cc, tmp_path):
    for y, flagged in ((1899, False), (1900, True), (2035, True), (2036, False)):
        out = findings(cc, f"Zorblax ({y}) said so.\n", tmp_path)
        assert bool(out) is flagged, y


def test_stoplist_shouting_and_acronym_tails_are_ignored(cc, tmp_path):
    text = ("In (2020) nothing. Market (2020) row. MSFT (2020) ticker. Pre-crisis (2020) marker. "
            "Asness-Frazzini QMJ (2019) shorthand. Shell (2020) and Toyota (2021). Q3 (2024).\n")
    assert findings(cc, text, tmp_path) == []


def test_stop_check_uses_first_word_of_each_lead(cc, tmp_path):
    out = findings(cc, "The Realist (2020) is not a stop word but The is.\n", tmp_path)
    # 'The Realist' does not match the NAME pattern as one name, so it is parsed as 'Realist' -> unknown
    assert [f[0] for f in out] == ["UNKNOWN"] and out[0][2] == "Realist (2020)"


def test_quote_adjacent_to_known_citation(cc, tmp_path):
    out = findings(cc, 'He wrote "value matters" Piotroski (2000) says.\nPiotroski (2000)" ends.\n“Piotroski (2000)”\n', tmp_path)
    assert [(f[0], f[1]) for f in out] == [("QUOTE?", 1), ("QUOTE?", 2), ("QUOTE?", 3)]
    assert out[0][3] == "quote mark abuts citation — verify verbatim"


def test_quote_window_is_two_characters_each_side(cc, tmp_path):
    # a quote three characters away is not flagged
    assert findings(cc, 'x "  Piotroski (2000)  " y\n', tmp_path) == []
    assert [f[0] for f in findings(cc, 'x" Piotroski (2000) "y\n', tmp_path)] == ["QUOTE?"]


def test_docstring_openers_are_not_quotes(cc, tmp_path):
    assert findings(cc, '"""Piotroski (2000) F-score\n', tmp_path) == []
    assert findings(cc, "'''Piotroski (2000) F-score\n", tmp_path) == []
    out = findings(cc, '"""He said "x" Piotroski (2000)\n', tmp_path)
    assert [f[0] for f in out] == ["QUOTE?"]                                 # a genuine quote inside a docstring still flags


def test_unreadable_file_yields_no_findings(cc, tmp_path):
    pairs, names = cc.load_bib()
    assert cc.check_file(tmp_path / "missing.md", pairs, names) == []


def test_non_utf8_bytes_are_replaced_not_fatal(cc, tmp_path):
    p = tmp_path / "bin.md"
    p.write_bytes(b"Zorblax (2020) \xff\xfe\n")
    pairs, names = cc.load_bib()
    assert [f[0] for f in cc.check_file(p, pairs, names)] == ["UNKNOWN"]


def test_accented_citation_matches_bib(cc, tmp_path):
    assert findings(cc, "Pástor & Stambaugh (2003) liquidity.\nDe Bondt & Thaler (1985).\n", tmp_path) == []


# ---------------- main ----------------
def run_main(cc, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["cite_check.py", *args])
    return cc.main()


def test_main_without_args_prints_usage(cc, monkeypatch, capsys):
    assert run_main(cc, monkeypatch) == 0
    assert "Citation checker" in capsys.readouterr().out


def test_main_missing_bib_returns_2(cc, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(cc, "BIB", tmp_path / "nope.bib")
    assert run_main(cc, monkeypatch, "x.md") == 2
    assert "cite_check: missing" in capsys.readouterr().err


def test_main_explicit_files_exit_codes_and_output(cc, monkeypatch, capsys, tmp_path):
    good = tmp_path / "good.md"
    good.write_text("Piotroski (2000).\n")
    warn = tmp_path / "warn.md"
    warn.write_text("Balvers & Wu (2005).\n")
    bad = tmp_path / "bad.md"
    bad.write_text("Zorblax (2020).\n")
    assert run_main(cc, monkeypatch, str(good)) == 0
    assert run_main(cc, monkeypatch, str(warn)) == 0                         # YEAR? is only a warning
    capsys.readouterr()
    assert run_main(cc, monkeypatch, str(warn), str(bad)) == 1
    cap = capsys.readouterr()
    assert f"YEAR?    {warn}:1  Balvers & Wu (2005)" in cap.out and f"UNKNOWN  {bad}:1  Zorblax (2020)" in cap.out
    assert "1 UNKNOWN citation(s)." in cap.err


def test_main_skips_self_and_audit_files(cc, monkeypatch, capsys, tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    for n in ("cite_check.py", "LITERATURE_AUDIT.md"):
        (d / n).write_text("Zorblax (2020).\n")
    assert run_main(cc, monkeypatch, str(d / "cite_check.py"), str(d / "LITERATURE_AUDIT.md")) == 0
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("flag,expected_cmd", [("--all", ["git", "ls-files"]), ("--staged", ["git", "diff", "--cached", "--name-only"])])
def test_main_git_modes(cc, monkeypatch, capsys, tmp_path, flag, expected_cmd):
    (tmp_path / "a.md").write_text("Zorblax (2020).\n")
    (tmp_path / "b.py").write_text("# Piotroski (2000)\n")
    (tmp_path / "c.txt").write_text("Zorblax (2020).\n")
    seen = {}

    def run(cmd, capture_output, text, check):
        seen["cmd"] = cmd
        return types.SimpleNamespace(stdout="a.md\nb.py\nc.txt\ngone.md\n")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(subprocess, "run", run)
    assert run_main(cc, monkeypatch, flag) == 1
    out = capsys.readouterr().out
    assert seen["cmd"] == expected_cmd
    assert "UNKNOWN  a.md:1" in out and "c.txt" not in out and "gone.md" not in out        # only existing .py/.md files


def test_main_all_flag_must_be_alone(cc, monkeypatch, capsys, tmp_path):
    f = tmp_path / "f.md"
    f.write_text("Piotroski (2000).\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("git must not be called"))
    # "--all" together with a file is treated as two file paths: "--all" does not exist, so only f.md is read
    assert run_main(cc, monkeypatch, "--all", str(f)) == 0


def test_entry_point(cc, monkeypatch, tmp_path):
    import runpy
    f = tmp_path / "f.md"
    f.write_text("Piotroski (2000).\n")
    monkeypatch.setattr(sys, "argv", ["cite_check.py", str(f)])
    with pytest.raises(SystemExit) as e:
        runpy.run_path(cc.__file__, run_name="__main__")
    assert e.value.code == 0
