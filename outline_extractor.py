# outline_extractor.py (Definitive Hybrid Version)
import fitz  # PyMuPDF

def get_document_title(doc):
    """
    Extracts the document title using metadata as a priority,
    falling back to the largest text on the first page.
    """
    if doc.metadata and doc.metadata.get("title"):
        title = doc.metadata.get("title").strip()
        # A basic filter to avoid garbage metadata titles
        if len(title) > 3 and len(title.split()) < 20:
            return title

    if doc.page_count > 0:
        # Fallback to finding the largest font size on the first page
        page = doc[0]
        max_size = 0
        potential_title = ""
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    if line["spans"]:
                        line_text = "".join(s["text"] for s in line["spans"]).strip()
                        # A title should not be excessively long
                        if len(line_text.split()) < 15:
                            span = line["spans"][0]
                            if span["size"] > max_size:
                                max_size = span["size"]
                                potential_title = line_text
        if potential_title:
             return potential_title

    return "Untitled Document"

def analyze_document_with_font_analysis(doc):
    """
    This is the robust fallback method. It performs a single-pass font
    analysis that is highly accurate and filters out common noise
    like headers and footers.
    """
    lines_by_size = {}
    font_counts = {}

    # --- Single-pass data collection ---
    for page_num, page in enumerate(doc):
        page_height = page.rect.height
        # Use a 7% margin for headers and footers
        header_margin = page_height * 0.07
        footer_margin = page_height * 0.93

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    if not line["spans"]:
                        continue

                    # Positional filtering for headers and footers
                    y0 = line["bbox"][1]
                    if y0 < header_margin or y0 > footer_margin:
                        continue

                    line_text = "".join(s["text"] for s in line["spans"]).strip()

                    # Content filtering for noise
                    if not line_text or len(line_text) < 2 or line_text.isnumeric():
                        continue

                    size = round(line["spans"][0]["size"], 1)

                    if size not in font_counts:
                        font_counts[size] = 0
                    font_counts[size] += 1

                    if size not in lines_by_size:
                        lines_by_size[size] = []
                    lines_by_size[size].append({"text": line_text, "page": page_num + 1})

    if not font_counts:
        return []

    # --- Heuristic-based heading detection ---
    # Assume the most frequent font size is body text
    primary_body_size = max(font_counts, key=font_counts.get) if font_counts else 10.0

    # Identify potential heading sizes (larger and less frequent than body text)
    potential_heading_sizes = sorted(
        [s for s in font_counts if s > primary_body_size * 1.1 and font_counts[s] < font_counts[primary_body_size]],
        reverse=True
    )

    heading_levels = {}
    if len(potential_heading_sizes) > 0: heading_levels["H1"] = potential_heading_sizes[0]
    if len(potential_heading_sizes) > 1: heading_levels["H2"] = potential_heading_sizes[1]
    if len(potential_heading_sizes) > 2: heading_levels["H3"] = potential_heading_sizes[2]

    # --- Build the outline ---
    outline = []
    for level, size in heading_levels.items():
        if size in lines_by_size:
            for item in lines_by_size[size]:
                outline.append({"level": level, "text": item["text"], "page": item["page"]})

    return sorted(outline, key=lambda x: x['page'])


def extract_outline(pdf_path):
    """
    Definitive extraction function that uses a hybrid strategy. It tries
    the fast TOC method first and falls back to a high-accuracy font analysis.
    """
    try:
        doc = fitz.open(pdf_path)
        title = get_document_title(doc)

        # --- Strategy 1: The Instant Method (Built-in TOC) ---
        toc = doc.get_toc()
        if toc:
            # If a TOC exists, use it directly as it's the most reliable source
            outline = [{"level": f"H{min(lvl, 3)}", "text": text, "page": page} for lvl, text, page in toc]
            doc.close()
            return {"title": title, "outline": outline}

        # --- Strategy 2: The Accurate Fallback (Deep Font Analysis) ---
        outline = analyze_document_with_font_analysis(doc)

        doc.close()
        return {"title": title, "outline": outline}

    except Exception as e:
        print(f"An unexpected error occurred while processing {pdf_path}: {e}")
        return {"title": "Error Processing Document", "outline": []}