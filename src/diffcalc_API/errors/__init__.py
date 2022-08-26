"""
Defines all errors that can be raised when accessing almost all endpoints.

Because some errors arise from persistence retrieval, those are defined in
structures within diffcalc_API.stores instead.
"""

from diffcalc_API.errors import constraints, hkl, ub

__all__ = ["hkl", "ub", "constraints"]
