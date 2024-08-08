from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain

from langchain_openai import ChatOpenAI,OpenAI
import langchain 
langchain.debug=True


#Loading the File
loader = PyPDFLoader("3.pdf")
docs=loader.load()
from langchain_text_splitters import CharacterTextSplitter

#Initiating a splitter function
text_splitter = CharacterTextSplitter(
    separator="\n", chunk_size=100000, chunk_overlap=100, length_function=len)


#Aggregating loaded doc into one single string
result = '\n'.join(doc.page_content for doc in docs)
print(len(result))

#Splitting the text based on Chunk size of 100000
docs = text_splitter.split_text(result)
from dotenv import load_dotenv
import os

from langchain_core.documents import Document
#Creating a Langchain Document Object for Summarization Chain

temp_doc=[Document(page_content=doc) for doc in docs]
len(docs)
#Assigning the
docs=temp_doc
load_dotenv(override=True)


api_key = os.getenv('open_ai_key')


llm = ChatOpenAI(openai_api_key=api_key,model="gpt-4o-mini", temperature=0)
chain = load_summarize_chain(llm, chain_type="refine",)
k=chain.invoke(docs)["output_text"]