from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from dotenv import load_dotenv

load_dotenv()

llm = Ollama(model = "mistral", request_timeout = 3600.0)

parser = LlamaParse(result_type="markdown")

file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

embed_model = resolve_embed_model("local:BAAI/bge-m3")
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=llm)

# tools = [
#     QueryEngineTool(
#         query_engine = query_engine,
#         metadata = ToolMetadata(
#             name = "mw_handy_guide",
#             description = "This is a guide for migrant workers. Use this for providing information"
#         )
#     )
# ]

result = query_engine.query("Give me the QR code to inform MOM of my number in Singapore.")
print(result)