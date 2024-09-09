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

# Testing FFT Stability Method on HEC-RAS Mesh Timeseries Output

```python
from rashdf import RasPlanHdf
```

```python
RAS_PLAN_HDF = '/mnt/c/temp/ElkMiddle.p01.hdf'
```

```python
plan_hdf = RasPlanHdf(RAS_PLAN_HDF)
```

```python
plan_hdf.mesh_areas().plot()
```

```python
mesh_name = plan_hdf.mesh_area_names()[0]
cells_ds = plan_hdf.mesh_cells_timeseries_output(mesh_name)
cells_ds
```

```python
cells_ws = cells_ds["Water Surface"]
cells_ws
```

```python
import hydrostab
import xarray as xr

def ufunc_fft_stable(hydrograph) -> bool:
    is_stable, high_freq_prop, power_spectrum, freqs = hydrostab.fft.fft_stable(hydrograph, relative=True)
    return is_stable, high_freq_prop

cells_ws_stab, cells_ws_high_freq = xr.apply_ufunc(ufunc_fft_stable, cells_ws, input_core_dims=[["time"]], output_core_dims=[[], []], vectorize=True)
cells_ws_stab
```

```python
cells_ws_high_freq
```

```python
cell_polygons = plan_hdf.mesh_cell_polygons()
cell_polygons = cell_polygons.join(cells_ws_stab.rename("stable").to_dataframe(), on=["cell_id"])
cell_polygons = cell_polygons.join(cells_ws_high_freq.rename("high_freq").to_dataframe(), on=["cell_id"])
cell_polygons.to_parquet("/mnt/c/temp/elkmiddle-stability.parquet")
```

```python
cell_polygons.plot(column="stable", legend=True, figsize=(15, 10))
```

```python
cell_polygons.plot(column="high_freq", legend=True, figsize=(15, 10))
```

```python

```
