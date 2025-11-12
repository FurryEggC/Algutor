from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Knowledge(db.Model):
    __tablename__ = 'knowledge'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), unique=True, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    example = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "explanation": self.explanation,
            "example": self.example or [],
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def add_example(self, language, code):
        """添加或更新特定语言的示例代码"""
        if self.example is None:
            self.example = []
        for code_pair in self.example:
            if code_pair['language'] == language:
                code_pair['code'] = code

    def get_example(self, language):
        """获取特定语言的示例代码"""
        if self.example is not None:
            for code_pair in self.example:
                if code_pair['language'] == language:
                    return code_pair
        return None


class AICodeGeneration(db.Model):
    """AI代码生成记录"""
    __tablename__ = 'ai_code_generations'

    id = db.Column(db.Integer, primary_key=True)
    original_prompt = db.Column(db.Text, nullable=False)
    generated_content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), nullable=False)
    function_type = db.Column(db.String(50), nullable=False)  # explain/generate/solve/debug
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "original_prompt": self.original_prompt,
            "generated_content": self.generated_content,
            "language": self.language,
            "function_type": self.function_type,
            "created_at": self.created_at.isoformat()
        }


class UserSession(db.Model):
    """用户会话记录"""
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_questions = db.Column(db.Text)  # 用户提问历史
    ai_responses = db.Column(db.Text)  # AI回复历史
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_questions": self.user_questions,
            "ai_responses": self.ai_responses,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }