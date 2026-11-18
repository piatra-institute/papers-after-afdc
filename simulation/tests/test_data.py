"""Checks on the frozen inputs. Skipped when data/raw/ has not been fetched."""
import statistics
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from afdc import data as D  # noqa: E402

raw_missing = not all(p.exists() for k, p in D.RAW_FILES.items() if k != "wrd")
needs_raw = pytest.mark.skipif(raw_missing, reason="run fetch_data.py first")


def _half_up(x):
    return int(x + 0.5)


def test_wrd_transcription_reproduces_printed_summary():
    w = pd.read_csv(D.RAW_FILES["wrd"])
    assert len(w) == 51
    # Table L5 prints a 1996 mean of $392 and median of $377 (one value per state, DC included)
    b96 = w["benefit_july1996"].tolist()
    assert _half_up(statistics.mean(b96)) == 392
    assert statistics.median(b96) == 377
    # 2016: printed mean $442 and median $431 are reproduced when Wisconsin (n.a.) is excluded
    b16 = w.loc[w.state != "Wisconsin", "benefit_july2016"].tolist()
    assert _half_up(statistics.mean(b16)) == 442
    assert _half_up(statistics.median(b16)) == 431


@needs_raw
def test_panel_and_official_totals():
    p, diag = D.build_panel()
    assert diag["sample_counties"] == 3106
    assert diag["states"] == 48
    fec = D.load_fec_margins().set_index("state_po")
    assert fec.loc["MI", "trump_margin"] == 10704
    assert fec.loc["WI", "trump_margin"] == 22748
    assert fec.loc["PA", "trump_margin"] == 44292
    m = D.load_medsl()
    m16 = m[(m.year == 2016)]
    for po, sf in [("MI", 26), ("PA", 42)]:
        q = m16[m16.fips // 1000 == sf]
        assert int(q.rep.sum()) == fec.loc[po, "trump"]
        assert int(q.dem.sum()) == fec.loc[po, "clinton"]


@needs_raw
def test_moderator_definitions():
    s = D.state_moderators()
    assert abs(s.loc["Michigan", "erosion"] - (s.loc["Michigan", "tpr_1996"] - s.loc["Michigan", "tpr_2016"])) < 1e-12
    cpi = D.load_cpi()
    assert cpi[1996] == 157.0 and cpi[2016] == 240.628
    assert (s.drop(index=["Alaska", "Hawaii"])["erosion"] > 0).all()
