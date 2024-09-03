"""hydrostab: A Python package for hydrograph stability analysis."""

import numpy as np

from hydrostab import metrics


def stable(flow: np.ndarray) -> bool:
    """Check if a time series hydrograph is stable.

    Parameters
    ----------
    flow : np.ndarray
        Time series hydrograph data.

    Returns
    -------
    bool
        True if the time series is stable, False otherwise.

    """
    # Compute relevant metrics
    # TODO: more/better metrics!
    spikes = metrics.spikes(flow)
    oscillations = metrics.oscillations(flow)

    # Check metrics
    # TODO: Make this better!
    if len(spikes) < 500 and len(oscillations) < 500:
        return True

    # TODO: return more info than simple true/false?
    return False
