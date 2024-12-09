import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough

import bs4

# Web, Text, Json, Pdf
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 프롬프트 pull받기 위함
from langchain import hub

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


os.environ['OPENAI_API_KEY'] = 'api_key'
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'langchain_endpoint'
os.environ['LANGCHAIN_API_KEY'] = 'langchain_key'
os.environ['LANGCHAIN_PROJECT'] = "project_name"

llm = ChatOpenAI(model="gpt-4o-mini")

# web site - RAG
# 1) Load
# 웹사이트에서 해당 클래스요소들을 가져오겠다.
loader = TextLoader("C:\\Users\\user\\경로 작성")
docs = loader.load()
# 첫번째 도큐먼트의 컨텐츠 길이
doc_size = len(docs[0].page_content)

# 2) Split
# docs
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True #chunk 200까지는 어느정도 반영하겠다.
)
all_splits = text_splitter.split_documents(docs)
split_size = len(all_splits)
print("split_size: ", split_size)

# 3) vector 스토어
# 질문과 유사한 RAG를 위한 docs를 추출할 수 있음
vectorstore = Chroma.from_documents(
    documents=all_splits,
    embedding=OpenAIEmbeddings()
)

# 4) Vector 스토어 활용해서 RAG를 위한 문서 뽑기
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k":6})

# 프롬프트만들어서 LLM
prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

parser = StrOutputParser()

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | parser
)

result = rag_chain.invoke("kaia코인 하반기 계획은?")
print(result)
