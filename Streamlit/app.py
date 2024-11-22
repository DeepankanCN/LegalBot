import streamlit as st
from alj_analysis import analyze_alj_decision
import os
from pdfextraction import process_pdf
from structured import *
from loopanalysis import analyse,load_docs,getquestion
from brief import split_text_from_briefpdf,load_analysisdoc_firstdraft,writebrief
import asyncio
from exhibit import process_documents

from fileprocess import createquestion,answerquestion,createfirstbrief,finalbrief

from rag import store_in_index,delete_index

def main():
    st.title("AI Document Analyzer")

    # Initialize session state
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 1
    if 'alj_processed' not in st.session_state:
        st.session_state.alj_processed = False
    if 'client_processed' not in st.session_state:
        st.session_state.client_processed = False
    if 'section3_result' not in st.session_state:
        st.session_state.section3_result = None
    if 'section4_result' not in st.session_state:
        st.session_state.section4_result = None
    if 'section5_result' not in st.session_state:
        st.session_state.section5_result = None
    # Display the appropriate section
    if st.session_state.current_section == 1:
        upload_alj_decision()
    elif st.session_state.current_section == 2:
        section_2_flow()
    elif st.session_state.current_section == 3:
        section_3_flow()
    elif st.session_state.current_section == 4:
        section_4_flow()
    elif st.session_state.current_section == 5:
        section_5_flow()
    

def upload_alj_decision():
    st.header("Upload ALJ Decision File")
    uploaded_file = st.file_uploader("Choose a PDF file...", type=['pdf'], key="alj_uploader")

    if uploaded_file is not None and not st.session_state.alj_processed:
        file_path = f"./temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Analyzing... This may take a while."):
            elapsed_time, message = analyze_alj_decision(file_path)

        st.success(message)
        st.write(f"Analysis completed in {elapsed_time}.")
        st.session_state.alj_processed = True
        os.remove(file_path)

    if st.button("Next to Section 2"):
        st.session_state.current_section = 2
        st.rerun()

def section_2_flow():
    st.header("Upload Client Electronic PDF")
    uploaded_file = st.file_uploader("Choose a client PDF file...", type=['pdf'], key="client_uploader")

    if uploaded_file is not None and not st.session_state.client_processed:
        pdf_path = f"./temp_{uploaded_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        path_name=f"toc.pdf"
        with open(path_name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            extracted_sections = process_pdf(pdf_path)
            message = "Successfully extracted sections:\n" + "\n".join(extracted_sections)

            # Display success message
            st.success(message.replace("\n", "  \n"))
            
            #st.success(f'Successfully extracted sections: {extracted_sections}')
            st.session_state.client_processed = True
        except Exception as e:
            st.error(f"Error processing PDF: {e}")

        os.remove(pdf_path)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to ALJ Decision"):
            st.session_state.current_section = 1
            st.session_state.client_processed = False
            st.rerun()
    with col2:
        if st.button("Next to Section 3"):
            st.session_state.current_section = 3
            st.rerun()

def section_3_flow():
    st.header("Convert raw data to structured format")
    
    if st.session_state.section3_result is None:
        if st.button("Make Structured Output"):
            with st.spinner("Performing analysis..."):
                # Call your section 3 analysis function here
                # for i in range(5):
                #     output_directory="segregation"
                #     output_path = os.path.join(output_directory, f'section_{i+1}.pdf')
                    
                #     result,text = chunk_control(100000,output_path)
                #     num=i+1
                #     pages= "Total Pages"+"  " + str(len(text))
                #     s="Total Chunks:  "+ str(len(result))
                #     s= s+ " in Section "+ str(i+1)
                #     st.write(pages+"   "+ s)
                #     #st.write(s)

                #     secs=structureformat(result,f'section_{i+1}.docx')
                #     st.write(f'section_{i+1} processed, time taken: {secs} secs')

                status_placeholder = st.empty()
                
                # Run the async process_documents function
                async def run_processing():
                    for i in range(1, 6):
                        status_placeholder.write(f"Processing section_{i}...")
                        await process_documents(i)  # Modified to process one section at a time
                        status_placeholder.write(f"Section_{i} processed")
                
                # Run the async function
                asyncio.run(run_processing())



                #st.session_state.section3_result = result
            st.success("Analysis complete!")
    
    if st.session_state.section3_result is not None:
        pass
        # st.write("Analysis Result:")
    #     st.write(st.session_state.section3_result)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Section 2"):
            st.session_state.current_section = 2
            st.rerun()
    with col2:
        if st.button("Next to Section 4"):
            st.session_state.current_section = 4
            st.rerun()
    with col3:
        if st.button("Finish"):
            st.session_state.current_section = 1
            st.session_state.alj_processed = False
            st.session_state.client_processed = False
            st.session_state.section3_result = None
            st.session_state.section4_result = None
            st.rerun()
def section_4_flow():
    st.header("Loopholes Analysis")
    
    if st.session_state.section4_result is None:
        if st.button("Perform Analysis"):
            with st.spinner("Performing analysis..."):
                # Call your section 4 analysis function here
                # For example:
                # st.session_state.section4_result = your_section4_function()
                # docs=load_docs()
                # st.write("Total number of Chunks : "+ str(len(docs)))
                # st.write("Processing Questions")
                # a,ques=getquestion()
                # st.success("Questions Processed!")
                # st.write("Combining and Analyzing")
                # secs=analyse(docs,a,ques)
                # st.write(f'Time taken: {secs}')

                chunk_size=10000
                docs=load_docs(chunk_size)
                # st.write(docs[0].page_content)

                st.write("Documents Loaded!")

                createquestion()
                st.write("Questions Created!")
                st.write("Storing Vectors, and deleting previous namespace!")


                delete_index()

                print("Length is ", len(docs))
                msg=store_in_index(docs)
                st.write(msg)
                st.write("Validating questions")
                answerquestion()
                st.write("Validated!")
        
                











                st.session_state.section4_result = "Sample Section 4 Result"
            st.success("Analysis complete!")
    
    if st.session_state.section4_result is not None:
        pass
        # st.write("Analysis Result:")
        # st.write(st.session_state.section4_result)

    
    file_path = "answer.txt"  # Replace with the actual path to your .docx file
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            file_contents = file.read()
        
        st.download_button(
            label="Download Result Document",
            data=file_contents,
            file_name="validatedloophole.txt",  # You can change this name if desired
           # mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
           mime="text/plain" 
        )
    else:
        st.error("The result file is not available. Please run the analysis first.")
       

    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button("Back to Section 3"):
    #         st.session_state.current_section = 3
    #         st.rerun()
    # with col2:
    #     if st.button("Finish"):
    #         st.session_state.current_section = 1
    #         st.session_state.alj_processed = False
    #         st.session_state.client_processed = False
    #         st.session_state.section3_result = None
    #         st.session_state.section4_result = None
    #         st.rerun()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Section 3"):
            st.session_state.current_section = 3
            st.rerun()
    with col2:
        if st.button("Next to Brief Draft"):
            st.session_state.current_section = 5
            st.rerun()
    with col3:
        if st.button("Finish"):
            st.session_state.current_section = 1
            st.session_state.alj_processed = False
            st.session_state.client_processed = False
            st.session_state.section3_result = None
            st.session_state.section4_result = None
            st.session_state.section5_result = None
            st.rerun()
def section_5_flow():
    st.header("Brief Draft  [Section 5]")
    # if st.session_state.section4_result is None:
    if st.button("Click here to draft a brief"):
        with st.spinner("Writing Brief..."):
            # Call your section 4 analysis function here
            # For example:
            # st.session_state.section4_result = your_section4_function()
            #****************************************
            # st.write("Loading Brief Document")
            # docs=split_text()
            # st.success("Brief Document Loaded!")
            # st.write("Loading Analysed document")
            # loadedanalysisdoc=load_analysisdoc()
            # st.success("Analysed Document Loaded!")
            # st.write("Combining and Analyzing")
            # brief=writebrief(loadedanalysisdoc,docs)

            # st.markdown(brief)
            st.write("Creating initial brief")
            createfirstbrief()
            st.write("Initial Brief Drafted!")
            st.write("Writing Final Brief")
            finalbrief()
            st.write("Final Brief Written!")


            



            
            #st.write(f'Time taken: {secs}')


            st.session_state.section4_result = "Sample Section 4 Result"
        st.success("Analysis complete!")
    file_path = "briefdraftnew\\brief.docx"  # Replace with the actual path to your .docx file
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            file_contents = file.read()
        
        st.download_button(
            label="Download Result Document",
            data=file_contents,
            file_name="brief_result.docx",  # You can change this name if desired
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.error("The result file is not available. Please run the analysis first.")
    # Add form inputs for brief details
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Section 4"):
            st.session_state.current_section = 4
            st.rerun()
    with col2:
        if st.button("Finish"):
            st.session_state.current_section = 1
            st.session_state.alj_processed = False
            st.session_state.client_processed = False
            st.session_state.section3_result = None
            st.session_state.section4_result = None
            st.session_state.section5_result = None
            st.rerun()

if __name__ == "__main__":
    main()