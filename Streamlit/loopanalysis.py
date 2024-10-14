

import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import CharacterTextSplitter
from alj_analysis import format_time,markdown_to_plain_text
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI,OpenAI
from langchain.chains import RefineDocumentsChain, LLMChain
from langchain_core.prompts import PromptTemplate
from docx import Document
from docx.shared import Pt

import time
load_dotenv(override=True)


api_key = os.getenv('open_ai_key')


llm = ChatOpenAI(openai_api_key=api_key,model="gpt-4o-mini", temperature=0)

def load_docs():

    l=["explanation of why claim was denied at the Initial or Reconsideration Stages by SSA","Denial letters from the Initial and Reconsideration Stages from SSA to client","contains earnings and additional statements from claimant or third party. Also contains Initial Application","work history reports, function reports, disability reports for the claimant and SSA, statements from the claimant or third parties, and resumes for medical or vocational experts for the hearing.","Medical Records for the claimant from multiple providers and Consultative Exam reports from SSA doctors"]
    whole_text=''
    for i in range(5):
        input_directory="StructuredOutput"
        input_path = os.path.join(input_directory, f'section_{i+1}.docx')
        context="\n This portion contains info about "+ l[i] + " \n"
        loader = Docx2txtLoader(input_path)
        data = loader.load()
        whole_text=whole_text+context
        for j in data:
            whole_text=whole_text+j.page_content+"\n"
        print(len(whole_text))
        print(context)

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=50000,
        chunk_overlap=4000,
        length_function=len,
        is_separator_regex=False,
        )
    docs = text_splitter.create_documents([whole_text])
    return docs


def getquestion():
    
    
    loader = Docx2txtLoader("loopholes.docx")

    data = loader.load()

    a=''
    for i in data:
        a=a+i.page_content+"\n"

   

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
        "Based on the following content,Please create appropriate questions from this document : {context}"
        "Remember you just have to create the questions"
    "Make it as detailed as possible"
    )
    initial_llm_chain = LLMChain(llm=llm, prompt=prompt)
    initial_response_name = "prev_response"

    # Updated prompt for refinement to enhance and finalize the questions, ensuring a total of 20 questions
    prompt_refine = PromptTemplate.from_template(
        "Here are the intial info from the document: {prev_response}. "
        "Refine the questions and create based questions based on the loopholes which are given in the  context: {context}"
        "Quote each and everything, find the smallest details"
        "Remember you just have to create the questions"
        "I dont need answers for it"
        "Dont write this in markdown format"
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

    ques=chain.run(data)

    return a, ques



def analyse(docs,a,ques):
    start_time = time.time()



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
    "These are the possible loopholes from a judge decision \n "+a+
    "\n Based on the above content, Go through these documents and find, where possible loopholes were actually true : {context}"
    "These are the questions that you need to answer from the documents, questions are "+ ques+
        "Please answer in this format \n Question: \n then the answer:\n ."
    )
    initial_llm_chain = LLMChain(llm=llm, prompt=prompt)
    initial_response_name = "prev_response"

    # Updated prompt for refinement to enhance and finalize the questions, ensuring a total of 20 questions
    prompt_refine = PromptTemplate.from_template(
        "These are the possible loopholes from a judge decision \n "+a+
    "\n Based on the above content, Go through these documents and find, where possible loopholes were actually true :"
    "Here are the intial info from the document: {prev_response}. "
    "These are the questions that you need to answer from the documents, questions are "+ ques+
    "Answer all the loopholes from the documents with proper reasoning and whether the assumptions for loopholes were true, based on the following additional context: {context}"
    "Quote each and everything, find the smallest details. \n Please answer in this format \n Question: \n then the answer:\n"
        "Please answer in this format \n Question: \n then the answer:\n"
    "Dont write this in markdown format"
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
    k=chain.run(docs)
    plain_text = markdown_to_plain_text(k)
    create_word_doc(plain_text,"loopAnalysis", "analysis.docx")

    elapsed_time = time.time() - start_time
    formatted_time = format_time(elapsed_time)
    return formatted_time


def create_word_doc(text, folder_name, file_name='document.docx'):
    """Create a Word document with the provided plain text in the specified folder."""
    # Ensure the folder exists
    os.makedirs(folder_name, exist_ok=True)
    
    # Construct full file path
    file_path = os.path.join(folder_name, file_name)

    doc = Document()
    
    # Set default font size for the document
    style = doc.styles['Normal']
    font = style.font
    font.size = Pt(12)

    # Add the plain text to the document
    doc.add_paragraph(text)

    # Save the document
    doc.save(file_path)
    print(f"Document saved as {file_path}")









