from pypdf import PdfReader, PdfWriter
import os

# Define the input PDF path
input_pdf_path = '../data/mw-handy-guide-english.pdf'

# Load the uploaded PDF
with open(input_pdf_path, 'rb') as input_pdf:
    reader = PdfReader(input_pdf)

    # Define the sections with non-consecutive page ranges
    sections2 = {
        "Living-in-Singapore": [(1, 6)],
        "Working-in-Singapore": [(7, 19), (27, 32)],
        "Health-and-Safety": [(25, 31), (44, 45)],
        "Legal-and-Financial Matters": [(20, 24), (32, 41)],
        "Help-and-Resources": [(42, 43)]
    }

    # Base directory to save the PDF files
    base_dir = '../data'

    # Function to extract and save non-consecutive pages
    def extract_section(section_name, page_numbers):
        # Create a directory for the section
        section_dir = os.path.join(base_dir, section_name)
        os.makedirs(section_dir, exist_ok=True)  # Create directory if it doesn't exist
        
        writer = PdfWriter()
        for page_range in page_numbers:
            start, end = page_range
            for page_num in range(start, end + 1):
                # 0 - intro, 1 - content page
                writer.add_page(reader.pages[page_num + 1])

        # Save the PDF to the section's directory
        output_path = os.path.join(section_dir, f"{section_name}.pdf")
        with open(output_path, 'wb') as output_pdf:
            writer.write(output_pdf)
        return output_path

    # Extract and save PDFs for each section
    for section, pages in sections2.items():
        extract_section(section, pages)
