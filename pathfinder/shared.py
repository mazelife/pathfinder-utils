"""Shared functions and utilities."""
from pathlib import Path


def data_dir() -> Path:
    return Path(__file__).parent / "data"