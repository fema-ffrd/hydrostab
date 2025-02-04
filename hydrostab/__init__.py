"""hydrostab: A Python package for hydrograph stability analysis."""

import numpy as np
import numpy.typing as npt

from typing import Tuple

from .utils import coerce_array


def stability_score(
    hydrograph: npt.NDArray[np.float64], range_threshold: float = 0.1
) -> float:
    """Compute a stability score for a hydrograph based on slope sign changes.

    A higher score indicates more instability. The score is computed by:
    1. Normalizing the hydrograph to 0-1 range
    2. Computing differences between consecutive points
    3. Detecting sign changes in the differences
    4. Summing the magnitude of sign changes
    5. Normalizing by the length of the hydrograph

    Parameters
    ----------
    hydrograph : np.ndarray
        1D array of hydrograph data (flow or stage)
    range_threshold : float, optional
        If the range of values in the hydrograph is less than this threshold,
        return a score of 0.0, by default 0.1

    Returns
    -------
    float
        Stability score between 0.0 and 1.0, where 0.0 indicates perfect stability
        and higher values indicate more instability
    """
    hyd = coerce_array(hydrograph)

    # Check if the hydrograph is flat
    h_range = np.ptp(hyd)
    if h_range < range_threshold:
        return 0.0

    # Normalize to range of 0.0 to 1.0
    h_norm = (hydrograph - np.min(hyd)) / h_range

    # Compute first differences
    diff = np.diff(h_norm)

    # Detect sign changes (positive to negative or vice versa)
    sign_changes = np.sign(diff[1:]) != np.sign(diff[:-1])

    # Compute magnitude of sign changes
    sign_changes_magnitude = np.abs(np.diff(diff))

    # Sum the magnitude of sign changes and divide by the number of points
    score = np.sum(sign_changes_magnitude[sign_changes]) / len(hyd)
    return score


def is_stable(
    hydrograph: npt.NDArray[np.float64],
    unstable_threshold: float = 0.002,
    range_threshold: float = 0.1,
) -> bool:
    """Check if a time series hydrograph is stable.

    Parameters
    ----------
    hydrograph : np.ndarray
        Time series hydrograph values.

    Returns
    -------
    bool
        True if the time series is stable, False otherwise.

    """
    score = stability_score(hydrograph, range_threshold)
    return score < unstable_threshold


def stability(
    hydrograph: npt.NDArray[np.float64],
    unstable_threshold: float = 0.002,
    range_threshold: float = 0.1,
) -> Tuple[bool, float]:
    """
    Classify a hydrograph as stable or unstable based on slope sign changes.

    Parameters
    ----------
    hydrograph : np.ndarray
        1D array of hydrograph data (flow or stage).
    score_threshold : float
        Threshold for the score to classify stability. If the
        score is less than this threshold, the hydrograph is
        considered stable.
    range_threshold : float
        If `np.ptp(hydrograph)` is less than `range_threshold`,
        then the hydrograph is considered stable with a
        score of 0.0.

    Returns
    -------
    is_stable : bool
        True if the hydrograph is classified as stable, False otherwise.
    score : float
        Stability score based on slope sign changes.
    """
    score = stability_score(hydrograph, range_threshold)
    return score < unstable_threshold, score
