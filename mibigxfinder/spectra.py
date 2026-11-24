# src/mibig_finder/spectra.py
"""MGF loading + MS/MS similarity (modified cosine, cosine)."""

from __future__ import annotations

from pathlib import Path

from matchms import Spectrum, calculate_scores
from matchms.importing import load_ms2_dataset, load_from_parquet
from matchms.similarity import CosineGreedy, ModifiedCosine

from matchms.filtering.default_pipelines import DEFAULT_FILTERS, CLEAN_PEAKS
from matchms.filtering.spectrum_processor import SpectrumProcessor
from matchms.filtering.spectra_processor import ProcessingReport
from matchms.importing import load_from_mgf



similarity_funcs = {
    "modified_cosine": ModifiedCosine,
    "cosine":          CosineGreedy,
}

def load_spectra(path: Path) -> list[Spectrum]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    if p.suffix.lower() == ".mgf":
        return list(load_ms2_dataset(str(p), metadata_harmonization=False))
    if p.suffix.lower() == ".parquet":
        return list(load_from_parquet(str(p)))
    raise ValueError(f"unsupported spectra format: {p.suffix}")

def cleaning_spectra(MGF_FILE, CLEANED_SPECTRA_FILE):
    file_extension = Path(MGF_FILE).suffix.lower()

    if file_extension == ".mgf":
        spectra_list = list(load_ms2_dataset(MGF_FILE))
    elif file_extension == ".parquet":
        spectra_list = list(load_from_parquet(MGF_FILE))
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    print(f"Loaded {len(spectra_list)} spectra from {MGF_FILE}.")

    for idx, s in enumerate(spectra_list):
        if s.get("feature_id") is None:
            s.set("feature_id", idx + 1)

    report = ProcessingReport()
    cleaned = SpectrumProcessor(DEFAULT_FILTERS + CLEAN_PEAKS).process_spectra(
            spectra_list, processing_report=report
        )
    print(report)
    return cleaned


def harmonizing_spectra(MGF_FILE, HARMONIZED_SPECTRA_FILE):
    spectra_list = list(load_from_mgf(MGF_FILE))
    print(f"Loaded {len(spectra_list)} spectra from MGF.")

    for idx, s in enumerate(spectra_list):
        if s.get("feature_id") is None:
            s.set("feature_id", idx + 1)

    report = ProcessingReport()
    harmonized = SpectrumProcessor(DEFAULT_FILTERS).process_spectra(
                spectra_list, processing_report=report
            )
    print(report)
    return harmonized


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