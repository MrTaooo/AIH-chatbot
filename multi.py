from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from prompts import context
from dotenv import load_dotenv
import os

load_dotenv()

# Load the LLM model
llm = Ollama(model="mistral", request_timeout=3600.0)

# prompt = "What are the social norms in Singapore?"

# result = llm.complete("hello world")
# print(result)

# result = llm.query("What are the social norms in Singapore?")

# Initialize the parser for PDFs
parser = LlamaParse(result_type="markdown")
file_extractor = {".pdf": parser}

# Path to the directory containing the parsed PDF files
base_dir = "./data/"

# Create specialized agents for each section
sections = {
    "Living-in-Singapore": os.path.join(base_dir, "Living-in-Singapore"),
    "Working-in-Singapore": os.path.join(base_dir, "Working-in-Singapore"),
    "Health-and-Safety": os.path.join(base_dir, "Health-and-Safety"),
    "Legal-and-Financial Matters": os.path.join(base_dir, "Legal-and-Financial Matters"),
    "Help-and-Resources": os.path.join(base_dir, "Help-and-Resources"),
    "all" : os.path.join(base_dir, "all")
}

agents = {}

# Set up an agent for each section
for section_name, section_path in sections.items():
    documents = SimpleDirectoryReader(section_path, file_extractor=file_extractor).load_data()
    embed_model = resolve_embed_model("local:BAAI/bge-m3")
    vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    query_engine = vector_index.as_query_engine(llm=llm)

    tools = [
        QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name=section_name,
                description=f"Specialized agent for the {section_name} section."
            ),
        ),
    ]
    
    # Store each specialized agent in a dictionary
    agents[section_name] = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context)

# # need a sensible orchestrator to route queries to the correct agent
# # Orchestrator to route queries to the correct agent
def orchestrator(keyword):
    # Define routing logic based on keywords
    if "Living-in-Singapore" in keyword:
        print("Query contains keywords related to 'Living in Singapore'.")
        return agents["Living-in-Singapore"]
    elif "Working-in-Singapore" in keyword:
        print("Query contains keywords related to 'Working in Singapore'.")
        return agents["Working-in-Singapore"]
    elif "Health-and-Safety" in keyword:
        print("Query contains keywords related to 'Health and Safety'.")
        return agents["Health-and-Safety"]
    elif "Legal-and-Financial Matters" in keyword:
        print("Query contains keywords related to 'Legal and Financial Matters'.")
        return agents["Legal-and-Financial Matters"]
    elif "Help-and-Resources" in keyword:
        print("Query contains keywords related to 'Help and Resources")
        return agents["Help-and-Resources"]
    else:
        print("No specific agent found for the query. Defaulting to 'Working in Singapore'.")
        return agents["all"]  # Default agent

# print("Orchestrator is running...")

while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    print("Received prompt:", prompt)  # Check if prompt is received
    initial_result = llm.complete(f"Which topic is the prompt - {prompt} related to? \nA. Living-in-Singapore \nB. Working-in-Singapore \nC. Health-and-Safety \nD. Legal-and-Financial Matters \nE. Help-and-Resources \nF: Others")
    print(initial_result)
    agent = orchestrator(initial_result)       # Verify orchestrator selection
    print("Orchestrator selected agent:", agent)  # Check selected agent
    if agent == "Others":
        result = llm.complete(prompt)
    else:
        result = agent.query(prompt)       # Check if querying is working
    print(result)
