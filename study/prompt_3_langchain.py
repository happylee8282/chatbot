import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

os.environ['OPENAI_API_KEY'] = 'api 키 입력'
llm = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

system_template = "당신은 {type} 감독입니다."
user_template = "{category} 추천해봐."

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("user", user_template)
    ]
)

chain = prompt_template | llm | parser


#invoke llm 요청
#
result = chain.stream({"type": "로맨스", "category": "소설"})
for chunk in result:
    print(chunk,end="",flush = True)

print(result)
