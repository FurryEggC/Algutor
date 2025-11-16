from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_mail import Mail, Message
from models import db, Knowledge, AICodeGeneration, User, UserKnowledge, EmailVerification
from dotenv import load_dotenv
import os
import re

from sqlalchemy import text

app = Flask(__name__)
# 允许跨域请求，开发环境允许所有来源
CORS(app, resources={r"/api/*": {"origins": ["https://algutor.xyz", "http://localhost:3000", "http://127.0.0.1:3000"], "supports_credentials": True}})

# JWT 配置
import datetime
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')  # 生产环境必须更改
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)  # 访问令牌有效期
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=7)  # 刷新令牌有效期
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# 用户认证装饰器
# 用户认证装饰器
from functools import wraps
def auth_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"status": "error", "message": "未提供API密钥"}), 401
        
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({"status": "error", "message": "无效的API密钥"}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    return decorator

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @auth_required  # 首先需要认证用户
    def decorator(*args, **kwargs):
        user = g.current_user
        
        # 检查用户是否是管理员
        if not user.is_admin:
            return jsonify({"status": "error", "message": "需要管理员权限"}), 403
        
        return f(*args, **kwargs)
    return decorator

# 可选的用户认证装饰器
def optional_auth(f):
    def decorator(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key:
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                g.current_user = user
        return f(*args, **kwargs)
    
    decorator.__name__ = f.__name__
    return decorator

# 在文件开头加载环境变量
load_dotenv()

# 配置
# 从环境变量获取数据库URL，如果没有设置则报错
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL环境变量未设置！请检查.env文件")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail配置
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your_app_password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'your_email@gmail.com')

# 初始化Mail
mail = Mail(app)

# 初始化数据库
db.init_app(app)

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({
        "status": "alive",
        "service": "Knowledge Base API",
        "version": "0.20",
        "features": ["user_auth", "public_knowledge", "private_knowledge", "copy_from_public"]
    })


@app.route('/api/auth/send_verification_code', methods=['POST'])
def send_verification_code():
    """发送邮箱验证码接口"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({"status": "error", "message": "邮箱为必填项"}), 400
        
        email = data.get('email')
        
        # 验证邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({"status": "error", "message": "邮箱格式不正确"}), 400
        
        # 检查该邮箱是否已被验证注册
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.email_verified:
            return jsonify({"status": "error", "message": "该邮箱已被注册"}), 409
        
        # 检查是否在短时间内重复发送（防止恶意请求）
        recent_verification = EmailVerification.query.filter_by(
            email=email,
            is_used=False
        ).order_by(EmailVerification.created_at.desc()).first()
        
        if recent_verification:
            # 计算距离上次发送的时间
            from datetime import datetime, timedelta
            time_diff = datetime.now() - recent_verification.created_at
            if time_diff < timedelta(minutes=1):  # 1分钟内不允许重复发送
                remaining_time = 60 - time_diff.seconds
                return jsonify({
                    "status": "error", 
                    "message": f"请稍后再试，{remaining_time}秒后可重新发送"
                }), 429
        
        # 创建新的验证码记录
        verification = EmailVerification.create_verification(email)
        
        try:
            # 在开发环境下，我们只打印验证码，不实际发送邮件
            print(f"【开发环境】验证码 {verification.verification_code} 应发送至 {email}，有效期30分钟")
            
            # 真实邮件发送代码（在生产环境中使用）
            # msg = Message('Algutor注册验证码', recipients=[email])
            # msg.body = f"""您好！
            # 
            # 感谢您注册Algutor。您的验证码是：
            # {verification.verification_code}
            # 
            # 此验证码有效期为30分钟，请在注册时输入。
            # 
            # 如果您没有进行此操作，请忽略此邮件。
            # 
            # --
            # Algutor团队"""
            # mail.send(msg)
            
        except Exception as mail_error:
            # 发送失败时记录但不影响流程
            print(f"邮件发送失败: {str(mail_error)}")
            # 在实际生产环境中，可能需要添加重试机制或发送失败通知
        
        return jsonify({
            "status": "success", 
            "message": "验证码已发送，请注意查收",
            "data": {
                "email": email,
                "expires_in": 30  # 验证码有效期（分钟）
            }
        })
        
    except Exception as e:
        print(f"发送验证码出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册接口（需要邮箱验证码）"""
    try:
        data = request.get_json()
        
        # 验证数据
        if not data:
            return jsonify({"status": "error", "message": "请求数据不能为空"}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        verification_code = data.get('verification_code')
        
        if not all([username, email, password, verification_code]):
            return jsonify({"status": "error", "message": "用户名、邮箱、密码和验证码为必填项"}), 400
        
        # 验证用户名格式
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return jsonify({"status": "error", "message": "用户名必须为3-20位字母、数字或下划线"}), 400
        
        # 验证邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({"status": "error", "message": "邮箱格式不正确"}), 400
        
        # 验证密码长度
        if len(password) < 6:
            return jsonify({"status": "error", "message": "密码长度至少为6位"}), 400
        
        # 验证验证码
        verification = EmailVerification.query.filter_by(
            email=email,
            verification_code=verification_code,
            is_used=False
        ).order_by(EmailVerification.created_at.desc()).first()
        
        if not verification:
            return jsonify({"status": "error", "message": "验证码无效"}), 400
        
        if not verification.is_valid():
            return jsonify({"status": "error", "message": "验证码已过期"}), 400
        
        if verification.attempt_count >= 5:  # 限制尝试次数
            return jsonify({"status": "error", "message": "验证码尝试次数过多，请重新获取"}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({"status": "error", "message": "用户名已存在"}), 409
        
        # 检查邮箱是否已被验证注册
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.email_verified:
            return jsonify({"status": "error", "message": "该邮箱已被注册"}), 409
        
        # 创建新用户或更新现有未验证用户
        if existing_user:
            user = existing_user
            user.username = username
            user.set_password(password)
        else:
            user = User(username=username, email=email)
            user.set_password(password)
        
        # 标记邮箱为已验证
        user.email_verified = True
        user.generate_api_key()
        
        # 标记验证码为已使用
        verification.mark_as_used()
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "注册成功",
            "data": {
                "user": user.to_dict(),
                "api_key": user.api_key
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"注册出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "请求数据不能为空"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({"status": "error", "message": "邮箱和密码为必填项"}), 400
        
        # 查找用户
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"status": "error", "message": "用户不存在"}), 401
        
        # 验证密码
        if not user.check_password(password):
            return jsonify({"status": "error", "message": "密码错误"}), 401
        
        # 如果没有API密钥或需要重新生成
        if not user.api_key:
            user.generate_api_key()
            db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "登录成功",
            "data": {
                "user": user.to_dict(),
                "api_key": user.api_key
            }
        })
        
    except Exception as e:
        print(f"登录出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/auth/refresh', methods=['POST'])
@auth_required
def refresh_api_key():
    """刷新API密钥"""
    try:
        user = g.current_user
        user.generate_api_key()
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "API密钥刷新成功",
            "data": {
                "api_key": user.api_key
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"刷新API密钥出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/user/profile', methods=['GET'])
@auth_required
def get_user_profile():
    """获取用户信息"""
    try:
        user = g.current_user
        return jsonify({
            "status": "success",
            "data": user.to_dict()
        })
        
    except Exception as e:
        print(f"获取用户信息出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/analyse', methods=['POST'])
def analyse_code():
    """代码分析接口 - 集成语法检查和知识点映射"""


@app.route('/api/knowledge/public', methods=['GET'])
@optional_auth
def get_public_knowledge():
    """获取公共知识库"""
    try:
        knowledge_id = request.args.get("id", type=int)
        topic = request.args.get("topic")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        # 构建查询
        query = Knowledge.query.filter_by(is_public=True)
        
        if knowledge_id:
            knowledge = query.filter_by(id=knowledge_id).first()
            if knowledge:
                return jsonify({"status": "success", "data": knowledge.to_dict()})
            return jsonify({"status": "error", "message": "公共知识点不存在"}), 404
        
        if topic:
            knowledge = query.filter_by(topic=topic).first()
            if knowledge:
                return jsonify({"status": "success", "data": knowledge.to_dict()})
            return jsonify({"status": "error", "message": "公共知识点不存在"}), 404
        
        # 分页查询所有公共知识点
        all_knowledge = query.order_by(Knowledge.created_at.desc()).limit(limit).offset(offset).all()
        total = query.count()
        
        return jsonify({
            "status": "success",
            "data": {
                "items": [k.to_dict() for k in all_knowledge],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        })
    except Exception as e:
        print(f"获取公共知识库时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/knowledge/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
@auth_required
def handle_user_knowledge():
    """用户个人知识库管理接口"""
    try:
        if request.method == 'GET':
            return get_user_knowledge()
        elif request.method == 'POST':
            return add_user_knowledge()
        elif request.method == 'PUT':
            return update_user_knowledge()
        elif request.method == 'DELETE':
            return delete_user_knowledge()
    except Exception as e:
        print(f"处理用户知识库时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


def get_user_knowledge():
    """获取用户个人知识库"""
    try:
        user = g.current_user
        knowledge_id = request.args.get("id", type=int)
        topic = request.args.get("topic")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        # 获取用户收藏的知识点
        query = UserKnowledge.query.filter_by(user_id=user.id)
        
        if knowledge_id:
            user_knowledge = query.join(Knowledge).filter(Knowledge.id == knowledge_id).first()
            if user_knowledge:
                return jsonify({"status": "success", "data": user_knowledge.to_dict()})
            return jsonify({"status": "error", "message": "知识点不存在于您的个人知识库"}), 404
        
        if topic:
            user_knowledge = query.join(Knowledge).filter(Knowledge.topic == topic).first()
            if user_knowledge:
                return jsonify({"status": "success", "data": user_knowledge.to_dict()})
            return jsonify({"status": "error", "message": "知识点不存在于您的个人知识库"}), 404
        
        # 分页查询用户的所有知识点
        all_user_knowledge = query.order_by(UserKnowledge.created_at.desc()).limit(limit).offset(offset).all()
        total = query.count()
        
        return jsonify({
            "status": "success",
            "data": {
                "items": [uk.to_dict() for uk in all_user_knowledge],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        })
    except Exception as e:
        print(f"获取用户知识库时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


def add_user_knowledge():
    """用户添加个人知识点"""
    try:
        user = g.current_user
        data = request.get_json()
        
        if not data or "topic" not in data or "explanation" not in data:
            return jsonify({"status": "error", "message": "必须提供topic和explanation字段"}), 400
        
        # 检查用户是否已有相同主题的知识点
        existing = Knowledge.query.filter_by(topic=data['topic'], created_by=user.id).first()
        if existing:
            return jsonify({"status": "error", "message": "您的知识库中已存在该主题"}), 409
        
        # 创建新的知识点
        knowledge = Knowledge(
            topic=data['topic'],
            explanation=data['explanation'],
            example=data.get('example', []),
            is_public=False,  # 用户创建的默认为私有
            created_by=user.id
        )
        db.session.add(knowledge)
        db.session.flush()  # 获取knowledge.id
        
        # 创建用户知识点关联
        user_knowledge = UserKnowledge(
            user_id=user.id,
            knowledge_id=knowledge.id,
            notes=data.get('notes'),
            is_edited=False
        )
        db.session.add(user_knowledge)
        db.session.commit()
        
        result = user_knowledge.to_dict()
        return jsonify({"status": "success", "data": result}), 201
    except Exception as e:
        db.session.rollback()
        print(f"添加用户知识点时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


def update_user_knowledge():
    """用户更新个人知识点"""
    try:
        user = g.current_user
        knowledge_id = request.args.get("id", type=int)
        data = request.get_json()
        
        if not knowledge_id:
            return jsonify({"status": "error", "message": "必须提供知识点ID"}), 400
        
        # 查找用户的知识点关联
        user_knowledge = UserKnowledge.query.filter_by(
            user_id=user.id,
            knowledge_id=knowledge_id
        ).first()
        
        if not user_knowledge:
            return jsonify({"status": "error", "message": "知识点不存在于您的个人知识库"}), 404
        
        # 查找知识点
        knowledge = Knowledge.query.get(knowledge_id)
        if not knowledge:
            return jsonify({"status": "error", "message": "知识点不存在"}), 404
        
        # 检查权限
        if knowledge.created_by != user.id:
            # 如果不是用户创建的，检查是否在用户的收藏中
            if not user_knowledge:
                return jsonify({"status": "error", "message": "无权修改该知识点"}), 403
        
        try:
            # 更新知识点内容
            if 'topic' in data:
                # 检查新主题是否与用户其他知识点冲突
                existing = Knowledge.query.filter_by(
                    topic=data['topic'], 
                    created_by=user.id
                ).filter(Knowledge.id != knowledge_id).first()
                if existing:
                    return jsonify({"status": "error", "message": "您的知识库中已存在该主题"}), 409
                knowledge.topic = data['topic']
                user_knowledge.is_edited = True
            
            if 'explanation' in data:
                knowledge.explanation = data['explanation']
                user_knowledge.is_edited = True
            
            if 'example' in data:
                knowledge.example = data['example']
                user_knowledge.is_edited = True
            
            if 'notes' in data:
                user_knowledge.notes = data['notes']
            
            db.session.commit()
            return jsonify({"status": "success", "data": user_knowledge.to_dict()})
        except Exception as e:
            db.session.rollback()
            print(f"更新知识点时出错: {str(e)}")
            return jsonify({"status": "error", "message": "数据库错误"}), 500
    except Exception as e:
        print(f"处理更新请求时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


def delete_user_knowledge():
    """用户删除个人知识点"""
    try:
        user = g.current_user
        knowledge_id = request.args.get("id", type=int)
        
        if not knowledge_id:
            return jsonify({"status": "error", "message": "必须提供知识点ID"}), 400
        
        # 查找用户的知识点关联
        user_knowledge = UserKnowledge.query.filter_by(
            user_id=user.id,
            knowledge_id=knowledge_id
        ).first()
        
        if not user_knowledge:
            return jsonify({"status": "error", "message": "知识点不存在于您的个人知识库"}), 404
        
        # 查找知识点
        knowledge = Knowledge.query.get(knowledge_id)
        if not knowledge:
            return jsonify({"status": "error", "message": "知识点不存在"}), 404
        
        try:
            # 删除用户关联
            db.session.delete(user_knowledge)
            
            # 如果是用户创建的且不是公共的，删除知识点本身
            if knowledge.created_by == user.id and not knowledge.is_public:
                db.session.delete(knowledge)
            
            db.session.commit()
            return jsonify({"status": "success", "message": "知识点删除成功"})
        except Exception as e:
            db.session.rollback()
            print(f"删除知识点时出错: {str(e)}")
            return jsonify({"status": "error", "message": "数据库错误"}), 500
    except Exception as e:
        print(f"处理删除请求时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/knowledge/copy', methods=['POST'])
@auth_required
def copy_from_public_knowledge():
    """从公共知识库拷贝知识点到个人知识库"""
    try:
        user = g.current_user
        data = request.get_json()
        
        if not data or "public_knowledge_id" not in data:
            return jsonify({"status": "error", "message": "必须提供公共知识点ID"}), 400
        
        public_knowledge_id = int(data.get("public_knowledge_id"))
        
        # 查找公共知识点
        public_knowledge = Knowledge.query.filter_by(
            id=public_knowledge_id,
            is_public=True
        ).first()
        
        if not public_knowledge:
            return jsonify({"status": "error", "message": "公共知识点不存在"}), 404
        
        # 检查用户是否已经拷贝过该知识点
        existing_copy = UserKnowledge.query.filter_by(
            user_id=user.id,
            original_knowledge_id=public_knowledge_id
        ).first()
        
        if existing_copy:
            # 如果已经拷贝过，返回已存在的知识点
            return jsonify({
                "status": "success",
                "message": "您已经拷贝过该知识点",
                "data": existing_copy.to_dict(),
                "already_copied": True
            })
        
        # 检查用户是否已有相同主题的知识点
        existing_topic = Knowledge.query.filter_by(
            topic=public_knowledge.topic,
            created_by=user.id
        ).first()
        
        if existing_topic:
            # 如果有相同主题，检查是否已经关联
            existing_link = UserKnowledge.query.filter_by(
                user_id=user.id,
                knowledge_id=existing_topic.id
            ).first()
            
            if existing_link:
                return jsonify({
                    "status": "success",
                    "message": "您已经有相同主题的知识点",
                    "data": existing_link.to_dict(),
                    "already_exists": True
                })
        
        try:
            # 创建新的知识点副本
            new_knowledge = Knowledge(
                topic=public_knowledge.topic,
                explanation=public_knowledge.explanation,
                example=public_knowledge.example,
                is_public=False,  # 拷贝的默认为私有
                created_by=user.id
            )
            db.session.add(new_knowledge)
            db.session.flush()  # 获取new_knowledge.id
            
            # 创建用户知识点关联
            user_knowledge = UserKnowledge(
                user_id=user.id,
                knowledge_id=new_knowledge.id,
                original_knowledge_id=public_knowledge_id,
                notes=data.get('notes'),
                is_edited=False
            )
            db.session.add(user_knowledge)
            db.session.commit()
            
            result = user_knowledge.to_dict()
            return jsonify({
                "status": "success",
                "message": "知识点拷贝成功",
                "data": result
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"拷贝知识点时出错: {str(e)}")
            return jsonify({"status": "error", "message": "数据库错误"}), 500
    
    except Exception as e:
        print(f"处理拷贝请求时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/knowledge/sync', methods=['POST'])
@auth_required
def sync_from_public_knowledge():
    """同步更新从公共知识库拷贝的知识点"""
    try:
        user = g.current_user
        data = request.get_json()
        
        if not data or "user_knowledge_id" not in data:
            return jsonify({"status": "error", "message": "必须提供用户知识点ID"}), 400
        
        user_knowledge_id = data.get("user_knowledge_id", type=int)
        
        # 查找用户的知识点关联
        user_knowledge = UserKnowledge.query.filter_by(
            id=user_knowledge_id,
            user_id=user.id
        ).first()
        
        if not user_knowledge:
            return jsonify({"status": "error", "message": "知识点不存在于您的个人知识库"}), 404
        
        # 检查是否是从公共知识库拷贝的
        if not user_knowledge.original_knowledge_id:
            return jsonify({"status": "error", "message": "该知识点不是从公共知识库拷贝的"}), 400
        
        # 查找原始公共知识点
        public_knowledge = Knowledge.query.filter_by(
            id=user_knowledge.original_knowledge_id,
            is_public=True
        ).first()
        
        if not public_knowledge:
            return jsonify({"status": "error", "message": "原始公共知识点不存在"}), 404
        
        # 查找用户的知识点
        user_copied_knowledge = Knowledge.query.get(user_knowledge.knowledge_id)
        if not user_copied_knowledge:
            return jsonify({"status": "error", "message": "用户知识点不存在"}), 404
        
        # 如果用户已经编辑过，询问是否强制更新
        force_update = data.get("force_update", False)
        if user_knowledge.is_edited and not force_update:
            return jsonify({
                "status": "warning",
                "message": "您已经编辑过该知识点，是否强制更新？",
                "requires_force_update": True
            })
        
        try:
            # 保存用户的笔记
            user_notes = user_knowledge.notes
            
            # 更新知识点内容
            user_copied_knowledge.topic = public_knowledge.topic
            user_copied_knowledge.explanation = public_knowledge.explanation
            user_copied_knowledge.example = public_knowledge.example
            
            # 恢复用户笔记
            user_knowledge.notes = user_notes
            user_knowledge.is_edited = False  # 重置编辑状态
            
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": "知识点同步成功",
                "data": user_knowledge.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"同步知识点时出错: {str(e)}")
            return jsonify({"status": "error", "message": "数据库错误"}), 500
    
    except Exception as e:
        print(f"处理同步请求时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


# 保留旧的接口但添加权限控制和状态管理
@app.route('/api/knowledge', methods=['GET'])
def handle_knowledge_get():
    """获取知识点接口（公开访问）"""
    try:
        # 获取公共知识库
        all_knowledge = Knowledge.query.filter_by(is_public=True).all()
        return jsonify({
            "status": "success",
            "data": [k.to_dict() for k in all_knowledge]
        })
    except Exception as e:
        print(f"获取知识点时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500

@app.route('/api/knowledge', methods=['POST', 'PUT', 'DELETE'])
@admin_required
def handle_knowledge_admin():
    """知识点管理接口（需要管理员权限）"""
    try:
        user = g.current_user
        
        if request.method == 'POST':
            # 添加公共知识点
            data = request.get_json()
            if not data or "topic" not in data or "explanation" not in data:
                return jsonify({"status": "error", "message": "必须提供topic和explanation字段"}), 400
            
            # 检查是否已存在相同主题的公共知识点
            existing = Knowledge.query.filter_by(topic=data['topic'], is_public=True).first()
            if existing:
                return jsonify({"status": "error", "message": "已存在相同主题的公共知识点"}), 409
            
            # 创建新的公共知识点
            knowledge = Knowledge(
                topic=data['topic'],
                explanation=data['explanation'],
                example=data.get('example', []),
                is_public=True,
                created_by=user.id
            )
            db.session.add(knowledge)
            db.session.commit()
            
            return jsonify({"status": "success", "data": knowledge.to_dict()}), 201
        
        elif request.method == 'PUT':
            # 更新公共知识点
            knowledge_id = request.args.get("id", type=int)
            if not knowledge_id:
                return jsonify({"status": "error", "message": "必须提供知识点ID"}), 400
            
            knowledge = Knowledge.query.filter_by(id=knowledge_id, is_public=True).first()
            if not knowledge:
                return jsonify({"status": "error", "message": "公共知识点不存在"}), 404
            
            data = request.get_json()
            if data:
                if "topic" in data:
                    # 检查新主题是否与其他公共知识点冲突
                    existing = Knowledge.query.filter_by(
                        topic=data['topic'], 
                        is_public=True,
                        id=knowledge_id
                    ).first()
                    if existing and existing.id != knowledge_id:
                        return jsonify({"status": "error", "message": "已存在相同主题的公共知识点"}), 409
                    knowledge.topic = data['topic']
                
                if "explanation" in data:
                    knowledge.explanation = data['explanation']
                    
                if "example" in data:
                    knowledge.example = data['example']
                
                knowledge.updated_at = datetime.now()
                db.session.commit()
            
            return jsonify({"status": "success", "data": knowledge.to_dict()})
        
        elif request.method == 'DELETE':
            # 删除公共知识点
            knowledge_id = request.args.get("id", type=int)
            if not knowledge_id:
                return jsonify({"status": "error", "message": "必须提供知识点ID"}), 400
            
            knowledge = Knowledge.query.filter_by(id=knowledge_id, is_public=True).first()
            if not knowledge:
                return jsonify({"status": "error", "message": "公共知识点不存在"}), 404
            
            try:
                db.session.delete(knowledge)
                db.session.commit()
                return jsonify({"status": "success", "message": "知识点删除成功"})
            except Exception as e:
                db.session.rollback()
                return jsonify({"status": "error", "message": "删除失败，可能有其他数据引用此知识点"}), 500
    except Exception as e:
        print(f"处理知识点管理时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


@app.route('/api/ai/explain', methods=['POST'])
def ai_explain_code():
    """AI代码解释（带数据库保存）"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')

        if not code:
            return jsonify({"error": "代码不能为空"}), 400

        prompt = f"请用中文解释以下{language}代码的功能和工作原理：\n\n{code}"

        try:
            # 使用微型模型生成解释
            explanation = "explanation..."

            # 保存到数据库
            ai_record = AICodeGeneration(
                original_prompt=prompt,
                generated_content=explanation,
                language=language,
                function_type="explain"
            )
            db.session.add(ai_record)
            db.session.commit()

            return jsonify({
                "status": "success",
                "explanation": explanation,
                "record_id": ai_record.id
            })
        except Exception as e:
            db.session.rollback()
            print(f"AI解释生成失败: {str(e)}")
            return jsonify({"error": f"AI服务暂时不可用: {str(e)}"}), 503

    except Exception as e:
        print(f"AI解释接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/ai/generate', methods=['POST'])
def ai_generate_code():
    """AI代码生成（带数据库保存）"""
    try:
        data = request.get_json()
        requirement = data.get('requirement', '')
        language = data.get('language', 'python')

        if not requirement:
            return jsonify({"error": "需求描述不能为空"}), 400

        prompt = f"请根据以下需求编写{language}代码，要求代码规范且有详细注释：\n\n需求：{requirement}"

        try:
            # 使用微型模型生成代码
            code = "code..."

            # 保存到数据库
            ai_record = AICodeGeneration(
                original_prompt=requirement,
                generated_content=code,
                language=language,
                function_type="generate"
            )
            db.session.add(ai_record)
            db.session.commit()

            return jsonify({
                "status": "success",
                "code": code,
                "record_id": ai_record.id
            })
        except Exception as e:
            db.session.rollback()
            print(f"AI代码生成失败: {str(e)}")
            return jsonify({"error": f"AI服务暂时不可用: {str(e)}"}), 503

    except Exception as e:
        print(f"AI生成接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/ai/solve', methods=['POST'])
def ai_solve_problem():
    """AI算法题目求解（带数据库保存）"""
    try:
        data = request.get_json()
        problem = data.get('problem', '')
        language = data.get('language', 'python')

        if not problem:
            return jsonify({"error": "题目描述不能为空"}), 400

        prompt = f"请解决以下算法题目，使用{language}编写代码，要求有详细注释和解题思路：\n\n题目：{problem}"

        try:
            # 使用微型模型生成解决方案
            solution = "solution..."

            # 保存到数据库
            ai_record = AICodeGeneration(
                original_prompt=problem,
                generated_content=solution,
                language=language,
                function_type="solve"
            )
            db.session.add(ai_record)
            db.session.commit()

            return jsonify({
                "status": "success",
                "solution": solution,
                "record_id": ai_record.id
            })
        except Exception as e:
            db.session.rollback()
            print(f"AI解题失败: {str(e)}")
            return jsonify({"error": f"AI服务暂时不可用: {str(e)}"}), 503

    except Exception as e:
        print(f"AI解题接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/ai/debug', methods=['POST'])
def ai_debug_code():
    """AI代码调试（带数据库保存）"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        error = data.get('error', '')
        language = data.get('language', 'python')

        if not code:
            return jsonify({"error": "代码不能为空"}), 400

        prompt = f"请帮助调试以下{language}代码：\n\n代码：{code}\n\n错误信息：{error}\n\n请分析错误原因并提供修复方案："

        try:
            # 使用微型模型生成调试信息
            debug_info = "debug_info..."

            # 保存到数据库
            ai_record = AICodeGeneration(
                original_prompt=prompt,
                generated_content=debug_info,
                language=language,
                function_type="debug"
            )
            db.session.add(ai_record)
            db.session.commit()

            return jsonify({
                "status": "success",
                "debug_info": debug_info,
                "record_id": ai_record.id
            })
        except Exception as e:
            db.session.rollback()
            print(f"AI调试失败: {str(e)}")
            return jsonify({"error": f"AI服务暂时不可用: {str(e)}"}), 503

    except Exception as e:
        print(f"AI调试接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/ai/history', methods=['GET'])
def get_ai_history():
    """获取AI生成历史"""
    try:
        function_type = request.args.get('type', '')
        limit = request.args.get('limit', 10, type=int)

        query = AICodeGeneration.query

        if function_type:
            query = query.filter_by(function_type=function_type)

        records = query.order_by(AICodeGeneration.created_at.desc()).limit(limit).all()

        return jsonify({
            "status": "success",
            "data": [record.to_dict() for record in records]
        })
    except Exception as e:
        print(f"获取AI历史失败: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/ai/history/<int:record_id>', methods=['DELETE'])
def delete_ai_history(record_id):
    """删除特定的AI生成记录"""
    try:
        record = AICodeGeneration.query.get(record_id)

        if not record:
            return jsonify({"error": "记录不存在"}), 404

        db.session.delete(record)
        db.session.commit()
        return jsonify({"status": "success", "message": "记录删除成功"})
    except Exception as e:
        db.session.rollback()
        print(f"删除AI历史记录失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 健康检查端点
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return jsonify({
        "status": "alive",
        "database": db_status,
        "service": "Python Learning Assistant API"
    })


# 只使用一次：数据库添加列
def upgrade_knowledge_table():
    try:
        # 检查列是否已存在
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='knowledge' and column_name='example'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE knowledge ADD COLUMN example JSON"))
                conn.commit()
    except Exception as e:
        print(f"添加列失败: {e}")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建表
        upgrade_knowledge_table()
    app.run(host='0.0.0.0', port=5000, debug=True)