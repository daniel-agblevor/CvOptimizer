# CV Optimizer

A suite of tools to automatically optimize CVs and generate polished, one-page resumes from templates using Google's Gemini AI.

## Overview

This project provides two main functionalities:

1.  **`optimize.py`**: A script that rewrites the content of a CV to align with a specific job description. It analyzes the text in paragraphs and tables, and uses Gemini to rephrase it, incorporating relevant keywords from the job description.
2.  **`OnePage.py`**: A template-driven tool that condenses a candidate's CV into a concise, one-page resume. It uses a `.docx` template with placeholders to structure the information and generate a professional-looking document.

## Features

-   **AI-Powered Content Optimization**: Leverages the Gemini AI to rewrite and improve CV content.
-   **Template-Based CV Generation**: Creates one-page resumes from customizable `.docx` templates.
-   **Structured Logging**: Comprehensive logging to provide insights into the script's execution and the AI's output.
-   **Preserves Basic Formatting**: Attempts to maintain simple formatting (bold, italics) when rewriting text.
-   **Easy to Configure**: Uses a `.env` file for simple configuration of the API key.

## Requirements

-   Python 3.8+
-   A Google Generative AI API key.

## Setup and Configuration

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/daniel-agblevor/CvOptimizer.git
    cd CvOptimizer
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure your API key:**
    -   Create a file named `.env` in the root of the project.
    -   Add your Google Generative AI API key to the `.env` file:
        ```
        GOOGLE_API_KEY="your_api_key_here"
        ```

## Usage

### Optimizing a CV (`optimize.py`)

This script will take an existing CV and rewrite its content to better match a job description.

1.  **Prepare the files:**
    -   Place the CV you want to optimize in the root of the project and name it `CandidateCV.docx`.
    -   Add the job description to the `job_description.txt` file.

2.  **Run the script:**
    ```bash
    python optimize.py
    ```
    The optimized CV will be saved as `OptimizedCV.docx`.

### Generating a One-Page CV (`OnePage.py`)

This script will generate a one-page CV based on a template.

1.  **Prepare the files:**
    -   Place the candidate's CV in the root of the project and name it `CandidateCV.docx`.
    -   Use the provided `Standard.docx` template, or create your own with `{{PLACEHOLDERS}}` for the fields you want to include.

2.  **Run the script:**
    ```bash
    python OnePage.py
    ```
    The generated one-page CV will be saved as `Final_OnePage_CV.docx`.

## Dependencies

This project relies on the following key Python libraries:

-   `google-generativeai`: To interact with the Gemini AI.
-   `python-docx`: For reading and writing `.docx` files.
-   `python-decouple`: For managing environment variables.

A full list of dependencies is available in the `requirements.txt` file.
