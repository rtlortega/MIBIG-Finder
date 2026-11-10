# src/mibig_finder/spectra.py
"""MGF loading + MS/MS similarity (modified cosine, cosine)."""

from __future__ import annotations

from pathlib import Path

from matchms import Spectrum, calculate_scores
from matchms.importing import load_from_mgf #, load_from_parquet
from matchms.similarity import CosineGreedy, ModifiedCosine

from matchms.filtering.default_pipelines import DEFAULT_FILTERS, CLEAN_PEAKS
from matchms.filtering.SpectrumProcessor import SpectrumProcessor
from matchms.importing import load_from_mgf



similarity_funcs = {
    "modified_cosine": ModifiedCosine,
    "cosine":          CosineGreedy,
}


def load_mgf(path: Path) -> list[Spectrum]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return list(load_from_mgf(str(path), metadata_harmonization=False))   # ← keep custom keys


# def load_from_parquet(path: Path) -> list[Spectrum]: 
#     path = Path(path)
#     if not path.exists():
#         raise FileNotFoundError(path)
#     return list(load_from_parquet(str(path)))

def cleaning_spectra(MGF_FILE, CLEANED_SPECTRA_FILE):
    spectra_list = list(load_from_mgf(MGF_FILE))
    print(f"Loaded {len(spectra_list)} spectra from MGF.")

    for idx, s in enumerate(spectra_list):
        if s.get("feature_id") is None:
            s.set("feature_id", idx + 1)

    cleaned_spectra, _ = SpectrumProcessor(DEFAULT_FILTERS + CLEAN_PEAKS).process_spectra(
        spectra_list,
        cleaned_spectra_file=CLEANED_SPECTRA_FILE,
        create_report=True,
    )
    print("Spectra left after cleaning:", len(cleaned_spectra))
    return cleaned_spectra


def harmonizing_spectra(MGF_FILE, HARMONIZED_SPECTRA_FILE):
    spectra_list = list(load_from_mgf(MGF_FILE))
    print(f"Loaded {len(spectra_list)} spectra from MGF.")

    for idx, s in enumerate(spectra_list):
        if s.get("feature_id") is None:
            s.set("feature_id", idx + 1)

    harmonized_spectra, _ = SpectrumProcessor(DEFAULT_FILTERS).process_spectra(
        spectra_list,
        cleaned_spectra_file=HARMONIZED_SPECTRA_FILE,
        create_report=True,
    )
    print("Spectra left after harmonization:", len(harmonized_spectra))
    return harmonized_spectra


def score(
    queries: list[Spectrum],
    references: list[Spectrum],
    similarity: str = "modified_cosine",
    tolerance: float = 0.02,
):
    """Return a matchms Scores object. Iterate for (query, ref, (score, n_matches))."""
    if similarity not in similarity_funcs:
        raise ValueError(
            f"unknown similarity: {similarity!r}. choose from {list(SIMILARITY_FUNCS)}"
        )
    sim = similarity_funcs[similarity](tolerance=tolerance)
    return calculate_scores(references, queries, similarity_function=sim)