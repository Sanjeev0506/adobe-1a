import fitz
import json
import os

def get_document_info(doc):
    """
    Pass 1: Iterates through the document to collect all unique font sizes.
    This helps in dynamically determining heading levels.
    """
    unique_font_sizes = set()
    all_blocks = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        all_blocks.extend(blocks)
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        unique_font_sizes.add(span["size"])
    
    return {
        "unique_font_sizes": sorted(list(unique_font_sizes), reverse=True),
        "all_blocks": all_blocks
    }

def determine_heading_levels(doc_info):
    """
    Pass 2: Analyzes font sizes to create a dynamic set of rules for headings.
    This avoids hardcoding font sizes and makes the solution more robust.
    """
    font_sizes = doc_info["unique_font_sizes"]
    
    # A simple heuristic: The largest font sizes are most likely headings.
    # We will pick the top 3-4 largest font sizes as candidates for H1, H2, etc.
    rules = {}
    if len(font_sizes) > 0:
        rules["H1"] = font_sizes[0]
    if len(font_sizes) > 1:
        rules["H2"] = font_sizes[1]
    if len(font_sizes) > 2:
        rules["H3"] = font_sizes[2]
    # You can add more levels here if needed.
    
    return rules

def find_headings(doc, heading_rules):
    """
    Pass 3: Finds and extracts headings based on the rules determined in Pass 2.
    """
    outline = []
    
    # Reverse the rules dictionary to make lookup faster later.
    size_to_level = {v: k for k, v in heading_rules.items()}
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        font_size = span["size"]
                        
                        # Check if the font size matches one of our heading rules.
                        if font_size in size_to_level:
                            level = size_to_level[font_size]
                            
                            # Heuristics: headings are usually short.
                            if len(text.split()) < 10:
                                outline.append({
                                    "level": level,
                                    "text": text,
                                    "page": page_num + 1
                                })
                                
    return outline

def extract_outline(pdf_path):
    """
    Orchestrates the three passes to extract a structured outline.
    """
    try:
        doc = fitz.open(pdf_path)
        
        # --- Get Title ---
        title = ""
        if doc.page_count > 0:
            first_page = doc[0]
            text_blocks = first_page.get_text("blocks")
            if text_blocks:
                title = text_blocks[0][4].strip().split('\n')[0]

        # --- Three-Pass Extraction ---
        doc_info = get_document_info(doc)
        heading_rules = determine_heading_levels(doc_info)
        outline = find_headings(doc, heading_rules)
        
        doc.close()
        
        return {"title": title, "outline": outline}
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

def main():
    # The paths are relative to where your script is located (E:\adobe).
    input_dir = "Challenge_1a/input"
    output_dir = "Challenge_1a/output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            print(f"Processing {filename}...")
            result = extract_outline(pdf_path)
            if result:
                output_filename = os.path.splitext(filename)[0] + ".json"
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, "w") as f:
                    json.dump(result, f, indent=4)
                print(f"Successfully created {output_filename}")
            else:
                print(f"Failed to process {filename}")

if __name__ == "__main__":
    main()