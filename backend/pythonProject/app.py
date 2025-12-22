import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import re

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

from models import db, Knowledge

app = Flask(__name__)
CORS(app, origins="*")

# 在文件开头加载环境变量
load_dotenv()

# 加载 client
client = OpenAI(
    api_key=os.environ.get('API_KEY'),
    base_url="https://api.deepseek.com")

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
            # noinspection PyTypeChecker
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个编程辅助助手"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            # 使用 API 接口生成解释
            explanation = response.choices[0].message.content

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
            # noinspection PyTypeChecker
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个编程辅助助手"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            # 使用 API 接口生成代码
            code = response.choices[0].message.content

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
            # noinspection PyTypeChecker
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个编程辅助助手"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            # 使用 API 接口生成解释
            solution = response.choices[0].message.content

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
            # noinspection PyTypeChecker
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个编程辅助助手"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            # 使用 API 接口生成解释
            debug_info = response.choices[0].message.content

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


@app.route('/api/execute', methods=['POST'])
def execute_code():
    """代码执行"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python').lower()
        timeout = data.get('timeout', 3)  # 默认超时3秒
        memorylimit = data.get('memorylimit', 256)  # 默认内存限制256MB
        args = data.get('args', [])  # 获取命令行参数列表
        input_data = data.get('input', '')  # 获取程序输入

        if memorylimit < 16 or memorylimit > 512:
            return {
                "status": "error",
                "error": f"内存限制错误: {memorylimit}, 预期: [16-512]"
            }, 400

        if timeout < 1 or timeout > 6:
            return {
                "status": "error",
                "error": f"超时时间错误: {timeout}, 预期: [1-6]"
            }, 400

        if not language in ['python', 'c', 'cpp', 'c++', 'java']:
            return {
                "status": "error",
                "error": f"未知语言: {language}, 预期: {['python', 'c', 'cpp', 'c++', 'java']}"
            }, 400
        if not code:
            return {
                "status": "error",
                "message": "代码不能为空"
            }, 400

        output = ""
        error = ""
        temp_dir = None

        if not isinstance(args, list):
            return {
                "status": "error",
                "message": "args参数必须是数组格式"
            }, 400

        if language == 'python':
            return execute_python(code, args, timeout, memorylimit * 1024 * 1024, input_data)
        elif language == 'c':
            return execute_c(code, args, timeout, memorylimit * 1024 * 1024, input_data)
        elif language == 'cpp' or language == 'c++':
            return execute_cpp(code, args, timeout, memorylimit * 1024 * 1024, input_data)
        elif language == 'java':
            return execute_java(code, args, timeout, memorylimit * 1024 * 1024, input_data)

    except Exception as e:
        print(f"代码执行接口错误: {str(e)}")
        return {
            "status": "error",
            "message": "服务器内部错误"
        }, 500


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
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)


