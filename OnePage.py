import os
import json
import re
from decouple import config
import google.generativeai as genai
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table

class OnePageCVBuilder:
    # Fields that require specific array handling (like multiple jobs)
    DYNAMIC_ARRAY_FIELDS = ["EXPERIENCE"]
    
    # Fields that require special formatting (like bullet points)
    SPECIAL_FORMATTING_FIELDS = ["JOB_DESC"]

    def __init__(self, api_key, template_path, output_path="Final_OnePage_CV.docx"):
        self.template_path = template_path
        self.output_path = output_path
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 3. Read Template Placeholders and Build Dynamic Schema
        self.all_blocks = self._get_all_blocks(template_path)
        self.static_placeholders, self.dynamic_placeholders = self._get_placeholders_from_template()
        self.schema_guidelines = self._build_dynamic_schema()

    def _get_all_blocks(self, file_path):
        """Helper to get all paragraphs, including those in tables."""
        doc = Document(file_path)
        all_blocks = list(doc.paragraphs)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    all_blocks.extend(cell.paragraphs)
        return all_blocks
    
    def _get_placeholders_from_template(self):
        """Scans the template to find all unique placeholders."""
        static = set()
        dynamic = set()
        
        for block in self.all_blocks:
            # Find all {{KEY}} patterns
            placeholders = re.findall(r"\{\{([A-Z_]+)\}\}", block.text)
            for key in placeholders:
                # Differentiate between indexed job fields (JOB1_TITLE) and static fields (NAME)
                if re.match(r"JOB[1-4]_[A-Z_]+", key):
                    # We only care about the base job fields for dynamic handling
                    base_key = re.sub(r"JOB[1-4]_", "JOB_", key)
                    dynamic.add(base_key)
                elif key not in self.DYNAMIC_ARRAY_FIELDS:
                    static.add(key)
        
        return list(static), list(dynamic)

    def _build_dynamic_schema(self):
        """Creates the schema guidelines for the AI based on detected placeholders."""
        schema = {}
        
        # 1. Build Static Fields Schema
        for key in self.static_placeholders:
            # Add a generic description, could be enhanced with manual mapping if needed
            schema[key] = {"description": f"Candidate's content for the {key} field. Ensure it is concise and relevant."}
        
        # 2. Add Dynamic Array Fields (e.g., EXPERIENCE)
        if self.dynamic_placeholders:
            # Define the structure for the EXPERIENCE array dynamically
            job_structure = {key.replace("JOB_", ""): {"type": "string"} for key in self.dynamic_placeholders}
            
            schema["EXPERIENCE"] = {
                "description": "Array containing the 3-4 most relevant job experiences. Each job must be an object with the following keys:",
                "example_structure": job_structure
            }
        
        return schema


    def extract_text_from_candidate(self, file_path):
        """Simple extractor for DOCX. Can be expanded for PDF."""
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        # Also grab table text
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    full_text.append(cell.text)
        return "\n".join(full_text)

    def optimize_content(self, raw_text):
        """Uses Gemini to structure and condense the CV into a dynamic schema."""
        print("--- Optimizing content with Gemini... ---")
        
        # Build a clear JSON object defining the expected output structure for the AI
        required_json_keys = self.static_placeholders.copy()
        if "EXPERIENCE" in self.schema_guidelines:
            required_json_keys.append("EXPERIENCE")

        prompt = f"""
        You are an expert CV writer. Your goal is to rewrite the candidate's CV to fit a STRICT ONE-PAGE layout.
        
        INSTRUCTIONS:
        1. Extract and rewrite details based on the schema derived from the template placeholders.
        2. Strictly limit the EXPERIENCE array to the 4 most relevant jobs.
        3. Rewrite descriptions to be punchy, using active verbs (e.g., "Led," "Developed," "Optimized").
        4. Job descriptions (JOB_DESC) must be 3-5 bullet points. Use newline characters (\\n) to separate bullets within the JOB_DESC string.
        5. Output ONLY valid JSON. If a piece of information is missing (e.g., LINKEDIN), return an empty string "" for that key.
        
        RAW CANDIDATE TEXT:
        {raw_text[:8000]}
        
        SCHEMA DEFINITIONS (Derived from Template):
        {json.dumps(self.schema_guidelines, indent=2)}
        
        REQUIRED JSON OUTPUT FORMAT:
        Return a single flat JSON object containing ONLY the keys: {required_json_keys}.
        """
        
        response = self.model.generate_content(prompt)
        json_str = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_str)

    def _replace_text_preserve_style(self, element, placeholder, new_text):
        """Replaces placeholder in a paragraph or run while preserving style."""
        if isinstance(element, Paragraph) and placeholder in element.text:
            
            for run in element.runs:
                if placeholder in run.text:
                    run.text = run.text.replace(placeholder, new_text)
                    return
            
            # Fallback for complex run splits 
            if placeholder in element.text:
                element.text = element.text.replace(placeholder, new_text)

    def generate_document(self, candidate_path):
        
        # 1 & 2. Get Content & Optimize (Uses self.schema_guidelines)
        raw_text = self.extract_text_from_candidate(candidate_path)
        data_map = self.optimize_content(raw_text)
        
        # 3. Load Template & Get Blocks
        print(f"--- Loading template: {self.template_path} ---")
        doc = Document(self.template_path)
        all_blocks_to_modify = self._get_all_blocks(self.template_path) # Reload blocks from doc object
        
        print("--- Injecting optimized data with comprehensive cleanup... ---")
        
        # Extract dynamic job data before proceeding
        experience_array = data_map.pop("EXPERIENCE", [])
        
        # 4.1 Inject Static Fields (including new fields like PROJECTS) and clean up if missing
        print(f"Injecting {len(self.static_placeholders)} static and new fields...")
        for block in all_blocks_to_modify:
            for key in self.static_placeholders:
                value = data_map.get(key, "")
                placeholder = f"{{{{{key}}}}}"
                
                if placeholder in block.text:
                    # --- CRITICAL CLEANUP FOR STATIC FIELDS ---
                    # If the AI returns an empty value for this field, clear the entire paragraph.
                    if not value and isinstance(block, Paragraph):
                        block.clear()
                        continue
                    
                    # Normal replacement if data exists
                    self._replace_text_preserve_style(block, placeholder, value)

        # 4.2 Inject Dynamic Fields (Experience) - Using a loop that depends on array size
        print(f"Injecting {len(experience_array)} job entries...")
        max_jobs_injected = 0
        
        for i, job in enumerate(experience_array):
            if i >= 4:
                break # Still limiting to 4 jobs for one-page CV constraint
            
            max_jobs_injected = i + 1
            job_index = i + 1
            
            # Find and inject into all blocks
            for block in all_blocks_to_modify:
                # Inject all fields found in the dynamic structure (TITLE, COMPANY, DATE, DESC, etc.)
                for base_field in self.dynamic_placeholders:
                    field = base_field.replace("JOB_", "")
                    key_name = f"JOB{job_index}_{field}"
                    placeholder = f"{{{{{key_name}}}}}"
                    
                    if placeholder in block.text:
                        value = job.get(field, "")

                        # Apply special formatting (e.g., bullets for JOB_DESC)
                        if field in self.SPECIAL_FORMATTING_FIELDS:
                            bullets = value.replace('\n', '\n• ')
                            if bullets and not bullets.startswith('• '):
                                bullets = '• ' + bullets
                            value = bullets
                        
                        self._replace_text_preserve_style(block, placeholder, value)

        # 4.3 Cleanup: Remove remaining job placeholders if not all 4 slots were used
        # This loop iterates through any slots that were NOT filled (e.g., Job 3 and Job 4 if only 2 jobs were returned)
        print("Cleaning up unused placeholders...")
        for job_index in range(max_jobs_injected + 1, 5): # Check for slots 1 to 4
            for block in all_blocks_to_modify:
                for base_field in self.dynamic_placeholders:
                    field = base_field.replace("JOB_", "")
                    key_name = f"JOB{job_index}_{field}"
                    placeholder = f"{{{{{key_name}}}}}"
                    if placeholder in block.text:
                        # Clear the entire paragraph/block to remove the unused section
                        if isinstance(block, Paragraph):
                             block.clear()
        
        # 5. Save
        doc.save(self.output_path)
        print(f"--- Complete! Optimized CV saved as {self.output_path} ---")

# --- Execution ---
if __name__ == "__main__":
    # CONFIGURATION
    API_KEY = config("GOOGLE_API_KEY")
    CANDIDATE_FILE = "CandidateCV.docx" # The messy input
    TEMPLATE_FILE = "Standard.docx" # The pretty template with {{PLACEHOLDERS}}
    
    # Create dummy files for testing if they don't exist
    if not os.path.exists(CANDIDATE_FILE):
        print("Please provide a candidate file.")
    elif not os.path.exists(TEMPLATE_FILE):
        print("Please provide the Standard.docx template with placeholders.")
    else:
        builder = OnePageCVBuilder(API_KEY, TEMPLATE_FILE)
        builder.generate_document(CANDIDATE_FILE)