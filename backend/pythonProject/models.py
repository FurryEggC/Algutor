from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import secrets

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    api_key = db.Column(db.String(100), unique=True, nullable=True)
    
    def set_password(self, password):
        # 简单的密码哈希，实际项目中应使用更安全的方法
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def generate_api_key(self):
        self.api_key = secrets.token_urlsafe(32)
        return self.api_key
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class Knowledge(db.Model):
    __tablename__ = 'knowledge'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    example = db.Column(db.JSON, nullable=True)
    is_public = db.Column(db.Boolean, default=False, nullable=False)  # 是否为公共知识库
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    
    # 关联关系
    creator = db.relationship('User', backref=db.backref('created_knowledges', lazy=True))
    
    # 确保公共知识库的topic唯一
    __table_args__ = (
        db.UniqueConstraint('topic', 'created_by', name='_topic_user_uc'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "explanation": self.explanation,
            "example": self.example or [],
            "is_public": self.is_public,
            "created_by": self.created_by,
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


class UserKnowledge(db.Model):
    """用户的个人知识库收藏/拷贝"""
    __tablename__ = 'user_knowledge'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), nullable=False)
    original_knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), nullable=True)  # 原始公共知识库ID（如果是从公共拷贝的）
    notes = db.Column(db.Text, nullable=True)  # 用户添加的笔记
    is_edited = db.Column(db.Boolean, default=False, nullable=False)  # 用户是否编辑过
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('user_knowledges', lazy=True), foreign_keys=[user_id])
    knowledge = db.relationship('Knowledge', foreign_keys=[knowledge_id], backref=db.backref('user_collections', lazy=True))
    original_knowledge = db.relationship('Knowledge', foreign_keys=[original_knowledge_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "knowledge_id": self.knowledge_id,
            "original_knowledge_id": self.original_knowledge_id,
            "notes": self.notes,
            "is_edited": self.is_edited,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "knowledge": self.knowledge.to_dict() if self.knowledge else None
        }


class UserSession(db.Model):
    """用户会话记录"""
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_questions = db.Column(db.Text)  # 用户提问历史
    ai_responses = db.Column(db.Text)  # AI回复历史
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "user_questions": self.user_questions,
            "ai_responses": self.ai_responses,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }