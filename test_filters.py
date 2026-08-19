#!/usr/bin/env python3
"""Filter regression tests.

Every title below is a REAL posting title observed in the community trackers
(or a close variant), so this pins the two things most likely to break the
watcher for Sam: chip-design roles must survive, and verification / physical
design must not.

Run:  python3 test_filters.py
"""
import json
import sys

import watcher as w

FILTERS = json.load(open("config.json"))["filters"]

# (title, should_be_relevant, expected_category_or_None)
#   category 0 = DSP/signal processing, 1 = FPGA, 2 = ASIC/SoC/RTL, 3 = other
KEEP = [
    # --- real titles seen in the trackers ---
    ("Hardware ASIC Design Intern", 2),
    ("NVIDIA Internships: Hardware Engineering", 3),
    ("Hardware Engineering Intern", 3),
    ("SoC Digital Design Engineer Intern", 2),
    ("CPU Microarchitecture Engineer Intern", 2),
    ("RTL Design Intern - Bachelor's Degree", 2),
    ("FPGA Intern", 1),
    ("FPGA Engineer Intern", 1),
    ("FPGA System Developer Intern", 1),
    ("FPGA Intern Engineer", 1),
    ("Internship - FPGA Hardware Design Engineer", 1),
    ("Silicon Hardware Engineering Intern/Co-op - Silicon Engineering", 2),
    ("Intern Semiconductor Design Engineer", 2),
    ("Digital Design Intern", 2),
    ("ASIC Intern", 2),
    ("Hardware - Engineering Internship - CPU - GPU - SoC - Digital Design", 2),
    ("Intern - Silicon Solutions Group", 2),
    ("SoC Performance Modeling Internship - Platform Architecture", 2),
    # --- DSP / signal processing: Sam's stated priority, must land in cat 0 ---
    ("Machine Learning and Digital Signal Processing Intern", 0),
    ("DSP Firmware Engineering Co-op/Intern", 0),
    ("Signal Processing Intern", 0),
    ("Radar Systems Engineering Intern", 0),
    ("Baseband Modem Design Intern", 0),
    ("Software Defined Radio Engineering Intern", 0),
    ("Beamforming Algorithms Intern", 0),
    # --- generic but legitimate ---
    ("Computer Engineering Intern", 3),
    ("Embedded Systems Engineering Intern", 3),
    ("Firmware Engineering Intern", 3),
]

DROP = [
    # --- verification: explicitly excluded ---
    "Intern - ASIC Design Verification - ASIC Design Verification",
    "ASIC Design and Verification Engineer Intern - Video Silicon IP",
    "ASIC Design Verification Engineer",
    "Design DSP Verification Intern - Bachelor's Degree",
    "Intern - Firmware Verification Engineering",
    "Summer Intern - Validation Software Engineer - Silicon Validation Infra",
    "Chassis Validation Engineer Intern, Vehicle Firmware",
    "UVM Testbench Development Intern",
    "Post-Silicon Validation Intern",
    # --- physical design: explicitly excluded ---
    "Physical Design Engineer Intern",
    "GPU Internships - RTL Design - RTL Power Optimisation & Physical Design",
    "Place and Route Engineering Intern",
    "Static Timing Analysis Intern",
    "Layout Design Intern",
    "Floorplanning Engineer Intern",
    "Design for Test (DFT) Engineering Intern",
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
    ("GPU/AI Application System Software Engineer Intern", 3),
    ("Chip Simulation Software Intern", 3),
    ("Compiler Engineer Intern, GPU", 3),
    ("CUDA Software Development Intern", 3),
    ("SoC Driver Software Engineer Intern", 3),
    # ...but a hard design signal outranks the software wording
    ("FPGA Software Design Engineer", 1),
    ("RTL Design Software Engineer Intern", 2),
]:
    got = w._role_category(title)
    flag = "ok " if got == want_cat else "FAIL"
    print(f"  {flag} cat {got} (want {want_cat}) | {title[:56]}")
    check(got == want_cat,
          f"DEMOTION {title!r} -> cat {got}, want {want_cat}")

print("\n=== TOP_PICKS want/skip gate ===")
for title, _ in KEEP:
    inpick = bool(w.WANT_RE.search(title) and not w.SKIP_RE.search(title))
    if not inpick:
        print(f"  note: not in TOP_PICKS (matched no WANT term): {title}")
for title in DROP[:16]:
    inpick = bool(w.WANT_RE.search(title) and not w.SKIP_RE.search(title))
    check(not inpick, f"TOP_PICKS kept an excluded role: {title}")

print("\n" + "=" * 62)
if fails:
    print(f"{len(fails)} FAILURE(S):")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print(f"All {len(KEEP) + len(DROP) + len(CYCLE)} filter assertions passed.")
