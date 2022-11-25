"""API configuration options."""

import logging

from pydantic import BaseSettings

from ._version_git import __version__

release = __version__

# The short X.Y version.
if "+" in release:
    # Not on a tag
    version = "master"
else:
    version = release


class Settings(BaseSettings):
    """Class which gets environment variables.

    Environment variables set to the attributes of this class are automatically
    set to the values of these attributes, and used in the application.
    """

    mongo_url: str = "localhost:27017"
    api_version = version
    logging_level: str = "WARN"
    logging_format: str = "[%(asctime)s] %(levelname)s:%(message)s"


settings = Settings()
try:
    logging.basicConfig(level=settings.logging_level, format=settings.logging_format)
except ValueError:
    logging.basicConfig(level="WARN")
    logging.warn(
        f"{settings.logging_level} is not a valid logging level "
        + "(See logging python library for details). Initializing basic logging."
    )

SAVE_PICKLES_FOLDER = "/"
CONSTRAINTS_WITH_NO_VALUE = {"a_eq_b", "bin_eq_bout", "mu_is_gam", "bisect"}


ALL_CONSTRAINTS = {
    "delta",
    "gam" "qaz",
    "naz",
    "a_eq_b",
    "alpha",
    "beta",
    "psi",
    "bin_eq_bout",
    "betain",
    "betaout",
    "mu",
    "eta",
    "chi",
    "phi",
    "mu_is_gam",
    "bisect",
    "omega",
}
