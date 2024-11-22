import fitz  # PyMuPDF
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI,OpenAI

from langchain_core.documents import Document
from loopanalysis import create_word_doc
load_dotenv(override=True)
from alj_analysis import format_time,markdown_to_plain_text

api_key = os.getenv('open_ai_key')
llm = ChatOpenAI(openai_api_key=api_key,model="gpt-4o-mini", temperature=0)

# llm = ChatOpenAI(openai_api_key=api_key,model="gpt-4o-mini", temperature=0)
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


def split_text():
    pdf_name = 'brief.pdf'  # Replace with your PDF file name
    extracted_text = extract_text_from_pdf(pdf_name)
    


#Initiating a splitter function
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=10000, chunk_overlap=1000, length_function=len)
    result=''
    result = '\n'.join(doc for doc in extracted_text)
    docs = text_splitter.split_text(result)
    print(type(docs))
    print(len(docs))
    new_docs=[]
    for i in docs:
        new_docs.append(Document(page_content=i))

    docs=new_docs
    return docs



def load_analysisdoc():
    loader = Docx2txtLoader("loopAnalysis\\analysis.docx")
    analyis=loader.load()
    print(len(analyis))
    s=''


    for i in analyis:
        s=s+" \n"+i.page_content+"\n"
    

    print(s)
    loaded_analysisdoc=s

    return loaded_analysisdoc


def writebrieffromrecords(docs):
    
    new_docs=[]
    for i in docs:
        new_docs.append(Document(page_content=i))

    docs=new_docs

    from langchain.chains import RefineDocumentsChain, LLMChain
    from langchain_core.prompts import PromptTemplate
    from langchain_community.llms import OpenAI

    # This controls how each document will be formatted. Specifically,
    # it will be passed to `format_document` - see that function for more
    # details.
    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    )
    document_variable_name = "context"


    # Updated prompt for initial processing to generate exactly 20 questions
    prompt = PromptTemplate.from_template(
        "You are given documents, where Judge has made the mistake and you have to write a brief for this"
        "\n Based on the above content, Go through these documents and write a brief, with respective to the above loopholes, these documents will tell you about different type of briefs,and you will have to write a brief for the case, \n {context}"
        "Please be very precise about writing the draft"
        "You need to include each point, that you think should be required to benefit this brief draft"
                """
You must quote all relevant laws, include the sender's and receiver's names, addresses, and contact information, provide a concise summary of the arguments, and present the arguments with specific legal citations."""
     "Also, You have to quote Exhibit Title, and Page Number"    
"Ensure that every detail is included with the utmost care and precision, as even the smallest element can be critically important. When it comes to legal citations, accuracy is paramount. Every citation must be meticulously checked and presented in its correct form—any minor error or omission could have significant consequences. Be thorough and exacting in your attention to detail, as even a slight oversight can undermine the integrity of the work."  
         "Write Receiver's name and address and Sender's Name and address"
    )
    initial_llm_chain = LLMChain(llm=llm, prompt=prompt)
    initial_response_name = "prev_response"

    # Updated prompt for refinement to enhance and finalize the questions, ensuring a total of 20 questions
    prompt_refine = PromptTemplate.from_template(
              "You are given documents, where Judge has made the mistake and you have to write a brief for this"
           
        "\n Based on the above content, Go through these documents and write a brief, with respective to the above loopholes, these documents will tell you about different type of briefs,and you will have to write a brief for the case, \n"
        "Here are the intial info from the document: {prev_response}. "
        "Please be very precise about writing the draft"
        "You need to include each and every law, that you think should be required to benefit this brief draft"
        "It should contain, Summary of Arguments and Arguments"
        "Make sure, You act like a US Lawyer when you are writing this brief"
        """
         "Also, You have to quote Exhibit Title, and Page Number" 
You must quote all relevant details include the sender's and receiver's names, addresses, and contact information, provide a concise summary of the arguments, and present the arguments with specific legal citations."""
        
"Ensure that every detail is included with the utmost care and precision, as even the smallest element can be critically important. When it comes to legal citations, accuracy is paramount. Every citation must be meticulously checked and presented in its correct form—any minor error or omission could have significant consequences. Be thorough and exacting in your attention to detail, as even a slight oversight can undermine the integrity of the work."
         "Write Receiver's name and address and Sender's Name and address"
    )
    refine_llm_chain = LLMChain(llm=llm, prompt=prompt_refine)

    # Create the RefineDocumentsChain with updated chains and prompts
    chain = RefineDocumentsChain(
        initial_llm_chain=initial_llm_chain,
        refine_llm_chain=refine_llm_chain,
        document_prompt=document_prompt,
        document_variable_name=document_variable_name,
        initial_response_name=initial_response_name,
    )
    t=chain.run(docs)
    plain_text = markdown_to_plain_text(t)
    create_word_doc(plain_text,"briefdraft", "brief.docx")

    return t



