---
description: Tailor Sam's resume to a job posting, compile it, draft short answers, fill and upload the application in Chrome, and log it
---
The user gives a job-posting URL or pasted job description as: $ARGUMENTS

Private inputs (gitignored, never commit them; this repo is public):
- `resumes/PROFILE.md`: the bullet bank and story bank. Every claim you may use, tagged [verified] / [confirm] / [never].
- `resumes/base/hardware.tex`: the base resume (Jake Gutierrez template).
- `applications.md`: form defaults and the application tracker.

1. **Get the posting.** WebFetch the URL (fallback `curl.exe -sL <url>`). Extract company, exact title,
   location, cycle, required and preferred qualifications, and every short-answer / essay question
   (with its word or character limit). If the company is a quant / HFT firm, stop and say so: Sam does
   not apply to them. If the role is pure design verification (DV / UVM / testbench, not "design and
   verification"), say so and ask before continuing: Sam has dropped DV roles.

2. **Tailor with minimal edits.** Copy the base to
   `resumes/out/<Company>/Im_Samuel_<Company>.tex` (never edit the base). Then only reorder bullets,
   swap in other [verified] bullets from PROFILE.md, reorder skills and coursework, and **bold**
   phrases that match the posting's wording. Rules:
   - NEVER invent a metric, tool, or claim. Use [confirm] bullets only after Sam OKs them; never [never].
   - If a preferred qualification is almost true, name the small task that would make it true
     instead of writing it.
   - No em-dashes. Plain, human voice. Keep LaTeX escapes (`\&`, `\%`, `\#`).

3. **Compile:** run `tectonic Im_Samuel_<Company>.tex` in that folder. Tectonic is installed at
   `C:\Users\samue\AppData\Local\Programs\tectonic\tectonic.exe` if it is not on PATH.
   Check it is exactly one page:
   `python -c "from pypdf import PdfReader; print(len(PdfReader('Im_Samuel_<Company>.pdf').pages))"`.
   If it is two pages, drop or shorten the least relevant bullet and recompile.
   Show the PDF with `explorer /select,"<full path to the PDF>"`.

4. **Coverage table:** each requirement and preferred qualification, and where the resume now covers
   it, or "gap".

5. **Auto-draft short answers.** For every question found in step 1 (and, if the form has an optional
   cover-letter or "anything else" box, one short paragraph for it), write a draft from PROFILE.md
   only: the "About me", "Why this area" and "Stories" sections first, then the bullets. Rules:
   - Every fact must trace to a [verified] item in PROFILE.md. No invented numbers, tools or feelings.
   - Pick the one or two stories that best match the question and the posting; name the company's
     product or team only if the posting itself mentions it.
   - Respect the limit. Plain first-person voice, short sentences, no em-dashes, no "passionate",
     "leverage", "synergy", "I am excited to", or similar filler.
   - Save them to `resumes/out/<Company>/answers.md` (question, limit, draft, word count) and show them
     in chat. They are drafts for Sam to read and edit.

6. **Fill the application in Chrome** with the Claude in Chrome extension (load the chrome-browser
   skill first; load `file_upload` together with the core tools). Open the apply URL in a new tab.
   - Text and select fields: from `applications.md` → "Form defaults" only. If a field has no default
     there, leave it blank and list it for Sam. Double-check the work-authorization, sponsorship and
     citizenship answers.
   - **Resume upload:** find the resume `<input type="file">` with `find` / `read_page` (never click the
     upload button: that opens a native picker) and call `file_upload` with the absolute path of the
     tailored PDF from step 3. Then confirm the page shows the file name. If the form also has a
     separate cover-letter upload, leave it empty unless Sam asked for one. If `file_upload` rejects the
     path, say so and give Sam the path to upload by hand.
   - **Short answers:** paste the step-5 drafts into their fields so Sam can read them in place, and
     list every field you filled this way. These are drafts; Sam edits them before submitting.
   - NEVER click Submit. Sam reviews and submits.

7. **Log it** in the `applications.md` tracker: date, company, role, status `prepared`, resume
   file, deadline. When Sam says "applied", change the status to `applied`.
