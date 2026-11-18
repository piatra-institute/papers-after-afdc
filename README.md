# After AFDC

A test on public data, specified in advance in the project brief, of whether the post-1996 erosion of state cash assistance (AFDC/TANF) amplified the county presidential-vote response to the China trade shock, with a check of whether cash assistance responded to the shock at all, a documentary history of the 1996 welfare law and a translation of the estimate into 2016 votes in Michigan, Wisconsin and Pennsylvania. The interaction is not distinguishable from zero, and family-assistance payments did not measurably respond to the shock.

[Read the paper](https://piatra.institute/papers/after-afdc.pdf) · [Manuscript](paper/PAPER.md) · [Analysis and reproduction](simulation/README.md) · [Analysis plan](brief.md)

## Build

```bash
uv run build.py          # -> paper/PAPER.pdf  (vendored canonical recipe)
```

Requires `pandoc` and `xelatex` on PATH. From the workspace you can also run `papers build after-afdc`.

## Reproduce the analysis

```bash
cd simulation
uv run python fetch_data.py   # downloads and verifies every input (SHA-256)
uv run python run_all.py      # writes output/results.json and paper/figures/
uv run pytest -q
```
