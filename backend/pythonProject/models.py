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
