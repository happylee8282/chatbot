import openai
import os

key = "받은 openai 키값"

client = openai.OpenAI(api_key=key)

#이준혁이 말한 1. 히스토리 관리
history_messages = [
    {"role": "system", "content": "이준혁이 말한 3.초기시스템 설정"},
]

def get_recommendation(history_messages):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=history_messages
    )

    result = completion.choices[0].message.content
    return result

def make_message(role, content):
    history_messages.append({"role": role, "content": content})

while (message := input("메시지를 입력하세요 : ")) != "-1":
	#이준혁이 말한 2. 프롬프트 질문
    make_message("user", message)
    result = get_recommendation(history_messages)
    print("------------------------------------------------")
    # 파일 추가
    with open("get.txt", "w", encoding="utf-8") as file:
        file.write(result)
    # print(result)
    make_message("system", result)
