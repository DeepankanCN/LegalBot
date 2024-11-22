
import fitz
import asyncio

from langchain_core.documents import Document
def extract_toc_fitz(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    doc.close()
    return toc

# toc=extract_toc_fitz("toc.pdf")


def extract_content_from_list(input_list):
    results = []
    for input_string in input_list:
        # Use regex to find the content from ':' to the first '('
        match = re.search(r':\s*(.*?)\s*\(', input_string)
        if match:
            results.append(match.group(1).strip())  # Append the matched group to results
        else:
            results.append(None)  # Append None if no match is found
    return results
from langchain_community.document_loaders import PyPDFLoader
def find_strings_in_paragraphs(paragraphs, search_strings):
    import ftfy
    import re
    results = []
    all_matched_strings = set()  # To track unique matched strings
    non_matching_docs = []  # To track docs without matches
    
    print(f"Total number of documents to process: {len(paragraphs)}")
    
    # Dictionary to keep track of page numbers for each exhibit title
    exhibit_page_numbers = {}
    
    for i, paragraph in enumerate(paragraphs):
        found_strings = set()  # Using set to avoid duplicates
        paragraph.page_content = re.sub(r'\n', ' ', paragraph.page_content)
        paragraph.page_content = ftfy.fix_text(paragraph.page_content)
        
        # Check if any search string is in the paragraph
        for search_string in search_strings:
            if search_string in paragraph.page_content:
                found_strings.add(search_string)
                all_matched_strings.add(search_string)
        
        # If any strings found, add to results
        if found_strings:
            for search_string in found_strings:
                # For the first time this exhibit title is found, initialize its page number
                if search_string not in exhibit_page_numbers:
                    exhibit_page_numbers[search_string] = 1  # Start page numbering from 1
                    # Update the content with the page number and exhibit title
                    paragraph.page_content = f" \n \n Exhibit title: {search_string} \n\n\n\n Page Number {exhibit_page_numbers[search_string]} \n "+  paragraph.page_content #+ f" \n \n End of:Exhibit title: {search_string} \nPage No. {exhibit_page_numbers[search_string]} \n"
                else:
                    # Increment the page number for subsequent appearances of the same exhibit title
                    exhibit_page_numbers[search_string] += 1
                    # Update the content with the updated page number
                    paragraph.page_content = f"\n\n\n\n Exhibit title: {search_string} \n\n\n Page Number {exhibit_page_numbers[search_string]} \n" + paragraph.page_content #+ f" \n \n End of : Exhibit title: {search_string}\n Page No. {exhibit_page_numbers[search_string]} \n"
            
            results.append((paragraph, list(found_strings)))
        else:
            non_matching_docs.append(i)  # Store index of non-matching doc
    
    # Print summary
    print(f"\nResults summary:")
    print("Len of List of String was:", len(search_strings))
    print(f"Number of documents with matches: {len(results)}")
    print(f"Total unique strings matched: {len(all_matched_strings)}")
    print(f"Unique matched strings: {sorted(list(all_matched_strings))}")
    
    if non_matching_docs:
        print(f"\nDocuments with no matches (document numbers): {non_matching_docs}")
    else:
        print("Every document was mapped")
    
    return results
# from structured2 import structureformat,new_chunk_control
from dochandler import structureformat,new_chunk_control
import re




#**********************


def find_exhibit_numbers(items):
    # Define the regex pattern to find a string that starts with a number followed by a letter
    pattern = r'^\d+[A-Z]'
    
    matched_patterns = []
    matched_strings = []
    i=0

    for item in items:
        match = re.match(pattern, item[1])
        if match:
            matched_patterns.append(match.group())  # Append the matched pattern (e.g., '2A')
            matched_strings.append(item[1])             # Append the whole string
        i=i+1

    return matched_patterns, matched_strings

# matched_patterns, matched_strings=find_exhibit_numbers(toc)

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    # List to store the text of each page
    text_list = []

    # Open the PDF file
    with fitz.open(pdf_path) as pdf:
        # Iterate over each page
        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            # Extract text from the page
            text = page.get_text()
            # Append text to the list
            text_list.append(text)

    return text_list

# Example usage
#pdf_name = 'section_5.pdf'  # Replace with your PDF file name




def find_pattern(documents, character):
    # Compile a regex pattern to match strings that start with a number followed by the specified character
    pattern = re.compile(rf'^\d+{character}:')
    
    # Filter the documents based on the pattern
    matching_documents = [doc for doc in documents if pattern.match(doc)]
    
    return matching_documents

docs_dict = {}
my_string=""
valid_letters = ['A', 'B', 'D', 'E', 'F']
async def process_documents(i):  # 1 to 5 (inclusive)
    #filename = f"section_{i}.pdf"  # Construct the filename dynamically
    filename = f"segregation/section_{i}.pdf"

    # loader = PyPDFLoader(filename)
    # docs = loader.load()
    toc=extract_toc_fitz("toc.pdf")
    matched_patterns, matched_strings=find_exhibit_numbers(toc)


    extracted_text = extract_text_from_pdf(filename)
    docs= [Document(page_content=x) for x in extracted_text]
    #print(i)
    print(valid_letters[i-1])
    print("*****************************")
    character_to_find = valid_letters[i-1]
    result = find_pattern(matched_strings, character_to_find)
    output = extract_content_from_list(result)
    
    result2 = find_strings_in_paragraphs(docs, output)
    docs= [i[0].page_content for i in result2]
    print(len(docs))
    docs=new_chunk_control(docs,10000)
    print(len(docs))
    filename = f"section_{i}.docx"
    s=""
        # for i in result:
        #    print(i)
        #    #  s=s+i+"\n"

    time= await structureformat(docs,filename,output)
    #print(docs[0])
    # for k in range(0,6):
    #     my_string= "\n"+my_string+"\n\n"+docs[k]+"\n\n"
    my_string = docs[1]

    # Open the file in write mode ('w'). This will create the file if it doesn't exist.
    with open("output.txt", "w") as file:
        file.write(my_string)
# Make sure the main entry point is async
# if __name__ == "__main__":
#     asyncio.run(process_documents())  # run the async loop







# Define the string you want to write to the file


# print("String written to file successfully.")

# for zz in output:
#     print(zz)

