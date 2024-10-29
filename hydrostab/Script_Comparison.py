import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import os

# Define the oscillation fraction thresholds and corresponding labels
oscillation_thresholds = {
    0.05: "Stable",
    0.10: "Somewhat Stable",
    0.15: "Somewhat Unstable",
    0.20: "Unstable"
}

# Define the standard deviation thresholds and corresponding labels
std_dev_thresholds = {
    5.0: "Stable",
    10.0: "Somewhat Stable",
    25.0: "Somewhat Unstable",
    50.0: "Unstable"
}


def calculate_oscillation_fraction(file_path, rate_of_change_threshold):
    """
    Calculate the oscillation fraction from the hydrograph data.

    Parameters:
    file_path (str): The path to the CSV file containing the hydrograph data.
    rate_of_change_threshold (float): The threshold for the rate of change to consider an oscillation.

    Returns:
    tuple: A tuple containing the oscillation fraction, flow data, rate of change percentage, time data, standard deviation, and inferred time interval in minutes.
    """
    # Read the CSV file
    data = pd.read_csv(file_path)
    
    # Ensure you are working with a copy of the DataFrame slice
    data = data.copy()
    
    # Convert time data to datetime, inferring the format
    data['time'] = pd.to_datetime(data['time'], infer_datetime_format=True, errors='coerce')
    
    # Assuming the hydrograph data is in columns named 'time' and 'flow'
    time_data = data['time']
    flow_data = data['flow']
    
    # Convert negative values in flow_data to 0
    flow_data[flow_data < 0] = 0
    
    # Calculate the mean of the flow data
    mean_flow = np.mean(flow_data)
    
    # Use 10% of the mean value as epsilon
    epsilon = 0.1 * mean_flow
    
    # Infer the time interval in minutes
    time_diffs = time_data.diff().dropna()
    time_interval_minutes = time_diffs.mode().iloc[0].total_seconds() / 60
    
    # Convert time interval from minutes to hours
    time_interval_hour = time_interval_minutes / 60
    
    # Calculate the first derivative (rate of change)
    rate_of_change = np.diff(flow_data, prepend=flow_data[0])
    
    # Normalize the rate of change by the time interval to account for different sampling frequencies, 
    # penalizing higher resolution intervals (e.g., 15 min) more than lower resolution intervals (e.g., 60 min)
    normalized_rate_of_change = rate_of_change / time_interval_hour
    
    # Calculate the percentage change relative to the original data
    # Adding epsilon to avoid division by very small numbers and reduce the impact of small spikes when values are close to 0.
    rate_of_change_percentage = (normalized_rate_of_change / (flow_data + epsilon)) * 100  # Convert to percentage

    # Determine the number of oscillations
    oscillations = np.sum(np.abs(rate_of_change_percentage) > (rate_of_change_threshold * 100))

    # Calculate the oscillation fraction
    oscillation_fraction = oscillations / len(flow_data)

    # Calculate the standard deviation of the rate of change percentage
    std_dev_rate_of_change = np.std(rate_of_change_percentage)

    return oscillation_fraction, flow_data, rate_of_change_percentage, time_data, std_dev_rate_of_change, time_interval_minutes

def plot_hydrograph(file_path, rate_of_change_threshold, oscillation_fraction, flow_data, rate_of_change_percentage, time_data, std_dev_rate_of_change, time_interval_minutes):
    """
    Plot the hydrograph and the rate of change.

    Parameters:
    file_path (str): The path to the CSV file containing the hydrograph data.
    rate_of_change_threshold (float): The threshold for the rate of change to consider an oscillation.
    oscillation_fraction (float): The calculated oscillation fraction.
    flow_data (pd.Series): The flow data from the hydrograph.
    rate_of_change_percentage (np.ndarray): The rate of change percentage.
    time_data (pd.Series): The time data from the hydrograph.
    std_dev_rate_of_change (float): The standard deviation of the rate of change percentage.
    time_interval_minutes (float): The inferred time interval between data points in minutes.
    """
    print("Oscillation Threshold Table:")
    print("----------------------------")
    selected_label_found = False
    for threshold, class_label in sorted(oscillation_thresholds.items(), key=lambda item: item[0]):
        if not selected_label_found and oscillation_fraction <= threshold:
            selected = f" <-- Selected ({oscillation_fraction:.2f})"
            selected_label_found = True
        else:
            selected = ""
        print(f"{threshold:.2f}: {class_label}{selected}")

    print("\nStandard Deviation Threshold Table:")
    print("-----------------------------------")
    selected_label_found = False
    for threshold, class_label in sorted(std_dev_thresholds.items(), key=lambda item: item[0]):
        if not selected_label_found and std_dev_rate_of_change <= threshold:
            selected = f" <-- Selected ({std_dev_rate_of_change:.2f})"
            selected_label_found = True
        else:
            selected = ""
        print(f"{threshold:.2f}: {class_label}{selected}")

    # Determine the labels based on the oscillation fraction and standard deviation
    oscillation_label = "Unstable"  # Default label
    for threshold, class_label in sorted(oscillation_thresholds.items(), key=lambda item: item[0]):
        if oscillation_fraction <= threshold:
            oscillation_label = class_label
            break

    std_dev_label = "Unstable"  # Default label
    for threshold, class_label in sorted(std_dev_thresholds.items(), key=lambda item: item[0]):
        if std_dev_rate_of_change <= threshold:
            std_dev_label = class_label
            break

    # Plot the original hydrograph and the rate of change
    fig, ax1 = plt.subplots(figsize=(10, 4))  # Shrink the plot vertically
    
    ax1.plot(time_data, flow_data, label='Original Hydrograph', color='tab:blue')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Flow', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    
    ax2 = ax1.twinx()
    ax2.plot(time_data, rate_of_change_percentage, label='Rate of Change (%)', color='tab:orange')
    ax2.axhline(y=rate_of_change_threshold * 100, color='r', linestyle='--', label='Positive Threshold')
    ax2.axhline(y=-rate_of_change_threshold * 100, color='b', linestyle='--', label='Negative Threshold')
    ax2.set_ylabel('Rate of Change (%)', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')
        
    # Format x-axis to display both date and time values correctly
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=10))  # Limit the number of ticks on the x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))  # Format to show date and time
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.gcf().autofmt_xdate()  # Auto-format date labels

    fig.tight_layout(rect=[0, 0.1, 1, 0.95])  # Adjust layout to make space for the legend
    fig.subplots_adjust(top=0.85, bottom=0.4)  # Adjust the top and bottom margins to minimize white space
    # Extract the file name without the extension from the file path
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    fig.suptitle(f'Hydrograph Analysis - {file_name}', y=0.99)  # Adjust the y position of the title

    # Add the percentage of oscillations outside of the stability threshold
    plt.figtext(0.5, 0.90, f'Time adjusted oscillations ({time_interval_minutes:.0f} min), exceeding stability threshold: {oscillation_fraction * 100:.2f}% - {oscillation_label}', ha='center', fontsize=10, color='black')
    plt.figtext(0.5, 0.86, f'Standard deviation of rate of change: {std_dev_rate_of_change:.2f} - {std_dev_label}', ha='center', fontsize=10, color='black')
    #plt.figtext(0.5, 0.82, f'Inferred time interval: {time_interval_minutes:.2f} minutes', ha='center', fontsize=10, color='black')

    fig.legend(loc='lower center', ncol=2)  # Place the legend horizontally at the bottom
    plt.show()

    return oscillation_label, std_dev_label

def analyze_and_plot_hydrograph(file_path, rate_of_change_threshold):
    """
    Analyze the hydrograph data and plot the results

    This function calculates the oscillation fraction and plots the hydrograph
    along with the rate of change.

    Parameters:
    file_path (str): The path to the CSV file containing the hydrograph data.
    rate_of_change_threshold (float): The threshold for the rate of change to consider an oscillation.
    """
    # Calculate oscillation fraction
    oscillation_fraction, flow_data, rate_of_change_percentage, time_data, std_dev_rate_of_change, time_interval_minutes = calculate_oscillation_fraction(file_path, rate_of_change_threshold)
    
    # Plot hydrograph
    oscillation_label, std_dev_label = plot_hydrograph(file_path, rate_of_change_threshold, oscillation_fraction, flow_data, rate_of_change_percentage, time_data, std_dev_rate_of_change, time_interval_minutes)

    return oscillation_label, std_dev_label

#%% Point Change

def plot_point_change(signal, abrupt_changes):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(signal, label='signal')

    abrupt_changes = abrupt_changes.astype(int)
    ax.plot(signal[abrupt_changes==1], 'ro', label='abrupt changes')
    
    
# ChatGPT Point Change Detection
def detect_abrupt_changes(data, percent_change, max_time_interval):
    """
    Detect abrupt changes in a time series signal based on the specified parameters.
    
    Parameters:
        signal (pandas.Series): One-dimensional time series signal.
        percent_change (float): The minimum percentage change in the signal range that is considered an abrupt change.
        max_time_interval (int): The maximum time interval in samples between two data points to be considered part of the same change.
    
    Returns:
        pandas.Series: A boolean mask indicating the positions of the abrupt changes in the input signal.
    """

    # Read the CSV file
    data = pd.read_csv(data)
    
    # Ensure you are working with a copy of the DataFrame slice
    data = data.copy()
    
    # Convert time data to datetime, inferring the format
    data['time'] = pd.to_datetime(data['time'], infer_datetime_format=True, errors='coerce')
    
    # Assuming the hydrograph data is in columns named 'time' and 'flow'
    
    signal = data['flow']

    
    # Calculate the absolute change in the signal.
    abs_change = abs(signal.diff())
    
    # Calculate the threshold for the minimum change required to be considered an abrupt change.
    change_threshold = (signal.max() - signal.min()) * percent_change
    print(change_threshold)
    # change_threshold = signal.mean() * percent_change
    # print(change_threshold)
    
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

    plot_point_change(signal, abrupt_changes)

    ls_abrupt_changes = abrupt_changes.tolist()

    unstable_pt = ls_abrupt_changes.count(1)
    # print(unstable_pt)
    
    return unstable_pt

#%% Run Comparison

path = 'C:/Users/USQC714579/Documents/hydrostab/tests/data/hydrographs/DSS_Hydrographs/'
files = []
for i in os.listdir(path):
    if os.path.isfile(os.path.join(path,i)) and i[0].isdigit():
        files.append(i)
        
        
ls_firstDerivative = []
ls_std = []
ls_pt_change = []
i = 0

for f in files:
    f_path = path + f
    print(f_path)

    rate_of_change_threshold = 0.25  # Example threshold

    # Analyze and plot hydrograph
    oscillation_label, std_dev_label = analyze_and_plot_hydrograph(f_path, rate_of_change_threshold)
     
    # Point Change 
    unstable_pt = detect_abrupt_changes(f_path, 0.06, 10)
    
    ls_firstDerivative.append(oscillation_label)
    ls_std.append(std_dev_label)
    ls_pt_change.append(unstable_pt)


    
ls_pt_change_label = []

for i in range(len(ls_pt_change)):
    if ls_pt_change[i] > 1 :
        ls_pt_change_label.append( "Unstable")
    else:
        ls_pt_change_label.append("Stable")

df_hydrograph = pd.DataFrame({'Hydrograph Title' : files,
                              'First Derivative' : ls_firstDerivative,
                              'Std' : ls_std,
                              'Point Change' : ls_pt_change_label }, 
                              columns=['Hydrograph Title','First Derivative', 'Std', 'Point Change'])

