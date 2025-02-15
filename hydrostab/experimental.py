"""Experimental methods for hydrograph stability analysis."""

import numpy as np
import numpy.typing as npt
import pandas as pd

from typing import Tuple

from hydrostab.utils import coerce_array


def fft_stability(
    hydrograph: npt.NDArray[np.float64],
    sampling_rate: float = 1.0,
    unstable_period: float = 10.0,
    threshold: float = 0.002,
    normalize: bool = False,
    relative: bool = False,
    standardize: bool = False,
    detrend: bool = False,
) -> Tuple[bool, float, npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Check if a time series hydrograph is stable using Fourier Transforms.

    EXPERIMENTAL: This method is still under development.

    Parameters
    ----------
    hydrograph : npt.NDArray[np.float64]
        Time series hydrograph data
    sampling_rate : float, optional
        Sampling rate of the hydrograph data (time between each point), by default 1.0
    unstable_period : float, optional
        Time period threshold for unstable oscillations, by default 10.0.
        Oscillations faster than this are considered problematic.
        Must be in the same units as sampling_rate.
    threshold : float, optional
        Power threshold for classifying instability, by default 0.002.
        If the proportion of power in high-frequency components exceeds this,
        the hydrograph is considered unstable.
    normalize : bool, optional
        Normalize data to [0, 1] range, by default False
    relative : bool, optional
        Adjust data relative to minimum value, by default False
    standardize : bool, optional
        Standardize data to zero mean and unit variance, by default False
    detrend : bool, optional
        Remove the mean from the data, by default False

    Returns
    -------
    is_unstable : bool
        True if the time series is unstable, False otherwise
    high_freq_proportion : float
        Proportion of power in high-frequency components
    power_spectrum : npt.NDArray[np.float64]
        Power spectrum of the hydrograph data
    freqs : npt.NDArray[np.float64]
        Frequencies of the power spectrum

    Raises
    ------
    ValueError
        If input array has less than 2 points or contains invalid values
    ImportError
        If scipy is not installed
    """
    import scipy.signal

    if detrend:
        hydrograph = scipy.signal.detrend(hydrograph, type="constant")
    if standardize:
        hydrograph = (hydrograph - np.mean(hydrograph)) / np.std(hydrograph)
    if relative:
        hydrograph = hydrograph - np.min(hydrograph)
    if normalize:
        hydrograph = hydrograph / np.max(hydrograph)

    # compute the Fourier Transform
    fft_values = np.fft.rfft(hydrograph)

    # compute frequencies, dropping negative frequencies
    n = len(hydrograph)
    d = 1.0 / sampling_rate
    freqs = np.fft.rfftfreq(n, d=d)

    # compute power spectrum, dropping negative frequencies
    power_spectrum = np.abs(fft_values)

    # identify high-freq components
    threshold_freq = 1.0 / unstable_period
    high_freq_power = power_spectrum[freqs > threshold_freq]

    total_power = np.sum(power_spectrum)
    high_freq_proportion = np.sum(high_freq_power) / total_power

    # convert from numpy bool to Python bool
    is_stable = bool(high_freq_proportion < threshold)
    return is_stable, high_freq_proportion, power_spectrum, freqs


# Define the oscillation fraction thresholds and corresponding labels
oscillation_thresholds = {
    0.05: "Stable",
    0.10: "Somewhat Stable",
    0.15: "Somewhat Unstable",
    0.20: "Unstable",
}

# Define the standard deviation thresholds and corresponding labels
std_dev_thresholds = {
    5.0: "Stable",
    10.0: "Somewhat Stable",
    25.0: "Somewhat Unstable",
    50.0: "Unstable",
}


def _coerce_dt_array(dt_array: npt.ArrayLike) -> pd.Series[pd.Timestamp]:
    """Coerce 1D array of input datetime values to pandas datetime."""
    dt_array = np.asarray(dt_array)  # Convert to NumPy array
    if dt_array.ndim != 1:
        raise ValueError("Input must be 1D")
    return pd.to_datetime(dt_array)


def oscillation_fraction(
    hydrograph_values: npt.ArrayLike,
    hydrograph_times: npt.ArrayLike,
    rate_of_change_threshold: float,
) -> tuple[float, npt.NDArray[np.float64], float, float]:
    """Calculate the oscillation fraction from the hydrograph data.

    EXPERIMENTAL: This method is still under development.

    Parameters
    ----------
    hydrograph_values : npt.ArrayLike
        Array of hydrograph values (flow or stage)
    hydrograph_times : npt.ArrayLike
        Array of datetime values corresponding to hydrograph_values
    rate_of_change_threshold : float
        Threshold for the rate of change to consider an oscillation

    Returns
    -------
    oscillation_fraction : float
        Fraction of points that exceed the rate of change threshold
    rate_of_change_percentage : npt.NDArray[np.float64]
        Percentage rate of change at each point
    std_dev_rate_of_change : float
        Standard deviation of the rate of change percentage
    time_interval_minutes : float
        Inferred time interval between measurements in minutes

    Raises
    ------
    ValueError
        If input arrays have different lengths or contain invalid values
    """
    hyd_values = coerce_array(hydrograph_values)
    hyd_times = _coerce_dt_array(hydrograph_times)

    # Convert negative values in hyd_values to 0
    hyd_values[hyd_values < 0] = 0

    # Calculate the mean of the flow data
    mean_flow = np.mean(hyd_values)

    # Use 10% of the mean value as epsilon
    epsilon = 0.1 * mean_flow

    # Infer the time interval in minutes
    time_diffs = hyd_times.diff().dropna().to_series()
    time_interval_minutes = time_diffs.mode()[0].total_seconds() / 60

    # Convert time interval from minutes to hours
    time_interval_hour = time_interval_minutes / 60

    # Calculate the first derivative (rate of change)
    rate_of_change = np.diff(hyd_values, prepend=hyd_values[0])

    # Normalize the rate of change by the time interval to account for different sampling frequencies,
    # penalizing higher resolution intervals (e.g., 15 min) more than lower resolution intervals (e.g., 60 min)
    normalized_rate_of_change = rate_of_change / time_interval_hour

    # Calculate the percentage change relative to the original data
    # Adding epsilon to avoid division by very small numbers and reduce the impact of small spikes when values are close to 0.
    rate_of_change_percentage = (
        normalized_rate_of_change / (hyd_values + epsilon)
    ) * 100  # Convert to percentage

    # Determine the number of oscillations
    oscillations = np.sum(
        np.abs(rate_of_change_percentage) > (rate_of_change_threshold * 100)
    )

    # Calculate the oscillation fraction
    oscillation_fraction = oscillations / len(hyd_values)

    # Calculate the standard deviation of the rate of change percentage
    std_dev_rate_of_change = np.std(rate_of_change_percentage)

    return (
        oscillation_fraction,
        rate_of_change_percentage,
        std_dev_rate_of_change,
        time_interval_minutes,
    )


def _find_first_peak(flow: npt.NDArray[np.float64]) -> int:
    """Find the first peak data point in a data array.

    Parameters
    ----------
    flow : npt.NDArray[np.float64]
        Array of hydrograph data (flow or stage)

    Returns
    -------
    int
        Index location of the first peak data point in the input array
    """
    # Set the initial maximum flow to be 0
    max = 0

    # Find the first data point that is not the maximum value compared to all data points beforehand
    for i in range(len(flow) - 1):
        if i != 0:
            max = np.max(flow[0:i])
            if flow[i - 1] != max:
                ind = i
                # Return the index value
                if ind != 0 and ind != (len(flow) - 1):
                    return ind
                else:
                    return 0


def abrupt_changes(
    hydrograph_values: npt.ArrayLike, percent_change: float, max_time_interval: int
) -> bool:
    """Detect abrupt changes in a time series hydrograph.

    EXPERIMENTAL: This method is still under development.

    Parameters
    ----------
    hydrograph_values : npt.ArrayLike
        Array of hydrograph data (flow or stage)
    percent_change : float
        Minimum percentage change in the hydrograph range to be considered an abrupt change
    max_time_interval : int
        Maximum number of samples between points to be considered part of the same change

    Returns
    -------
    bool
        True if the hydrograph is classified as stable, False otherwise

    Raises
    ------
    ValueError
        If input array has less than 2 points or contains invalid values
    """
    # Find location of the first peak
    first_peak_index = _find_first_peak(hydrograph_values)

    hyd_values = pd.Series(coerce_array(hydrograph_values))

    # Calculate the absolute change in the flow.
    abs_change = hyd_values.diff().abs()

    # Calculate the threshold for the minimum change required to be considered an abrupt change.
    change_threshold = (np.max(hyd_values) - np.min(hyd_values)) * percent_change

    # Initialize a mask of False values to indicate no abrupt changes have been detected yet.
    abrupt_changes = pd.Series(False, index=range(len(hyd_values)))

    # Loop over each data point in the flow.
    for i in range(1, len(hyd_values)):
        # If the absolute change is greater than the threshold, mark this data point as the start of an abrupt change.
        if abs_change[i] >= change_threshold:
            abrupt_changes[i] = True

            # Keep track of the end of the current change.
            end_of_change = i

            # Continue checking subsequent data points to see if they are still part of the same change.
            for j in range(i + 1, min(i + max_time_interval, len(hyd_values))):
                if abs_change[j] >= change_threshold:
                    # If the change is still above the threshold, mark this data point as part of the same change.
                    abrupt_changes[j] = True

                    # Update the end of the current change.
                    end_of_change = j
                else:
                    # If the change has fallen below the threshold, stop checking subsequent data points.
                    break

            # Skip checking data points that are already part of the current change.
            i = end_of_change

    # Transform change points array to a list
    ls_abrupt_changes = abrupt_changes.tolist()

    # Calculate the abrupt change points detected that are prior to the first peak
    ls_abrupt_changes_before_peak = ls_abrupt_changes[0:first_peak_index]

    # Calculate the number of change points prior to the first peak
    unstable_pt_before_peak = ls_abrupt_changes_before_peak.count(1)
    unstable_pt = ls_abrupt_changes.count(1)

    # Determine the hydrograph to be stable if all abrupt change points detected are before the first peak.
    # This is to improve metric performance with quick ramp-up in data.
    if unstable_pt_before_peak == unstable_pt:
        return True
    # Return the hydrograph to be stable if no abrupt change point detected. Otherwise return unstable.
    elif unstable_pt == 0:
        return True
    else:
        return False
