PDF Outline Extractor - Adobe India Hackathon: Round 1A
This project is a solution for the "Connecting the Dots" Hackathon, By B Sanjeev and Aditya K Menon for Round 1A challenge. It provides a robust and efficient system for extracting a structured outline (Title, H1, H2, H3) from any given PDF document.

The Challenge
The goal of Round 1A is to build a tool that can programmatically understand the structure of a PDF. The solution must accept a PDF file, extract its title and hierarchical headings (up to H3), and output this structure into a clean, valid JSON file. Key constraints include a strict execution time limit of 10 seconds for a 50-page document, offline operation within a Docker container, and no GPU dependencies.

Our Approach
To meet the dual requirements of high speed and high accuracy, this solution implements a two-stage hybrid strategy:

1. The Instant Method: Built-in Table of Contents (TOC)
For maximum efficiency, the program first attempts to read the PDF's embedded Table of Contents (TOC). If a valid TOC is present, it is used as the definitive source for the outline. This method is nearly instantaneous and provides a perfectly accurate, author-intended structure. This gives our solution a significant performance advantage on well-structured documents.

2. The Accurate Fallback: Deep Font Analysis
If the PDF does not contain a TOC, the system seamlessly falls back to a high-accuracy, single-pass font analysis. This "Deep Scan" is designed to be both fast and intelligent:

Single-Pass Processing: The script reads through the entire document only once to simultaneously gather font statistics and group text lines by size. This avoids redundant file I/O and significantly reduces processing time.

Intelligent Noise Filtering: It incorporates heuristics to filter out common non-heading elements. It identifies and ignores text in the typical header and footer regions of a page (e.g., top and bottom 7%).

Dynamic Heading Detection: The script doesn't rely on hardcoded font sizes. It first identifies the primary body text font size and then dynamically determines that headings are text lines with a larger font size that appear less frequently. This allows it to adapt to a wide variety of document styles.

This hybrid approach ensures that our solution is not only compliant with the time constraints but also robust enough to deliver high-quality outlines for a diverse range of PDF documents.

Models or Libraries Used
This project is lightweight and does not use any pre-trained machine learning models. The core logic is powered by a single, highly efficient library:

PyMuPDF (fitz): A high-performance Python library for data extraction from PDF documents. It is used for all text, metadata, and TOC extraction tasks.

Folder Structure
The project is organized as follows:

ADOBE_1A/
├── .gitignore
├── Dockerfile
├── main_1a.py             # Main script to run the process
├── outline_extractor.py   # Core logic for outline extraction
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── input/                 # (empty) For placing input PDFs
└── output/                # (empty) For storing output JSONs
