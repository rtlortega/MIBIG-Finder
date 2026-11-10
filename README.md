# MIBiG-Finder

Match MS/MS spectra and chemical structures against a MIBiG-linked reference library.

Reference library is built in [MIBIG-Spectra-Lib](https://github.com/vdhooftcompmet/MIBIG-Spectra-Lib). This repo is retrieval only.

## Install

```bash
git clone https://github.com/vdhooftcompmet/mibig-finder.git
cd mibig-finder
pip install -r requirements-dev.txt    # matchms dev branch
pip install -e .
```

Python ≥ 3.11. For `--fps map4`: `pip install map4 tmap`.

## Run

Spectra matching:

```bash
mibig-finder spectra -q query.mgf -d library.mgf -o out/
```

Structure matching:

```bash
mibig-finder structure -q structures.tsv -d library.mgf -o out/
```

Options: `--tolerance` (0.02), `--similarity` (modified_cosine | cosine_flash), `--top-n` (2), `--sim-threshold` (0.7), `--fps` (morgan[,map4,rdkit]).

Outputs: `*_matches.csv` and `*_matches.parquet` in `--out-dir`.

## Input expectations

Reference MGF metadata per spectrum: `SMILES`, `INCHIKEY`, `BGC_MATCH`, `BGC_SIMILARITY`, `SCANS`.

Structure TSV: two columns, `id` and `smiles`, header row.

### *Structure input can also be** — 
one SMILES per line:
CCO
c1ccccc1O
CC(=O)Oc1ccccc1C(=O)O

Or a TSV/CSV with a `smiles` column (and optional `id`).


## Python API

```python
from mibig_finder.config import SpectraSearchConfig
from mibig_finder.services import search_spectra

df = search_spectra(SpectraSearchConfig(query=..., database=..., sim_threshold=0.7))
```

Same pattern for `search_structures` / `StructureSearchConfig`.

## Test data

`tests/fixtures/` — 20-spectra library, 10-spectra query, 10 SMILES. Five of each are copies of library entries, so you should see ≈1.0 self-matches.

```bash
mibig-finder spectra -q tests/fixtures/query.mgf -d tests/fixtures/library.mgf -o out/
```

## Layout
src/mibig_finder/
├── cli.py
├── config.py # typed configs
├── database.py # load reference MGF
├── spectra.py # MGF + similarity
├── chem.py # fingerprints + Tanimoto
└── services.py # search_spectra, search_structures

Early development — API may change.
