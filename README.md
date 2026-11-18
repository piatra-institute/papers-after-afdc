# After AFDC

A pre-registered test, on public data, of whether the post-1996 erosion of state cash assistance (AFDC/TANF) amplified the county presidential-vote response to the China trade shock, with a documentary history of the 1996 welfare law and a translation of the estimate into 2016 votes in Michigan, Wisconsin and Pennsylvania. The estimated interaction has the opposite sign to the hypothesis and an interval that includes zero.

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
