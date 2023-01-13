"""Pydantic models relating to all endpoint responses."""
from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import BaseModel

from diffcalc_api.models.ub import (
    HklModel,
    MiscutModel,
    PositionModel,
    SphericalCoordinates,
    XyzModel,
)


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

@dataclass
class Orientation:
    """Reference orientation of the sample.

    Similar to diffcalc.ub.reference.Orientation
    """

    h: float
    k: float
    l: float
    x: float
    y: float
    z: float
    pos: PositionModel
    tag: Optional[str]


@dataclass
class Reflection:
    """Reference reflection of the sample.

    Similar to diffcalc.ub.reference.Reflection
    """

    h: float
    k: float
    l: float
    pos: PositionModel
    energy: float
    tag: Optional[str]


class ReflectionResponse(BaseModel):
    """Response for any operation returning a reflection."""

    payload: Reflection

    class Config:
        """Necessary config to make validation easier.

        As this is a response model, there is no need to enforce validation.
        """

        orm_mode = True


class OrientationResponse(BaseModel):
    """Response for any operation returning an orientation."""

    payload: Orientation

    class Config:
        """Necessary config to make validation easier.

        As this is a response model, there is no need to enforce validation.
        """

        orm_mode = True
