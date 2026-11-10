# src/mibig_finder/database.py
"""Load the reference MGF as a list of matchms spectra. """

#later change this to parquet

from __future__ import annotations

from pathlib import Path

from matchms.importing import load_from_mgf
from matchms import Spectrum


def load(path: Path) -> list[Spectrum]:
    """Load reference library spectra from an MGF file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return list(load_from_mgf(str(path)))