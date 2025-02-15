"""Utilies for hydrostab package."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import pandas as pd


def coerce_array(array: npt.ArrayLike) -> npt.NDArray[np.float64]:
    """Coerce input values to a 1D NumPy array of floats."""
    array = np.asarray(array, dtype=np.float64)  # Convert to NumPy array
    if array.ndim != 1:
        raise ValueError("Input must be 1D")
    return array


def coerce_dt_array(dt_array: npt.ArrayLike) -> pd.Series[pd.Timestamp]:
    """Coerce 1D array of input datetime values to pandas datetime.

    Parameters
    ----------
    dt_array : npt.ArrayLike
        Input array of datetime-like values

    Returns
    -------
    pd.Series[pd.Timestamp]
        Series of pandas Timestamps

    Raises
    ------
    ValueError
        If input is not 1D
    """
    dt_array = np.asarray(dt_array)  # Convert to NumPy array
    if dt_array.ndim != 1:
        raise ValueError("Input must be 1D")
    return pd.to_datetime(dt_array)


"""Utility functions for hydrostab."""

import numpy as np
import numpy.typing as npt


def coerce_array(arr: npt.ArrayLike) -> npt.NDArray[np.float64]:
    """Convert input to numpy array and validate.

    Parameters
    ----------
    arr : npt.ArrayLike
        Input array to validate

    Returns
    -------
    npt.NDArray[np.float64]
        Validated numpy array

    Raises
    ------
    ValueError
        If array has less than 2 points or contains NaN/infinite values
    """
    arr = np.asarray(arr, dtype=np.float64)

    if arr.size < 2:
        raise ValueError("Input must have at least 2 points")

    if np.any(np.isnan(arr)) or np.any(np.isinf(arr)):
        raise ValueError("Input contains NaN or infinite values")

    return arr
