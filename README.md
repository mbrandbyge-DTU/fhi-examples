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
- `srtio3_pbe/` and `srtio3_hse_exx/` only: `band1NNN.out` -- FHI-aims' own
  band-structure dump along the path in `control.in`. The one in
  `srtio3_pbe/` is used in `notebooks/02_srtio3_bands_crosscheck.ipynb` to
  cross-check sisl's own band structure; the one in `srtio3_hse_exx/` is
  included for completeness (same kind of file) but not currently read by
  any notebook -- `03_srtio3_hse_exx_gap.ipynb` compares semi-local vs.
  hybrid eigenvalues directly, not against this dump.

## Notebooks

Each notebook is real, executed output against the real fixtures above (not
a mockup) -- plots and printed numbers are baked in, so they can be read
without re-running anything, and re-run to regenerate if the reader ever
changes.

| Notebook | What it shows |
|---|---|
| `01_cu_bulk_bands.ipynb` | Band structure of bulk Cu along the standard FCC path -- the textbook narrow 3d manifold crossed by a free-electron-like 4s band. Sanity check, no external cross-check available for this system. |
| `02_srtio3_bands_crosscheck.ipynb` | The strongest validation here: sisl's band structure overlaid directly on FHI-aims' *own* independently-computed band dump along the same path. Agreement is ~1e-6 eV near the Fermi level and ~1e-3 eV even for the deepest core levels (~-16000 eV) -- this checks the physics in the reconstructed H/S, not just that the reader runs. |
| `03_srtio3_hse_exx_gap.ipynb` | Semi-local vs. hybrid (HSE06 + exact exchange) eigenvalues at the 8 SCF k-points of a real hybrid-functional run, showing the expected gap-opening effect of exact exchange -- demonstrates the real-orbital-basis and hybrid-EXX features composing correctly. |

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
