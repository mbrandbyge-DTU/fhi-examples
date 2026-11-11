"""Build the FHI-aims -> sisl benchmark/validation PDF report."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
    Image,
)

OUT = "/home/mabr2/build/fhi-aims2sisl/fhiaims-sisl-benchmarks.pdf"
BANDS_PNG = "/home/mabr2/build/fhi-aims2sisl/srtio3_bands_crosscheck.png"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("H1", parent=styles["Heading1"], spaceBefore=18, spaceAfter=8))
styles.add(ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1a3c6e")))
styles.add(ParagraphStyle("Body", parent=styles["Normal"], spaceAfter=6, leading=14))
styles.add(ParagraphStyle("Caption", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#555555"), spaceAfter=10))
styles.add(ParagraphStyle("CellHead", parent=styles["Normal"], fontSize=8.5, leading=10.5, textColor=colors.white, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8.5, leading=10.5))

story = []


def sup(s):
    """A reportlab <super> tag -- never a raw Unicode superscript character
    (base-14 PDF fonts render those as solid black boxes)."""
    return f"<super>{s}</super>"


def h1(t):
    story.append(Paragraph(t, styles["H1"]))


def h2(t):
    story.append(Paragraph(t, styles["H2"]))


def body(t):
    story.append(Paragraph(t, styles["Body"]))


def caption(t):
    story.append(Paragraph(t, styles["Caption"]))


def table(headers, rows, col_widths=None):
    # every cell goes through Paragraph so <super>/<sub> tags and entities
    # (&times; &minus; &mdash; ...) are actually parsed, not drawn as literal text
    data = [[Paragraph(h, styles["CellHead"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(c, styles["Cell"]) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5fa")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 10))


def bullets(items):
    story.append(
        ListFlowable(
            [ListItem(Paragraph(t, styles["Body"])) for t in items],
            bulletType="bullet",
            leftIndent=14,
        )
    )
    story.append(Spacer(1, 6))


# ---------------------------------------------------------------- title ----
story.append(Paragraph("FHI-aims &rarr; sisl Reader: Benchmark and Validation Report", styles["Title"]))
caption(
    "Branch <font face='Courier'>fhi-dev</font> of the sisl fork "
    "(github.com/mbrandbyge-DTU/sisl), 12 commits ahead of "
    "<font face='Courier'>main</font>. Covers <font face='Courier'>sisl.io.fhiaims</font>: "
    "<font face='Courier'>rsSileFHIaims</font> (semi-local H/S and real orbital basis) and "
    "<font face='Courier'>add_exact_exchange</font> (hybrid-functional exact exchange). "
    "Not yet merged upstream."
)
body(
    "This report lists every real-FHI-aims-data check performed while building this reader, "
    "the exact pass criterion used, and the measured number &mdash; including the one real bug "
    "found and fixed along the way. It is not a sales pitch: where a result is a documented "
    "limitation rather than a defect, that is stated as such, and the &quot;not yet verified&quot; "
    "section at the end is deliberately explicit about remaining gaps."
)

# ============================================================ section 1 ===
h1("1. Semi-local Hamiltonian / Overlap reader")
body(
    "<b>What:</b> <font face='Courier'>rsSileFHIaims</font> reads FHI-aims' "
    "<font face='Courier'>output_rs_matrices plain</font> export, a packed upper-triangle "
    "(i_basis_1 &le; i_basis_2) sparse list per lattice cell, reconstructs the missing half "
    "via H(R)<sub>&mu;&nu;</sub> = H(&minus;R)<sub>&nu;&mu;</sub>, and builds the "
    "<font face='Courier'>Hamiltonian</font>/<font face='Courier'>Overlap</font> through sisl's "
    "public <font face='Courier'>fromsp</font> construction path (not direct "
    "<font face='Courier'>SparseCSR</font> attribute assignment)."
)
body(
    "<b>Pass criteria:</b> Hermiticity of H(k) and S(k), positive-definiteness of S(k), at "
    "several k; no duplicate (row, col, cell) entry (the packed-triangle assumption not "
    "violated); Cu's known atomic-level ordering; a TSHS write/re-read round trip."
)

table(
    ["System", "Atoms / species", "Orbitals", "max |H(k)-H(k)*| / |S(k)-S(k)*| (* = conjugate transpose)", "min eig(S(k))"],
    [
        ["Cu bulk FCC", "1 / 1", "31", f"5.7&times;10{sup('-14')} eV", "2.9&times;10" + sup("-4")],
        ["Cu(111) slab", "9 / 1", "279", f"5.7&times;10{sup('-14')} eV", "1.7&times;10" + sup("-4")],
        ["Cu(111) electrode", "separate fixture, not in fhi-examples", "-", f"~1&times;10{sup('-14')} eV (original port check)", "positive"],
        ["SrTiO3 PBE", "5 / 3", "108", f"3.6&times;10{sup('-14')} eV", "4.2&times;10" + sup("-4")],
    ],
    col_widths=[3.2 * cm, 2.6 * cm, 1.6 * cm, 5.8 * cm, 3.0 * cm],
)
caption(
    "Cu bulk / Cu(111) slab / SrTiO3 PBE numbers re-measured fresh for this report, directly "
    "against the curated real data now in the <font face='Courier'>fhi-examples</font> repo "
    "(3 k-points each: &Gamma;, (0.21, 0.13, 0), (0.5, 0, 0)). Cu(111) electrode is from the "
    "original 3-system port validation and was not re-measured here (its full output was not "
    "carried into <font face='Courier'>fhi-examples</font>)."
)
body(
    "Cu bulk FCC &Gamma;-point eigenvalues (relative to the SCF Fermi level) reproduce the "
    "expected atomic-core-to-valence ordering: 1s/2s/2p/3s/3p core levels in the &minus;9000 .. "
    "&minus;70 eV range, 4s at &minus;9.35 eV, 3d at &minus;2.1 .. &minus;2.93 eV. A TSHS write/"
    f"re-read round trip agrees to ~1&times;10{sup('-12')} eV. No duplicate (row, col, cell) "
    "triplet was found in any of the 3 originally-ported systems (bulk Cu, Cu(111) slab, Cu(111) "
    "electrode)."
)

# ============================================================ section 2 ===
h1("2. Independent cross-check: band structure vs. FHI-aims' own output")
body(
    "<b>What:</b> all of section 1's checks are internal (Hermiticity, positive-definiteness, "
    "no duplicate entries) &mdash; they can confirm <font face='Courier'>rsSileFHIaims</font> "
    "is self-consistent without confirming it reproduces the <i>right</i> physics. A stronger, "
    "independent check is available for any run with <font face='Courier'>output band</font> "
    "in <font face='Courier'>control.in</font>: FHI-aims computes and dumps its own band "
    "structure (<font face='Courier'>band1001.out</font> ... <font face='Courier'>band1005.out</font>) "
    "along the same path, entirely independently of "
    "<font face='Courier'>output_rs_matrices</font>. Diagonalizing sisl's reconstructed H(k)/S(k) "
    "along that exact path and comparing to FHI-aims' own numbers checks the physics actually "
    "encoded in H/S, not merely that the reader runs without error."
)
body(
    "<b>Pass criterion:</b> sisl's eigenvalues along the Gamma&ndash;X&ndash;M&ndash;Gamma&ndash;"
    "R&ndash;X path of a real SrTiO3 PBE run (5 atoms, 3 species, 108 orbitals, 67 bands dumped "
    "by FHI-aims) must agree with FHI-aims' own band dump to numerical precision, once a format "
    "detail found empirically (not assumed) is accounted for: FHI-aims' own band dump reports "
    "<font face='Courier'>E &minus; E</font><sub>F</sub> directly, while sisl's raw diagonalization "
    "gives absolute (unshifted) eigenvalues."
)
story.append(Image(BANDS_PNG, width=15.5 * cm, height=15.5 * cm * 490 / 690))
caption(
    "sisl's bands (solid blue) overlaid on FHI-aims' own independently-computed band dump "
    "(dashed red), SrTiO3 PBE. The two are visually indistinguishable throughout."
)
table(
    ["Comparison region", "max |E_sisl &minus; E_FHI-aims|"],
    [
        [f"Near E{sup('F')} (|E &minus; E{sup('F')}| &lt; 15 eV; valence/conduction bands)", f"9.45&times;10{sup('-7')} eV"],
        ["All 67 dumped bands, including the deepest 1s core levels (&minus;16000 eV range)", f"1.04&times;10{sup('-3')} eV (relative error ~6&times;10{sup('-8')})"],
    ],
    col_widths=[11.0 * cm, 5.0 * cm],
)
body(
    "The residual ~1 meV discrepancy at the deep-core end is consistent with FHI-aims' own band-"
    "dump file format simply printing fewer decimal digits there, not with any error in the "
    "reconstructed Hamiltonian. This check (and the executed notebook that produced it, "
    "<font face='Courier'>fhi-examples/notebooks/02_srtio3_bands_crosscheck.ipynb</font>) was "
    "added after this report's first version, at the maintainer's prompt that the original report "
    "had no plots despite the project producing band-structure figures."
)

# ============================================================ section 3 ===
h1("3. Hybrid exact exchange")
body(
    "<b>What:</b> FHI-aims never stores the exact-exchange operator in real space for a hybrid "
    "functional (HSE, PBE0); <font face='Courier'>output_rs_matrices</font> only ever dumps the "
    "semi-local part. <font face='Courier'>add_exact_exchange</font> reads the k-resolved exchange "
    "(<font face='Courier'>output hf_exchange_mat</font>, one ELSI-CSC file per spin/k-point) and "
    "Fourier-transforms it onto the Born&ndash;von Karman real-space lattice of the SCF k-grid, "
    "where the transform is exact and exactly invertible."
)
body(
    "<b>Pass criterion:</b> at every SCF k-point, H<sub>merged</sub>(k) &minus; "
    "H<sub>semilocal</sub>(k) must equal FHI-aims' own raw exchange matrix for that k-point, "
    "to numerical precision."
)
table(
    ["System", "k-grid", "SCF k-points checked", "max |merged &minus; semilocal &minus; raw exchange|"],
    [
        ["SrTiO3 HSE06 (original port check)", "2&times;2&times;2", "8", f"~2&times;10{sup('-11')} eV"],
        ["SrTiO3 HSE06 (original port check)", "4&times;4&times;4", "64", f"~2&times;10{sup('-11')} eV"],
        ["SrTiO3 HSE06 + output basis combined (re-measured for this report)", "2&times;2&times;2", "8", f"1.68&times;10{sup('-12')} eV"],
    ],
    col_widths=[6.0 * cm, 2.2 * cm, 3.0 * cm, 4.8 * cm],
)
h2("Documented limitation, not a bug: Hermiticity away from SCF k-points")
body(
    "The exchange is placed on one representative R per Born&ndash;von-Karman class, not "
    "mirrored to &minus;R (mirroring would double-count it at the SCF k-points). Away from the "
    "SCF k-points, H<sub>merged</sub>(k) is therefore a genuine Fourier interpolation and, in "
    "general, <b>not</b> exactly Hermitian &mdash; only the SCF k-points are guaranteed correct. "
    "This was re-verified directly for this report, at an arbitrary non-SCF k = "
    "(0.1234, 0.0567, &minus;0.021):"
)
table(
    ["Hamiltonian", "max |H(k) &minus; H(k)*| at a generic (non-SCF) k (* = conjugate transpose)"],
    [
        ["Semi-local only", f"4.6&times;10{sup('-14')} eV (Hermitian, as expected)"],
        ["Semi-local + exact exchange (merged)", "15.2 eV (not Hermitian away from SCF k &mdash; expected, documented)"],
    ],
    col_widths=[7.0 * cm, 9.0 * cm],
)
body(
    "At the 8 SCF k-points of the same run, the merged H(k) <i>is</i> exactly Hermitian "
    f"(max 7.1&times;10{sup('-14')} eV, re-measured for this report) &mdash; confirming the "
    "limitation is confined to where the documentation says it is, and nowhere else."
)

# ============================================================ section 4 ===
h1("4. Orbital quantum-number labeling")
body(
    "<b>What:</b> <font face='Courier'>basis-indices.out</font> lists, per basis function, its "
    "atom, <font face='Courier'>(n, l, m)</font> and FHI-aims basis type. The reader groups "
    "contiguous blocks of 2l+1 rows into one shell and assigns "
    "<font face='Courier'>zeta</font> when the same atom repeats an (n, l) shell (FHI-aims can "
    "define, e.g., both an <font face='Courier'>atomic</font> and a "
    "<font face='Courier'>hydro</font> basis function at the same (n, l))."
)
body(
    "<b>Pass criterion:</b> every fixture parses without a <font face='Courier'>SileError</font> "
    "(raised on an incomplete/non-contiguous shell rather than silently mis-grouped), and the "
    "resulting zeta=2 shells match each species' known extra basis tier."
)
table(
    ["Fixture", "Result"],
    [
        ["Bulk Cu", "parses cleanly; 3s and 3d each get a zeta=2 shell"],
        ["Cu(111) slab", "parses cleanly"],
        ["Cu(111) electrode", "parses cleanly"],
        ["SrTiO3 PBE (2 k-grids)", "parses cleanly; Sr 5s, Ti 3d, O 2p each get a zeta=2 shell"],
        ["SrTiO3 HSE06 (2 k-grids)", "parses cleanly; same zeta=2 pattern as PBE"],
    ],
    col_widths=[6.0 * cm, 10.0 * cm],
)
caption("All 6 fixtures checked in the original labeling commit; no SileError in any of them.")

# ============================================================ section 5 ===
h1("5. Real orbital radial functions (output basis)")
body(
    "<b>What:</b> with <font face='Courier'>output basis</font> in "
    "<font face='Courier'>control.in</font>, FHI-aims dumps the real, "
    "post-on-site-orthonormalization radial function of every basis-function shell &mdash; the "
    "FHI-aims analogue of a Siesta <font face='Courier'>.ion</font> file. "
    "<font face='Courier'>sisl.io.fhiaims.basis</font> reads these dumps and builds one "
    "<font face='Courier'>SphericalOrbital</font> per shell."
)
body(
    "Two format details were settled numerically against real data rather than assumed from the "
    "manual's prose: the dumped column is u(r) = r&middot;R(r), not R(r) directly "
    "(&int;u(r)" + sup("2") + "dr = 1 for every shell checked, independent of l; the "
    "&int;R(r)" + sup("2") + "r" + sup("2") + "dr = 1 convention does not hold for any of them); "
    "and the dump filename's shell index is confirmed directly from FHI-aims' own writer source, "
    "<font face='Courier'>src/shrink_fixed_basis.f90</font>."
)

h2("The one real bug found and fixed")
body(
    "<b>Bug:</b> the first implementation assumed each species' shells are numbered from 1 in "
    "the dump filename. This is indistinguishable from the correct behavior on a single-species "
    "system and was only caught when a <b>second, structurally different</b> system was tested, "
    "as this project's own planning convention (an outside judge decides, not a second look at "
    "the same case) requires."
)
body(
    "<b>Symptom:</b> running SrTiO3 PBE (3 species: Sr, Ti, O) immediately raised "
    "<font face='Courier'>SileError</font> on Ti's first shell &mdash; the predicted dump "
    "filename (<font face='Courier'>at_2_01_01_s.dat</font>) did not exist; the real file was "
    "<font face='Courier'>at_2_14_01_s.dat</font>."
)
body(
    "<b>Root cause</b> (confirmed by reading FHI-aims' own Fortran source, read-only, never "
    "vendored): <font face='Courier'>do i_function = 1, n_basis_fns</font> in "
    "<font face='Courier'>shrink_fixed_basis.f90</font> is <b>one flat loop across every "
    "species combined</b> &mdash; species 1's shells first, then species 2's continuing from "
    "there &mdash; not reset to 1 per species. SrTiO3's species 1 (Sr) has shells 1&ndash;13, "
    "species 2 (Ti) continues at 14&ndash;24, species 3 (O) at 25&ndash;30."
)
body(
    "<b>Fix:</b> compute each species' global shell offset as the total shell count of every "
    "species before it. A dedicated 2-species synthetic regression test for exactly this "
    "failure mode was added to sisl's own test suite."
)

h2("Re-verification after the fix, on 4 systems")
table(
    ["System", "Atoms / species", "Result"],
    [
        [
            "Cu bulk FCC",
            "1 / 1",
            "unaffected by the fix (single species, offset 0); all 11 predicted dump files "
            "existed; R0 = 0.334 &Aring; (1s)",
        ],
        [
            "SrTiO3 PBE",
            "5 / 3",
            "all 30 predicted dump files now existed; R0 = 0.251 &Aring; (Sr 1s); R grows with "
            "decreasing binding energy (Sr 1s 0.25 &Aring; &rarr; 5s 9.56 &Aring;)",
        ],
        [
            "Cu(111) slab",
            "9 / 1",
            "a structurally different case (many atoms, one species, not one atom per "
            "species): confirmed the radial function is parsed once per species and the same "
            "SphericalOrbital object is reused across all 9 atoms, not re-parsed per atom",
        ],
        [
            "SrTiO3 HSE06 + exact exchange",
            "5 / 3",
            "output basis combined with the hybrid-EXX path: no interaction bug (orbital shape "
            "and sparse H/S/exchange values are independent)",
        ],
    ],
    col_widths=[4.6 * cm, 2.4 * cm, 9.0 * cm],
)
body(
    "In all cases, <font face='Courier'>Geometry.close</font> (which raises on the R=1 "
    "placeholder) runs correctly, and Hermiticity/positive-definiteness are unaffected by the "
    "orbital radial shape, as expected (it is a distinct data path from the sparse H/S/exchange "
    "values)."
)

h2("Known, stated limitation: species-ordering heuristic")
body(
    "FHI-aims assigns an atom's species number by matching its name in "
    "<font face='Courier'>geometry.in</font> against <font face='Courier'>control.in</font>'s "
    "own, ordered species-block list. <font face='Courier'>basis.py</font> does not parse "
    "<font face='Courier'>control.in</font>; it infers the species number from the order "
    "distinct shell signatures first appear while scanning atoms. This is exact whenever "
    "<font face='Courier'>control.in</font> lists species in the same order "
    "<font face='Courier'>geometry.in</font> introduces them &mdash; true of every fixture "
    "checked here &mdash; but is <b>not derived from control.in and is unverified for an "
    "ordering that diverges from it</b>. Every predicted dump filename is still checked to "
    "exist; a partial match raises <font face='Courier'>SileError</font> rather than silently "
    "mixing in a wrong radial function."
)

# ============================================================ section 6 ===
h1("6. Code review and fixes (vectorized parsing loop)")
body(
    "A <font face='Courier'>/code-review</font> pass (effort 1) on the branch found 3 issues, "
    "all in the per-cell, per-nonzero-column Python loop that had just been vectorized for "
    "performance (flagged by sisl's own performance convention as a slow idiom to avoid, not "
    "just benchmark):"
)
bullets(
    [
        "<b>Malformed-input crash.</b> A corrupted <font face='Courier'>rs_indices.out</font> "
        "(end index &lt; start index &minus; 1 for a column flagged as having entries) made the "
        "vectorized code crash inside <font face='Courier'>np.repeat</font> with a raw "
        "&quot;negative dimensions are not allowed&quot; error, instead of the codebase's own "
        "<font face='Courier'>SileError</font> this function already raises for other malformed "
        "input. <b>Fixed:</b> segment lengths are now validated explicitly before use, raising "
        "<font face='Courier'>SileError</font>; a regression test was added for exactly this "
        "failure.",
        "<b>Reimplementing an existing utility.</b> The hand-rolled &quot;flatten a list of "
        "ragged ranges&quot; arithmetic (cumulative sums + repeats) duplicated sisl's own "
        "<font face='Courier'>sisl._array.array_arange</font>, already used for the same kind of "
        "pointer/count bookkeeping in <font face='Courier'>SparseGeometry</font>. <b>Fixed:</b> "
        "replaced with that call.",
        "<b>Redundant special case.</b> An explicit empty-input branch was unnecessary (the "
        "generic vectorized path already degrades cleanly to size-0 arrays) and hardcoded "
        "<font face='Courier'>dtype=np.float64</font> instead of deriving it from the actual "
        "data. <b>Fixed:</b> branch removed.",
    ]
)
body(
    "After all 3 fixes: the fhiaims test suite (22 tests) passes, and the vectorized code was "
    "cross-checked directly against the real 279-orbital/81-supercell Cu(111)-slab run again, "
    "reproducing identical Hermiticity and positive-definiteness numbers to before the change."
)

# ============================================================ section 7 ===
h1("7. Current state")
table(
    ["Item", "Status"],
    [
        ["Branch", "fhi-dev, 12 commits ahead of main"],
        ["Code review", "1 pass completed; all 3 findings fixed and re-verified"],
        [
            "Merge status",
            "not merged upstream; briefly merged to main locally then reverted back to a "
            "separate branch at the maintainer's request",
        ],
        ["Remote", "pushed to github.com/mbrandbyge-DTU/sisl, branch fhi-dev"],
        ["sisl test suite", "22/22 fhiaims tests pass (synthetic fixtures only, see section 8)"],
        [
            "Real-data fixtures",
            "curated into a separate repo, fhi-examples (not in the sisl repo itself); includes "
            "3 executed plotting/validation notebooks, one of which produced section 2 above",
        ],
    ],
    col_widths=[4.0 * cm, 12.0 * cm],
)

# ============================================================ section 8 ===
h1("8. What is NOT yet independently verified")
bullets(
    [
        "<b>No committed real-data regression test.</b> Every number in sections 1-6 above was "
        "produced by running the reader against real FHI-aims output, by hand, during "
        "development (and freshly re-measured for this report). sisl's own committed test suite "
        "(the 22 passing tests) only exercises small, hand-written <i>synthetic</i> fixtures "
        "that mimic the file format &mdash; it does not re-run these real-data checks "
        "automatically. A CI run of sisl's test suite proves the parser logic is self-consistent, "
        "not that it matches a real calculation.",
        "<b>Species-ordering heuristic</b> (section 5) is confirmed correct only for every "
        "fixture checked so far, all of which happen to list species in "
        "<font face='Courier'>control.in</font> in the same order "
        "<font face='Courier'>geometry.in</font> introduces them. An ordering that diverges from "
        "this has not been tested; the code is designed to raise an error rather than silently "
        "mismatch in that case, but that error path itself has not been exercised against a real "
        "divergent-ordering run.",
        "<b>Polarized (spin-up/spin-down) hybrid exact exchange</b> has not been checked against "
        "real FHI-aims spin-polarized hybrid output in this session &mdash; only the unpolarized "
        "SrTiO3 HSE06 case was run and verified. The spin-indexing logic itself was unit-tested "
        "(synthetic fixtures) after a related bug was found and fixed while porting from the "
        "earlier implementation (exchange was previously always added to Hamiltonian channel 0 "
        "regardless of the requested spin channel).",
        "<b>Cu(111) electrode</b> numbers quoted in section 1 are from the original port "
        "validation and were not re-measured for this report (its output was not carried into "
        "the <font face='Courier'>fhi-examples</font> repo).",
        "<b>gzip-compressed sibling-file lookup</b> (fixed earlier in a separate review round, "
        "not covered in detail above) is verified only against a synthetic fixture with every "
        "sibling file compressed, not a real FHI-aims run that was gzip-archived after the fact.",
    ]
)

doc = SimpleDocTemplate(
    OUT,
    pagesize=letter,
    topMargin=2.2 * cm,
    bottomMargin=2.0 * cm,
    leftMargin=2.0 * cm,
    rightMargin=2.0 * cm,
    title="FHI-aims to sisl Reader: Benchmark and Validation Report",
)
doc.build(story)
print("wrote", OUT)
