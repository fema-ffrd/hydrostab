import pandas as pd

from pathlib import Path

import hydrostab


STABLE_HYDROGRAPHS = Path("tests/data/hydrographs/stable").rglob("*.csv")
UNSTABLE_HYDROGRAPHS = Path("tests/data/hydrographs/unstable").rglob("*.csv")


def test_stable():
    for csv in STABLE_HYDROGRAPHS:
        hydrograph = pd.read_csv(csv)
        flows = hydrograph["flow"].values
        assert hydrostab.stable(flows) is True


def test_unstable():
    for csv in UNSTABLE_HYDROGRAPHS:
        hydrograph = pd.read_csv(csv)
        flows = hydrograph["flow"].values
        assert hydrostab.stable(flows) is False
