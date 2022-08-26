"""Pydantic models relating to all endpoint responses."""
from typing import Dict, List

from pydantic import BaseModel

from diffcalc_API.models.ub import HklModel


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


class MillerIndicesResponse(BaseModel):
    """Miller Indices Response.

    Used for any endpoint with an attached service that returns a set of miller
    indices.
    """

    payload: HklModel
