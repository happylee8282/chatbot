import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_experimental.tabular_synthetic_data.openai import (
    create_openai_data_generator,
)
from langchain_experimental.tabular_synthetic_data.prompts import (
    SYNTHETIC_FEW_SHOT_PREFIX,
    SYNTHETIC_FEW_SHOT_SUFFIX,
)
from pydantic import BaseModel
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 환경 변수 설정
os.environ['OPENAI_API_KEY'] = 'api_key'
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'langchain_endpoint'
os.environ['LANGCHAIN_API_KEY'] = 'langchain_key'
os.environ['LANGCHAIN_PROJECT'] = "project_name"

# 데이터 클래스
class MedicalBilling(BaseModel):
    patient_id: int
    patient_name: str
    diagnosis_code: str
    procedure_code: str
    total_charge: float
    insurance_claim_amount: float

    def __str__(self):
        return (f"Patient ID: {self.patient_id}, Patient Name: {self.patient_name}, "
                f"Diagnosis Code: {self.diagnosis_code}, Procedure Code: {self.procedure_code}, "
                f"Total Charge: ${self.total_charge}, Insurance Claim Amount: ${self.insurance_claim_amount}")

# 예제 데이터
examples = [
    {
        "example": """Patient ID: 123456, Patient Name: John Doe, Diagnosis Code: 
        J20.9, Procedure Code: 99203, Total Charge: $500, Insurance Claim Amount: $350"""
    },
    {
        "example": """Patient ID: 789012, Patient Name: Johnson Smith, Diagnosis 
        Code: M54.5, Procedure Code: 99213, Total Charge: $150, Insurance Claim Amount: $120"""
    },
    {
        "example": """Patient ID: 345678, Patient Name: Emily Stone, Diagnosis Code: 
        E11.9, Procedure Code: 99214, Total Charge: $300, Insurance Claim Amount: $250"""
    },
]

# 프롬프트 템플릿 설정
OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")

prompt_template = FewShotPromptTemplate(
    prefix=SYNTHETIC_FEW_SHOT_PREFIX,
    examples=examples,
    suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
    input_variables=["subject", "extra"],
    example_prompt=OPENAI_TEMPLATE,
)

# 데이터 생성기
synthetic_data_generator = create_openai_data_generator(
    output_schema=MedicalBilling,
    llm=ChatOpenAI(model="gpt-4o", temperature=1),
    prompt=prompt_template
)

# 문서 로드 및 분할
loader = TextLoader("C:\\Users\\leejh\\Desktop\\result.txt")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
all_splits = text_splitter.split_documents(docs)
split_size = len(all_splits)
print("split_size: ", split_size)

# 데이터 생성 실행
result = synthetic_data_generator.generate(
    subject="medical_billing",
    extra="the name must be chosen at random. Make it something you wouldn't normally choose.",
    runs=10
)

# 벡터 저장소 설정
vectorstore = Chroma.from_documents(
    documents=all_splits,
    embedding=OpenAIEmbeddings()
)

# 결과 파일 저장
with open("result.txt", "a") as f:
    f.write("\n".join(str(item) for item in result))
