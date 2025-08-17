import ast


# 知识点映射表
KNOWLEDGE_MAP = {
    "语法错误": ["Python基础语法"],
    "缩进错误": ["Python缩进规则"]
}


def map_knowledge(error: str) -> list:
    for kw, topics in KNOWLEDGE_MAP.items():
        if kw in error:
            return topics
    return ["通用编程概念"]


# 使用 ast 基础检查
def check_python_syntax(code: str) -> list:
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as er:
        errors.append(f"line {er.lineno}, {er.msg}")
    return errors


if __name__ == "__main__":
    # 测试代码
    test_code = """for i in range(1, 105, 3)
    print(i)
"""
    print(check_python_syntax(test_code))
    for i in check_python_syntax(test_code):
        print(map_knowledge(i))
