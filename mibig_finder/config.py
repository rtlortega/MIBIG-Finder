# src/mibig_finder/config.py
"""Typed configs for each subcommand. CLI and future FastAPI both build these."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SpectraSearchConfig(BaseModel):
    query: Path
    database: Path                                   # local MGF for now
    tolerance: float = 0.02
    similarity: Literal["modified_cosine", "cosine_flash"] = "modified_cosine"
    top_n: int = 2
    sim_threshold: float = 0.7
    clean: bool = False
    out_dir: Path = Path("./out")

    @field_validator("query", "database")
    @classmethod
    def _file_ok(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"file not found: {v}")
        if v.suffix.lower() != ".mgf":
            raise ValueError(f"expected .mgf, got {v.suffix}")
        return v

    @field_validator("tolerance")
    @classmethod
    def _tolerance_range(cls, v: float) -> float:
        if not (0 < v <= 1.0):
            raise ValueError("tolerance must be in (0, 1.0]")
        return v

    @field_validator("sim_threshold")
    @classmethod
    def _threshold_range(cls, v: float) -> float:
        if not (0 <= v <= 1):
            raise ValueError("sim_threshold must be in [0, 1]")
        return v


class StructureSearchConfig(BaseModel):
    query: Path
    database: Path                                   # local MGF (SMILES pulled from spectrum metadata)
    fps: list[Literal["morgan", "map4", "rdkit"]] = Field(default_factory=lambda: ["morgan"])
    similarity_threshold: float = 0.7
    out_dir: Path = Path("./out")

    @field_validator("query")
    @classmethod
    def _query_ok(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"file not found: {v}")
        if v.suffix.lower() not in {".tsv", ".csv", ".smi", ".txt"}:
            raise ValueError(f"expected .tsv/.csv/.smi/.txt, got {v.suffix}")
        return v

    @field_validator("database")
    @classmethod
    def _db_ok(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"file not found: {v}")
        if v.suffix.lower() != ".mgf":
            raise ValueError(f"expected .mgf, got {v.suffix}")
        return v

    @field_validator("similarity_threshold")
    @classmethod
    def _threshold_range(cls, v: float) -> float:
        if not (0 <= v <= 1):
            raise ValueError("similarity_threshold must be in [0, 1]")
        return v