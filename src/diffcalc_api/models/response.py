"""Pydantic models relating to all endpoint responses."""
from typing import Dict, List, Union

from pydantic import BaseModel

from diffcalc_api.models.ub import HklModel, MiscutModel, SphericalCoordinates, XyzModel


class InfoResponse(BaseModel):
    """Used for all HTTP requests that simply change persisted state."""

    message: str


class StringResponse(BaseModel):
    """Used for some HTTP get requests.

    InfoResponse models should only be returned to inform the client that
    a persisted state has changed. The StringResponse model however addresses
    the case where a HTTP get request needs to return a string. The distinction
    is minor but important.
    """

    payload: str


class ArrayResponse(BaseModel):
    """Used for UB calculation retrieval."""

    payload: List[List[float]]


class ScanResponse(BaseModel):
    """Used for all scans in hkl endpoints."""

    payload: Dict[str, List[Dict[str, float]]]


class DiffractorAnglesResponse(BaseModel):
    """Diffractor Angles Response.

    Used for any endpoint with an attached service that returns a set of diffractor
    angles.
    """

    payload: List[Dict[str, float]]


class CoordinateResponse(BaseModel):
    """Coordinate response model.

    Returns coordinates, in three dimensions, for a given coordinate system.
    Supported systems include spherical coordinates, reciprocal and real space.
    """

    payload: Union[SphericalCoordinates, HklModel, XyzModel]


class MiscutResponse(BaseModel):
    """Response for any operation returning miscuts.

    Only used for endpoints in ub routes.
    """

    payload: MiscutModel
