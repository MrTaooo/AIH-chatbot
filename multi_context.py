import os
import openai
import sys
import numpy as np
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
import json
import chromadb


load_dotenv('./.env')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGSMITH_API_KEY')

# Initialize LLM
llm_name = "gpt-3.5-turbo-16k"
llm = ChatOpenAI(model_name=llm_name, temperature=0)

with open('source.json', 'r') as f:
    pdf_to_url_mapping = json.load(f)

    # Orchestrator function to classify the question
def classify_question(question):
    prompt = f"""Given the following categories:
A. Living-in-Singapore - Questions about daily life outside of work, including housing, transportation, local customs, recreation, neighbour, dorm life and communication with family.
B. Working-in-Singapore - Questions about employment terms, workplace rights, working hours, job expectations, and day-to-day work experiences.
C. Health-and-Safety - Questions about health care access, workplace safety protocols, terrorism, mental well-being, and injury prevention.
D. Legal - Questions about rights, legal obligations, employment laws, and dispute resolution.
E. Financial - Questions on managing money, banking, remittance, understanding deductions, and savings options.
F. Work-Permit - Questions about work permit eligibility, renewal processes, permit transfers, and employer responsibilities.
G. Salary-and-Wages - Questions about pay, understanding payslips, salary expectations, disputes, and complaints about wages or deductions.
H. Help-and-Resources - Questions about support services, emergency contacts, and assistance from NGOs or government resources.

Which category does the following question belong to? Please just output the letter corresponding to the category. 
Example Response: A
If none of the category fits, please respond "None"

Question: {question}
"""
    classification = llm.predict(prompt)

    print("Classification:", classification)

    mapping = {
        "A": "Living-in-Singapore",
        "B": "Working-in-Singapore",
        "C": "Health-and-Safety",
        "D": "Legal",
        "E": "Financial",
        "F": "Work-Permit",
        "G": "Salary-and-Wages",
        "H": "Help-and-Resources"
    }
    category = classification.strip().upper()
    section = mapping.get(category, None)
    return section


def getAgent(source_docs: str):

    loader = PyPDFDirectoryLoader(source_docs)
    pages = loader.load()

    for page in pages:

        page_number = int(page.metadata.get('page_number', 0)) + 1
        page.metadata['page_number'] = page_number  # Update the page number

        pdf_name = os.path.splitext(os.path.basename(page.metadata.get('source', '')))[0]  # Get the PDF file name without extension
        page.metadata['source'] = pdf_to_url_mapping.get(pdf_name, pdf_name)  # Use URL if available, otherwise use the file name

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )

    splits = text_splitter.split_documents(pages)

    # Embeddings and vector store
    embedding = OpenAIEmbeddings()
    
    # persist_directory = './docs/vectordb'
    
    # Create vector store (without persistence for simplicity)
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        # persist_directory=persist_directory
    )
    
    # Code below will enable tracing so we can take a deeper look into the chain
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"
    os.environ["LANGCHAIN_PROJECT"] = "Chatbot"

    # Create retriever
    retriever = vectordb.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.6,})

    return retriever


def getRetriever(sectionName):

    embedding = OpenAIEmbeddings()

    persistent_client = chromadb.PersistentClient(path="./docs/vectordb")
    vector_store_from_client = Chroma(
        client=persistent_client,
        collection_name=sectionName,
        embedding_function=embedding,
    )
    retriever = vector_store_from_client.as_retriever(
        search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.6,}
    )

    return retriever

def getResponse(question: str) -> dict:
    """
    A modified implementation to define routing logic based on keywords
    and use an orchestrator to route queries to the correct agent.
    """

    # Get the appropriate section for the question
    section = classify_question(question)

    print("Section:", section)

    if section is None:
        # Default to section with all docs or handle accordingly
        section = "all"

    # Define sections and their corresponding directories
    sections = {
        "Living-in-Singapore": {
            "source_docs": "./docs/Living-in-Singapore",
            "template": "You are responsible for helping migrant workers settle into daily life in Singapore, covering topics like accommodation, public transportation, understanding local customs, utilities, neighbour, dorm life and general living tips. You also provide information about recreation options, cultural events, and affordable ways to communicate with family back home."
        },
        "Working-in-Singapore": {
            "source_docs": "./docs/Working-in-Singapore",
            "template": "You are responsible for answering questions about employment in Singapore, including working hours, workplace rights, contract terms, holidays, and fair treatment. You also help workers understand job expectations and how to balance work and personal life."
        },
        "Health-and-Safety": {
            "source_docs": "./docs/Health-and-Safety",
            "template": "You are responsible for guiding workers on health and safety matters, including access to healthcare services, workplace safety protocols, mental health support, what to do during terrorism attacks and safety practices to prevent injury both at work and outside."
        },
        "Legal": {
            "source_docs": "./docs/Legal",
            "template": "You are responsible for providing information on legal matters, such as employment rights, documentation requirements, dealing with disputes, and ensuring workers understand local laws affecting their rights."
        },
        "Financial": {
            "source_docs": "./docs/Financial",
            "template": "You are responsible for assisting with financial matters, including banking, savings options, remittance processes, understanding deductions, and financial literacy resources to help workers manage their earnings effectively."
        },
        "Work-Permit": {
            "source_docs": "./docs/Work-Permit",
            "template": "You are responsible for providing information on work permit-related issues, including eligibility, renewal processes, employer responsibilities, and guidance on permit transfers or status checks."
        },
        "Salary-and-Wages": {
            "source_docs": "./docs/Salary-and-Wages",
            "template": "You are responsible for addressing salary-related questions, including understanding payslips, salary expectations, pay disputes, and processes for raising complaints about wage issues or deductions."
        },
        "Help-and-Resources": {
            "source_docs": "./docs/Help-and-Resources",
            "template": "You are responsible for connecting workers with support resources, including helplines, government services, NGOs, and other organizations offering assistance to migrant workers facing challenges or in need of help."
        },
        "all": {
            "source_docs": "./docs/all",
            "template": ""
        }
    }


        # Create chain
    
    # retriever = getAgent(sections[section]["source_docs"])

    retriever = getRetriever(section)

    print("Retriever:", retriever)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key='question',
        output_key='answer'
    )

    template = sections[section]["template"]
    
    # Define template prompt
    general_template = f"""You are a friendly chatbot helping a migrant worker settle down in Singapore, more specifically MOM's Settling-in Programme (SIP). {template} Use the following pieces of context to answer the question at the end. Always say Thanks for asking at the end of the answer.
    {{context}}
    Question: {{question}}
    Helpful Answer:"""
    your_prompt = PromptTemplate.from_template(general_template)

    chain = ConversationalRetrievalChain.from_llm(
        llm,
        combine_docs_chain_kwargs={"prompt": your_prompt},
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
        memory=memory
    )

    # Execute the chain
    result = chain({"question": question})

    # print("Result:", result)

    sources = set()

    for doc in result["source_documents"]:
        if 'source' in doc.metadata:
            sources.add(doc.metadata['source'])

    print("Sources:", sources)

    relevant_chunks = set()
    for doc in result['source_documents']:
        relevant_chunks.add(doc.page_content)

    # print(f"ANSWER: {result['answer']}")
    print(f"CONTEXTS: {relevant_chunks}")
    print(f"RESULT: {result}")
    return {"answer": result['answer'], "source_documents": result['source_documents'], "relevant_chunks": relevant_chunks}
