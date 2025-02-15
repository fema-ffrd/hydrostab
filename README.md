# hydrostab
[![CI](https://github.com/fema-ffrd/hydrostab/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/fema-ffrd/hydrostab/actions/workflows/ci.yml)
[![Release](https://github.com/fema-ffrd/hydrostab/actions/workflows/release.yml/badge.svg)](https://github.com/fema-ffrd/hydrostab/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/hydrostab.svg)](https://badge.fury.io/py/hydrostab)

A Python package for analyzing the numerical stability of hydrograph time series data.
Intended to be used with hydrographs from hydrodynamic models, such as
[HEC-RAS](https://www.hec.usace.army.mil/software/hec-ras/).

## Installation

To install from PyPI:
```
pip install hydrostab
```

To install with dependencies for analyzing HEC-RAS model data (`rashdf`):
```
pip install "hydrostab[ras]"
```

To install with dependencies for experimental methods:
```
pip install "hydrostab[exp]"
```

## Methods

### Slope Change
The default and recommended method for stability analysis. This method can be used with flow,
depth, or water surface elevation. It is also indifferent to time, though it assumes that the
hydrograph has a constant timestep. This methods works by measuring the magitude of
slope reversals (+/-) in the hydrograph shape.

Steps:
1. Normalizes hydrograph values to a 0-1 range
2. Computes differences between consecutive values (assuming a constant timestep)
3. Detects sign changes in the differences (i.e., slope reversals)
4. Sums the magnitude of these sign changes
5. Normalizes by the length of the hydrograph (i.e., the number of values)

This produces a score between 0 and 1, where:
- 0.0 indicates perfect stability (no oscillations)
- Higher values indicate more instability
- Default threshold of 0.002 classifies hydrographs as stable/unstable

![stable](https://raw.githubusercontent.com/fema-ffrd/hydrostab/main/docs/stable.png "Stable")
![unstable](https://raw.githubusercontent.com/fema-ffrd/hydrostab/main/docs/unstable.png "Unstable")

More examples: [notebooks/stability-examples.ipynb](notebooks/stability-examples.ipynb)

### Experimental Methods
The following methods are experimental and not recommended for typical production use:

- Abrupt Change Detection: Identifies sudden changes in flow values
- Normalized First Derivative: Analyzes rate of change patterns
- FFT Analysis: Uses Fast Fourier Transforms to identify high-frequency oscillations

## Developer Setup
Create a virtual environment in the project directory:
```
$ python -m venv venv-hydrostab
```

Activate the virtual environment:
```
$ source ./venv-hydrostab/bin/activate
(venv-hydrostab) $
```

Install the package in editable mode:
```
(venv-hydrostab) $ pip install -e .
```

Install dev dependencies:
```
(venv-hydrostab) $ pip install ".[dev]"
```

Install dependencies for notebooks:
```
(venv-hydrostab) $ pip install ".[nb]"
```

Install git hook scripts (used for automatic liniting/formatting)
```
(venv-hydrostab) $ pre-commit install
```

With the virtual environment activated, run the tests:
```
(venv-hydrostab) $ pytest
```

## Usage
### Single Hydrograph
```python
import hydrostab
import pandas as pd

# Load your hydrograph data
df = pd.read_csv("hydrograph.csv")
flow = df["flow"]

# Basic stability check
is_stable = hydrostab.is_stable(flow)

# Get both stability classification and score
is_stable, score = hydrostab.stability(flow)

# Adjust thresholds if needed
is_stable = hydrostab.is_stable(flow, unstable_threshold=0.003, range_threshold=0.2)
```

### HEC-RAS Model Analysis
A couple methods leveraging [rashdf](https://github.com/fema-ffrd/rashdf) are included to assist with analyzing stability of HEC-RAS model outputs.
This requires installation of the `rashdf` library -- either run `pip install rashdf` after installing `hydrostab`, or:

```
pip install hydrostab[ras]
```

#### Reference Lines Hydrograph Stability
```python
>>> from hydrostab.ras import reflines_stability, mesh_cells_stability
>>> from rashdf import RasPlanHdf
>>> plan = RasPlanHdf("ElkMiddle.p04.hdf")
>>> print(plan)
<HDF5 file "ElkMiddle.p04.hdf" (mode r)>
>>> plan.reference_lines_timeseries_output()
<xarray.Dataset> Size: 28kB
Dimensions:        (time: 577, refln_id: 5)
Coordinates:
  * time           (time) datetime64[ns] 5kB 1996-01-14T12:00:00 ... 1996-02-...
  * refln_id       (refln_id) int64 40B 0 1 2 3 4
    refln_name     (refln_id) <U17 340B 'Herold Gage' ... 'DS Sutton Gage'
    mesh_name      (refln_id) <U9 180B 'ElkMiddle' 'ElkMiddle' ... 'ElkMiddle'
Data variables:
    Flow           (time, refln_id) float32 12kB 3.314 758.6 ... 148.9 137.2
    Water Surface  (time, refln_id) float32 12kB 931.0 608.5 ... 776.2 812.0
>>> reflines_stability(plan) # reflines stability as xarray Dataset
<xarray.Dataset> Size: 28kB
Dimensions:                        (time: 577, refln_id: 5)
Coordinates:
  * time                           (time) datetime64[ns] 5kB 1996-01-14T12:00...
  * refln_id                       (refln_id) int64 40B 0 1 2 3 4
    refln_name                     (refln_id) <U17 340B 'Herold Gage' ... 'DS...
    mesh_name                      (refln_id) <U9 180B 'ElkMiddle' ... 'ElkMi...
Data variables:
    Flow                           (time, refln_id) float32 12kB 3.314 ... 137.2
    Water Surface                  (time, refln_id) float32 12kB 931.0 ... 812.0
    Flow Stability Score           (refln_id) float64 40B 0.0007717 ... 0.0104
    Flow is Stable                 (refln_id) bool 5B True True True True False
    Water Surface Stability Score  (refln_id) float64 40B 0.0003811 ... 0.007469
    Water Surface is Stable        (refln_id) bool 5B True True True True False
>>> reflines_stability(plan, gdf=True) # reflines stability as GeoDataFrame
   refln_id         refln_name  mesh_name      type                                           geometry  ... water_surface_stability_score  water_surface_is_stable
0         0        Herold Gage  ElkMiddle  Internal  LINESTRING (4284949.51 6009708.559, 4284382.80...  ...                      0.000381                     True
1         1  Queen Shoals Gage  ElkMiddle  Internal  LINESTRING (4156474.299 5951074.402, 4155756.7...  ...                      0.000124                     True
2         2          Clay Gage  ElkMiddle  Internal  LINESTRING (4211649.866 5955409.88, 4211315.60...  ...                      0.000146                     True
3         3     Frametown Gage  ElkMiddle  Internal  LINESTRING (4261185.452 6013057.623, 4260451.4...  ...                      0.000064                     True
4         4     DS Sutton Gage  ElkMiddle  Internal  LINESTRING (4305558.092 6045936.846, 4305629.2...  ...                      0.007469                    False

[5 rows x 17 columns]
```

#### 2D Mesh Cells Hydrograph Stability
```python
>>> plan.mesh_cells_timeseries_output("ElkMiddle")
<xarray.Dataset> Size: 66MB
Dimensions:                              (time: 577, cell_id: 14188)
Coordinates:
  * time                                 (time) datetime64[ns] 5kB 1996-01-14...
  * cell_id                              (cell_id) int64 114kB 0 1 ... 14187
Data variables:
    Water Surface                        (time, cell_id) float32 33MB 1.092e+...
    Cell Cumulative Precipitation Depth  (time, cell_id) float32 33MB 0.0 ......
Attributes:
    mesh_name:  ElkMiddle
>>> mesh_cells_stability(plan, "ElkMiddle")  # mesh cells stability as xarray Dataset
<xarray.Dataset> Size: 66MB
Dimensions:                              (time: 577, cell_id: 14188)
Coordinates:
  * time                                 (time) datetime64[ns] 5kB 1996-01-14...
  * cell_id                              (cell_id) int64 114kB 0 1 ... 14187
Data variables:
    Water Surface                        (time, cell_id) float32 33MB 1.092e+...
    Cell Cumulative Precipitation Depth  (time, cell_id) float32 33MB 0.0 ......
    Water Surface Stability Score        (cell_id) float64 114kB 0.0 ... 5.65...
    Water Surface is Stable              (cell_id) bool 14kB True True ... True
Attributes:
    mesh_name:  ElkMiddle
>>> mesh_cells_stability(plan, "ElkMiddle", gdf=True) # mesh cells stability as GeoDataFrame
       mesh_name  cell_id                                           geometry  ... water_surface_stability_score  water_surface_is_stable
0      ElkMiddle        0  POLYGON ((4313815.212 6066402.721, 4313815.212...  ...                      0.000000                     True
1      ElkMiddle        1  POLYGON ((4313815.212 6064483.392, 4313815.212...  ...                      0.000000                     True
2      ElkMiddle        2  POLYGON ((4286315.212 6061983.392, 4286149.808...  ...                      0.000000                     True
3      ElkMiddle        3  POLYGON ((4288815.212 6061983.392, 4288815.212...  ...                      0.000000                     True
4      ElkMiddle        4  POLYGON ((4291315.212 6061983.392, 4291315.212...  ...                      0.000175                     True
...          ...      ...                                                ...  ...                           ...                      ...
14183  ElkMiddle    14183  POLYGON ((4154877.704 5951410.744, 4154809.092...  ...                      0.000106                     True
14184  ElkMiddle    14184  POLYGON ((4154877.704 5951410.744, 4154735.661...  ...                      0.000219                     True
14185  ElkMiddle    14185  POLYGON ((4153903.574 5951208.58, 4153939.554 ...  ...                      0.000133                     True
14186  ElkMiddle    14186  POLYGON ((4153903.574 5951208.58, 4153511.347 ...  ...                      0.000074                     True
14187  ElkMiddle    14187  POLYGON ((4153847.847 5950208.646, 4154061.979...  ...                      0.000057                     True

[14188 rows x 13 columns]
```
