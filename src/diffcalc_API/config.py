import logging

from pydantic import BaseSettings

from ._version_git import __version__

logging.basicConfig(
    level=logging.DEBUG, format="[%(asctime)s] %(levelname)s:%(message)s"
)
release = __version__

# The short X.Y version.
if "+" in release:
    # Not on a tag
    version = "master"
else:
    version = release


class Settings(BaseSettings):
    mongo_url: str = "localhost:27017"
    api_version = version


SAVE_PICKLES_FOLDER = "/"
VECTOR_PROPERTIES = ["n_hkl", "n_phi", "surf_nhkl", "surf_nphi"]
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
