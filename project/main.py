import sys
import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QComboBox, QListWidget, QMessageBox
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Set OpenAI API key
os.environ['OPENAI_API_KEY'] = 'api_key'

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:****@localhost/chatbot_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define token limit
TOKEN_LIMIT = 1000

# User model
class User(Base):
    __tablename__ = "users"
    id = Column(String(255), primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    history = Column(Text, nullable=True)

# Create database tables
Base.metadata.create_all(bind=engine)

class RegisterLoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chatbot System - Register/Login")
        self.layout = QVBoxLayout()

        # Register Form
        self.register_label = QLabel("회원가입")
        self.register_id = QLineEdit()
        self.register_id.setPlaceholderText("ID를 입력하세요")
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setPlaceholderText("비밀번호를 입력하세요")
        self.register_button = QPushButton("회원가입")
        self.register_button.clicked.connect(self.register_user)

        # Login Form
        self.login_label = QLabel("로그인")
        self.login_id = QLineEdit()
        self.login_id.setPlaceholderText("ID를 입력하세요")
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("비밀번호를 입력하세요")
        self.login_button = QPushButton("로그인")
        self.login_button.clicked.connect(self.login_user)

        # Add widgets to layout
        self.layout.addWidget(self.register_label)
        self.layout.addWidget(self.register_id)
        self.layout.addWidget(self.register_password)
        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.login_label)
        self.layout.addWidget(self.login_id)
        self.layout.addWidget(self.login_password)
        self.layout.addWidget(self.login_button)
        self.setLayout(self.layout)

    def register_user(self):
        session = SessionLocal()
        user_id = self.register_id.text()
        password = self.register_password.text()
        new_user = User(id=user_id, password=password, history="")
        session.add(new_user)
        session.commit()
        session.close()
        QMessageBox.information(self, "등록 완료", f"{user_id}님이 등록되었습니다.")

    def login_user(self):
        session = SessionLocal()
        user_id = self.login_id.text()
        password = self.login_password.text()
        user = session.query(User).filter(User.id == user_id).first()
        
        if user and user.password == password:
            self.chat_window = ChatWindow(user_id, user.history)
            self.chat_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "로그인 실패", "ID 또는 비밀번호가 올바르지 않습니다.")
        session.close()

class ChatWindow(QMainWindow):
    def __init__(self, user_id, initial_history):
        super().__init__()
        self.user_id = user_id
        self.history = initial_history
        self.setWindowTitle(f"{user_id}님의 채팅창")
        self.setGeometry(200, 200, 600, 400)

        # Main layout
        self.main_layout = QVBoxLayout()

        # Tone selection
        self.tone_label = QLabel("말투 선택")
        self.tone_select = QComboBox()
        self.tone_select.addItems(["귀엽게", "친근하게"])

        # System template selection
        self.template_label = QLabel("챗봇 타입 선택")
        self.template_select = QComboBox()
        self.template_select.addItems(["영화감독", "운동선수", "작가"])

        # Model selection
        self.model_label = QLabel("모델 선택")
        self.model_select = QComboBox()
        self.model_select.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"])

        # Chat history display
        self.chat_history = QListWidget()
        self.load_chat_history()

        # Input field and send button
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("질문을 입력하세요...")
        self.send_button = QPushButton("전송")
        self.send_button.clicked.connect(self.send_message)

        # Layout setup
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.tone_label)
        options_layout.addWidget(self.tone_select)
        options_layout.addWidget(self.template_label)
        options_layout.addWidget(self.template_select)
        options_layout.addWidget(self.model_label)
        options_layout.addWidget(self.model_select)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        self.main_layout.addLayout(options_layout)
        self.main_layout.addWidget(self.chat_history)
        self.main_layout.addLayout(input_layout)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def load_chat_history(self):
        for entry in self.history.split("\n"):
            if entry:
                self.chat_history.addItem(entry)

    def send_message(self):
        user_input = self.input_field.text()

        # 선택된 말투와 역할을 매번 history에 추가
        tone = self.tone_select.currentText()
        role = self.template_select.currentText()
        
        # 매번 말투와 역할을 추가
        self.history += f"system: 말투는 {tone} 설정되었습니다.\n"
        self.history += f"system: 챗봇 역할은 {role}로 설정되었습니다.\n"
        
        self.history += f"user: {user_input}\n"

        # 토큰 제한을 초과하면 요약 수행
        if len(self.history) > TOKEN_LIMIT:
            self.history = self.summarize_history()

        llm = self.get_llm()
        messages = self.convert_history_to_messages()
        responses = [llm.invoke(messages).content for _ in range(3)]

        self.display_responses(responses)
        self.input_field.clear()

        # 갱신된 히스토리를 데이터베이스에 저장
        self.save_history()



    def display_responses(self, responses):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("응답 선택")
        msg_box.setText("다음 중 하나를 선택하세요:")

        for idx, response in enumerate(responses, 1):
            msg_box.addButton(QPushButton(f"{idx}. {response}"), QMessageBox.AcceptRole)

        selected = msg_box.exec_() - 1
        chosen_response = responses[selected]
        self.chat_history.addItem(f"assistant: {chosen_response}")
        self.history += f"assistant: {chosen_response}\n"

        # Check token limit after adding response and summarize if needed
        if len(self.history) > TOKEN_LIMIT:
            self.history = self.summarize_history()

        # Save updated history to database
        self.save_history()

    def save_history(self):
        """Save the updated history to the database."""
        session = SessionLocal()
        user = session.query(User).filter(User.id == self.user_id).first()
        if user:
            user.history = self.history
            session.commit()
        session.close()

    def summarize_history(self):
        llm = self.get_llm()
        summary_prompt = HumanMessage(content=f"이전 대화를 요약해 주세요:\n{self.history}")
        summary_message = llm.invoke([summary_prompt]).content
        summarized_history = f"system: 이전 대화 요약: {summary_message}\n"
        
        # Display summarized history for user feedback
        QMessageBox.information(self, "히스토리 요약", summarized_history)
        
        return summarized_history

    def get_llm(self):
        model_name = self.model_select.currentText()
        return ChatOpenAI(model=model_name)

    def convert_history_to_messages(self):
        messages = []
        for entry in self.history.split("\n"):
            if entry and ":" in entry:
                role, content = entry.split(":", 1)
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
                elif role == "system":
                    messages.append(SystemMessage(content=content))
        return messages

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterLoginWindow()
    window.show()
    sys.exit(app.exec_())
