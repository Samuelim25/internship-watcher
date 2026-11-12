---
description: Tailor Sam's resume to a job posting, compile it, fill the application in Chrome, and log it
---
The user gives a job-posting URL or pasted job description as: $ARGUMENTS

Private inputs (gitignored, never commit them; this repo is public):
- `resumes/PROFILE.md`: the bullet bank. Every claim you may use, tagged [verified] / [confirm] / [never].
- `resumes/base/hardware.tex`: the base resume (Jake Gutierrez template).
- `applications.md`: form defaults and the application tracker.

1. **Get the posting.** WebFetch the URL (fallback `curl.exe -sL <url>`). Extract company, exact title,
   location, cycle, required and preferred qualifications, and any short-answer questions.
   If the company is a quant / HFT firm, stop and say so: Sam does not apply to them.

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

5. **Draft short answers** in Sam's voice, as drafts for him to edit. Never submit prose on his behalf.

6. **Fill the application in Chrome** with the Claude in Chrome extension (load the chrome-browser
   skill first). Open the apply URL in a new tab and fill text and select fields from
   `applications.md` → "Form defaults" only. If a field has no default there, leave it blank and
   list it for Sam. Double-check the work-authorization, sponsorship and citizenship answers.
   Claude cannot upload files: stop at the resume field and give Sam the PDF path.
   NEVER click Submit. Sam reviews and submits.

7. **Log it** in the `applications.md` tracker: date, company, role, status `prepared`, resume
   file, deadline. When Sam says "applied", change the status to `applied`.
