import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

os.environ['OPENAI_API_KEY'] = 'api_key'
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'langchain_endpoint'
os.environ['LANGCHAIN_API_KEY'] = 'langchain_key'
os.environ['LANGCHAIN_PROJECT'] = "project_name"

parser = StrOutputParser()

model = ChatOpenAI(model="gpt-4o")

chain = model | parser

chat_histories = []


# 대화 기록을 최신 메시지로 유지
# 시스템 메시지를 포함하여 토큰 수가 65를 넘지 않도록 조정
# 첫 번째 사용자 메시지부터 카운팅 시작

trimmer = trim_messages(
    max_tokens=65, # 트리밍 후 허용되는 최대 토큰 수 (토큰 수 초과대화는 알아서 맞춰짐)
    strategy="last", # 어떤 메시지 잘라낼지 결정. last: 가장 최근 메시지 유지. 필요한 경우 오래된 메시지 삭제
    token_counter=model, # 주어진 모델 기준으로 토큰 카운팅
    include_system=True, # system(instruction) 토큰 고려할지 말지.
    allow_partial=False, # 메시지를 중간에 자르지 않도록 함. 전체 단위로 포함하거나 제외. (False)
    start_on="human", # Human -> AI -> Human -> AI. 첫번째 질문부터 적용
)


while True:
    print("번호를 선택하세요")
    select = int(input())
    
    if select == 1:
        print("질문을 입력하세요")
        question = input()

        # trimmer로 히스토리 토큰 관리
        trimmed_chat_histories = trimmer.invoke(chat_histories)

        chat_histories.append(HumanMessage(content=question))
        result = chain.invoke(chat_histories)
        print(result)

        # 히스토리 업데이트
        # 질문
        chat_histories.append(HumanMessage(content=question))

        # 답변
        chat_histories.append(AIMessage(content=result))

    else:
        break

print(chat_histories)

#요약해주는 gpt를 따로

#llm mix token limit 퍼럼에서 많이 나오고 있다
