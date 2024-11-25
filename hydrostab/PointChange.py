import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from astropy.stats import bootstrap as bootstrap
from statsmodels.tsa.seasonal import seasonal_decompose

def plot_point_change(flow: np.ndarray, abrupt_changes: np.ndarray):   
    """
    plot abrupt change detected with the original dataset.

    Parameters
    ----------
    flow : np.ndarray
        Array of hydrograph data (flow or stage).
    abrupt_changes: np:ndarray
        Array of abrupt change points detected 
    """
    # Plot hydrograph
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(flow, label='flow')
    
    # Plot abrupt change points
    abrupt_changes = abrupt_changes.astype(int)
    ax.plot(flow[abrupt_changes==1], 'ro', label='abrupt changes')
    plt.show()
    
def find_first_peak(flow: np.ndarray):
       """
    Find the first peak data point in a data array.
    
    Parameters:
        flow : np.ndarray
            Array of hydrograph data (flow or stage)
    
    Returns:
        A integar showing the location of the first peak data point in the input array
    """
    # Set the initial maximum flow to be 0 
    max = 0

    # Find the first data point that is not the maximum value compared to all data points beforehand 
    for i in range(len(flow)-1):

        if i != 0:   
            max = np.max(flow[0:i])
            
            if flow[i-1] != max:
                ind = i            
                
                # Return the index value 
                if ind != 0 and ind != (len(flow)-1):
                    return ind
                else:
                    return 0
                
                
# ChatGPT Point Change Detection
def detect_abrupt_changes(flow: np.ndarray, time: np.ndarray, percent_change, max_time_interval):
    """
    Detect abrupt changes in a time series hydrograph data based on the specified parameters.
    
    Parameters:
        flow : np.ndarray
            Array of hydrograph data (flow or stage)
        Time : np.ndarray
            Array of timestamps associated with flow 
        percent_change : float
            The minimum percentage change in the hydrograph flow data range that is considered an abrupt change.
        max_time_interval : int
            The maximum time interval in samples between two data points to be considered part of the same change.
    
    Returns:
        A string showing the result of the hydrograph, stable or unstable.
    """
    # Find location of the first peak
    first_peak_index = find_first_peak(flow)
    # print(first_peak_index)

    
    # Calculate the absolute change in the flow.
    abs_change = abs(flow.diff())
    
    # Calculate the threshold for the minimum change required to be considered an abrupt change.
    change_threshold = (flow.max() - flow.min()) * percent_change
    # print(change_threshold)
    # change_threshold = flow.mean() * percent_change
    # print(change_threshold)
    
    # Initialize a mask of False values to indicate no abrupt changes have been detected yet.
    abrupt_changes = pd.Series(False, index=flow.index)
    
    # Loop over each data point in the flow.
    for i in range(1, len(flow)):
        # If the absolute change is greater than the threshold, mark this data point as the start of an abrupt change.
        if abs_change[i] >= change_threshold:
            abrupt_changes[i] = True
            
            # Keep track of the end of the current change.
            end_of_change = i
            
            # Continue checking subsequent data points to see if they are still part of the same change.
            for j in range(i+1, min(i+max_time_interval, len(flow))):
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

    # Plot the hydrograph with change points detected
    plot_point_change(flow, abrupt_changes)

    # Transform change points array to a list
    ls_abrupt_changes = abrupt_changes.tolist()

    # Calculate the abrupt change points detected that are prior to the first peak 
    ls_abrupt_changes_before_peak = ls_abrupt_changes[0:first_peak_index]

    # Calculate the number of change points prior to the first peak
    unstable_pt_before_peak = ls_abrupt_changes_before_peak.count(1)
    unstable_pt = ls_abrupt_changes.count(1)

    # print(ls_abrupt_changes_before_peak)
    # print(unstable_pt_before_peak)
    # print(unstable_pt)

    # Determine the hydrograph to be stable if all abrupt change points detected are before the first peak - this is to improve metric performance with quick ramp-up in data
    if unstable_pt_before_peak == unstable_pt:
        return "Stable"
    else:
        # Return the hydrograph to be stable if no abrupt change point detected. Otherwise return unstable.
        if unstable_pt == 0:
            return "Stable"
        else:
            return "Unstable"

    