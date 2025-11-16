import requests
import json
import os

# API基础URL
BASE_URL = "http://localhost:5000/api"

# 测试数据
test_user = {
    "username": "test_user",
    "email": "test@example.com",
    "password": "test_password"
}

# 保存用户凭证
api_key = None
user_id = None

# 辅助函数：打印响应
def print_response(response):
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"响应内容: {response.text}")
        return None

# 测试1: ping接口
def test_ping():
    print("\n=== 测试ping接口 ===")
    response = requests.get(f"{BASE_URL}/ping")
    print_response(response)

# 测试2: 用户注册
def test_register():
    global api_key, user_id
    print("\n=== 测试用户注册 ===")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=test_user
    )
    data = print_response(response)
    
    if response.status_code == 201 and data:
        api_key = data.get("data", {}).get("api_key")
        user_id = data.get("data", {}).get("user", {}).get("id")
        print(f"成功注册用户，API密钥: {api_key[:20]}..." if api_key else "注册成功，但未获取API密钥")

# 测试3: 用户登录
def test_login():
    global api_key, user_id
    print("\n=== 测试用户登录 ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )
    data = print_response(response)
    
    if response.status_code == 200 and data:
        api_key = data.get("data", {}).get("api_key")
        user_id = data.get("data", {}).get("user", {}).get("id")
        print(f"成功获取API密钥: {api_key[:20]}..." if api_key else "登录成功，但未获取API密钥")
        print(f"当前API密钥: {api_key}")

# 测试4: 刷新令牌
def test_refresh_token():
    global api_key
    print("\n=== 测试刷新令牌 ===")
    if not api_key:
        print("没有API密钥，跳过测试")
        return
        
    print(f"使用API密钥: {api_key}")
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        headers={"X-API-Key": api_key}
    )
    data = print_response(response)
    
    if response.status_code == 200 and data:
        new_api_key = data.get("data", {}).get("api_key")
        if new_api_key:
            api_key = new_api_key
            print(f"成功刷新API密钥: {api_key[:20]}...")

# 测试5: 获取用户信息
def test_get_user_profile():
    print("\n=== 测试获取用户信息 ===")
    if not api_key:
        print("没有API密钥，跳过测试")
        return
        
    print(f"使用API密钥: {api_key}")
    response = requests.get(
        f"{BASE_URL}/user/profile",
        headers={"X-API-Key": api_key}
    )
    print_response(response)

# 测试6: 查看公共知识库
def test_get_public_knowledge():
    print("\n=== 测试查看公共知识库 ===")
    response = requests.get(f"{BASE_URL}/knowledge/public")
    data = print_response(response)
    return data

# 测试7: 添加用户私有知识点
def test_add_user_knowledge():
    print("\n=== 测试添加用户私有知识点 ===")
    if not api_key:
        print("没有API密钥，跳过测试")
        return None
        
    test_knowledge = {
        "topic": "测试知识点",
        "explanation": "这是一个测试知识点的解释",
        "example": "示例代码或用法",
        "notes": "用户笔记"
    }
    
    print(f"使用API密钥: {api_key}")
    response = requests.post(
        f"{BASE_URL}/knowledge/user",
        headers={"X-API-Key": api_key},
        json=test_knowledge
    )
    data = print_response(response)
    
    if response.status_code == 201 and data:
        return data.get("data", {}).get("knowledge_id")
    return None

# 测试8: 查看用户私有知识库
def test_get_user_knowledge():
    print("\n=== 测试查看用户私有知识库 ===")
    if not api_key:
        print("没有API密钥，跳过测试")
        return
        
    print(f"使用API密钥: {api_key}")
    response = requests.get(
        f"{BASE_URL}/knowledge/user",
        headers={"X-API-Key": api_key}
    )
    print_response(response)

# 测试9: 拷贝公共知识点
def test_copy_public_knowledge(public_data):
    print("\n=== 测试拷贝公共知识点 ===")
    if not api_key:
        print("没有API密钥，跳过测试")
        return
        
    if not public_data or "data" not in public_data:
        print("公共知识库数据不可用，无法测试拷贝功能")
        return
    
    # 尝试获取第一个公共知识点ID
    try:
        # 解析正确的数据结构 (data.items 是知识点列表)
        knowledge_items = public_data["data"].get("items", [])
        if isinstance(knowledge_items, list) and len(knowledge_items) > 0:
            public_knowledge_id = knowledge_items[0].get("id")
            
            if public_knowledge_id:
                print(f"拷贝知识点ID: {public_knowledge_id}")
                print(f"使用API密钥: {api_key}")
                copy_response = requests.post(
                    f"{BASE_URL}/knowledge/copy",
                    headers={"X-API-Key": api_key},
                    json={"public_knowledge_id": public_knowledge_id}
                )
                print_response(copy_response)
            else:
                print("无法获取公共知识点ID")
        else:
            print(f"公共知识库为空或格式不符合预期，items数量: {len(knowledge_items) if isinstance(knowledge_items, list) else '未知'}")
    except Exception as e:
        print(f"获取公共知识点ID时出错: {str(e)}")

# 运行所有测试
def run_all_tests():
    print("开始测试API功能...")
    
    test_ping()
    test_register()  # 可能会失败，因为用户可能已存在
    test_login()     # 这个应该会成功
    
    # 验证API密钥是否成功获取
    if api_key:
        print(f"\nAPI密钥验证: 已成功获取API密钥")
        test_refresh_token()
        test_get_user_profile()
    else:
        print(f"\nAPI密钥验证: 未能获取API密钥")
    
    # 获取公共知识库数据
    public_data = test_get_public_knowledge()
    
    # 添加用户知识点和获取用户知识点
    if api_key:
        test_add_user_knowledge()
        test_get_user_knowledge()
        test_copy_public_knowledge(public_data)
    
    print("\nAPI测试完成!")

if __name__ == "__main__":
    run_all_tests()