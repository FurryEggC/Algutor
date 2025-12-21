#!/usr/bin/env python3
"""
测试内存使用量跟踪功能的脚本
"""

def test_memory_extraction():
    """测试内存使用量提取逻辑"""
    # 模拟/usr/bin/time -v的输出
    mock_stderr = """
Command being timed: "/usr/bin/prlimit --as=268435456 python3 test.py"
User time (seconds): 0.10
System time (seconds): 0.02
Percent of CPU this job got: 99%
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:00.12
Average shared text size (kbytes): 0
Average unshared data size (kbytes): 0
Average stack size (kbytes): 0
Average total size (kbytes): 0
Maximum resident set size (kbytes): 15360
Average resident set size (kbytes): 0
Major (requiring I/O) page faults: 0
Minor (reclaiming a frame) page faults: 3840
Voluntary context switches: 10
Involuntary context switches: 5
Swaps: 0
File system inputs: 0
File system outputs: 0
Socket messages sent: 0
Socket messages received: 0
Signals delivered: 0
Page size (bytes): 4096
Exit status: 0
    """
    
    # 模拟包含原始错误输出的情况
    mock_stderr_with_error = """
Traceback (most recent call last):
  File "test.py", line 1, in <module>
    print("Hello, World!")
Command being timed: "/usr/bin/prlimit --as=268435456 python3 test.py"
User time (seconds): 0.10
System time (seconds): 0.02
Percent of CPU this job got: 99%
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:00.12
Average shared text size (kbytes): 0
Average unshared data size (kbytes): 0
Average stack size (kbytes): 0
Average total size (kbytes): 0
Maximum resident set size (kbytes): 20480
Average resident set size (kbytes): 0
Major (requiring I/O) page faults: 0
Minor (reclaiming a frame) page faults: 3840
Voluntary context switches: 10
Involuntary context switches: 5
Swaps: 0
File system inputs: 0
File system outputs: 0
Socket messages sent: 0
Socket messages received: 0
Signals delivered: 0
Page size (bytes): 4096
Exit status: 0
    """
    
    print("测试1: 提取内存使用量")
    memory_used = 0
    original_error = ""
    
    if mock_stderr:
        lines = mock_stderr.split('\n')
        time_output_lines = []
        original_error_lines = []
        
        found_time_output = False
        for line in lines:
            if "Command being timed:" in line:
                found_time_output = True
                time_output_lines.append(line)
            elif found_time_output:
                time_output_lines.append(line)
                if 'Maximum resident set size' in line:
                    try:
                        memory_used = int(line.split(':')[1].strip())
                        memory_used = round(memory_used / 1024, 2)
                    except:
                        pass
            else:
                original_error_lines.append(line)
        
        original_error = '\n'.join(original_error_lines).strip()
    
    print(f"提取的内存使用量: {memory_used} MB")
    print(f"原始错误输出: '{original_error}'")
    print(f"测试1 {'通过' if memory_used == 15.0 else '失败'}\n")
    
    print("测试2: 从包含错误输出的stderr中提取内存使用量")
    memory_used = 0
    original_error = ""
    
    if mock_stderr_with_error:
        lines = mock_stderr_with_error.split('\n')
        time_output_lines = []
        original_error_lines = []
        
        found_time_output = False
        for line in lines:
            if "Command being timed:" in line:
                found_time_output = True
                time_output_lines.append(line)
            elif found_time_output:
                time_output_lines.append(line)
                if 'Maximum resident set size' in line:
                    try:
                        memory_used = int(line.split(':')[1].strip())
                        memory_used = round(memory_used / 1024, 2)
                    except:
                        pass
            else:
                original_error_lines.append(line)
        
        original_error = '\n'.join(original_error_lines).strip()
    
    print(f"提取的内存使用量: {memory_used} MB")
    print(f"原始错误输出:\n{original_error}")
    print(f"测试2 {'通过' if memory_used == 20.0 else '失败'}\n")
    
    print("测试3: 无内存使用信息的情况")
    mock_stderr_no_memory = """
Command being timed: "/usr/bin/prlimit --as=268435456 python3 test.py"
User time (seconds): 0.10
System time (seconds): 0.02
Percent of CPU this job got: 99%
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:00.12
    """
    
    memory_used = 0
    original_error = ""
    
    if mock_stderr_no_memory:
        lines = mock_stderr_no_memory.split('\n')
        time_output_lines = []
        original_error_lines = []
        
        found_time_output = False
        for line in lines:
            if "Command being timed:" in line:
                found_time_output = True
                time_output_lines.append(line)
            elif found_time_output:
                time_output_lines.append(line)
                if 'Maximum resident set size' in line:
                    try:
                        memory_used = int(line.split(':')[1].strip())
                        memory_used = round(memory_used / 1024, 2)
                    except:
                        pass
            else:
                original_error_lines.append(line)
        
        original_error = '\n'.join(original_error_lines).strip()
    
    print(f"提取的内存使用量: {memory_used} MB")
    print(f"测试3 {'通过' if memory_used == 0 else '失败'}\n")
    
    print("所有测试完成！")

if __name__ == "__main__":
    test_memory_extraction()
