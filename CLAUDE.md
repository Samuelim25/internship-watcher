# Internship Watcher

**CURRENT MODE (2026-08-19): retuned for Sam — FPGA / ASIC digital design.**

The watcher was originally built for a different user (quant / SWE, NYC-first,
Fall 2027). On 2026-08-19 it was retuned end-to-end for chip design. If you are
reading old commit messages or old `TOP_PICKS.md` diffs, that is why they talk
about quant firms.

Two crons, both live:

1. **Hourly role sweep** — polls semiconductor, defense and community-tracker
   sources for **Summer 2027 FPGA / ASIC / RTL / DSP design internships** and
   emails the moment a new one opens. Gated by `summer_2027_only` in
   `config.json → filters`; `top_firms_only` is **off**, because the chip-design
   keyword gate is already narrow and the best FPGA seats are often at mid-size
   firms and defense primes rather than the household names.
2. **Sunday 14:00 UTC digest** (`DIGEST_MODE=1`) — chip-design programs, tapeout
   shuttles, conference student programs, scholarships and lab REUs. See
   "Weekly digest".

**Expect a slow start.** Semiconductor firms post Summer 2027 intern reqs from
roughly September through January, so an empty inbox in late August is the
system working correctly, not a broken filter. Check the run log's
`Filter drops this run:` line to confirm roles are being seen and rejected for
the right reasons rather than not being fetched at all.

## Who this is for (drives all filtering)

- **Graduating May 2028** — eligible for essentially every Summer 2027 intern req
- **Target: FPGA and ASIC _design_.** Explicitly **NOT** design verification
  (DV / UVM / testbench) and **NOT** physical design (place & route, floorplan,
  timing closure, layout, DFT). Those two are the largest adjacent job families
  and without the exclusions in `title_exclude` they dominate the inbox — the
  community trackers alone carry Micron "ASIC Design Verification", Cisco "ASIC
  Design Verification Engineer" and Apple "RTL Power Optimisation & Physical
  Design" right now.
- **Email is ranked into 4 categories, in this exact order:**
  ① DSP / signal processing (his stated sub-area priority) ② FPGA design
  ③ ASIC / SoC / RTL design ④ everything else that matched. See
  `build_email_html` and `_role_category`.
- **Anywhere in the US.** No city is promoted over another — `priority_locations`
  is empty and `_loc_rank` only pushes roles with a recognisable chip-hub
  location above ones whose location is vague. **US-only** is still enforced by
  `_is_us_location()`; Canada is excluded deliberately, since Tenstorrent and
  Marvell post heavily in Toronto and Ottawa.
- **Defense and national labs are IN** — Northrop, RTX, Leidos, Draper, GDMS,
  Sandia, MIT Lincoln Lab, JHU APL. This is the densest single source of FPGA
  design internships. Sam has **not** said he holds a clearance, so
  `is_clearance()` no longer drives the email layout; it just flags roles with
  🇺🇸 in `TOP_PICKS.md` and prints a count in the run log.
- **HFT / trading firms are OUT as boards.** All ~250 quant board entries were
  removed. Note that the community trackers still surface HFT FPGA roles (DRW
  "FPGA Intern", Jane Street "Hardware Engineer (FPGA/ASIC) Intern", Optiver
  "FPGA Engineer Intern", IMC and Akuna "Hardware Engineer Intern") — these are
  genuine FPGA design roles and are left in rather than specially blocked. Add
  firm substrings to `EXCLUDE_FIRMS` in `watcher.py` to hide them.

## Weekly digest (the live feature)

Sunday 14:00 UTC → `DIGEST_MODE=1` → `send_weekly_digest()`, which:

1. Runs `run_digest_sweep()` over the **program / conference / scholarship**
   sources only (parallel, 12 workers) and reports pages that **changed since
   last Sunday** — usually meaning applications just opened.
2. Appends the `PROGRAMS.md` master calendar, then a clickable index of every
   watched page (generated from config, so it can't go stale).

A source is in the digest iff `_is_digest_source()`: explicit `"digest": true`
in config wins, else the `name:` prefix is one of Competition / Hackathon /
Scholarship / Fellowship / Abroad / Program / NatSec / Lab / Conference / Grant.
Company job boards (`Chip:`, `Defense:`, `Hardware:`, `Page:`) are
internship-hunting and stay OUT — they carry `"digest": false` explicitly.

**Pagewatch keying (gotcha #9):** pagewatch state keys are
`pw::<url>::#<content-hash>` via `_pw_key()`. Keyed by URL alone — as it was
before 2026-08-03 — a watcher fires **exactly once, ever**, then goes silent, so
"tell me when applications open" never fires again. The dedicated prefix also
avoids colliding with job URLs that contain `#` fragments. A URL with no recorded
hash yet is baselined **silently**, so a keying change can't flood the first email.

## Layout

| File | Purpose |
|---|---|
| `.github/workflows/watch.yml` | Hourly cron + manual "Run workflow" button |
| `watcher.py` | All logic. Fetchers → filters → dedup → email |
| `config.json` | Sources + filters. **Most changes belong here, not in code.** |
| `seen_jobs.json` | State. Auto-committed each run. Never hand-edit. |
| `OPEN_ROLES.md` | Auto-generated snapshot of every role currently open, rewritten each full sweep and committed. Never hand-edit. |
| `TOP_PICKS.md` | Curated shortlist: FPGA/ASIC/DSP design roles only, ranked. Auto-generated; never hand-edit. |
| `PROGRAMS.md` | Hand-maintained deadline calendar, appended to the Sunday digest. **Edit this one by hand.** |
| `verify_sources.py` | Probes every source and reports the dead ones. Run it in CI — a mistyped token returns 0 jobs silently. |
| `test_filters.py` | Filter regression tests over real posting titles. Run before any filter change lands. |
| `applications.md` | **Private, gitignored** (repo is public!). Application tracker: one section per role — company, status, resume used, notes. Claude edits this directly on request. Never commit it. |

**Secrets (repo → Settings → Secrets → Actions):** `SMTP_USERNAME` (a Gmail
address), `SMTP_PASSWORD` (Gmail **App Password**, not the account password),
`EMAIL_TO`. Optional: `USAJOBS_API_KEY` + `USAJOBS_EMAIL`.

## Architecture

Every entry in `config.json` → `firms[]` has an `ats` field that routes it to a
fetcher in `watcher.py`'s `FETCHERS` dict. Every fetcher returns normalized dicts:
`{id, title, company, location, url, content, ...}`.

| `ats` | What it does |
|---|---|
| `greenhouse` `lever` `ashby` `smartrecruiters` `workable` | Public ATS JSON APIs. `token` = the slug in the board URL. |
| `workday` | Undocumented-but-public CXS endpoint. Needs `host` / `tenant` / `site` — get them from the careers page's DevTools → Network → the POST to `/wday/cxs/.../jobs`. Use `search_text` to filter server-side and `max_pages` to cap. |
| `amazon` | Undocumented `amazon.jobs/en/search.json`. Covers AWS / Robotics / all. |
| `usajobs` | Federal: NASA, DOE labs, NSA, Army/Navy research, Pathways. Needs a free key. |
| `github_json` | Tracker repos publishing `listings.json` (vanshb03). |
| `github_md` | Tracker repos whose data is a markdown **table** (sndsh404, speedyapply). |
| `autodiscover` | **The big one.** Harvests every apply URL from all trackers, decodes each company's ATS board, and polls ~270 boards **in parallel**. Self-expanding: any company a tracker adds gets polled from then on. |
| `pagewatch` | Change-detector for feed-less pages. Used for the big chip employers with no pollable API — AMD, Qualcomm, Apple, TI, Synopsys, Arm, Lattice — plus the labs (NASA OSTEM, SULI, JHU APL, Sandia). Alerts when watched keywords appear/change. |

Failed sources are **skipped and logged** (`x <name> skipped`), never crash the run.
Read the Actions log to see which sources actually resolved.

## Filtering (`config.json` → `filters`)

1. `title_keywords` — must look like an internship
2. `title_require_any` — must be a **chip-design** domain (61 keywords: fpga, asic,
   rtl, verilog, digital design, soc, microarchitecture, dsp, serdes, ...)
3. `title_exclude` — **verification and physical design first** (79 entries), then
   PhD/Masters, off-cycle, and non-EE/CE engineering. This list is what keeps DV
   and PnR reqs out; treat it as load-bearing.
4. **Cycle check** — see gotcha #1 below
5. **US-only gate** (`_is_us_location`) — clearly-non-US roles are dropped after the
   relevance check; empty/ambiguous locations are kept (never silent-drop a US role)
6. `clearance_keywords` — still computed by `is_clearance()` for the run log and the
   🇺🇸 flag in TOP_PICKS, but no longer creates an email section (see "Who this is for")

Then, at ranking time (not a filter — nothing is dropped here):

7. `_role_category()` sorts a title into DSP → FPGA → ASIC/SoC → other. A title
   matching `_SOFTWARE_RE` **without** a hard design signal is demoted to "other",
   because "GPU/AI Application System Software Engineer Intern" is a real posting
   that otherwise landed in the ASIC bucket on the word "GPU" alone.

## HARD-WON GOTCHAS — read before changing anything

1. **NEVER require the year in the job title.** Most companies don't put it there
   (Palantir: `"Forward Deployed Software Engineer - Internship - Intel"`). An
   earlier version required `"2027"` in the title and **silently discarded every
   such role** across all direct ATS sources for weeks.
   Current logic: if the title names *any* year, one of them must be ours; else
   check the description; **if no year appears anywhere, KEEP it** — a live intern
   posting is almost always the current cycle, since recruiting runs a year ahead.

2. **Silent drops are the most dangerous bug class.** #1 went unnoticed because a
   filtered-out role produces no log line. **If you add a filter, log what it drops.**

3. **Auto-discovery must stay parallel.** 211 boards polled sequentially takes
   *hours* (Workday paginates 20 at a time). Keep `ThreadPoolExecutor`,
   `max_pages=3`, and `budget_seconds`. A sequential version hung a run for 20+ min.

4. **`git push` must rebase first.** The `Save state` step does
   `git pull --rebase` before pushing — otherwise editing files via the GitHub web
   UI moves `main` and the run's state-commit fails with a non-fast-forward error.

5. **Community trackers go stale.** `sharunkumar` is really a *2026* repo; its few
   "2027" tags produced dead links and closed roles. It's disabled. **Verify a
   tracker's actual cycle before enabling it.**

6. **Trackers lag; boards don't.** Polling a company's board directly beats reading
   a tracker — you see the posting the hour it goes up instead of when a maintainer
   adds it. That's the whole point of `autodiscover`.

7. **Substring keyword matching floods the email with garbage.** `"intern" in
   title` matches Intern**al**, Intern**ational**, Intern**als**, Intern**et** —
   one baseline email had 100+ "Internal Audit" / "International Sales" directors.
   Same trap: `"systems"` matched "Eco**systems**". `_title_is_internship()` and
   `_has_term()` use word-boundary regexes; keep it that way for any new keyword
   gate. Filters now count every drop by reason (`DROP_COUNTS`) and print a
   summary at the end of each run — check it after any filter change.

8. **Emails show one line per role.** `_collapse_locations()` merges the same
   company+title posted in N cities into one entry ("NYC · Palo Alto +2 more").
   Display-only: every posting URL is still tracked individually in
   `seen_jobs.json`, so a role opening in a new city later still alerts.

9. **Pagewatch keys must include the content hash.** `_pw_key()` builds
   `pw::<url>::#<hash>`. Keyed by URL alone, a watcher fires exactly once ever and
   then goes silent forever — which defeats the entire point of "tell me when
   applications open". A URL with no recorded hash is baselined silently.

10. **Verification and physical design are the noise, not the signal.** They are
    the two largest job families adjacent to RTL design, they share almost all of
    its vocabulary, and there are more of them than of design roles. `title_exclude`
    (config) and `SKIP_RE` (code) are both load-bearing here, and `test_filters.py`
    pins them with real titles. If you loosen either, re-run the tests: the failure
    mode is a quiet inbox full of DV reqs, which reads as "the watcher works" until
    you actually open the email.

11. **`\bgpu\b` alone does not mean chip design.** Silicon vocabulary shows up in
    pure software titles. `_role_category()` demotes anything matching
    `_SOFTWARE_RE` unless it also carries a hard design signal. Real example that
    forced this: "GPU/AI Application System Software Engineer Intern".

## Pending / next upgrades

- **Run `verify_sources.py` once, early.** The Workday host/site pairs and ATS
  tokens in `config.json` were harvested from live tracker URLs rather than typed
  from memory, but a handful (Applied Materials, MemX, Vatic Labs) are unverified
  and carry no `"verified": true`. One CI run tells you which to drop.
- **A hardware-specific tracker would be the biggest coverage win.** The trackers
  currently configured are SWE-oriented; chip roles reach them only incidentally.
  If an ECE/hardware equivalent of `SimplifyJobs` appears, add it as `github_json`.
  (Probe: `https://raw.githubusercontent.com/<owner>/<repo>/dev/.github/scripts/listings.json`)
- **AMD, Qualcomm, Apple, TI and Lockheed have no pollable feed** — they use
  Radancy/Phenom, not Workday's public CXS endpoint, so they are `pagewatch` only
  and the signal is weak. Set *native* job alerts on those five careers sites as
  the real backup; that is the single highest-value manual step.
- **USAJOBS is configured but inert** until `USAJOBS_API_KEY` / `USAJOBS_EMAIL`
  secrets are set. Free key: <https://developer.usajobs.gov/apirequest/>
- **iCIMS fetcher** — several defense contractors use it; no clean public API.
  (GD Mission Systems turned out to be on SmartRecruiters as `gdmsi` and is polled
  directly — it posts "FPGA Intern Engineer".)
- **Eightfold fetcher** — Netflix and others.
- **FAANG page-watchers are weak** (JS single-page apps; the static HTML doesn't
  change when a job posts). Set *native* job alerts at Google / Meta / Apple /
  Microsoft / Netflix as the real backup.
- LinkedIn / Indeed have **no public API** and scraping them gets IP-blocked from
  Actions runners. They mostly re-list ATS postings anyway, so polling the ATS
  directly is both earlier and cleaner. Don't go down this road.

## Testing

Filters are pure functions, so the regression suite needs no network. **Run it
before changing any filter** — every title in it is a real posting observed in
the community trackers:

```bash
python3 test_filters.py
```

It pins the two things most likely to break this watcher: chip-design roles must
survive (`Hardware ASIC Design Intern`, `SoC Digital Design Engineer Intern`,
`FPGA Intern`, `DSP Firmware Engineering Co-op`) and verification / physical
design must not (`ASIC Design Verification`, `RTL Power Optimisation & Physical
Design`, `Static Timing Analysis Intern`).

Check the sources are actually alive (needs network; run it in CI):

```bash
python3 verify_sources.py           # human-readable
python3 verify_sources.py --json    # machine-readable
python3 verify_sources.py --prune   # drop dead entries from config.json
```

A mistyped Greenhouse token or renamed Workday site does **not** raise — the
fetcher returns zero jobs and the log says "0 relevant", which is
indistinguishable from "nothing is open". That is what this script is for.

Full local run (sends a real email):

```bash
pip install -r requirements.txt
SMTP_USERNAME=... SMTP_PASSWORD=... EMAIL_TO=... python watcher.py
```

Delete `seen_jobs.json` locally to force a fresh baseline. **Don't commit that
deletion** unless you want a full catch-up email.
