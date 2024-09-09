"""Using Fourier Transforms to analyze hydrograph stability."""

import numpy as np

from typing import Tuple


def fft_stable(
    hydrograph: np.ndarray,
    sampling_rate: float = 1.0,
    unstable_period: float = 10.0,
    threshold: float = 0.2,
    normalize: bool = True,
    relative: bool = False,
) -> Tuple[bool, float, np.ndarray, np.ndarray]:
    """Check if a time series hydrograph is stable using Fourier Transforms.

    Parameters
    ----------
    hydrograph : np.ndarray
        Time series hydrograph data.
    sampling_rate: float, optional
        Sampling rate of the hydrograph data. i.e., the time between each data
        point.
    unstable_period : float, optional
        Time period for unstable oscillations. Oscillations happening faster
        than this are considered problematic. Must be in the same units as
        the sampling rate.
    threshold : float, optional
        Power threshold of unstable oscillations for classifying. If the
        stability. If the proportion of power in high-frequency components
        exceeds this threshold, the hydrograph is considered unstable.
    normalize : bool, optional
        Normalize hydrograph data to the range [0, 1].
    relative : bool, optional
        Adjust hydrograph data relative to the minimum value.

    Returns
    -------
    is_unstable: bool
        True if the time series is unstable, False otherwise.
    high_freq_proportion: float
        Proportion of power in high-frequency components.
    power_spectrum: np.ndarray
        Power spectrum of the hydrograph data.
    freqs: np.ndarray
        Frequencies of the power spectrum.

    """
    if relative:
        hydrograph = hydrograph - np.min(hydrograph)
    if normalize:
        hydrograph = hydrograph / np.max(hydrograph)

    # compute the Fourier Transform
    fft_values = np.fft.fft(hydrograph)

    # compute frequencies, dropping negative frequencies
    n = len(hydrograph)
    d = 1.0 / sampling_rate
    freqs = np.fft.fftfreq(n, d=d)[: n // 2]

    # compute power spectrum, dropping negative frequencies
    power_spectrum = np.abs(fft_values)[: n // 2]

    # identify high-freq components
    threshold_freq = 1.0 / unstable_period
    high_freq_power = power_spectrum[freqs > threshold_freq]

    total_power = np.sum(power_spectrum)
    high_freq_proportion = np.sum(high_freq_power) / total_power

    # convert from numpy bool to Python bool
    is_stable = bool(high_freq_proportion < threshold)
    return is_stable, high_freq_proportion, power_spectrum, freqs
