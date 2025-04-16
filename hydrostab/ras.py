"""Utilities for working with HEC-RAS model data."""

import geopandas as gpd
from rashdf import RasPlanHdf
import xarray as xr

from typing import Union

import hydrostab


def _reformat_var_name(var_name: str) -> str:
    """Reformat variable name for Pandas DataFrame.

    Parameters
    ----------
    var_name : str
        Variable name to reformat

    Returns
    -------
    str
        Reformatted variable name in lowercase with spaces replaced by underscores
    """
    return var_name.lower().replace(" ", "_")


def _calculate_stability(
    dataset: xr.Dataset,
    variables: list[str],
    unstable_threshold: float,
    range_threshold: float,
) -> tuple[xr.Dataset, list[str]]:
    """Calculate stability scores and flags for given variables in a dataset.

    Parameters
    ----------
    dataset : xr.Dataset
        Dataset containing variables to analyze
    variables : list[str]
        List of variable names to check for stability
    unstable_threshold : float
        Threshold above which a stability score indicates instability
    range_threshold : float
        Threshold for range normalization in stability calculation

    Returns
    -------
    tuple[xr.Dataset, list[str]]
        Modified dataset with stability scores and flags, and list of added variable names
    """
    stability_vars = []
    for var in dataset.data_vars:
        if var in variables:
            da = dataset[var]
            da_scores = xr.apply_ufunc(
                hydrostab.stability_score,
                da,
                input_core_dims=[["time"]],
                kwargs={"range_threshold": range_threshold},
                vectorize=True,
            )
            da_stable = da_scores < unstable_threshold
            stability_score_var = var + " Stability Score"
            stability_var = var + " is Stable"
            stability_vars.extend([stability_score_var, stability_var])
            dataset[stability_score_var] = da_scores
            dataset[stability_var] = da_stable
    return dataset, stability_vars


def reflines_stability(
    plan_hdf: RasPlanHdf,
    unstable_threshold: float = 0.002,
    range_threshold: float = 0.1,
    gdf: bool = False,
) -> Union[xr.Dataset, gpd.GeoDataFrame]:
    """Calculate stability metrics for reference lines.

    Parameters
    ----------
    plan_hdf : RasPlanHdf
        HEC-RAS plan HDF file object
    unstable_threshold : float, optional
        Threshold above which a stability score indicates instability, by default 0.002
    range_threshold : float, optional
        Threshold for range normalization in stability calculation, by default 0.1
    gdf : bool, optional
        Return results as GeoDataFrame if True, by default False

    Returns
    -------
    Union[xr.Dataset, gpd.GeoDataFrame]
        Dataset or GeoDataFrame containing stability metrics
    """
    ds_reflines = plan_hdf.reference_lines_timeseries_output()
    ds_reflines, stability_vars = _calculate_stability(
        ds_reflines, ["Flow", "Water Surface"], unstable_threshold, range_threshold
    )

    if gdf:
        gdf_reflines = plan_hdf.reference_lines()
        for stabvar in stability_vars:
            gdf_reflines[_reformat_var_name(stabvar)] = ds_reflines[stabvar].to_series()
        return gdf_reflines
    return ds_reflines


def refpoints_stability(
    plan_hdf: RasPlanHdf,
    unstable_threshold: float = 0.002,
    range_threshold: float = 0.1,
    gdf: bool = False,
) -> Union[xr.Dataset, gpd.GeoDataFrame]:
    """Calculate stability metrics for reference points.

    Parameters
    ----------
    plan_hdf : RasPlanHdf
        HEC-RAS plan HDF file object
    unstable_threshold : float, optional
        Threshold above which a stability score indicates instability, by default 0.002
    range_threshold : float, optional
        Threshold for range normalization in stability calculation, by default 0.1
    gdf : bool, optional
        Return results as GeoDataFrame if True, by default False

    Returns
    -------
    Union[xr.Dataset, gpd.GeoDataFrame]
        Dataset or GeoDataFrame containing stability metrics
    """
    ds_refpoints = plan_hdf.reference_points_timeseries_output()
    ds_refpoints, stability_vars = _calculate_stability(
        ds_refpoints, ["Flow", "Water Surface"], unstable_threshold, range_threshold
    )

    if gdf:
        gdf_refpoints = plan_hdf.reference_points()
        for stabvar in stability_vars:
            gdf_refpoints[_reformat_var_name(stabvar)] = ds_refpoints[
                stabvar
            ].to_series()
        return gdf_refpoints
    return ds_refpoints


def mesh_cells_stability(
    plan_hdf: RasPlanHdf,
    mesh_name: str,
    unstable_threshold: float = 0.002,
    range_threshold: float = 0.1,
    gdf: bool = False,
) -> Union[xr.Dataset, gpd.GeoDataFrame]:
    """Calculate stability metrics for mesh cells.

    Parameters
    ----------
    plan_hdf : RasPlanHdf
        HEC-RAS plan HDF file object
    mesh_name : str
        Name of the mesh to analyze
    unstable_threshold : float, optional
        Threshold above which a stability score indicates instability, by default 0.002
    range_threshold : float, optional
        Threshold for range normalization in stability calculation, by default 0.1
    gdf : bool, optional
        Return results as GeoDataFrame if True, by default False

    Returns
    -------
    Union[xr.Dataset, gpd.GeoDataFrame]
        Dataset or GeoDataFrame containing stability metrics
    """
    ds_mesh = plan_hdf.mesh_cells_timeseries_output(mesh_name)
    ds_mesh, stability_vars = _calculate_stability(
        ds_mesh, ["Water Surface"], unstable_threshold, range_threshold
    )

    if gdf:
        gdf_mesh = plan_hdf.mesh_cell_polygons()
        gdf_mesh = gdf_mesh[gdf_mesh["mesh_name"] == mesh_name]
        for stabvar in stability_vars:
            gdf_mesh[_reformat_var_name(stabvar)] = ds_mesh[stabvar].to_series()
        return gdf_mesh
    return ds_mesh
