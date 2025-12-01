# CvOptimizer

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
- Dependencies listed in `requirements.txt`

Install dependencies using the provided `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Or optionally create and activate a virtual environment first:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Key dependencies:**
- `python-docx` (1.2.0) — for reading and writing `.docx` files
- `google-generativeai` (0.8.5) — Google Generative AI / Gemini client
- `python-decouple` (3.8) — environment variable management

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
├── OptimizedCV.docx        # Output: Result of optimization
├── extract_structure.py    # Utility to extract document structure to JSON
├── optimize.py             # Main CV optimization script
├── job_description.txt     # Input: Target job description for context
├── requirements.txt        # Pinned dependencies
├── README.md               # This file
└── venv/                   # Virtual environment (not committed)
```

### Extract Document Structure

To analyze the structure of a Word document and produce a JSON blueprint:

```powershell
python extract_structure.py
```

- If no input file is specified, the script creates a sample `test_doc.docx` automatically.
- Output: `blueprint.json` containing document metadata, sections, paragraphs, tables, and formatting details.

### Optimize a CV

To optimize a CV document to better match a job description:

1. **Prepare input files:**
   - Place your candidate CV as `CandidateCV.docx` in the project root.
   - Ensure `job_description.txt` contains the target job description (a sample is included).
   - Set `GOOGLE_API_KEY` in your `.env` file.

2. **Run the optimizer:**

```powershell
python optimize.py
```

- The script processes all meaningful text segments in paragraphs and tables.
- Output: `OptimizedCV.docx` with rewritten content aligned to the job description.

### Programmatic Usage

Import and use the classes directly in your own code:

```python
from optimize import CVoptimizer
from extract_structure import DocxBlueprintExtractor
from decouple import config

# Extract document structure
extractor = DocxBlueprintExtractor("input_document.docx")
blueprint = extractor.extract()
extractor.save_json("output_blueprint.json")

# Optimize a CV
api_key = config('GOOGLE_API_KEY')
optimizer = CVoptimizer(
    api_key=api_key,
    jd_path='job_description.txt',
    cv_path='CandidateCV.docx',
    output_path='OptimizedCV.docx'
)
optimizer.process()
```

## File Descriptions

### `extract_structure.py`

Provides the `DocxBlueprintExtractor` class for analyzing Word documents:
- Reads a `.docx` file and extracts its complete structure.
- **Metadata:** Author, created/modified timestamps, revision count.
- **Sections:** Page dimensions, orientation, margins.
- **Content:** Paragraphs, tables, runs, styles, alignment, and font properties.
- **Methods:**
  - `extract()` — Returns a blueprint dictionary.
  - `save_json(output_path)` — Persists the blueprint as JSON.

### `optimize.py`

Provides the `CVoptimizer` class for rewriting CVs using Gemini:
- Loads a CV document and a job description.
- Identifies meaningful text segments (filters out short headers, names, dates).
- Sends each segment to Google Generative AI (Gemini) with the job description as context.
- Rewrites content to align with the JD while preserving facts.
- Attempts to preserve basic formatting (font size, bold/italic/underline).
- **Methods:**
  - `process()` — Optimizes the CV in-place and saves to output file.

**Environment variable:** `GOOGLE_API_KEY` (required)

### `job_description.txt`

Plain-text file containing the target job description. Used as context for CV rewriting. The included sample is a Financial Analyst role at Canonical.

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

Suggestions and improvements are welcome. Potential enhancements:
- Add `argparse` CLI with flags for `--cv`, `--jd`, `--out`, `--model`, `--dry-run`.
- Implement advanced run-level formatting preservation to maintain mixed inline styles.
- Add unit tests for parsing and replacement logic.
- Add a `--diff` mode showing side-by-side comparisons before/after.
- Support additional document formats (`.pdf`, `.odt`, etc.).
- Add logging for API calls and performance metrics.

## Support & Issues

- **File not found errors:** Verify that `.docx` files exist and paths are correct.
- **API errors:** Ensure `GOOGLE_API_KEY` is set correctly and your API quota is active.
- **Network issues:** Confirm outbound connectivity to Google's generative AI API.
- **Formatting issues:** Complex inline styles may be simplified; this is a known limitation.

---

**Next steps:**
- Obtain a Google Generative AI API key from [Google AI Studio](https://aistudio.google.com).
- Create a `.env` file with your key.
- Add your CV (`CandidateCV.docx`) and target job description.
- Run `python optimize.py` to start optimizing.
