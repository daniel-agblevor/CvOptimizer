# CVoptimizer

> A small toolkit to extract document structure from `.docx` files and optimize CVs to better match job descriptions using Google Generative AI (Gemini).

## Overview

`CVoptimizer` contains two main utilities:
- `extract_structure.py` — Analyzes a Word (`.docx`) document and produces a JSON "blueprint" describing paragraphs, tables, runs, styles, and basic metadata.
- `optimize.py` — Loads a candidate CV `.docx` and a `job_description.txt`, then rewrites meaningful CV text segments using Google Generative AI (Gemini) to better align the CV with the job description.

These tools are intended as a developer-focused starting point for programmatically improving or analyzing CV documents.

## Features

- Extracts paragraph and table structure, run-level formatting, and document metadata into JSON (`extract_structure.py`).
- Rewrites paragraph and table text segments while attempting to preserve simple formatting (`optimize.py`).
- Simple, readable code you can adapt for other document processing workflows.

## Requirements

- Python 3.8+
- `python-docx`
- `python-decouple`
- `google-generativeai` (Gemini client)

Install dependencies with pip:

```powershell
python -m pip install python-docx python-decouple google-generativeai
```

Optionally, create a `venv` first:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install python-docx python-decouple google-generativeai
```

## Configuration

The `optimize.py` script expects an API key for Google Generative AI. The project uses `python-decouple` to read environment variables. Create a `.env` file in the project root containing:

```
GOOGLE_API_KEY=your_api_key_here
```

Notes:
- Keep your API key secret. Do not commit `.env` to source control. Add `.env` to `.gitignore` if needed.
- The code uses the Gemini model `gemini-2.5-pro` by default; you may change the model identifier inside `optimize.py` as desired by editing the `CVoptimizer` class constructor.

## Usage

Basic examples assume you are in the project root where the files live.

- Extract a blueprint of a Word document (example uses `test_doc.docx` created by the script if missing):

```powershell
python extract_structure.py
# This will write `blueprint.json` in the working directory (per current script behavior).
```

- Optimize a CV to match a job description:

1. Ensure `job_description.txt` contains the target JD (there is a sample `job_description.txt` in the repo).
2. Place the candidate CV in the project root (default filename used in the script: `CandidateCV.docx`).
3. Ensure your `.env` contains `GOOGLE_API_KEY`.

```powershell
python optimize.py
# The script attempts to create sample files if missing and saves the optimized CV as `OptimizedCV.docx` by default.
```

If you want to call the classes from other code, example usage is:

```python
from optimize import CVoptimizer
from decouple import config

api_key = config('GOOGLE_API_KEY')
optimizer = CVoptimizer(api_key=api_key, jd_path='job_description.txt', cv_path='CandidateCV.docx')
optimizer.process()
```

## File Descriptions

- `extract_structure.py`: Contains `DocxBlueprintExtractor` which:
  - Reads a `.docx` file using `python-docx`.
  - Extracts metadata (author, created/modified timestamps, revision, etc.).
  - Extracts section/page layout data.
  - Iterates document body elements to capture paragraph and table structures and run-level formatting.
  - Provides `extract()` which returns a blueprint dict and `save_json(output_path)` to persist it.

- `optimize.py`: Contains `CVoptimizer` which:
  - Loads `job_description.txt` and a candidate CV `.docx`.
  - Uses `google.generativeai` (Gemini) to rewrite meaningful text segments.
  - Attempts to preserve basic formatting (font size, bold/italic/underline on the paragraph level); complex mixed inline styles are flattened.
  - Saves optimized CV to `OptimizedCV.docx` by default.

- `job_description.txt`: Plain text job description used as the target context for rewriting.

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

Suggestions and improvements are welcome. If you plan to extend the project, consider:
- Adding a CLI wrapper with `argparse` for clearer runtime flags.
- Adding a `requirements.txt` or `pyproject.toml` for reproducible installs.
- Adding unit tests for the parsing and replacement logic.

## Example Next Steps

- Add a small CLI to accept `--cv`, `--jd`, `--out`, and `--model` parameters.
- Add a `--dry-run` mode that generates a side-by-side diff of original vs optimized text.

---

If you'd like, I can:
- create a `requirements.txt` with pinned dependency versions,
- add a simple CLI wrapper to `optimize.py`, or
- run a quick sanity test to produce a sample `OptimizedCV.docx` (you'll need to supply `CandidateCV.docx` and a valid `GOOGLE_API_KEY`).

Tell me which one you'd like next.
