import pandas as pd
import pytest

from pathlib import Path

import hydrostab


STABLE_HYDROGRAPHS = list(Path("tests/data/hydrographs/stable").rglob("*.csv"))
UNSTABLE_HYDROGRAPHS = list(Path("tests/data/hydrographs/unstable").rglob("*.csv"))


def test_stable():
    for csv in STABLE_HYDROGRAPHS:
        print(csv)
        hydrograph = pd.read_csv(csv)
        flows = hydrograph["flow"]
        is_stable, _ = hydrostab.stability(flows)
        assert bool(is_stable) is True


def test_unstable():
    for csv in UNSTABLE_HYDROGRAPHS:
        print(csv)
        hydrograph = pd.read_csv(csv)
        flows = hydrograph["flow"]
        is_stable, _ = hydrostab.stability(flows)
        assert bool(is_stable) is False
