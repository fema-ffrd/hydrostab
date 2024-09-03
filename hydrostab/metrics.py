"""Metrics for analyzing time series data."""

import numpy as np
from scipy.signal import find_peaks


def spikes(data: np.ndarray, threshold=3) -> np.ndarray:
    """Find spikes in a series using a simple threshold distance method.

    Note that data is a 1D array; no time series data is required.

    Parameters
    ----------
    data : np.ndarray
        Time series data.
    threshold : int, optional
        Threshold y-distance for identifying spikes.

    Returns
    -------
    np.ndarray
        Indices of spikes in the time series.

    """
    # Calculate differences between successive data points
    diff = np.diff(data)

    # Find indices the value of i+1 is greater than the value of i + threshold
    spikes = np.where(diff > threshold)
    return spikes


def oscillations(data: np.ndarray, distance=5) -> np.ndarray:
    """Find oscillations in a series.

    Note that data is a 1D array; no time series data is required.

    Parameters
    ----------
    data : np.ndarray
        Time series data.
    distance : int, optional
        Minimum distance between peaks and troughs.

    Returns
    -------
    np.ndarray
        Indices of oscillations in the time series.

    """
    peaks, _ = find_peaks(data, distance=distance)
    troughs, _ = find_peaks(-data, distance=distance)
    oscillations = np.sort(np.concatenate([peaks, troughs]))
    return oscillations


def noi(data: np.ndarray) -> float:
    """Calculate the normalized oscillation index (NOI) for a time series.

    The normalized oscillation index (NOI) is a measure of the variability of a time series.

    Parameters
    ----------
    data : np.ndarray
        Time series data.

    Returns
    -------
    float
        The normalized oscillation index (NOI) of the time series.

    """
    # Calculate differences between successive data points
    differences = np.diff(data)

    # Normalize differences
    max_value = np.max(data)
    normalized_differences = differences / max_value

    # Sum the absolute values of the normalized differences
    noi = np.sum(np.abs(normalized_differences))

    return noi
