from pypdf import PdfReader, PdfWriter
import os

file_name = "mw-handy-guide-english"
# file_name = "sgsecure-guide-for-workplaces"
# file_name = "sgsecure-hotel-guide"
# file_name = "singpass-registration-guide"
# Define the input PDF path
input_pdf_path = f'../docs/all/{file_name}.pdf'


# Load the uploaded PDF
with open(input_pdf_path, 'rb') as input_pdf:
    reader = PdfReader(input_pdf)

    print(f"Number of pages: {len(reader.pages)}")

    # Define the sections with non-consecutive page ranges
    # mw-handy-guide-english
    sections2 = {
        "Living-in-Singapore": [(1, 7), (25, 26)],
        "Working-in-Singapore": [(7, 19), (21, 21), (27, 32)],
        "Legal": [(12, 14), (20, 24), (27, 27), (32, 37), (39, 41)],
        "Financial": [(38, 39)],
        "Salary and Wages": [(12, 19)],
        "Health-and-Safety": [(16, 16), (25, 31), (44, 45)],
        "Help-and-Resources": [(42, 43)],
        "Work-Permit": [(20, 20)]
    }

    # file_name = "sgsecure-guide-for-workplaces"
    # sections2 = {
    #     "Living-in-Singapore": [(24, 26)],
    #     "Working-in-Singapore": [(2, 5), (8, 8), (11, 12), (16, 20), (24, 26)],
    #     "Health-and-Safety": [(9, 12), (16, 17)],
    #     "Help-and-Resources": [(28, 29)]
    # }

    # sgsecure-hotel-guide
    # sections2 = {
    #     "Working-in-Singapore": [(12, 12), (54, 55)],
    #     "Health-and-Safety": [(12, 12), (14, 30), (32, 39), (42, 51), (54, 55), (58, 69)],
    #     "Help-and-Resources": [(12, 12), (66, 72)]
    # }

    # sections2 = {
    #     "Living-in-Singapore": [(3, 29)],
    #     "Working-in-Singapore": [(31, 33)],
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
        output_path = os.path.join(section_dir, f"{file_name}.pdf")
        with open(output_path, 'wb') as output_pdf:
            writer.write(output_pdf)
        return output_path

    # Extract and save PDFs for each section
    for section, pages in sections2.items():
        if pages != []:
            extract_section(section, pages)


"""
How do I report a safety hazard in the workplace?

If you encounter any safety hazard or unsafe practices in your workplace,
you may use your FWMOMCare app to report unsafe workplace conditions.


"""