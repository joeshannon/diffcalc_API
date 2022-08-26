"""Defines interactions with a persistence layer.

Diffraction calculations can only be performed on HklCalculation objects,
which must be persisted.

diffcalc_API.stores.pickling defines a class for persisting them on-file,
diffcalc_API.stores.mongo defines a class for persisting them on mongodb.

This can be extended to any database or persistence model, so long as it follows
the protocol defined in diffcalc_API.stores.protocol.
"""

from . import pickling, protocol

__all__ = ["pickling", "protocol"]
