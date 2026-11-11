# Getting started: FHI-aims support in sisl

There are two git repositories involved. Keep them as two separate
checkouts, side by side.

| Repo | Contains | Where |
|---|---|---|
| **sisl** (fork, branch `fhi-dev`) | the actual reader code (`sisl.io.fhiaims`) | <https://github.com/mbrandbyge-DTU/sisl>, branch `fhi-dev` |
| **fhi-examples** | real FHI-aims test data + demo notebooks | <https://github.com/mbrandbyge-DTU/fhi-examples> |

`fhi-dev` is **not** on `zerothi/sisl` (the real upstream) and not on `main`
of the fork either -- it is a feature branch, not yet reviewed/merged
upstream. Always check it out explicitly.

## 1. Clone sisl and check out `fhi-dev`

```bash
git clone git@github.com:mbrandbyge-DTU/sisl.git
cd sisl
git checkout fhi-dev
```

## 2. Set up a Python environment and install sisl in editable mode

```bash
python3 -m venv ~/my-envs/sisl-fhi-dev
source ~/my-envs/sisl-fhi-dev/bin/activate
pip install -e .          # builds sisl's compiled (Cython) extensions
pip install matplotlib jupyter ipykernel   # for the notebooks
```

Confirm it is actually this checkout that gets imported:

```bash
python -c "import sisl; print(sisl.__file__)"
# -> .../sisl/src/sisl/__init__.py
```

## 3. Clone the test data / notebooks

```bash
git clone git@github.com:mbrandbyge-DTU/fhi-examples.git
```

## 4. Run the notebooks

```bash
source ~/my-envs/sisl-fhi-dev/bin/activate
cd fhi-examples/notebooks
jupyter notebook
```

Each notebook reads one of the sibling directories in `fhi-examples/`
(`cu_bulk_fcc/`, `srtio3_pbe/`, `cu111_slab/`, `srtio3_hse_exx/`) by its
path relative to `fhi-examples/notebooks/` -- no environment variable or
extra setup needed, as long as the two repos sit next to each other, e.g.:

```
~/work/sisl/              <- fhi-dev checked out
~/work/fhi-examples/       <- this repo
```

If you keep them somewhere else, edit the `DATA` path at the top of each
notebook.

## What's in `fhi-examples`

See its own `README.md` for the full layout and what each file is. In
short: one directory per validated system (bulk Cu, a Cu(111) slab, bulk
SrTiO3, and a hybrid-functional SrTiO3 run with exact exchange), each
holding the FHI-aims input (`control.in`/`geometry.in`) and only the small
output files sisl actually reads -- not FHI-aims' full output directory.

## Reading FHI-aims output into sisl, in short

```python
from sisl.io.fhiaims.rs import rsSileFHIaims

d = "../cu_bulk_fcc/"
H = rsSileFHIaims(d + "rs_indices.out").read_hamiltonian()   # Hamiltonian + overlap
S = rsSileFHIaims(d + "rs_indices.out").read_overlap()

# hybrid functional (HSE/PBE0): add the k-resolved exact exchange on top
H = rsSileFHIaims(d + "rs_indices.out").read_hamiltonian(exchange=True, directory=d)
```

`H.geometry` carries the real orbital radial functions whenever the run
had `output basis` in `control.in` (all 4 systems here do); otherwise
orbitals get a placeholder shape (fine for anything that only needs
angular character, e.g. an orbital-resolved PDOS).

## Keeping both repos in sync later

- Pull the latest `fhi-dev`: `git fetch origin && git checkout fhi-dev && git pull`
- Pull the latest test data: `cd fhi-examples && git pull`
- `fhi-dev` is a rebasing/rewriting-prone feature branch (not `main`): if a
  `git pull` ever refuses because history was rewritten upstream, use
  `git fetch origin && git reset --hard origin/fhi-dev` (only if you have
  no local changes you want to keep).
