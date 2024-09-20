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
    15.0: "Somewhat Unstable",
    20.0: "Unstable"
}



import pandas as pd
import numpy as np

def calculate_oscillation_fraction(file_path, rate_of_change_threshold, time_interval_minutes):
    """
    Calculate the oscillation fraction from the hydrograph data.

    Parameters:
    file_path (str): The path to the CSV file containing the hydrograph data.
    rate_of_change_threshold (float): The threshold for the rate of change to consider an oscillation.
    time_interval_minutes (float): The time interval between data points in minutes.

    Returns:
    tuple: A tuple containing the oscillation fraction, flow data, rate of change percentage, time data, and standard deviation.
    """
    # Read the CSV file
    data = pd.read_csv(file_path)
    
    # Assuming the hydrograph data is in columns named 'time' and 'flow'
    time_data = pd.to_datetime(data['time'])  # Convert time data to datetime
    flow_data = data['flow']
    
    # Convert negative values in flow_data to 0
    flow_data[flow_data < 0] = 0
    
    # Calculate the mean of the flow data
    mean_flow = np.mean(flow_data)
    
    # Use 10% of the mean value as epsilon
    epsilon = 0.1 * mean_flow
    
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

    return oscillation_fraction, flow_data, rate_of_change_percentage, time_data, std_dev_rate_of_change

def plot_hydrograph(file_path, rate_of_change_threshold, oscillation_fraction, flow_data, rate_of_change_percentage, time_data, std_dev_rate_of_change):
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
    plt.figtext(0.5, 0.90, f'Percentage of time adjusted oscillations outside of the stability threshold: {oscillation_fraction * 100:.2f}% - {oscillation_label}', ha='center', fontsize=10, color='black')
    plt.figtext(0.5, 0.86, f'Standard deviation of rate of change: {std_dev_rate_of_change:.2f} - {std_dev_label}', ha='center', fontsize=10, color='black')

    fig.legend(loc='lower center', ncol=2)  # Place the legend horizontally at the bottom
    plt.show()

def analyze_and_plot_hydrograph(file_path, rate_of_change_threshold, time_interval_minutes):
    """
    Analyze the hydrograph data and plot the results.

    This function calculates the oscillation fraction and plots the hydrograph
    along with the rate of change.

    Parameters:
    file_path (str): The path to the CSV file containing the hydrograph data.
    rate_of_change_threshold (float): The threshold for the rate of change to consider an oscillation.
    time_interval_minutes (float): The time interval between data points in minutes.
    """
    # Calculate oscillation fraction
    oscillation_fraction, flow_data, rate_of_change_percentage, time_data, std_dev_rate_of_change = calculate_oscillation_fraction(file_path, rate_of_change_threshold, time_interval_minutes)
    
    # Plot hydrograph
    plot_hydrograph(file_path, rate_of_change_threshold, oscillation_fraction, flow_data, rate_of_change_percentage, time_data, std_dev_rate_of_change)

if __name__ == "__main__":
    # Example usage
    #file_path = r"tests\data\hydrographs\stable\ElkMiddle_Queen Shoals Gage.csv"
    #file_path = r"tests\data\hydrographs\unstable\ElkMiddle_DS-Sutton-Gage.csv"
    #file_path = r"tests\data\hydrographs\unstable\ElkMiddle_DS-Sutton-Gage_15min.csv"
    #file_path = r"tests\data\hydrographs\stable\Denton_Nov15_RC_Outlet.csv"
    file_path = r"tests\data\hydrographs\stable\Denton_Dec91_RC_Outlet.csv"
    #file_path = r"tests\data\hydrographs\unstable\Denton_Aug2017_1.csv"
    #file_path = r"tests\data\hydrographs\unstable\Denton_Aug2017_2.csv"
    #file_path = r"tests\data\hydrographs\unstable\Denton_Aug2017_3.csv"
    
    rate_of_change_threshold = 0.25  # Example threshold
    time_interval_minutes = 15  # Example time interval in minutes
    
    # Analyze and plot hydrograph
    analyze_and_plot_hydrograph(file_path, rate_of_change_threshold, time_interval_minutes)