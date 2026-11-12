#!/usr/bin/env python3
"""Filter regression tests.

Every title below is a REAL posting title observed in the community trackers
or on a company board (or a close variant), so this pins the things most likely
to break the watcher for Sam: chip-design, RF and verification roles must
survive, physical design and post-silicon validation must not, and quant / HFT
firms must stay hidden.

Run:  python3 test_filters.py
"""
import json
import sys

import watcher as w

FILTERS = json.load(open("config.json", encoding="utf-8"))["filters"]

DSP, FPGA, ASIC, RF, DV, OTHER = (w.CAT_DSP, w.CAT_FPGA, w.CAT_ASIC,
                                  w.CAT_RF, w.CAT_DV, w.CAT_OTHER)

# (title, expected_category) -- every one of these must pass the filters
KEEP = [
    # --- real titles seen in the trackers ---
    ("Hardware ASIC Design Intern", ASIC),
    ("NVIDIA Internships: Hardware Engineering", OTHER),
    ("Hardware Engineering Intern", OTHER),
    ("SoC Digital Design Engineer Intern", ASIC),
    ("CPU Microarchitecture Engineer Intern", ASIC),
    ("RTL Design Intern - Bachelor's Degree", ASIC),
    ("FPGA Intern", FPGA),
    ("FPGA Engineer Intern", FPGA),
    ("FPGA System Developer Intern", FPGA),
    ("FPGA Intern Engineer", FPGA),
    ("Internship - FPGA Hardware Design Engineer", FPGA),
    ("Silicon Hardware Engineering Intern/Co-op - Silicon Engineering", ASIC),
    ("Intern Semiconductor Design Engineer", ASIC),
    ("Digital Design Intern", ASIC),
    ("ASIC Intern", ASIC),
    ("Hardware - Engineering Internship - CPU - GPU - SoC - Digital Design", ASIC),
    ("Intern - Silicon Solutions Group", ASIC),
    ("SoC Performance Modeling Internship - Platform Architecture", ASIC),
    # --- DSP / signal processing: Sam's stated priority, must land first ---
    ("Machine Learning and Digital Signal Processing Intern", DSP),
    ("DSP Firmware Engineering Co-op/Intern", DSP),
    ("Signal Processing Intern", DSP),
    ("Radar Systems Engineering Intern", DSP),
    ("Baseband Modem Design Intern", DSP),
    ("Software Defined Radio Engineering Intern", DSP),
    ("Beamforming Algorithms Intern", DSP),
    ("Signal Processing and RF Engineering Intern", DSP),
    # --- RF / wireless (added 2026-11-12) ---
    ("Antenna Intern (Summer 2027)", RF),
    ("Electrical Integration Intern - RF (Summer 2027)", RF),
    ("Wireless Hardware Engineer Intern - Summer 2027", RF),
    ("RF Hardware Design Intern", RF),
    ("RF/Microwave Engineering Intern", RF),
    ("RFIC Design Intern", RF),
    # --- design verification (allowed since 2026-11-12, ranked below design) ---
    ("Intern - ASIC Design Verification - ASIC Design Verification", DV),
    ("Design DSP Verification Intern - Bachelor's Degree", DV),
    ("Intern - Firmware Verification Engineering", DV),
    ("UVM Testbench Development Intern", DV),
    ("Design Verification Engineer Intern", DV),
    ("FPGA Design Verification Intern", DV),
    ("Digital Design Verification Engineer Intern", DV),
    ("Verification Engineer Intern", DV),
    # "design AND verification" is a design role: it stays in its design bucket
    ("ASIC Design and Verification Engineer Intern - Video Silicon IP", ASIC),
    # --- generic but legitimate ---
    ("Computer Engineering Intern", OTHER),
    ("Embedded Systems Engineering Intern", OTHER),
    ("Firmware Engineering Intern", OTHER),
]

# Physical design and post-silicon validation: must be dropped by the filters
# AND must never appear in TOP_PICKS.
NEVER = [
    # --- validation (not design verification): still excluded ---
    "Summer Intern - Validation Software Engineer - Silicon Validation Infra",
    "Chassis Validation Engineer Intern, Vehicle Firmware",
    "Post-Silicon Validation Intern",
    # --- physical design: explicitly excluded ---
    "Physical Design Engineer Intern",
    "GPU Internships - RTL Design - RTL Power Optimisation & Physical Design",
    "Place and Route Engineering Intern",
    "Static Timing Analysis Intern",
    "Layout Design Intern",
    "Floorplanning Engineer Intern",
    "Design for Test (DFT) Engineering Intern",
    # regression: the "dft" exclude was once stored as "\bdft\b", which JSON
    # reads as backspace characters, so it matched nothing and this leaked
    "ASIC DFT Engineer Intern",
]

DROP = NEVER + [
    # --- wrong discipline / function ---
    "Mechanical Engineer Intern",
    "Hardware Engineering Intern - Mechanical Design",
    "Manufacturing Engineer Intern",
    "Test Engineer Intern",
    "Product Engineering Intern",
    "Failure Analysis Intern",
    "Application Engineering Intern - Coherent DSP",
    "Supply Chain Intern",
    "Sales Engineering Intern",
    # --- not an internship at all ---
    "ASIC Design Verification Engineer",
    "Senior ASIC Design Engineer",
    "Principal RTL Design Engineer",
    "Internal Audit Manager",
    "International Sales Director",
    # --- wrong domain entirely ---
    "Software Engineer Intern, Backend",
    "Quantitative Trading Intern",
    "Data Science Intern",
    # --- wrong cycle ---
    "2026 Silicon Engineering Intern",
    "Fall 2027 FPGA Co-op",
    "Spring 2027 ASIC Design Intern",
    "Summer 2026 Digital Design Intern",
]

# (title, content, expected_is_summer_2027)
CYCLE = [
    ("Hardware ASIC Design Intern", "", True),          # no cycle named -> keep
    ("Summer 2027 FPGA Design Intern", "", True),
    ("FPGA Design Intern", "Summer 2027 program", True),
    ("Fall 2027 Digital Design Co-op", "", False),
    ("Spring 2027 RTL Intern", "", False),
    ("Summer 2026 ASIC Intern", "", False),
    ("Summer 2028 ASIC Intern", "", False),
    ("ASIC Design Intern", "This is our Fall 2027 co-op rotation.", False),
    ("RTL Design Intern", "Summer 2027 internship, 12 weeks", True),
]

# Quant / HFT firms are hidden everywhere (filters.exclude_firms). Trackers
# give display names; auto-discovered boards give the ATS token.
FIRM_HIDDEN = [
    "Jane Street", "janestreet", "Hudson River Trading", "wehrtyou",
    "Optiver", "optiverus", "Virtu Financial", "HPR (Hyannis Port Research)",
    "hyannisportresearch", "DRW", "drweng", "Two Sigma", "IMC Trading", "imc",
    "Citadel Securities", "Tower Research Capital", "towerresearchcapital",
    "Five Rings Capital", "fiveringsllc", "Akuna Capital", "akunacapital",
    "Susquehanna International Group (SIG)", "Jump Trading Group",
    "Defense: Vatic Labs", "vaticlabs", "Headlands Technologies",
    "headlandstechnologiesllc", "xtxmarketstechnologies", "D. E. Shaw",
    "DE Shaw", "G-Research",
]
# ...and these must NOT be caught by a careless substring match.
FIRM_KEPT = [
    "NVIDIA", "Chip: NVIDIA", "Virtusa", "Astranis", "Northrop Grumman",
    "Millennium Space Systems", "American Tower", "Tower Semiconductor",
    "Simcorp", "Jumpstart", "Two Six Technologies", "Radix Engineering",
    "Citizens Energy Group", "HP", "Draper",
]

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


print("=== titles that MUST pass the filters ===")
for title, want_cat in KEEP:
    job = {"title": title, "location": "Santa Clara, CA", "content": ""}
    ok = w.is_relevant(job, FILTERS)
    cat = w._role_category(title)
    flag = "ok " if ok else "FAIL"
    print(f"  {flag} [cat {cat}] {title[:66]}")
    check(ok, f"KEEP dropped: {title}")
    check(cat == want_cat,
          f"KEEP wrong category: {title} -> got {cat}, want {want_cat}")

print("\n=== titles that MUST be dropped ===")
for title in DROP:
    job = {"title": title, "location": "Santa Clara, CA", "content": ""}
    ok = w.is_relevant(job, FILTERS)
    flag = "FAIL" if ok else "ok "
    print(f"  {flag} {title[:72]}")
    check(not ok, f"DROP kept: {title}")

print("\n=== Summer-2027 cycle gate ===")
for title, content, want in CYCLE:
    got = w._is_summer_2027({"title": title, "content": content})
    flag = "ok " if got == want else "FAIL"
    print(f"  {flag} {str(got):5} (want {want}) | {title[:56]}")
    check(got == want, f"CYCLE {title!r} -> {got}, want {want}")

print("\n=== software-vs-design demotion ===")
# A title can name silicon and still be a pure software job. These must land in
# the catch-all category, not in the FPGA/ASIC buckets.
for title, want_cat in [
    ("GPU/AI Application System Software Engineer Intern", OTHER),
    ("Chip Simulation Software Intern", OTHER),
    ("Compiler Engineer Intern, GPU", OTHER),
    ("CUDA Software Development Intern", OTHER),
    ("SoC Driver Software Engineer Intern", OTHER),
    # ...but a hard design signal outranks the software wording
    ("FPGA Software Design Engineer", FPGA),
    ("RTL Design Software Engineer Intern", ASIC),
]:
    got = w._role_category(title)
    flag = "ok " if got == want_cat else "FAIL"
    print(f"  {flag} cat {got} (want {want_cat}) | {title[:56]}")
    check(got == want_cat,
          f"DEMOTION {title!r} -> cat {got}, want {want_cat}")

print("\n=== TOP_PICKS want/skip gate ===")
for title, cat in KEEP:
    inpick = bool(w.WANT_RE.search(title) and not w.SKIP_RE.search(title))
    if cat in (RF, DV):
        check(inpick, f"TOP_PICKS lost an RF / verification role: {title}")
    elif not inpick:
        print(f"  note: not in TOP_PICKS (matched no WANT term): {title}")
for title in NEVER:
    inpick = bool(w.WANT_RE.search(title) and not w.SKIP_RE.search(title))
    check(not inpick, f"TOP_PICKS kept an excluded role: {title}")

print("\n=== quant / HFT firm exclusion ===")
for name in FIRM_HIDDEN:
    hit = w._firm_excluded(name, FILTERS)
    print(f"  {'ok ' if hit else 'FAIL'} hidden  {name[:40]:40} <- {hit}")
    check(hit, f"FIRM not hidden: {name}")
for name in FIRM_KEPT:
    hit = w._firm_excluded(name, FILTERS)
    print(f"  {'FAIL' if hit else 'ok '} kept    {name[:40]:40}" + (f" <- {hit}" if hit else ""))
    check(not hit, f"FIRM wrongly hidden: {name} (matched {hit!r})")

print("\n" + "=" * 62)
if fails:
    print(f"{len(fails)} FAILURE(S):")
    for f in fails:
        print("  -", f)
    sys.exit(1)
total = len(KEEP) + len(DROP) + len(CYCLE) + len(FIRM_HIDDEN) + len(FIRM_KEPT)
print(f"All {total} filter assertions passed.")
