import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

# 환경 변수 설정
os.environ['OPENAI_API_KEY'] = 'api_key'
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'langchain_endpoint'
os.environ['LANGCHAIN_API_KEY'] = 'langchain_key'
os.environ['LANGCHAIN_PROJECT'] = "project_name"
os.environ['TAVILY_API_KEY'] = "Tavily_api_key"

# 모델 설정
llm = ChatOpenAI(model="gpt-4o")
search = TavilySearchResults(max_results=2)

#### 나이키 매출정보 RAG -> Tool ###############################
loader = PyPDFLoader("C:\\Users\\leejh\\Desktop\\code\\1014\\nike_reporte.pdf")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
all_splits = text_splitter.split_documents(docs)

vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})
retriever_tool_nike = create_retriever_tool(
    retriever,
    name="pdf_search",
    description="나이키 매출정보를 PDF 문서에서 검색합니다. '나이키'와 관련된 질문은 이 도구를 사용해야 합니다."
)

############################## 미국인 의료정보 RAG -> Tool ###############################
loader = TextLoader("C:\\Users\\leejh\\Desktop\\information.txt")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=100, add_start_index=True)
all_splits = text_splitter.split_documents(docs)

vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})
retriever_tool_health = create_retriever_tool(
    retriever,
    name="american_health_search",
    description="미국인들의 건강상태를 TXT파일에서 검색합니다. '미국인의 건강 또는 질병'에 대한 질문은 이 도구를 사용해야합니다."
)

# 도구 및 에이전트 설정
tools = [search, retriever_tool_nike, retriever_tool_health]
agent_executor = create_react_agent(llm, tools)

# 질문 실행 및 결과 출력
response = agent_executor.invoke({"messages": [HumanMessage(content="미국인들이 평균적으로 많이 가지는 질병코드는?")]})
# response = agent_executor.invoke({"messages": [HumanMessage(content="한국 공학대학교의 전화번호는?")]})
# response = agent_executor.invoke({"messages": [HumanMessage(content="나이키의 매출정보는?")]})
# response = agent_executor.invoke({"messages": [HumanMessage(content="2025년 애플의 주가 분석은?")]})

print(response["messages"])
