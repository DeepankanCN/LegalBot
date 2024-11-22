from langchain_openai import ChatOpenAI, OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from langchain_pinecone import PineconeVectorStore
from typing import List
import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv('open_ai_key')

class QuestionList(BaseModel):
    """Pydantic model for the list of questions."""
    questions: List[str] = Field(description="List of questions extracted from the text")

llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o-mini", temperature=0)

def read_questions_file(file_path):
    """Read questions from a text file."""
    with open(file_path, 'r') as file:
        return file.read()

def parse_questions(text_content, llm):
    """Parse questions using LangChain with output parser and return as a structured list."""
    
    # Initialize the parser
    parser = PydanticOutputParser(pydantic_object=QuestionList)
    
    # Define the prompt template
    prompt_template = """
    Extract the questions from the following text and return them as a structured list.
    
    Text:
    {text_content}
    
    {format_instructions}
    
    Return the questions in the specified format.
    """
    
    # Create the prompt
    prompt = PromptTemplate(
        input_variables=["text_content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template=prompt_template
    )
    
    # Create the chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        # Run the chain and parse the output
        result = chain.run(text_content=text_content)
        parsed_output = parser.parse(result)
        return parsed_output.questions
    except Exception as e:
        print(f"Error parsing LLM output: {e}")
        # Fallback: basic splitting by numbers
        return [q.strip() for q in text_content.split('\n') if q.strip()]

def get_question_list(file_path):
    # Read the file
    text_content = read_questions_file(file_path)
    
    # Parse the questions
    questions_list = parse_questions(text_content, llm)
    
    # Print the result
    print("Parsed Questions:")
    # for i, question in enumerate(questions_list, 1):
    #     print(f"{i}. {question}")
    
    return questions_list

import getpass
import os
import time

from pinecone import Pinecone, ServerlessSpec

if not os.getenv("PINECONE_API_KEY"):
    os.environ["PINECONE_API_KEY"] = getpass.getpass("Enter your Pinecone API key: ")

pinecone_api_key = os.environ.get("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)
index_name = "legal"  # change if desired

existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)



from langchain_openai import OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = api_key
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
def store_in_index(docs):
    from langchain_pinecone import PineconeVectorStore
    from uuid import uuid4

    vector_store = PineconeVectorStore(index=index, embedding=embeddings,namespace="Sample")
    uuids = [str(uuid4()) for _ in range(len(docs))]

    #vector_store.add_documents(documents=docs, ids=uuids)
    add_documents_in_batches(vector_store, docs, uuids, batch_size=100)
    
    print("Data Inserted Succesfully")

    return "Data Inserted"

def add_documents_in_batches(vector_store, docs, uuids, batch_size=100):
    k=1
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i:i+batch_size]
        batch_uuids = uuids[i:i+batch_size]
        vector_store.add_documents(documents=batch_docs, ids=batch_uuids)
        print("Batch Processed :",k)
        k=k+1

# Example usage:





from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


def analyze_legal_document(question: str):
    """
    Analyze legal documents based on a question and return relevant information with citations.
    
    Args:
        question: The question or issue to analyze
        pinecone_index: Your already initialized Pinecone index
        temperature: LLM temperature (default=0 for consistent responses)
    """
    vector_store = PineconeVectorStore(index=index, embedding=embeddings,namespace="Sample")
  
    
    # Create prompt template focused on legal analysis and citations
    # prompt_template = """
    # Based on the provided documents, analyze the following question:
    # {question}
    
    # Context from documents: {context}
    
    # Please provide:
    # 1. Your analysis of whether the evidence supports or contradicts the question
    # 2. Direct quotes from the documents that support your analysis
    # 3. Specific Exhibit Title and Page Number where the evidence was found (Write Exhibit Title and Page Number from the Context)
    
    # Response:
    # """


    prompt_template = """
    Based on the provided documents, analyze the following question:
    {question}
    
    Context from documents: {context}
    
    Please provide:
    1. Your analysis of whether the evidence supports or contradicts the question
    2. Direct quotes from the documents that support your analysis
    3. Specific exhibit Title and page numbers where the evidence was found
    
    Response:
    """


    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Create the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={'k': 5}),
        chain_type_kwargs={
            "prompt": prompt,
            "verbose": True
        }
        
    )
    
    # Get response
    response = qa_chain.run(question)
    return response




# def analyze_legal_laws(question: str, namespace:str):
#     """
#     Analyze legal documents based on a question and return relevant information with citations.
    
   
#     """
#     vector_store = PineconeVectorStore(index=index, embedding=embeddings,namespace=namespace)
  
    
#     # Create prompt template focused on legal analysis and citations
#     prompt_template = """
#     Based on the provided documents, analyze the following question:
#     {question}
    
#     Context from documents: {context}
    
#     Please provide:
#     1. The exact legal law that 
#     Response:
#     """
    
#     prompt = PromptTemplate(
#         template=prompt_template,
#         input_variables=["context", "question"]
#     )
    
#     # Create the QA chain
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever=vector_store.as_retriever(search_kwargs={'k': 5}),
#         chain_type_kwargs={
#             "prompt": prompt,
#             "verbose": True
#         }
#     )
    
#     # Get response
#     response = qa_chain.run(question)
#     return response






# def delete_index():


#     index.delete(delete_all=True,namespace="Sample")
    



import pinecone
from pinecone.exceptions import NotFoundException

def delete_index():
    namespace="Sample"
    try:
        # Attempt to delete the index (with or without specifying the namespace)
        index.delete(delete_all=True, namespace=namespace)
        print(f"Index in namespace '{namespace}' deleted successfully.")

    except NotFoundException as e:
        print(f"Error: Namespace '{namespace}' not found. {str(e)}")

    except Exception as e:
        # Catch other unexpected errors
        print(f"An unexpected error occurred: {str(e)}")





