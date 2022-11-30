"""Pydantic models relating to all endpoint responses."""
from typing import Dict, List

from pydantic import BaseModel

from diffcalc_api.models.ub import HklModel, MiscutModel, SphericalCoordinates, XyzModel
from diffcalc_api.types import Orientation, Reflection


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


class SphericalResponse(BaseModel):
    """Spherical coordinate response model.

    Returns a payload in spherical coordinates.
    """

    payload: SphericalCoordinates


class ReciprocalSpaceResponse(BaseModel):
    """Reciprocal space coordinate response model.

    Returns a payload in reciprocal space (hkl) coordinates.
    """

    payload: HklModel


class RealSpaceResponse(BaseModel):
    """Reciprocal space coordinate response model.

    Returns a payload in xyz coordinates.
    """

    payload: XyzModel


class MiscutResponse(BaseModel):
    """Response for any operation returning miscuts.

    Only used for endpoints in ub routes.
    """

    payload: MiscutModel


class ReflectionResponse(BaseModel):
    payload: Reflection

    class Config:
        orm_mode = True


class OrientationResponse(BaseModel):
    payload: Orientation

    class Config:
        orm_mode = True
