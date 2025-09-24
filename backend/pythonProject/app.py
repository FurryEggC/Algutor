from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Knowledge
from analyser import check_python_syntax, map_knowledge
# from ai_assistant.deepseek_client import DeepSeekClient
import os

app = Flask(__name__)
CORS(app)

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://knowledge_user:strong_password_123@localhost/knowledge_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 初始化AI客户端
# ai_client = DeepSeekClient()

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
    data = request.get_json()
    code = data.get('code', '')

    if not code:
        return jsonify({"error": "代码不能为空"}), 400

    # 语法检查
    syntax_errors = check_python_syntax(code)

    # 知识点映射
    knowledge_topics = []
    for error in syntax_errors:
        topics = map_knowledge(error)
        knowledge_topics.extend(topics)

    # 去重
    knowledge_topics = list(set(knowledge_topics))

    # 查询知识点详情
    knowledge_details = []
    for topic in knowledge_topics:
        knowledge = Knowledge.query.filter_by(topic=topic).first()
        if knowledge:
            knowledge_details.append(knowledge.to_dict())

    return jsonify({
        "syntax_errors": syntax_errors,
        "knowledge_topics": knowledge_topics,
        "knowledge_details": knowledge_details
    })


@app.route('/api/knowledge', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_knowledge():
    """统一的知识点CRUD接口"""
    if request.method == 'GET':
        return get_knowledge()
    elif request.method == 'POST':
        return add_knowledge()
    elif request.method == 'PUT':
        return update_knowledge()
    elif request.method == 'DELETE':
        return delete_knowledge()


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
        knowledge = Knowledge(topic=data['topic'], explanation=data['explanation'])
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
        knowledge.explanation = data.get('explanation', knowledge.explanation)
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

# bash: ngrok http 5000
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建表
    app.run(host='0.0.0.0', port=5000, debug=True)
