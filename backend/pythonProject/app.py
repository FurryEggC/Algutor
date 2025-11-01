from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Knowledge, AICodeGeneration
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
        "version": "1.0"
    })


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
            examples=data.get('examples', ''),
            difficulty=data.get('difficulty', 'beginner')
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
        if 'examples' in data:
            knowledge.examples = data['examples']
        if 'difficulty' in data:
            knowledge.difficulty = data['difficulty']

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建表
    app.run(host='0.0.0.0', port=5000, debug=True)