from pypdf import PdfReader, PdfWriter
import os

# Define the input PDF path
# input_pdf_path = '../data/all/mw-handy-guide-english.pdf'
input_pdf_path = '../docs/all/sgsecure-guide-for-workplaces.pdf'


# Load the uploaded PDF
with open(input_pdf_path, 'rb') as input_pdf:
    reader = PdfReader(input_pdf)

    # Define the sections with non-consecutive page ranges
    # handy-guide
    # sections2 = {
    #     "Living-in-Singapore": [(1, 6)],
    #     "Working-in-Singapore": [(7, 19), (27, 32)],
    #     "Health-and-Safety": [(25, 31), (44, 45)],
    #     "Legal-and-Financial Matters": [(20, 24), (32, 41)],
    #     "Help-and-Resources": [(42, 43)]
    # }

    # sgsecure-guide-for-workplaces
    sections2 = {
        "Living-in-Singapore": [(24, 26) ],
        "Working-in-Singapore": [(2, 5), (8, 8), (11, 12), (16, 20), (24, 26)],
        "Health-and-Safety": [(9, 12), (16, 17)],
        "Legal-and-Financial Matters": [],
        "Help-and-Resources": [(66, 72)]
    }

    # sgsecure-hotel-guide
    # sections2 = {
    #     "Living-in-Singapore": [],
    #     "Working-in-Singapore": [(8, 9), (12, 12), (14, 39), (42, 47), (48, 51), (54, 55)],
    #     "Health-and-Safety": [(42, 49), (58, 65)],
    #     "Legal-and-Financial Matters": [],
    #     "Help-and-Resources": [(12, 12), (48, 49), (66, 72)]
    # }

    # Base directory to save the PDF files
    base_dir = '../docs'

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
        output_path = os.path.join(section_dir, f"sgsecure-guide-for-workplaces.pdf")
        with open(output_path, 'wb') as output_pdf:
            writer.write(output_pdf)
        return output_path

    # Extract and save PDFs for each section
    for section, pages in sections2.items():
        extract_section(section, pages)


"""
How do I report a safety hazard in the workplace?

If you encounter any safety hazard or unsafe practices in your workplace,
you may use your FWMOMCare app to report unsafe workplace conditions.


"""