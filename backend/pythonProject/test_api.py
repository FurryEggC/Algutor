import requests
import json

BASE_URL = "http://localhost:5000/api"


def test_ping():
    """测试服务状态"""
    response = requests.get(f"{BASE_URL}/ping")
    print("服务状态:", response.json())


def test_analyse():
    """测试代码分析"""
    code = """
for i in range(10)
    print(i)
"""
    response = requests.post(f"{BASE_URL}/analyse", json={"code": code})
    print("代码分析结果:", json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_knowledge_crud():
    """测试知识点CRUD"""
    # 添加知识点
    data = {
        "topic": "Python缩进规则",
        "explanation": "Python使用缩进来表示代码块，通常使用4个空格"
    }
    response = requests.post(f"{BASE_URL}/knowledge", json=data)
    print("添加知识点:", response.json())

    # 查询知识点
    response = requests.get(f"{BASE_URL}/knowledge?topic=Python缩进规则")
    print("查询知识点:", response.json())

    # 获取所有知识点
    response = requests.get(f"{BASE_URL}/knowledge")
    print("所有知识点:", len(response.json()['data']))


if __name__ == "__main__":
    test_ping()
    test_analyse()
    test_knowledge_crud()