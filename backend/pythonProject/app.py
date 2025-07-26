from flask import Flask, jsonify
import os

# 加载环境变量
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({
        "status": "alive",
        "python_version": os.getenv("PYTHON_VERSION", "unknown")
    })


# 知识点存储
KNOWLEDGE_BASE = {
    "recursion": "函数调用自身需有终止条件"
}


@app.route('/api/knowledge/<topic>', methods=['GET', 'POST'])
def get_knowledge(topic):
    # 从"数据库"查询知识点
    explanation = KNOWLEDGE_BASE.get(topic, "知识点未收录")
    return jsonify({"topic": topic, "explanation": explanation})


# http://localhost:5000/api/knowledge/recursion
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
