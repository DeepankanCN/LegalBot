import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
import os
output_directory = "segregation"
os.makedirs(output_directory, exist_ok=True)

def extract_toc_fitz(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    doc.close()
    return toc

def extract_section(pdf_path, start_page, end_page, output_path):
    """ Extracts a specific section from a PDF """
    try:
        pdf_reader = PdfReader(pdf_path)
        pdf_writer = PdfWriter()

        # Validate page numbers
        num_pages = len(pdf_reader.pages)
        if start_page < 1 or end_page > num_pages or start_page > end_page:
            raise ValueError("Invalid page range")

        for page_num in range(start_page - 1, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        with open(output_path, 'wb') as out_pdf:
            pdf_writer.write(out_pdf)
        print(f'Successfully extracted pages {start_page} to {end_page} into {output_path}')
        message = f'Successfully extracted pages {start_page} to {end_page} into {output_path}'
        return message
    
    except Exception as e:
        print(f"Error extracting section: {e}")
        return e

def get_section_pages(toc, section_number, pdf_path):
    """ Gets the start and end pages for the specified section """
    if section_number < 1 or section_number > len(toc):
        raise ValueError("Invalid section number")

    start_page = toc[section_number - 1][2]

    # Determine the end page for the section
    if section_number < len(toc):
        next_section_start_page = toc[section_number][2]
    else:
        # Use the total number of pages if this is the last section
        pdf_reader = PdfReader(pdf_path)
        next_section_start_page = len(pdf_reader.pages) + 1  # Set next section start page beyond the last page

    end_page = next_section_start_page - 1
    return start_page, end_page

def process_pdf(pdf_path):
    toc = extract_toc_fitz(pdf_path)
    valid_letters = ['A', 'B', 'C', 'D', 'E', 'F']

    toc_new = [item for item in toc if item[1][0] in valid_letters]
    extracted_info=[]

    extracted_sections = []
    if not toc_new:
        raise ValueError("Failed to extract valid TOC from the uploaded PDF.")
    
    for i in range(1, len(toc_new) + 1):
        section_number = i

        try:
            start_page, end_page = get_section_pages(toc_new, section_number, pdf_path)
            output_directory="segregation"
            output_path = os.path.join(output_directory, f'section_{section_number}.pdf')
            temp_string=extract_section(pdf_path, start_page, end_page, output_path)
            extracted_sections.append(output_path)
            extracted_info.append(temp_string)

        except Exception as e:
            print(f"Error extracting section {section_number}: {e}")
    
    return extracted_info
