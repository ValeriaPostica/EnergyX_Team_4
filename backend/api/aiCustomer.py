"""
RAG, from now implemented using only the sites information that is stored selectively in simple_log.txt
"""

import sys
import bs4
# `hub` moved or may not be available in some langchain installs. Try optional import.
try:
	from langchain import hub  # type: ignore
except Exception:
	hub = None
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_community.document_loaders import TextLoader
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import getpass
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACING"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "pr-indelible-anywhere-47"
llm = None
try:
	llm = init_chat_model("gpt-4o-mini", model_provider="openai")
except Exception:
	print("Warning: Could not initialize chat model llm.")

# Set your OpenAI API key here or via environment variable OPENAI_API_KEY
# if not os.environ.get("OPENAI_API_KEY"):
# 	os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# System prompt to define AI's role and response style
SYSTEM_PROMPT = (
	"You are an expert energy consultant for residential customers. "
	#"Your job is to provide actionable, practical advice to help people reduce energy consumption and save money at home. "
	"Always answer in one short, clear sentence, focused on the most effective tip for the situation. "
	"Avoid technical jargon and keep your advice easy to understand. Here is the actual data of my household:"
)

# helper: build a fresh vector store from the current simple_log file
def build_vector_store_from_simple_log():
	# resolve the simple_log path relative to this file
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	simple_log_path = os.path.join(base_dir, "data", "simple_log.txt")

	# create embeddings instance once per build
	embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

	vs = InMemoryVectorStore(embeddings)

	# If file missing or empty, return empty store
	if not os.path.exists(simple_log_path):
		return vs

	try:
		loader = TextLoader(simple_log_path, encoding="utf-8")
		docs = loader.load()
	except Exception:
		# fallback: return empty store
		return vs

	# Split documents into chunks and add to vector store
	text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
	all_splits = text_splitter.split_documents(docs)
	if all_splits:
		vs.add_documents(documents=all_splits)
	return vs

# Try to obtain the reusable prompt from langchain hub if available.
prompt = None
if hub is not None:
	try:
		prompt = hub.pull("rlm/rag-prompt")
	except Exception:
		prompt = None

def get_ai_response(question: str) -> str:
	"""Build the vector store from the current simple_log and answer the question.

	This function rebuilds the index at call time so it reflects the latest
	contents of `backend/data/simple_log.txt`.
	"""
	try:
		# Build a fresh vector store from the live file
		vector_store = build_vector_store_from_simple_log()

		# Do a similarity search (may be empty)
		retrieved_docs = vector_store.similarity_search(question) if vector_store else []

		docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs) if retrieved_docs else ""

		# Build messages for the chat model. If a hub prompt is available use it,
		# otherwise construct a simple system+user messages list as a fallback.
		# Note: avoid duplicating SYSTEM_PROMPT in both context and system message.
		print("Context for RAG:\n", docs_content)

		if prompt is not None:
			# If the hub prompt exists, invoke it in the original way.
			messages = prompt.invoke({"question": question, "context": docs_content})
			if llm is not None:
				response = llm.invoke(messages)
		else:
			# Fallback: create chat messages manually. Provide system prompt and
			# put retrieved documents into the user message as context.
			user_content = """
Context:
{context}

Question: {question}
""".format(context=docs_content, question=question)
			messages = [
				{"role": "system", "content": SYSTEM_PROMPT},
				{"role": "user", "content": user_content},
			]
			# Invoke the chat model with the messages list
			if llm is not None:
				response = llm.invoke(messages)
			else:
				return None
		return response.content if hasattr(response, "content") else str(response)
	except Exception as e:
		# Return a simple fallback string on error so callers don't crash
		return f"Error generating response: {e}"


if __name__ == "__main__":
	print(get_ai_response("What wil be my energy usage tomorow at 2 pm?"))


