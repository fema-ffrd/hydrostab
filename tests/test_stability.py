import pandas as pd

from pathlib import Path

import hydrostab


STABLE_HYDROGRAPHS = list(Path("tests/data/hydrographs/stable").rglob("*.csv"))
UNSTABLE_HYDROGRAPHS = list(Path("tests/data/hydrographs/unstable").rglob("*.csv"))


def test_stable():
    for csv in STABLE_HYDROGRAPHS:
        print(csv)
        hydrograph = pd.read_csv(csv)
        flows = hydrograph["flow"].values
        assert hydrostab.stable(flows) is True


def test_unstable():
    for csv in UNSTABLE_HYDROGRAPHS:
        print(csv)
        hydrograph = pd.read_csv(csv)
        flows = hydrograph["flow"].values
        assert hydrostab.stable(flows) is False


def test_fft_stable():
    for csv in STABLE_HYDROGRAPHS:
        print(csv)
        hydrograph = pd.read_csv(csv)
        flows = hydrograph["flow"].values
        is_stable, _, _, _ = hydrostab.fft.fft_stable(flows)
        assert is_stable is True


def test_fft_unstable():
    for csv in UNSTABLE_HYDROGRAPHS:
        print(csv)
        hydrograph = pd.read_csv(csv)
        flows = hydrograph["flow"].values
        is_stable, _, _, _ = hydrostab.fft.fft_stable(flows)
        assert is_stable is False
