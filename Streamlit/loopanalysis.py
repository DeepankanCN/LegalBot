

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
from typing import Any
from langchain.callbacks.base import BaseCallbackHandler

import time
load_dotenv(override=True)


api_key = os.getenv('open_ai_key')


llm = ChatOpenAI(openai_api_key=api_key,model="gpt-4o", temperature=0)

def load_docs(chunk_size):

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
            whole_text="\n"+whole_text+j.page_content+"\n"
        print(len(whole_text))
        print(context)

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
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
    class SimpleDocTracker(BaseCallbackHandler):
        def __init__(self):
            self.doc_count = 0
            
        def on_chain_start(self, serialized: dict, inputs: dict, **kwargs) -> None:
            # This gets called at the start of each chain run
            if 'input_documents' in inputs:
                docs = inputs['input_documents']
                if isinstance(docs, list):
                    print(f"Starting to process batch of {len(docs)} documents")
            
        def on_chain_end(self, outputs: dict, **kwargs) -> None:
            # This gets called at the end of each chain run
            if hasattr(self, 'current_docs'):
                self.doc_count += len(self.current_docs)
                print(f"Finished processing documents. Total processed so far: {self.doc_count}")

        # Required method implementations
        def on_llm_start(self, *args, **kwargs) -> None:
            pass

        def on_llm_end(self, *args, **kwargs) -> None:
            pass

        def on_llm_error(self, *args, **kwargs) -> None:
            pass

        def on_chain_error(self, *args, **kwargs) -> None:
            pass
    
    doc_tracker = SimpleDocTracker()



    # This controls how each document will be formatted. Specifically,
    # it will be passed to `format_document` - see that function for more
    # details.
    document_prompt = PromptTemplate(
    input_variables=["page_content"],
    template="{page_content}"
    )
    document_variable_name = "context"


    # Updated prompt for initial processing to generate exactly 20 questions
#     prompt = PromptTemplate.from_template(
#     """
#     Based on the content provided, carefully go through these documents and identify where the possible loopholes in the judge's decision were actually true. 
#     Your task is to answer these questions from the documents: ."""+ques+""" 

#     For each question, provide the following:
#     - A clear answer, supported with relevant quotes from the document (Exhibit Title and Page Number).
#     - Identify if the assumptions for the loopholes were valid or not.
#     - If there are multiple possible answers or sources, include all relevant citations.

#     Please answer as concisely as possible. 

#     Context: {context}
    
#     """
# )
    prompt = PromptTemplate.from_template(
    """
    Analyze the provided documents and assess whether the identified loopholes in the judge's decision are valid or not.
    For each question, answer the following:
    1. Provide a clear answer to the question based on the document.
    2. Quote specific document sections (Exhibit Title and Page Number) to support your answer.
    3. Evaluate if the assumptions leading to the identified loophole were correct or not.
    4. If there are multiple potential answers or sources, include all relevant citations.
    

    Ideal format is:
    Exhibit Title:
    Page Number:
    Statement: T
    Keep your answer concise and ensure all claims are supported by clear document references.

    Context: {context}
    Question:"""+ques
)




    initial_llm_chain = LLMChain(llm=llm, prompt=prompt)
    initial_response_name = "prev_response"

    # Updated prompt for refinement to enhance and finalize the questions, ensuring a total of 20 questions
#     prompt_refine = PromptTemplate.from_template(
#     """
#     Based on the previous findings and additional context, analyze the documents to validate the loopholes identified. 

#     Answer the following questions: """ +ques+""""
    
#     For each question:
#     - State the answer with detailed reasoning, quoting relevant document sections (Exhibit Title and Page Number).
#     - Confirm whether the initial assumptions about the loopholes were true or false.
#     - Include multiple citations if necessary, but ensure each answer is supported by a clear document reference.


#     Context: {context}
#     Previous Findings: {prev_response}
#     """
# ) 
    prompt_refine = PromptTemplate.from_template(
    """
    Based on previous findings and any new context provided, re-analyze the documents to verify the validity of the identified loopholes.

    For each question, answer the following:
    1. State whether the identified loophole is valid, using detailed reasoning and strictly adhering to the document's text.
    2. Quote exact sections from the document (Exhibit Title and Page Number) to justify your reasoning. **Do not misquote or extrapolate.**
    3. Confirm if the initial assumptions about the loopholes were correct or false, solely based on what the document directly states.
    4. Provide any other necessary citations, ensuring each claim is well-supported by clear references from the document itself, with no misinterpretation.
    You have to help the claimant not the judge, write this very cautiously, if something is against a disabled person in any way, try to ignore it
    Context: {context}
    Previous Findings: {prev_response}
    Question: """+ques
)
    refine_llm_chain = LLMChain(llm=llm, prompt=prompt_refine)

    # Create the RefineDocumentsChain with updated chains and prompts
    chain = RefineDocumentsChain(
    initial_llm_chain=initial_llm_chain,
    refine_llm_chain=refine_llm_chain,
    document_prompt=document_prompt,
    document_variable_name=document_variable_name,
    initial_response_name=initial_response_name,
    callbacks=[doc_tracker]
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









