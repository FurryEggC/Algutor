from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Knowledge
from dotenv import load_dotenv
import os

from sqlalchemy import text

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://algutor.xyz"}})

# 在文件开头加载环境变量
load_dotenv()

# 配置
# 从环境变量获取数据库URL，如果没有设置则报错
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL环境变量未设置！请检查.env文件")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({
        "status": "alive",
        "service": "Knowledge Base API",
        "version": "0.10"
    })

@app.route('/api/password', methods=['POST'])
def password():
    data = request.get_json()
    password = os.getenv('OPERATOR_PASSWORD')
    if not password:
        return jsonify({"status": "success"})

    if data.get('password') != password:
        return jsonify({"status": "wrong password"})
    return jsonify({"status": "success"})


@app.route('/api/analyse', methods=['POST'])
def analyse_code():
    """代码分析接口 - 集成语法检查和知识点映射"""


@app.route('/api/knowledge', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_knowledge():
    """统一的知识点CRUD接口"""
    try:
        if request.method == 'GET':
            return get_knowledge()
        elif request.method == 'POST':
            return add_knowledge()
        elif request.method == 'PUT':
            return update_knowledge()
        elif request.method == 'DELETE':
            return delete_knowledge()
    except Exception as e:
        print(f"处理知识点时出错: {str(e)}")
        return jsonify({"status": "error", "message": "服务器内部错误"}), 500


def get_knowledge():
    """获取知识点"""
    topic = request.args.get("topic")
    if topic:
        knowledge = Knowledge.query.filter_by(topic=topic).first()
        if knowledge:
            return jsonify({"status": "success", "data": knowledge.to_dict()})
        return jsonify({"status": "error", "message": "知识点未收录"}), 404

    # 获取所有知识点
    all_knowledge = Knowledge.query.all()
    return jsonify({
        "status": "success",
        "data": [k.to_dict() for k in all_knowledge]
    })


def add_knowledge():
    """添加知识点"""
    data = request.get_json()
    if not data or "topic" not in data or "explanation" not in data:
        return jsonify({"status": "error", "message": "必须提供topic和explanation字段"}), 400

    if Knowledge.query.filter_by(topic=data['topic']).first():
        return jsonify({"status": "error", "message": "该主题已存在"}), 409

    try:
        knowledge = Knowledge(
            topic=data['topic'],
            explanation=data['explanation'],
            example=data.get('example', [])
        )
        db.session.add(knowledge)
        db.session.commit()
        return jsonify({"status": "success", "data": knowledge.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"数据库错误: {str(e)}"}), 500


def update_knowledge():
    """更新知识点"""
    topic = request.args.get("topic")
    data = request.get_json()

    knowledge = Knowledge.query.filter_by(topic=topic).first()
    if not knowledge:
        return jsonify({"status": "error", "message": "知识点不存在"}), 404

    try:
        if 'explanation' in data:
            knowledge.explanation = data['explanation']
        if 'example' in data:
            knowledge.example = data['example']

        db.session.commit()
        return jsonify({"status": "success", "data": knowledge.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"数据库错误: {str(e)}"}), 500


def delete_knowledge():
    """删除知识点"""
    topic = request.args.get("topic")
    knowledge = Knowledge.query.filter_by(topic=topic).first()

    if not knowledge:
        return jsonify({"status": "error", "message": "知识点不存在"}), 404

    try:
        db.session.delete(knowledge)
        db.session.commit()
        return jsonify({"status": "success", "message": "知识点删除成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"数据库错误: {str(e)}"}), 500


@app.route('/api/ai/explain', methods=['POST'])
def ai_explain_code():
    """AI代码解释功能 - 单次会话模式"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')

        if not code:
            return jsonify({"error": "代码不能为空"}), 400

        # 构建提示信息
        prompt = f"请详细解释以下{language}代码的功能和实现原理：\n\n代码：{code}\n\n请提供清晰、结构化的解释，包括：\n1. 代码的整体功能\n2. 关键部分的详细说明\n3. 使用的重要概念或算法\n4. 可能的优化建议（如果适用）"

        try:
            # 使用微型模型生成解释
            explanation = "explanation..."

            return jsonify({
                "status": "success",
                "explanation": explanation
            })
        except Exception as e:
            print(f"AI代码解释失败: {str(e)}")
            # 使用备用解释
            fallback_explanation = f"# AI服务暂时不可用，请稍后重试\n\n代码：{code}\n\n请手动分析以上代码。"
            return jsonify({
                "status": "partial",
                "explanation": fallback_explanation,
                "error": f"AI服务暂时不可用: {str(e)}"
            }), 206
    except Exception as e:
        print(f"AI代码解释接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/ai/generate', methods=['POST'])
def ai_generate_code():
    """AI代码生成功能 - 单次会话模式"""
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

            return jsonify({
                "status": "success",
                "generated_code": code
            })
        except Exception as e:
            print(f"AI代码生成失败: {str(e)}")
            # 使用备用代码
            fallback_code = f"# AI服务暂时不可用，请稍后重试\nprint('服务暂时不可用')"
            return jsonify({
                "status": "partial",
                "generated_code": fallback_code,
                "error": f"AI服务暂时不可用: {str(e)}"
            }), 206
    except Exception as e:
        print(f"AI代码生成接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/ai/solve', methods=['POST'])
def ai_solve_problem():
    """AI问题求解功能 - 单次会话模式"""
    try:
        data = request.get_json()
        problem = data.get('problem', '')
        language = data.get('language', 'python')

        if not problem:
            return jsonify({"error": "问题描述不能为空"}), 400

        # 构建提示信息
        prompt = f"请解决以下编程问题，并用{language}语言实现解决方案：\n\n问题描述：{problem}\n\n要求：\n1. 分析问题并提供清晰的解决方案\n2. 写出完整、可运行的代码\n3. 添加必要的注释\n4. 分析时间和空间复杂度\n\n请提供详细的解释和代码实现。"

        try:
            # 使用微型模型生成解决方案
            solution = "solution..."

            return jsonify({
                "status": "success",
                "solution": solution
            })
        except Exception as e:
            print(f"AI问题求解失败: {str(e)}")
            # 使用备用解决方案
            fallback_solution = f"# AI服务暂时不可用，请稍后重试\n\n问题：{problem}\n\n请稍后重试。"
            return jsonify({
                "status": "partial",
                "solution": fallback_solution,
                "error": f"AI服务暂时不可用: {str(e)}"
            }), 206
    except Exception as e:
        print(f"AI问题求解接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/ai/debug', methods=['POST'])
def ai_debug_code():
    """AI代码调试功能 - 单次会话模式"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        error = data.get('error', '')
        language = data.get('language', 'python')

        if not code:
            return jsonify({"error": "代码不能为空"}), 400

        prompt = f"请调试以下{language}代码并修复错误：\n\n代码：{code}\n\n错误信息：{error}\n\n请提供错误分析和修复后的完整代码。" if error else f"请分析以下{language}代码并找出潜在问题：\n\n代码：{code}\n\n请提供问题分析和优化后的完整代码。"

        try:
            # 使用微型模型生成调试信息
            debug_info = "debug_info..."

            return jsonify({
                "status": "success",
                "debugged_code": debug_info
            })
        except Exception as e:
            print(f"AI代码调试失败: {str(e)}")
            # 使用备用调试代码
            fallback_code = f"# AI服务暂时不可用，请稍后重试\n{code}\n# 请手动检查代码中的错误"
            return jsonify({
                "status": "partial",
                "debugged_code": fallback_code,
                "error": f"AI服务暂时不可用: {str(e)}"
            }), 206

    except Exception as e:
        print(f"AI代码调试接口错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500





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


# 数据库表结构维护函数
def upgrade_knowledge_table():
    try:
        with db.engine.connect() as conn:
            # 检查并添加example列（如果不存在）
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='knowledge' and column_name='example'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE knowledge ADD COLUMN example JSON"))
                conn.commit()
                print("成功添加example列")
            
            # 检查并移除多余的is_public列（如果存在）
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='knowledge' and column_name='is_public'
            """))
            if result.fetchone():
                conn.execute(text("ALTER TABLE knowledge DROP COLUMN is_public"))
                conn.commit()
                print("成功移除多余的is_public列")
    except Exception as e:
        print(f"表结构维护失败: {e}")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建表
        upgrade_knowledge_table()
    app.run(host='0.0.0.0', port=5000, debug=True)