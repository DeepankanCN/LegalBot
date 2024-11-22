from loopanalysis import analyse,load_docs,getquestion
from rag import get_question_list,store_in_index,analyze_legal_document
from newbrief import writebrieffromrecords,split_text
from dochandler import new_chunk_control


from brief import load_analysisdoc_firstdraft, split_text_from_briefpdf as st, writebrief as wb




def finalbrief():

    s=load_analysisdoc_firstdraft()
    docs=st()
    t=wb(s,docs)
    



#old brief refine
# s=load_analysisdoc()
# docs=st()
# t=wb(s,docs)
# print(t)


# print("Len  is ",s)








# chunk_size=10000
# docs=load_docs(chunk_size)

# a,ques=getquestion()

# print("**********************************")
# print("Len of Docs is ", len(docs))






# # Open a file named 'question.txt' in write mode ('w')
# with open("question.txt", "w") as file:
#     # Write the string to the file
#     file.write(ques)

print("String saved to question.txt")


# l=get_question_list("question.txt")
# print("len of ", len(l))




# for i in l:
#     print(i)


# store_in_index(docs)

# s=""


# k=1
# for i in l:


#     result=analyze_legal_document(i)
#     s=s+"\n"+str(k)+" Question : "+ i+" \n Answer: "+result+"\n"



# with open("answer.txt", "w") as file:
#     # Write the string to the file
#     file.write(s)




#inserting doc in pinecone

# brief_doc=split_text()
# msg=store_in_index(brief_doc,"brief")
# print(msg)



#Drafting Brief

# with open('answer.txt', 'r') as file:
#     content = file.read() 

# docs=new_chunk_control(content,10000)
# print(len(docs))


# result=writebrief(docs)



def createquestion():
    a,ques=getquestion()

    print("**********************************")
    






    # Open a file named 'question.txt' in write mode ('w')
    with open("question.txt", "w") as file:
        # Write the string to the file
        file.write(ques)
    print("String saved to question.txt")







def answerquestion():
    
    l=get_question_list("question.txt")
    print("len of ", len(l))
    s=""

    t=1


    k=1
    for i in l:


        result=analyze_legal_document(i)
        s=s+"\n"+str(k)+" Question : "+ i+" \n Answer: "+result+"\n"
        if t>=2:
            pass
        t=t+1
        



    with open("answer.txt", "w") as file:
        # Write the string to the file
        file.write(s)

print("Yeahhhhhhhhhhhhhhhhhhhhhhhhhhh!!!!!")





def createfirstbrief():
    with open('answer.txt', 'r') as file:
        content = file.read() 

    docs=new_chunk_control(content,10000)
    print(len(docs))


    result=writebrieffromrecords(docs)


# form= analyse(docs,a,ques)

# print(form)


