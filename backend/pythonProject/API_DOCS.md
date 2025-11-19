# Algutor API 文档

## 1. 概述

本文档提供了 Algutor 系统的 API 接口规范。Algutor 是一个算法学习和编程辅助平台，提供代码解释、代码生成、问题求解、代码调试以及知识库管理等功能。

## 2. 基础信息

- **API 基础 URL**: `/api`
- **请求格式**: JSON
- **响应格式**: JSON
- **字符编码**: UTF-8

## 3. AI 功能 API

### 3.1 代码解释

**描述**: 使用 AI 解释代码的功能和实现原理。

**端点**: `POST /api/ai/explain`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `code` | string | 是 | 要解释的代码 |
| `language` | string | 否 | 代码语言，默认为 "python" |

**成功响应示例**:

```json
{
  "status": "success",
  "explanation": "# 代码解释\n\n这是一段实现快速排序算法的Python代码..."
}
```

**错误响应示例**:

```json
{
  "status": "partial",
  "explanation": "# AI服务暂时不可用...",
  "error": "AI服务暂时不可用: 错误详情"
}
```

### 3.2 代码生成

**描述**: 根据提示词生成指定语言的代码。

**端点**: `POST /api/ai/generate`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `prompt` | string | 是 | 代码生成的提示词 |
| `language` | string | 否 | 目标编程语言，默认为 "python" |

**成功响应示例**:

```json
{
  "status": "success",
  "generated_code": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)"
}
```

### 3.3 问题求解

**描述**: 解决编程问题并提供详细的解决方案和代码实现。

**端点**: `POST /api/ai/solve`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `problem` | string | 是 | 问题描述 |
| `language` | string | 否 | 解决方案的编程语言，默认为 "python" |

**成功响应示例**:

```json
{
  "status": "success",
  "solution": "# 问题分析\n\n这是一个经典的动态规划问题...\n\n# 代码实现\ndef climbStairs(n):\n    if n <= 2:\n        return n\n    a, b = 1, 2\n    for _ in range(3, n+1):\n        a, b = b, a + b\n    return b"
}
```

### 3.4 代码调试

**描述**: 调试代码并找出错误原因，提供修复建议。

**端点**: `POST /api/ai/debug`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `code` | string | 是 | 要调试的代码 |
| `error` | string | 否 | 错误信息（如果有） |
| `language` | string | 否 | 代码语言，默认为 "python" |

**成功响应示例**:

```json
{
  "status": "success",
  "debug_result": "# 错误分析\n\n发现以下问题：\n1. 变量名拼写错误\n2. 缩进不正确\n\n# 修复后的代码\ndef calculate_average(numbers):\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)"
}
```

## 4. 知识点管理 API

### 4.1 获取所有知识点

**描述**: 获取系统中所有的知识点。

**端点**: `GET /api/knowledge`

**响应示例**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "topic": "快速排序",
      "explanation": "快速排序是一种分治算法...",
      "example": [
        {
          "language": "python",
          "code": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)"
        },
        {
          "language": "c",
          "code": "#include <stdio.h>\n\nvoid swap(int* a, int* b) {\n    int temp = *a;\n    *a = *b;\n    *b = temp;\n}\n\nint partition(int arr[], int low, int high) {\n    int pivot = arr[high];\n    int i = (low - 1);\n    for (int j = low; j <= high - 1; j++) {\n        if (arr[j] < pivot) {\n            i++;\n            swap(&arr[i], &arr[j]);\n        }\n    }\n    swap(&arr[i + 1], &arr[high]);\n    return (i + 1);\n}\n\nvoid quicksort(int arr[], int low, int high) {\n    if (low < high) {\n        int pi = partition(arr, low, high);\n        quicksort(arr, low, pi - 1);\n        quicksort(arr, pi + 1, high);\n    }\n}"
        }
      ],
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

### 4.2 获取单个知识点

**描述**: 根据 ID 获取特定的知识点。

**端点**: `GET /api/knowledge/<id>`

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `id` | integer | 是 | 知识点的唯一标识符 |

**响应示例**:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "topic": "快速排序",
    "explanation": "快速排序是一种分治算法...",
    "example": [
      {
        "language": "python",
        "code": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)"
      },
      {
        "language": "cpp",
        "code": "#include <vector>\n\nvoid quicksort(std::vector<int>& arr, int low, int high) {\n    if (low < high) {\n        int pivot = arr[high];\n        int i = low - 1;\n        for (int j = low; j < high; j++) {\n            if (arr[j] <= pivot) {\n                i++;\n                std::swap(arr[i], arr[j]);\n            }\n        }\n        std::swap(arr[i + 1], arr[high]);\n        int pi = i + 1;\n        quicksort(arr, low, pi - 1);\n        quicksort(arr, pi + 1, high);\n    }\n}"
      }
    ],
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
}
```

### 4.3 添加知识点

**描述**: 添加新的知识点到系统。

**端点**: `POST /api/knowledge`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `topic` | string | 是 | 知识点主题 |
| `explanation` | string | 是 | 知识点解释 |
| `example` | array | 否 | 代码示例数组，默认为空数组 |

**example数组中每个对象的结构**:

| 字段名 | 类型 | 必填 | 描述 | 可选值 |
|--------|------|------|------|--------|
| `language` | string | 是 | 编程语言 | python, c, cpp, java, javascript |
| `code` | string | 是 | 代码内容 | - |

**请求示例**:

```json
{
  "topic": "二分查找",
  "explanation": "二分查找是一种在有序数组中查找特定元素的高效算法...",
  "example": [
    {
      "language": "python",
      "code": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1"
    },
    {
      "language": "java",
      "code": "public class BinarySearch {\n    public static int binarySearch(int[] arr, int target) {\n        int left = 0;\n        int right = arr.length - 1;\n        while (left <= right) {\n            int mid = left + (right - left) / 2;\n            if (arr[mid] == target) {\n                return mid;\n            } else if (arr[mid] < target) {\n                left = mid + 1;\n            } else {\n                right = mid - 1;\n            }\n        }\n        return -1;\n    }\n}"
    }
  ]
}
```

**成功响应示例**:

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "topic": "二分查找",
    "explanation": "二分查找是一种在有序数组中查找特定元素的高效算法...",
    "example": [...],
    "created_at": "2024-01-01T13:00:00",
    "updated_at": "2024-01-01T13:00:00"
  }
}
```

### 4.4 更新知识点

**描述**: 更新指定的知识点。

**端点**: `PUT /api/knowledge/<id>`

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `id` | integer | 是 | 知识点的唯一标识符 |

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `topic` | string | 否 | 知识点主题 |
| `explanation` | string | 否 | 知识点解释 |
| `example` | array | 否 | 代码示例数组 |

**example数组格式**:
同添加知识点API

**成功响应示例**:

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "topic": "二分查找算法",
    "explanation": "更新后的解释...",
    "example": [...],
    "created_at": "2024-01-01T13:00:00",
    "updated_at": "2024-01-01T14:00:00"
  }
}
```

### 4.5 删除知识点

**描述**: 删除指定的知识点。

**端点**: `DELETE /api/knowledge/<id>`

**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `id` | integer | 是 | 知识点的唯一标识符 |

**成功响应示例**:

```json
{
  "status": "success",
  "message": "知识点删除成功"
}
```

## 5. 错误处理

所有 API 接口在出错时返回的错误响应格式如下：

```json
{
  "error": "错误描述"
}
```

常见错误码：

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误或不完整 |
| 404 | Not Found | 请求的资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |
| 206 | Partial Content | AI服务部分可用 |

## 6. 单次会话模式说明

当前所有 AI 功能均为单次会话模式，即：

- 每次 API 调用都是独立的，不会保留之前的上下文
- 不支持多轮对话式交互
- AI 生成的内容不会被系统持久化存储
- 所有 AI 操作都是实时进行的

## 7. 支持的编程语言

系统当前支持的编程语言包括：

- Python
- C
- C++ (cpp)
- Java
- JavaScript

当使用 AI 功能或添加知识点示例时，请确保指定的语言在支持列表中。