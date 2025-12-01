# CvOptimizer

> Tools to convert messy CVs into focused, targeted resumes and to generate one-page CVs from templates using Google Generative AI (Gemini).

## Overview

`CVoptimizer` contains two primary utilities and a template-driven one-page CV generator:
- `optimize.py` — Rewrites meaningful CV paragraphs/tables to better match a target `job_description.txt` using Gemini.
- `OnePage.py` — A template-driven builder that condenses and formats candidate information into a strict one-page CV using a `.docx` template with `{{PLACEHOLDERS}}`.

This repository is a developer-focused starting point for programmatic CV improvement and template-based one-page CV generation.

## Features

- Rewrites paragraph and table text segments while attempting to preserve simple formatting (`optimize.py`).
- Builds a strict one-page CV from a `.docx` template with placeholders (`OnePage.py`).
- Simple, readable code you can adapt for other document processing workflows.

## Requirements

- Python 3.8+
- Dependencies are pinned in `requirements.txt` (use the included file to reproduce the environment).

Install dependencies using the provided `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Optionally create and activate a virtual environment first:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Key dependencies (examples from `requirements.txt`):**
- `python-docx` — for reading and writing `.docx` files
- `google-generativeai` / `google-ai-generativelanguage` — Google Generative AI (Gemini) client libraries
- `python-decouple` — environment variable management

## Configuration

The `optimize.py` script requires an API key for Google Generative AI. The project uses `python-decouple` to read environment variables. Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_api_key_here
```

**Important security notes:**
- `.env` is already listed in `.gitignore` to prevent accidental commits of secrets.
- Keep your API key private and never commit it to version control.
- The code uses the Gemini model `gemini-2.5-pro` by default; you can change this by editing the model identifier in the `CVoptimizer` class constructor in `optimize.py`.

## Project Structure

```
CVoptimizer/
├── .env                    # Environment variables (not committed; add your GOOGLE_API_KEY here)
├── .gitignore              # Excludes .env, sample files, and venv from git
├── CandidateCV.docx        # Input: Candidate CV document to optimize
├── Final_OnePage_CV.docx   # Output: One-page CV produced from template (example)
├── OptimizedCV.docx        # Output: Result of `optimize.py`
├── OnePage.py              # Template-driven one-page CV generator
├── optimize.py             # CV rewriting script using Gemini
├── Standard.docx           # Template with `{{PLACEHOLDERS}}` used by `OnePage.py`
├── job_description.txt     # Input: Target job description for context
├── requirements.txt        # Pinned dependencies
├── README.md               # This file
└── venv/                   # Virtual environment (not committed)
```

### Optimize a CV (rewrite to match a Job Description)

To optimize an existing CV so its language and keywords better match a target job description:

1. **Prepare input files:**
  - Place your candidate CV as `CandidateCV.docx` in the project root.
  - Ensure `job_description.txt` contains the target job description (a sample is included).
  - Set `GOOGLE_API_KEY` in your `.env` file.

2. **Run the optimizer:**

```powershell
python optimize.py
```

- The script processes meaningful paragraphs and table cells, rewrites them with Gemini, and saves `OptimizedCV.docx`.

### Generate a One-Page CV from a Template (`OnePage.py`)

`OnePage.py` converts a candidate's raw CV into a clean, template-driven one-page resume. The template should contain `{{PLACEHOLDERS}}` for fields like `NAME`, `LINKEDIN`, and repeated job blocks such as `JOB1_TITLE`, `JOB1_COMPANY`, `JOB1_DATE`, `JOB1_DESC`, etc.

1. **Prepare files:**
  - Put the template (e.g., `Standard.docx`) in the repo and ensure placeholders follow the `{{KEY}}` pattern. The template in this repo is `Standard.docx`.
  - Place your candidate file as `CandidateCV.docx`.
  - Ensure `GOOGLE_API_KEY` is set in `.env`.

2. **Run the OnePage builder:**

```powershell
python OnePage.py
```

- Output: `Final_OnePage_CV.docx` (or the filename set in `OnePage.py`).
- The builder:
  - Extracts the candidate's raw text,
  - Uses Gemini to return a structured JSON matching the template schema (e.g., static fields and an `EXPERIENCE` array),
  - Injects values into the template, formats job descriptions as bullets, and removes unused placeholders to keep the layout clean.

## File Descriptions

### `optimize.py`

Rewrites CV text segments using Gemini to better match a provided `job_description.txt`:
- Filters out very short lines (names, dates) to avoid hallucination and reduce token usage.
- Replaces paragraph/table text while attempting to preserve basic paragraph-level formatting.
- Default model: `gemini-2.5-pro` (configurable in the file).

### `OnePage.py`

Template-driven one-page CV builder:
- Detects `{{PLACEHOLDERS}}` from the template and builds a schema for the AI to return structured JSON.
- Produces a compact, punchy one-page CV by limiting experience entries and formatting job bullets.
- Default model: `gemini-2.5-flash` (configurable in the file).

### `job_description.txt`

Plain-text file containing the target job description. Used as context by `optimize.py`.

## Design Notes & Limitations

- The `extract_structure.py` implementation uses `python-docx` and a simplified sequential iteration across the document body. It may not preserve every low-level OpenXML nuance.
- `optimize.py` filters out very short fragments (likely names, dates, or headers) to avoid wasting API tokens and to reduce hallucination risk.
- The optimizer flattens complex inline styles when replacing paragraph text to ensure a clean, coherent rewrite. If preserving mixed inline formatting is required, additional logic is necessary to map and reapply styles per run.
- The scripts include basic error handling and fallback behavior (e.g., returning original text on API failure), but they are not production-hardened.

## Cost & Safety Considerations

- Calling a generative API will incur usage costs and may have rate limits. Test on small samples first and monitor usage.
- The `optimize.py` prompts the model to not invent facts, but downstream verification by a human is strongly recommended.

## Troubleshooting

- If `python-docx` raises file-not-found errors, confirm the `.docx` file exists and the path passed into the constructor is correct.
- If API calls fail, ensure `GOOGLE_API_KEY` is set and valid, and your network allows outbound connections to Google APIs.

## Contributing

Contributions welcome. Ideas:
- Add an `argparse` CLI for both scripts (`optimize.py` and `OnePage.py`).
- Add unit tests to validate placeholder detection and JSON parsing from the AI.
- Implement finer-grained run-level style re-application when replacing paragraph text.
- Add an optional `--dry-run` / `--diff` output to preview changes.

## Support & Troubleshooting

- **File not found errors:** Verify input files exist (`CandidateCV.docx`, `Standard.docx`, etc.).
- **API errors / authentication failures:** Ensure `GOOGLE_API_KEY` is present in `.env` and valid.
- **Unexpected AI output / parsing errors:** The scripts expect the AI to return clean JSON (OnePage) or plain text (optimize). If parsing fails, inspect the raw response and adjust prompt/validation.
- **Formatting issues:** Complex inline styling may be simplified during replacement; templates should be designed to be resilient to paragraph-level changes.

---

**Quick start:**
1. Obtain a Google Generative AI API key and add `GOOGLE_API_KEY` to `.env`.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Place `CandidateCV.docx` and (for one-page) `Standard.docx` in the repo.
4. Run either:

```powershell
python optimize.py   # Rewrite CV fragments to match a job description
python OnePage.py    # Generate a one-page CV from a template
```

If you'd like, I can next:
- Add a small CLI wrapper to `OnePage.py` and `optimize.py` to accept `--cv`, `--template`, `--jd`, `--out`, and `--model` flags,
- Add a `--dry-run` diff mode,
- Or run a quick local sanity run (you must have `CandidateCV.docx`, `Standard.docx`, and a valid `GOOGLE_API_KEY`).
