#!/usr/bin/env python3
"""Filter regression tests.

Every title below is a REAL posting title observed in the community trackers
or on a company board (or a close variant), so this pins the things most likely
to break the watcher for Sam: RTL x DSP roles must rank first, chip-design and
DSP roles must survive; pure RF, design verification, physical design and
post-silicon validation must not; and quant / HFT firms must stay hidden.

Run:  python3 test_filters.py
"""
import json
import sys

import watcher as w

FILTERS = json.load(open("config.json", encoding="utf-8"))["filters"]

RTLDSP, FPGA, ASIC, DSP, OTHER = (w.CAT_RTL_DSP, w.CAT_FPGA, w.CAT_ASIC,
                                  w.CAT_DSP, w.CAT_OTHER)

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
    # --- RTL x DSP: Sam's top priority (2026-11-13), must land first ---
    ("FPGA DSP Design Intern", RTLDSP),
    ("FPGA Signal Processing Engineer Intern", RTLDSP),
    ("ASIC Design Intern - Baseband", RTLDSP),
    ("Digital Signal Processing Hardware Intern", RTLDSP),
    ("RF Digital Design Intern", RTLDSP),
    ("Radar FPGA Engineering Intern", RTLDSP),
    ("SDR RTL Design Intern", RTLDSP),
    # --- DSP with no RTL named: ranked below FPGA / ASIC design ---
    ("Machine Learning and Digital Signal Processing Intern", DSP),
    ("DSP Firmware Engineering Co-op/Intern", DSP),
    ("Signal Processing Intern", DSP),
    ("Radar Systems Engineering Intern", DSP),
    ("Baseband Modem Design Intern", DSP),
    ("Software Defined Radio Engineering Intern", DSP),
    ("Beamforming Algorithms Intern", DSP),
    ("Signal Processing and RF Engineering Intern", DSP),
    # --- RF / wireless survives only with a digital / SoC / RTL signal ---
    ("Wireless SoC Design Intern", ASIC),
    # "design AND verification" is a design role: it survives the DV drop
    ("ASIC Design and Verification Engineer Intern - Video Silicon IP", ASIC),
    # --- generic but legitimate ---
    ("Computer Engineering Intern", OTHER),
    ("Embedded Systems Engineering Intern", OTHER),
    ("Firmware Engineering Intern", OTHER),
]

# Physical design and post-silicon validation: must be dropped by the filters
# AND must never appear in TOP_PICKS.
NEVER = [
    # --- pure RF / wireless: dropped 2026-11-13 unless DSP / RTL is involved ---
    "Antenna Intern (Summer 2027)",
    "Electrical Integration Intern - RF (Summer 2027)",
    "Wireless Hardware Engineer Intern - Summer 2027",
    "RF Hardware Design Intern",
    "RF/Microwave Engineering Intern",
    "RFIC Design Intern",
    # --- design verification: dropped 2026-11-13 ---
    "Intern - ASIC Design Verification - ASIC Design Verification",
    "Design DSP Verification Intern - Bachelor's Degree",
    "Intern - Firmware Verification Engineering",
    "UVM Testbench Development Intern",
    "Design Verification Engineer Intern",
    "FPGA Design Verification Intern",
    "Digital Design Verification Engineer Intern",
    "Verification Engineer Intern",
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

print("\n=== the job description decides RTL x DSP and RF ===")
# (title, description, expected_keep, expected_category)
for title, content, want_keep, want_cat in [
    ("Signal Processing Intern",
     "implement filters in vhdl on xilinx fpgas", True, RTLDSP),
    ("FPGA Design Intern",
     "you will implement radar signal processing chains", True, RTLDSP),
    ("RF Systems Engineering Intern",
     "develop fpga-based digital receivers and channelizers", True, RTLDSP),
    ("RF Systems Engineering Intern",
     "write verilog for our transceiver control logic", True, ASIC),
    ("RF Systems Engineering Intern",
     "characterize amplifiers on the bench with a vna", False, None),
    ("Antenna Design Intern", "", False, None),
]:
    job = {"title": title, "location": "Huntsville, AL", "content": content}
    ok = bool(w.is_relevant(job, FILTERS))
    cat = w._role_category(title, content)
    good = ok == want_keep and (not want_keep or cat == want_cat)
    print(f"  {'ok ' if good else 'FAIL'} keep={ok} cat={cat} | {title[:30]} / {content[:30]}")
    check(ok == want_keep, f"DESC keep {title!r} + {content[:40]!r} -> {ok}")
    if want_keep:
        check(cat == want_cat, f"DESC cat {title!r} + {content[:40]!r} -> {cat}, want {want_cat}")

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
    if cat in (RTLDSP, FPGA):
        check(inpick, f"TOP_PICKS lost an RTL x DSP / FPGA role: {title}")
    elif not inpick:
        print(f"  note: not in TOP_PICKS (matched no WANT term): {title}")
for title in NEVER:
    inpick = bool(w.WANT_RE.search(title) and not w.SKIP_RE.search(title)
                  and not w._is_pure_dv(title) and not w._is_rf_only(title))
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
