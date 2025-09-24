import ast
import re

# 扩展的知识点映射表
KNOWLEDGE_MAP = {
    "语法错误": ["Python基础语法", "代码结构"],
    "缩进错误": ["Python缩进规则", "代码格式"],
    "括号不匹配": ["括号匹配", "语法规则"],
    "引号不匹配": ["字符串表示", "引号使用"],
    "无效语法": ["Python语法", "代码规范"],
    "未定义变量": ["变量作用域", "变量声明"],
    "无效字符": ["编码问题", "特殊字符处理"]
}


def map_knowledge(error: str) -> list:
    """根据错误信息映射知识点"""
    error_lower = error.lower()
    for kw, topics in KNOWLEDGE_MAP.items():
        if kw.lower() in error_lower:
            return topics
    return ["通用编程概念"]


def check_python_syntax(code: str) -> list:
    """检查Python语法错误"""
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        error_info = {
            "line": e.lineno,
            "message": e.msg,
            "detail": f"第{e.lineno}行: {e.msg}",
            "type": "语法错误"
        }
        errors.append(error_info)
    except Exception as e:
        errors.append({
            "line": 0,
            "message": str(e),
            "detail": f"解析错误: {str(e)}",
            "type": "解析错误"
        })
    return errors


def extract_code_blocks(text: str) -> list:
    """从文本中提取代码块"""
    code_pattern = r'```(?:\w+)?\s*(.*?)\s*```'
    return re.findall(code_pattern, text, re.DOTALL)


if __name__ == "__main__":
    # 测试代码
    test_cases = [
        """for i in range(1, 105, 3)
        print(i)""",

        """def test():
            print("hello"
        """,

        """print("hello world")"""
    ]

    for i, code in enumerate(test_cases):
        print(f"\n--- 测试用例 {i + 1} ---")
        errors = check_python_syntax(code)
        for error in errors:
            print(f"错误: {error['detail']}")
            print(f"知识点: {map_knowledge(error['message'])}")
