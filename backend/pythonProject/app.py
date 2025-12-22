from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_mail import Mail, Message
from models import db, Knowledge, AICodeGeneration, User, UserKnowledge, EmailVerification
from dotenv import load_dotenv
import os
import re

from sqlalchemy import text

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://algutor.xyz"}})

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
        "version": "1.00"
    })


@app.route('/api/password', methods=['POST'])
def password():
    data = request.get_json()
    operator_pwd = os.getenv('OPERATOR_PASSWORD')
    if not operator_pwd:
        return jsonify({"status": "success"})

    if data.get('password') != operator_pwd:
        return jsonify({"status": "wrong password"})
    return jsonify({"status": "success"})


# @app.route('/api/analyse', methods=['POST'])
# def analyse_code():
#     """代码分析接口 - 集成语法检查和知识点映射"""


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
        print(f"AI代码调试接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


def execute_python(code: str, args: list, timeout: int, memorylimit: int, input_data: str = ''):
    """执行Python代码并返回结果"""
    start_time = time.perf_counter()
    temp_file = None
    temp_file_path = None

    try:
        # 创建临时文件存储Python代码
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        # 构建命令列表
        cmd = ["/usr/bin/prlimit", f"--as={memorylimit}", sys.executable, temp_file_path] + args

        # 执行代码
        run_start_time = time.perf_counter()
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        end_time = time.perf_counter()

        run_time = round(end_time - run_start_time, 3)

        # 计算总执行时间
        total_execution_time = round(end_time - start_time, 3)

        return {
            "status": "success",
            "output": result.stdout,
            "error": result.stderr,
            "compile_time": 0.0,
            "run_time": run_time,
            "execution_time": total_execution_time
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "代码执行超时",
            "error": f"执行超时：{timeout}秒"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"代码执行失败: {str(e)}",
            "error": str(e)
        }
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass


def execute_c(code: str, args: list, timeout: int, memorylimit: int, input_data: str = ''):
    """执行C代码并返回结果"""
    start_time = time.perf_counter()
    temp_dir = None

    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 生成唯一文件名
        file_name = f"program_{uuid.uuid4().hex}"
        source_path = os.path.join(temp_dir, f"{file_name}.c")
        executable_path = os.path.join(temp_dir, file_name)

        # 写入C代码
        with open(source_path, 'w') as f:
            f.write(code)

        env = os.environ.copy()
        env['PATH'] = os.getenv("ENV_PATH")

        # 编译C代码
        compile_cmd = [os.getenv("C_COMPILER_PATH"), source_path, "-o", executable_path]
        compile_start_time = time.perf_counter()
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env
        )
        compile_time = round(time.perf_counter() - compile_start_time, 3)

        if compile_result.returncode != 0:
            # 编译失败
            return {
                "status": "error",
                "message": "代码编译失败",
                "error": compile_result.stderr,
                "compile_time": compile_time
            }

        # 执行编译后的程序
        cmd = ["/usr/bin/prlimit", f"--as={memorylimit}", executable_path] + args
        run_start_time = time.perf_counter()
        execute_result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )

        end_time = time.perf_counter()

        run_time = round(end_time - run_start_time, 3)

        # 计算总执行时间
        total_execution_time = round(end_time - start_time, 3)

        return {
            "status": "success",
            "output": execute_result.stdout,
            "error": execute_result.stderr,
            "compile_time": compile_time,
            "run_time": run_time,
            "execution_time": total_execution_time
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "代码执行超时",
            "error": f"执行超时：{timeout}秒"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"代码执行失败: {str(e)}",
            "error": str(e)
        }
    finally:
        # 清理临时目录
        if temp_dir:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


def execute_cpp(code: str, args: list, timeout: int, memorylimit: int, input_data: str = ''):
    """执行C++代码并返回结果"""
    start_time = time.perf_counter()
    temp_dir = None

    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 生成唯一文件名
        file_name = f"program_{uuid.uuid4().hex}"
        source_path = os.path.join(temp_dir, f"{file_name}.cpp")
        executable_path = os.path.join(temp_dir, file_name)

        # 写入C++代码
        with open(source_path, 'w') as f:
            f.write(code)

        env = os.environ.copy()
        env['PATH'] = os.getenv("ENV_PATH")

        # 编译C++代码
        compile_cmd = [os.getenv("CPP_COMPILER_PATH"), source_path, "-o", executable_path]
        compile_start_time = time.perf_counter()
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env
        )
        compile_time = round(time.perf_counter() - compile_start_time, 3)

        if compile_result.returncode != 0:
            # 编译失败
            return {
                "status": "error",
                "message": "代码编译失败",
                "error": compile_result.stderr,
                "compile_time": compile_time
            }

        # 执行编译后的程序
        cmd = ["/usr/bin/prlimit", f"--as={memorylimit}", executable_path] + args
        run_start_time = time.perf_counter()
        execute_result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )

        end_time = time.perf_counter()

        run_time = round(end_time - run_start_time, 3)

        # 计算总执行时间
        total_execution_time = round(end_time - start_time, 3)

        return {
            "status": "success",
            "output": execute_result.stdout,
            "error": execute_result.stderr,
            "compile_time": compile_time,
            "run_time": run_time,
            "execution_time": total_execution_time
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "代码执行超时",
            "error": f"执行超时：{timeout}秒"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"代码执行失败: {str(e)}",
            "error": str(e)
        }
    finally:
        # 清理临时目录
        if temp_dir:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


def execute_java(code: str, args: list, timeout: int, memorylimit: int, input_data: str = ''):
    """执行Java代码并返回结果"""
    start_time = time.perf_counter()
    temp_dir = None

    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 检查是否有package声明
        package_match = re.search(r'^\s*package\s+([\w.]+);', code.strip(), re.MULTILINE)
        package_name = package_match.group(1) if package_match else None

        # 查找public class名称
        class_match = re.search(r'public\s+class\s+(\w+)', code)
        if not class_match:
            # 如果没有找到public class，使用默认类名
            class_name = "Main"
            # 添加public class包装
            code = f"public class {class_name} {{\n{code}\n}}"
        else:
            class_name = class_match.group(1)

        # 如果没有package声明，添加默认的package声明
        if not package_name:
            package_name = "main"
            code = f"package {package_name};\n\n{code}"

        # 生成与package结构相对应的目录结构
        if package_name:
            package_dir = os.path.join(temp_dir, *package_name.split('.'))
            os.makedirs(package_dir, exist_ok=True)
            source_path = os.path.join(package_dir, f"{class_name}.java")
        else:
            source_path = os.path.join(temp_dir, f"{class_name}.java")

        # 写入Java代码
        with open(source_path, 'w') as f:
            f.write(code)

        # 获取Java编译器和运行时路径
        javac_path = os.getenv("JAVA_COMPILER_PATH", "javac")  # 默认使用系统PATH中的javac
        java_path = os.getenv("JAVA_RUNTIME_PATH", "java")  # 默认使用系统PATH中的java

        # 检查Java环境是否存在
        java_available = False
        javac_available = False

        # 直接检查配置的路径是否存在
        if os.path.exists(javac_path):
            javac_available = True
        elif javac_path == "javac":
            # 如果使用默认值，检查是否在系统PATH中
            try:
                if os.name == 'nt':  # Windows
                    result = subprocess.run(['where', javac_path], capture_output=True, text=True)
                    javac_available = result.returncode == 0
                else:  # Linux/Mac
                    result = subprocess.run(['which', javac_path], capture_output=True, text=True)
                    javac_available = result.returncode == 0
            except Exception:
                pass

        if os.path.exists(java_path):
            java_available = True
        elif java_path == "java":
            # 如果使用默认值，检查是否在系统PATH中
            try:
                if os.name == 'nt':  # Windows
                    result = subprocess.run(['where', java_path], capture_output=True, text=True)
                    java_available = result.returncode == 0
                else:  # Linux/Mac
                    result = subprocess.run(['which', java_path], capture_output=True, text=True)
                    java_available = result.returncode == 0
            except Exception:
                pass

        if not javac_available or not java_available:
            return {
                "status": "error",
                "message": "Java环境未找到",
                "error": "请安装Java开发工具包(JDK)并配置环境变量。需要javac和java命令都可用。"
            }

        # 编译Java代码
        compile_cmd = [javac_path, "-encoding", "UTF-8", source_path]
        compile_start_time = time.perf_counter()
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        compile_time = round(time.perf_counter() - compile_start_time, 3)

        if compile_result.returncode != 0:
            # 编译失败
            return {
                "status": "error",
                "message": "代码编译失败",
                "error": compile_result.stderr,
                "compile_time": compile_time
            }

        # 直接使用JVM参数限制内存，不使用prlimit
        heap_memory_mb = max(64, memorylimit // (1024 * 1024))

        # 构建Java运行命令，只使用JVM内存参数
        full_class_name = f"{package_name}.{class_name}"

        cmd = [
                  java_path,
                  f"-Xmx{heap_memory_mb}m",  # 最大堆内存
                  f"-Xms{max(16, heap_memory_mb // 2)}m",  # 初始堆内存
                  f"-Xss256k",  # 线程栈大小
                  f"-XX:MaxMetaspaceSize={max(32, heap_memory_mb // 4)}m",  # Metaspace限制
                  f"-XX:+UseSerialGC",  # 使用串行GC
                  "-cp",
                  temp_dir,
                  full_class_name
              ] + args

        run_start_time = time.perf_counter()

        execute_result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        end_time = time.perf_counter()

        run_time = round(end_time - run_start_time, 3)

        # 计算总执行时间
        total_execution_time = round(end_time - start_time, 3)

        return {
            "status": "success",
            "output": execute_result.stdout,
            "error": execute_result.stderr,
            "compile_time": compile_time,
            "run_time": run_time,
            "execution_time": total_execution_time
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "代码执行超时",
            "error": f"执行超时：{timeout}秒"
        }
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