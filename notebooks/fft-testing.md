---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Prototyping Fast Fourier Transforms for Detecting Hydrograph Instabilities

```python
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from IPython.display import display
import ipywidgets as widgets

import hydrostab
```

```python
HYDROGRAPHS = Path("../tests/data/hydrographs")
```

```python
import warnings

def check_fft(csv_path: Path, sampling_rate: float = 1.0, unstable_period: float = 10.0, threshold: float = 0.2):
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    time_diffs = df["time"].diff()
    time_diff = time_diffs.min()
    max_time_diff = time_diffs.max()
    if max_time_diff != time_diff:
        print(f"Timestep range: {time_diff} - {max_time_diff}")
        warnings.warn("FFT requires a regular time series.")
    print(f"Timestep: {time_diff}")    
    
    is_stable, unstable_proportion, power_spectrum, freqs = hydrostab.fft.fft_stable(df["flow"],
                                                                                     sampling_rate=sampling_rate,
                                                                                     unstable_period=unstable_period,
                                                                                     threshold=threshold,
                                                                                     normalize=True,
                                                                                     relative=False,
                                                                                    )

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))

    category = "Unstable" if "unstable" in str(csv_path) else "Stable"
    print(f"Stable: {is_stable} {'✅' if is_stable else '❌'}")
    print(f"Unstable period: {unstable_period}")
    print(f"Threshold: {threshold}")
    print(f"Unstable proportion: {unstable_proportion}")

    # Plot hydrograph
    df.plot(x="time", ax=axes[0], title=f"Hydrograph - {str(csv_path.name)} ({category})", marker=".")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Flow")

    # Plot power spectrum
    axes[1].plot(1/freqs, power_spectrum)
    axes[1].set_title("Hydrograph Power Spectrum")
    axes[1].set_xlabel("Period")
    axes[1].set_ylabel("Power")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].axvline(x=unstable_period, color="r", linestyle="--", label="Unstable period")

    return fig, axes
```

```python
stable_csv = HYDROGRAPHS.glob("stable/*.csv")
unstable_csv = HYDROGRAPHS.glob("unstable/*.csv")

options = []

for category in ["stable", "unstable"]:
    csv_paths = HYDROGRAPHS.glob(f"{category}/*.csv")
    for p in csv_paths:
        name = f"{p.name} ({category})"
        options.append((name, p))

output = widgets.Output()
        
select_hydrograph = widgets.Dropdown(
    options=options,
    value=options[0][1],
    description="Hydrograph:",
    disabled=False,
)
# display(select_hydrograph)

input_sampling_rate = widgets.FloatText(
    value=1.0,
    description='Sampling rate:',
    disabled=False
)
# display(input_sampling_rate)

input_unstable_period = widgets.FloatSlider(
    value=10.0,
    min=0.0,
    max=50.0,
    step=0.1,
    description='Unstable period:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
)
# display(input_threshold_period)

input_threshold = widgets.FloatSlider(
    value=0.2,
    min=0.0,
    max=1.0,
    step=0.01,
    description='Threshold:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='.2f',
)
# display(input_high_freq_threshold)

btn_analyze = widgets.Button(
    description='Analyze',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Run FFT Analysis',
    # icon='check' # (FontAwesome names without the `fa-` prefix)
)
# output = widgets.Output()


def on_analyze_clicked(b):
    with output:
        output.clear_output()
        hydrograph_csv_path = select_hydrograph.value
        sampling_rate = input_sampling_rate.value
        unstable_period = input_unstable_period.value
        threshold = input_threshold.value
        fig, ax = check_fft(hydrograph_csv_path, sampling_rate=sampling_rate, unstable_period=unstable_period, threshold=threshold)
        display(fig)

btn_analyze.on_click(on_analyze_clicked)

display(select_hydrograph, input_sampling_rate, input_threshold_period, input_high_freq_threshold, btn_analyze, output)
```

```python

```

```python

```
