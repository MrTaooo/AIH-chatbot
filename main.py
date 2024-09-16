from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from prompts import context
from dotenv import load_dotenv

load_dotenv()

llm = Ollama(model = "mistral", request_timeout = 3600.0)

parser = LlamaParse(result_type="markdown")

file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

embed_model = resolve_embed_model("local:BAAI/bge-m3")
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=llm)

tools = [
    QueryEngineTool(
        query_engine = query_engine,
        metadata = ToolMetadata(
            name = "mw_handy_guide",
            description = "This is a handy guide provided by Singapore Ministry of Manpower (MOM). Use this for providing information and guide migrant workers",
        ),
    )
]

agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context)

while (prompt := input("Enter a prompt (q to quit):")) != "q":
    # result = agent.query(prompt)
    result = query_engine.query(prompt)
    print(result)