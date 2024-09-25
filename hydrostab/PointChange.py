import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from astropy.stats import bootstrap as bootstrap
from statsmodels.tsa.seasonal import seasonal_decompose

# ChatGPT Point Change Detection
def detect_abrupt_changes(signal, percent_change, max_time_interval):
    """
    Detect abrupt changes in a time series signal based on the specified parameters.
    
    Parameters:
        signal (pandas.Series): One-dimensional time series signal.
        percent_change (float): The minimum percentage change in the signal range that is considered an abrupt change.
        max_time_interval (int): The maximum time interval in samples between two data points to be considered part of the same change.
    
    Returns:
        pandas.Series: A boolean mask indicating the positions of the abrupt changes in the input signal.
    """
    # Calculate the absolute change in the signal.
    abs_change = abs(signal.diff())
    
    # Calculate the threshold for the minimum change required to be considered an abrupt change.
    change_threshold = (signal.max() - signal.min()) * percent_change
    
    # Initialize a mask of False values to indicate no abrupt changes have been detected yet.
    abrupt_changes = pd.Series(False, index=signal.index)
    
    # Loop over each data point in the signal.
    for i in range(1, len(signal)):
        # If the absolute change is greater than the threshold, mark this data point as the start of an abrupt change.
        if abs_change[i] >= change_threshold:
            abrupt_changes[i] = True
            
            # Keep track of the end of the current change.
            end_of_change = i
            
            # Continue checking subsequent data points to see if they are still part of the same change.
            for j in range(i+1, min(i+max_time_interval, len(signal))):
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
    
    return abrupt_changes

path_unstable = "C:/Users/USQC714579/Documents/hydrostab/tests/data/hydrographs/unstable/Denton_Aug2017_3.csv"
df_unstable = pd.read_csv(path_unstable)

#Unstable Flow Example 
abrupt_changes_stable = detect_abrupt_changes(df_unstable['flow'], 0.06, 10)

print(abrupt_changes_stable)
print(np.sum(abrupt_changes_stable))

# Plot the time series
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_unstable['flow'], label='signal')

abrupt_changes_stable = abrupt_changes_stable.astype(int)
ax.plot(df_unstable['flow'][abrupt_changes_stable==1], 'ro', label='abrupt changes')