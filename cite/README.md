# cite/ — shared citation-check inputs

`cite_check.py` and `references.bib` are fetched by the `cite-check` job in each repo's
`quality-gates.yml` from `raw.githubusercontent.com/herrrickshaw/.github/main/cite/`.

They are **copies**. The canonical versions live in the private home repo at
`market-pipeline/code/python_files/`. Re-copy both files here after any change to either;
CI in the consuming repos reads whatever is on `main` here.

Why here: this repo is public, so unauthenticated `raw.githubusercontent.com` fetches work.
The previous source (`global-market-research-platform`) is private and its raw URLs always 404'd.
