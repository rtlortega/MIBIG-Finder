# src/mibig_finder/chem.py
"""SMILES canonicalisation, fingerprints (Morgan count, MAP4), Tanimoto."""

from __future__ import annotations

import numpy as np
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, rdFingerprintGenerator


# ---------------------------------------------------------------------------
# Standardisation
# ---------------------------------------------------------------------------

def canonical_smiles(smiles: str) -> str | None:
    """Return canonical SMILES, or None if RDKit can't parse."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True)


def inchikey14(smiles: str) -> str | None:
    """First 14 chars of the InChIKey (ignores stereo/charge layers)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    full = Chem.MolToInchiKey(mol)
    return full.split("-")[0] if full else None


# ---------------------------------------------------------------------------
# Fingerprints
# ---------------------------------------------------------------------------

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=4096)


def morgan_count(smiles: str) -> np.ndarray | None:
    """Morgan count fingerprint: radius=2, 4096 bits, counts (not bits)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    fp = morgan_gen.GetCountFingerprint(mol)
    arr = np.zeros((4096,), dtype=np.int32)
    DataStructs.ConvertToNumpyArray(fp, arr)
    return arr


def map4(smiles: str, dim: int = 1024, radius: int = 2) -> np.ndarray | None:
    """MAP4 fingerprint (MinHashed atom-pair, circular). Requires `map4` package."""
    try:
        from map4 import MAP4Calculator
    except ImportError as e:
        raise ImportError(
            "MAP4 not installed. `pip install map4` (and `tmap`)."
        ) from e

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    calc = MAP4Calculator(dimensions=dim, radius=radius, is_counted=False, is_folded=True)
    return np.asarray(calc.calculate(mol), dtype=np.int64)


FP_FUNCS = {
    "morgan": morgan_count,
    "map4": map4,
}


def compute_fp(smiles: str, kind: str) -> np.ndarray | None:
    if kind not in FP_FUNCS:
        raise ValueError(f"unknown fingerprint: {kind!r}. choose from {list(FP_FUNCS)}")
    return FP_FUNCS[kind](smiles)


# Similarity 
def tanimoto(a: np.ndarray, b: np.ndarray) -> float:
    """Tanimoto similarity for count or binary vectors (same length)."""
    if a.shape != b.shape:
        raise ValueError(f"fp shape mismatch: {a.shape} vs {b.shape}")
    inter = np.minimum(a, b).sum()
    union = np.maximum(a, b).sum()
    return float(inter / union) if union else 0.0