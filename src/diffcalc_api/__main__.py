"""Entrypoint to this library."""
from argparse import ArgumentParser

from uvicorn import run

from . import __version__

__all__ = ["main"]


def main(args=None):
    """Start the fastAPI server, or query the version of the API."""
    parser = ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(args)
    run("diffcalc_api.server:app", host="0.0.0.0")


if __name__ == "__main__":
    main()
