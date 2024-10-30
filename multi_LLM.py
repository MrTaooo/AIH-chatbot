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

def getResponse(question: str) -> dict:
    """
    A modified implementation to define routing logic based on keywords
    and use an orchestrator to route queries to the correct agent.
    """

    load_dotenv('./.env')

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    LANGCHAIN_API_KEY = os.getenv('LANGSMITH_API_KEY')

    # Initialize LLM
    llm_name = "gpt-3.5-turbo-16k"
    llm = ChatOpenAI(model_name=llm_name, temperature=0)

    # Define sections and their corresponding directories
    sections = {
        "Living-in-Singapore": "./docs/Living-in-Singapore",
        "Working-in-Singapore": "./docs/Working-in-Singapore",
        "Health-and-Safety": "./docs/Health-and-Safety",
        "Legal-and-Financial Matters": "./docs/Legal-and-Financial Matters",
        "Help-and-Resources": "./docs/Help-and-Resources",
        "all": "./docs/all"
    }

    retrievers = {}
    chains = {}

    # Create retrievers and chains for each section
    for section_name, section_path in sections.items():
        # Load documents
        loader = PyPDFDirectoryLoader(section_path)
        pages = loader.load()

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )

        splits = text_splitter.split_documents(pages)

        # Embeddings and vector store
        embedding = OpenAIEmbeddings()
        
        persist_directory = './docs/vectordb'
        
        # Create vector store (without persistence for simplicity)
        vectordb = Chroma.from_documents(
            documents=splits,
            embedding=embedding,
            persist_directory=persist_directory
        )

        # Create chain
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key='question',
            output_key='answer'
        )
        
        # Code below will enable tracing so we can take a deeper look into the chain
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"
        os.environ["LANGCHAIN_PROJECT"] = "Chatbot"

        # Create retriever
        retriever = vectordb.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.6, "k": 10})
        # retriever=vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 10})

        # Store retriever
        retrievers[section_name] = retriever
        
        # Define template prompt
        template = """You are a friendly chatbot helping a volunteer to help a migrant worker settle down in Singapore, more specifically MOM's Settling-in Programme (SIP). The SIP is a 1-day orientation programme to educate migrant workers on Singapore's social norms, their employment rights and responsibilities, Singapore laws and where and how to seek assistance. Use the following pieces of context to answer the question at the end. Always say Thanks for asking at the end of the answer.
        {context}
        Question: {question}
        Helpful Answer:"""
        your_prompt = PromptTemplate.from_template(template)

        chain = ConversationalRetrievalChain.from_llm(
            llm,
            combine_docs_chain_kwargs={"prompt": your_prompt},
            retriever=retriever,
            return_source_documents=True,
            return_generated_question=True,
            memory=memory
        )

        chains[section_name] = chain

    # Orchestrator function to classify the question
    def classify_question(question):
        prompt = f"""Given the following categories:
A. Living-in-Singapore
B. Working-in-Singapore
C. Health-and-Safety
D. Legal-and-Financial Matters
E. Help-and-Resources

Which category does the following question belong to? Please just output the letter corresponding to the category. Example: A

Question: {question}
"""
        classification = llm.predict(prompt)

        print("Classification:", classification)

        mapping = {
            "A": "Living-in-Singapore",
            "B": "Working-in-Singapore",
            "C": "Health-and-Safety",
            "D": "Legal-and-Financial Matters",
            "E": "Help-and-Resources"
        }
        category = classification.strip().upper()
        section = mapping.get(category, None)
        return section

    # Get the appropriate section for the question
    section = classify_question(question)

    print("Section:", section)

    if section is None:
        # Default to section with all docs or handle accordingly
        section = "all"

    # Get the corresponding chain
    chain = chains[section]

    # Execute the chain
    result = chain({"question": question})

    relevant_chunks = set()
    for doc in result['source_documents']:
        relevant_chunks.add(doc.page_content)

    # print(f"ANSWER: {result['answer']}")
    print(f"CONTEXTS: {relevant_chunks}")
    # print(f"RESULT: {result}")
    return {"answer": result['answer'], "source_documents": result['source_documents']}
