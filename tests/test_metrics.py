import numpy as np

from hydrostab import metrics


def test_spikes():
    data = np.array([1, 3, 5, 9, 8, 6, 4, 2])
    spikes = metrics.spikes(data, threshold=3)
    assert spikes == np.array([2])
    assert np.take(data, spikes) == 5

    data = np.array([1, 3, 5, 9, 8, 6, 4, 2])
    spikes = metrics.spikes(data, threshold=2)
    assert spikes == np.array([2])
    assert np.take(data, spikes) == 5


def test_oscillations():
    data = np.array([0, 1, 2, 3, 2, 1, 0, 5, 10, 15, 10, 5, 0])
    oscillations = metrics.oscillations(data, distance=2)
    print(oscillations, type(oscillations))
    assert np.array_equal(oscillations, np.array([3, 6, 9]))
    assert np.array_equal(np.take(data, oscillations), np.array([3, 0, 15]))


def test_noi():
    data = np.array([0, 1, 2, 3, 4, 5])
    noi = metrics.noi(data)
    assert noi == 1.0

    data = np.array([0, 1, 0, 1, 0])
    noi = metrics.noi(data)
    assert noi == 4.0
