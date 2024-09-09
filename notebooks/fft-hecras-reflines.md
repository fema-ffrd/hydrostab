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

# Testing FFT Stability Method on HEC-RAS Reference Lines Output

```python
from rashdf import RasPlanHdf
```

```python
RAS_PLAN_HDF = '/mnt/c/Users/USTW720127/Downloads/kanawha-ElkMiddle-results_2024-07/ras-results/ElkMiddle-1200/ElkMiddle.p01.hdf'
```

```python
plan_hdf = RasPlanHdf(RAS_PLAN_HDF)
```

```python
plan_hdf.mesh_cell_points().plot()
```

```python
reflines_ds = plan_hdf.reference_lines_timeseries_output()
reflines_ds
```

```python
reflines_flow = reflines_ds["Flow"]
reflines_flow
```

```python
import hydrostab
import xarray as xr

def ufunc_fft_stable(hydrograph) -> bool:
    is_stable, high_freq_prop, power_spectrum, freqs = hydrostab.fft.fft_stable(hydrograph, relative=True)
    return is_stable, high_freq_prop

reflines_flow_stab, reflines_flow_high_freq = xr.apply_ufunc(ufunc_fft_stable, reflines_flow, input_core_dims=[["time"]], output_core_dims=[[], []], vectorize=True)
reflines_flow_stab
```

```python
reflines_flow_high_freq
```

```python
import matplotlib.pyplot as plt

for rid in reflines_ds.refln_id:
    refline_stable = reflines_flow_stab.sel(refln_id=rid)
    refline_high_freq = reflines_flow_high_freq.sel(refln_id=rid)
    refline_flow = reflines_flow.sel(refln_id=rid)
    refline_flow.plot()
    text = "Stable" if refline_stable else "Unstable"
    text += f" {refline_high_freq.values}"
    color = "green" if refline_stable else "red"
    plt.text(x=refline_flow.time.min(), y=refline_flow.max(), s=text, color=color)
    plt.show()
```

```python
reflines_ws = reflines_ds["Water Surface"]
reflines_ws
```

```python
reflines_stability_ws, reflines_ws_high_freq = xr.apply_ufunc(ufunc_fft_stable, reflines_ws, input_core_dims=[["time"]], output_core_dims=[[], []], vectorize=True)
reflines_stability_ws
```

```python
reflines_ws_high_freq
```

```python
for rid in reflines_ds.refln_id:
    refline_stable = reflines_stability_ws.sel(refln_id=rid)
    refline_high_freq = reflines_ws_high_freq.sel(refln_id=rid)
    refline_ws = reflines_ws.sel(refln_id=rid)
    refline_ws.plot()
    text = "Stable" if refline_stable else "Unstable"
    text += f" {refline_high_freq.values}"
    color = "green" if refline_stable else "red"
    plt.text(x=refline_ws.time.min(), y=refline_ws.max(), s=text, color=color)
    plt.show()
```

```python

```
