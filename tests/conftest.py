import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]

BIB_TEXT = r"""% comment
@article{piotroski2000,
  author  = {Piotroski, Joseph D.},
  year    = {2000},
  title   = {Value investing}
}
@article{famafrench1993,
  author  = {Fama, Eugene F. and French, Kenneth R.},
  year    = {1993},
  title   = {Common risk factors}
}
@article{debondt1985,
  author  = {De Bondt, Werner and Thaler, Richard},
  year    = {1985}
}
@article{pastor2003,
  author  = {P\'astor, \v{L}ubo\v{s} and Stambaugh, Robert},
  year    = {2003}
}
@article{novymarx2013,
  author  = {Novy-Marx, Robert},
  year    = {2013}
}
@article{corwinschultz2012,
  author  = {Corwin, Shane A. and Schultz, Paul},
  year    = {2012}
}
@article{balvers2006,
  author  = {Balvers, Ronald and Wu, Yangru},
  year    = {2006}
}
@article{blankname2010,
  author  = {, Nameless and Realname, Joe},
  year    = {2010}
}
@article{muller2001,
  author  = {Müller, Hans},
  year    = {2001}
}
@article{meer2005,
  author  = {{Van der Meer}, Hans},
  year    = {2005}
}
@article{twoyears,
  author  = {Twoyears, Tom},
  year    = {2000},
  year    = {1999}
}
@article{noyear,
  author  = {Ghost, Author}
}
@book{{prado2018},
  author  = {{L{\'o}pez de Prado}, Marcos},
  year    = {2018}
}
"""


@pytest.fixture
def cc(tmp_path, monkeypatch):
    bib = tmp_path / "references.bib"
    bib.write_text(BIB_TEXT, encoding="utf-8")
    monkeypatch.setenv("CITE_CHECK_BIB", str(bib))
    spec = importlib.util.spec_from_file_location("cite_check_under_test", REPO / "cite" / "cite_check.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.BIB_PATH = bib
    yield mod
    sys.modules.pop(spec.name, None)
