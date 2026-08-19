#!/usr/bin/env python3
"""Check every source in config.json and report the dead ones.

Why this exists: a mistyped Greenhouse token or a renamed Workday site does not
raise -- the fetcher just returns zero jobs and the sweep logs "0 relevant",
which is indistinguishable from "nothing is open right now". Over a season that
silently rots the config.

Run it in CI (the GitHub runner has open network access):

    python3 verify_sources.py            # check everything, human-readable
    python3 verify_sources.py --json     # machine-readable summary
    python3 verify_sources.py --prune    # rewrite config.json without the dead

A source is reported DEAD only if the endpoint itself fails (404, connection
error, malformed payload). A live board with zero open postings is reported
EMPTY, which is normal off-season and is never pruned.
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

import watcher as w

CONFIG = "config.json"
TIMEOUT = 20


def probe(firm):
    """Return (firm, status, detail). status in {ok, empty, dead, skipped}."""
    name = firm.get("name", "?")
    ats = firm.get("ats")

    # Page watchers are change detectors; a 200 is all that matters.
    if ats == "pagewatch":
        try:
            r = requests.get(firm["url"], headers=w.HEADERS, timeout=TIMEOUT,
                             allow_redirects=True)
            if r.status_code >= 400:
                return firm, "dead", f"HTTP {r.status_code}"
            return firm, "ok", f"HTTP {r.status_code}, {len(r.content)}B"
        except Exception as e:
            return firm, "dead", type(e).__name__

    fetcher = w.FETCHERS.get(ats)
    if not fetcher:
        return firm, "dead", f"unknown ats {ats!r}"

    # These aggregate many boards and are slow; treat any successful run as ok.
    try:
        jobs = fetcher(firm)
    except Exception as e:
        return firm, "dead", f"{type(e).__name__}: {str(e)[:70]}"

    if not jobs:
        return firm, "empty", "0 postings"
    return firm, "ok", f"{len(jobs)} postings"


def main():
    as_json = "--json" in sys.argv
    prune = "--prune" in sys.argv

    cfg = json.load(open(CONFIG))
    firms = cfg["firms"]
    results = []

    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(probe, f) for f in firms]
        for fut in as_completed(futs):
            results.append(fut.result())

    order = {"dead": 0, "empty": 1, "ok": 2}
    results.sort(key=lambda r: (order[r[1]], r[0].get("name", "")))

    dead = [r for r in results if r[1] == "dead"]
    empty = [r for r in results if r[1] == "empty"]
    ok = [r for r in results if r[1] == "ok"]

    if as_json:
        print(json.dumps({
            "total": len(firms),
            "ok": len(ok), "empty": len(empty), "dead": len(dead),
            "dead_sources": [{"name": f.get("name"), "ats": f.get("ats"),
                              "reason": d} for f, _, d in dead],
        }, indent=1))
    else:
        if dead:
            print(f"===== DEAD ({len(dead)}) -- these silently return nothing =====")
            for f, _, d in dead:
                print(f"  {f.get('ats',''):16} {f.get('name','?')[:52]:54} {d}")
        if empty:
            print(f"\n===== EMPTY ({len(empty)}) -- live, but nothing open =====")
            for f, _, d in empty:
                print(f"  {f.get('ats',''):16} {f.get('name','?')[:52]:54} {d}")
        print(f"\n===== OK ({len(ok)}) =====")
        for f, _, d in ok:
            print(f"  {f.get('ats',''):16} {f.get('name','?')[:52]:54} {d}")
        print(f"\n{len(ok)} ok · {len(empty)} empty · {len(dead)} dead "
              f"· {len(firms)} total")

    if prune and dead:
        dead_names = {f.get("name") for f, _, _ in dead}
        cfg["firms"] = [f for f in firms if f.get("name") not in dead_names]
        json.dump(cfg, open(CONFIG, "w"), indent=2)
        print(f"\nPruned {len(dead_names)} dead source(s) from {CONFIG}.")

    # Dead sources are informational, not a build failure -- a transient outage
    # should not turn the whole workflow red.
    return 0


if __name__ == "__main__":
    sys.exit(main())
