# fhi-examples

Real FHI-aims runs used to validate and demonstrate sisl's FHI-aims reader
(`sisl.io.fhiaims`: `rsSileFHIaims`, `add_exact_exchange`, the `output basis`
orbital reader). Kept in its own git repository, separate from sisl itself,
so sisl's history stays free of large data files.

The reader code lives on the `fhi-dev` branch of
<https://github.com/mbrandbyge-DTU/sisl> (a fork of `zerothi/sisl`). See
`GETTING-STARTED.md` (sent separately) for how the two repositories fit
together and exact commands to clone/run both.

## Layout

| Directory | System | Demonstrates |
|---|---|---|
| `cu_bulk_fcc/` | bulk fcc Cu, 1 atom, 1 species | semi-local H/S, real orbital radial functions |
| `srtio3_pbe/` | bulk SrTiO3, 5 atoms, 3 species | semi-local H/S, multi-species orbital basis |
| `cu111_slab/` | Cu(111) slab, 9 atoms, 1 species | semi-local H/S on a many-atom, one-species system |
| `srtio3_hse_exx/` | bulk SrTiO3, HSE06 hybrid | hybrid exact exchange + real orbitals together |
| `notebooks/` | - | plotting/demo notebooks reading the systems above |

Each system directory contains only what is needed to reproduce the run and
the small output files sisl actually reads -- not FHI-aims' full output
directory:

- `control.in`, `geometry.in` -- the actual FHI-aims input used (reproducible
  with an FHI-aims license/build: `mpirun -np <N> aims.x > aims.out`)
- `aims.out` -- FHI-aims' own log, kept for provenance; not read by sisl
- `rs_indices.out`, `rs_hamiltonian.out`, `rs_overlap.out` -- the
  `output_rs_matrices plain` dump; what `rsSileFHIaims` reads for H/S
- `basis-indices.out` -- per-basis-function `(n, l, m, type)` labeling
- `<type>_<species>_<shell>_<n>_<l>.dat` -- the `output basis` real
  radial-function dump files that `sisl.io.fhiaims.basis` reads. FHI-aims'
  `output basis` also writes many other, much larger internal basis/
  product-basis dumps (free-atom basis, confined basis, RI product basis,
  kinetic-energy parts, ...) that sisl does not use -- those are **not**
  included here.
- `srtio3_hse_exx/` only: `hf_exchange_spin_01_kpt_NNNNNN.csc` -- the raw
  ELSI-CSC k-resolved exact-exchange matrices (`output hf_exchange_mat`)
  that `add_exact_exchange` reads
- `srtio3_pbe/` only: `band1NNN.out` -- FHI-aims' own band-structure dump
  along the path in `control.in`, used in the notebook to cross-check
  sisl's own band structure

## Using these fixtures directly

```python
from sisl.io.fhiaims.rs import rsSileFHIaims

d = "cu_bulk_fcc/"
H = rsSileFHIaims(d + "rs_indices.out").read_hamiltonian()
S = rsSileFHIaims(d + "rs_indices.out").read_overlap()
```

For the hybrid case, add the exact exchange on top:

```python
H = rsSileFHIaims(d + "rs_indices.out").read_hamiltonian(
    exchange=True, directory=d
)
```
