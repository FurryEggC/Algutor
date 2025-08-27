from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from dotenv import load_dotenv

# 自动从项目根目录加载 .env 文件
load_dotenv()

app = Flask(__name__)

# 配置 MySQL 数据库连接
# 格式: mysql+pymysql://用户名:密码@服务器地址/数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://username:password@localhost/knowledge_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 数据库迁移
migrate = Migrate(app, db)


class Knowledge(db.Model):
    __tablename__ = 'knowledge'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), unique=True, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# 创建数据库表（如果不存在）
with app.app_context():
    db.create_all()


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({
        "status": "alive",
        "python_version": os.getenv("PYTHON_VERSION", "unknown"),
        "database": "connected" if db.session.execute('SELECT 1').first() else "disconnected"
    })


@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    # 从数据库查询知识点
    topic = request.args.get("topic")
    knowledge = Knowledge.query.filter_by(topic=topic).first()
    if knowledge:
        return jsonify({
            "status": "success",
            "data": knowledge.to_dict()
        })
    else:
        return jsonify({
            "status": "error",
            "message": "知识点未收录"
        }), 404


@app.route('/api/knowledge', methods=['POST'])
def add_knowledge():
    # 添加知识点
    data = request.get_json()

    if not data or "topic" not in data or "explanation" not in data:
        return jsonify({
            "status": "error",
            "message": "必须提供topic和explanation字段"
        }), 400

    # 检查是否存在该主题
    existing = Knowledge.query.filter_by(topic=data['topic']).first()
    if existing:
        return jsonify({
            "status": "error",
            "message": "该主题已存在"
        }), 409

    new_knowledge = Knowledge(
        topic=data['topic'],
        explanation=data['explanation']
    )

    # 尝试添加
    try:
        db.session.add(new_knowledge)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "知识点添加成功",
            "data": new_knowledge.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"数据库错误: {str(e)}"
        }), 500


@app.route('/api/knowledge', methods=['PUT'])
def update_knowledge():
    # 更新知识点
    topic = request.args.get("topic")
    data = request.get_json()
    knowledge = Knowledge.query.filter_by(topic=topic).first()

    # 检查知识点存在，不存在抛 404
    if not knowledge:
        return jsonify({
            "status": "error",
            "message": "知识点不存在"
        }), 404

    # 用 try-except 检查数据库是否成功更新数据，异常抛 500
    try:
        knowledge.explanation = data['explanation']
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "知识点更新成功"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"数据库错误: {str(e)}"
        }), 500


@app.route('/api/knowledge', methods=['DELETE'])
def delete_knowledge():

    # 删除知识点
    topic = request.args.get("topic")
    knowledge = Knowledge.query.filter_by(topic=topic).first()

    # 检查知识点存在，不存在抛 404
    # Your code...

    # 用 try-catch 检查数据库是否成功删除数据，异常抛 500
    # 提示：使用 db.session.delete(knowledge) 删除数据库知识点
    # Your code...


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
