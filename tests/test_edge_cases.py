import numpy as np
import pytest

from hydrostab import stability_score, is_stable, stability


def test_constant_signal():
    """Test that a constant signal is considered stable."""
    signal = np.ones(100)
    assert stability_score(signal) == 0.0
    assert is_stable(signal) is True


def test_single_point():
    """Test handling of single-point signals."""
    signal = np.array([1.0])
    with pytest.raises(ValueError):
        stability_score(signal)


def test_nan_values():
    """Test handling of NaN values."""
    signal = np.array([1.0, np.nan, 3.0])
    with pytest.raises(ValueError):
        stability_score(signal)


def test_infinite_values():
    """Test handling of infinite values."""
    signal = np.array([1.0, np.inf, 3.0])
    with pytest.raises(ValueError):
        stability_score(signal)


def test_zero_range():
    """Test signals with zero range."""
    signal = np.zeros(100)
    assert stability_score(signal) == 0.0
    assert is_stable(signal) is True
