# main_1a.py (Corrected paths for Docker)
import os
import json
from outline_extractor import extract_outline

def process_all_pdfs():
    # Use absolute paths inside the container
    input_dir = '/app/input'
    output_dir = '/app/output'

    print(f"Starting processing for PDFs in {input_dir}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = extract_outline(pdf_path)

            output_filename = os.path.splitext(filename)[0] + '.json'
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, 'w') as f:
                json.dump(result, f, indent=4)
            print(f"Successfully created {output_filename}")

if __name__ == "__main__":
    process_all_pdfs()