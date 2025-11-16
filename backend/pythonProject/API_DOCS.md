# Algutor 知识库后端 API 文档

本文档详细描述了 Algutor 知识库后端提供的所有 API 接口，供前端开发者使用。

## 认证方式

### API Key 认证

大多数需要用户身份验证的 API 接口使用 API Key 认证机制。

- **认证头**: `X-API-Key`
- **格式**: `X-API-Key: your-api-key-here`

用户在注册或登录成功后会获得 API Key，后续请求中需要在请求头中携带此 API Key。

## 基础服务 API

### 服务状态检查

```
GET /api/ping
```

**描述**: 检查服务是否正常运行

**参数**: 无

**响应示例**:

```json
{
  "status": "alive",
  "service": "Knowledge Base API",
  "version": "0.20",
  "features": ["user_auth", "public_knowledge", "private_knowledge", "copy_from_public"]
}
```

### 健康检查

```
GET /api/health
```

**描述**: 检查服务健康状态

**参数**: 无

## 用户认证 API

### 用户注册

```
POST /api/auth/register
```

**描述**: 创建新用户账户

**请求体**:

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**参数说明**:

- `username`: 用户名，3-20位字母、数字或下划线
- `email`: 邮箱地址，格式必须正确
- `password`: 密码，长度至少6位

**响应示例**:

```json
{
  "status": "success",
  "message": "注册成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "created_at": "2026-01-01 12:00:00",
      "updated_at": "2026-01-01 12:00:00"
    },
    "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 用户登录

```
POST /api/auth/login
```

**描述**: 用户登录获取 API Key

**请求体**:

```json
{
  "email": "string",
  "password": "string"
}
```

**参数说明**:

- `email`: 邮箱地址
- `password`: 密码

**响应示例**:

```json
{
  "status": "success",
  "message": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "created_at": "2026-01-01 12:00:00",
      "updated_at": "2026-01-01 12:00:00"
    },
    "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 刷新 API Key

```
POST /api/auth/refresh
```

**描述**: 刷新用户的 API Key

**认证**: 需要 `X-API-Key`

**参数**: 无

**响应示例**:

```json
{
  "status": "success",
  "message": "API密钥刷新成功",
  "data": {
    "api_key": "new-api-key-here"
  }
}
```

### 获取用户信息

```
GET /api/user/profile
```

**描述**: 获取当前用户信息

**认证**: 需要 `X-API-Key`

**参数**: 无

**响应示例**:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2026-01-01 12:00:00",
    "updated_at": "2026-01-01 12:00:00"
  }
}
```

## 知识点管理 API

### 获取公共知识库

```
GET /api/knowledge/public
```

**描述**: 获取公共知识点列表或特定知识点

**认证**: 可选 `X-API-Key`

**查询参数**:

- `id`: 知识点ID（可选，获取特定知识点）
- `topic`: 知识点主题（可选，根据主题获取知识点）
- `limit`: 返回数量限制（可选，默认50）
- `offset`: 偏移量（可选，默认0）

**响应示例**:

1. 获取所有公共知识点:
   
   ```json
   {
   "status": "success",
   "data": {
    "items": [
      {
        "id": 1,
        "topic": "Python 基础",
        "explanation": "Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言。",
        "example": [
          {
            "language": "python",
            "code": "print('Hello, World!')"
          }
        ],
        "is_public": true,
        "created_by": 1,
        "created_at": "2026-01-01 12:00:00",
        "updated_at": "2026-01-01 12:00:00"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
   }
   }
   ```

2. 获取特定知识点:
   
   ```json
   {
   "status": "success",
   "data": {
    "id": 1,
    "topic": "Python 基础",
    "explanation": "Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言。",
    "example": [
      {
        "language": "python",
        "code": "print('Hello, World!')"
      }
    ],
    "is_public": true,
    "created_by": 1,
    "created_at": "2026-01-01 12:00:00",
    "updated_at": "2026-01-01 12:00:00"
   }
   }
   ```

### 公共知识库管理

```
GET /api/knowledge
POST /api/knowledge
PUT /api/knowledge
DELETE /api/knowledge
```

**认证**: GET方法无需认证，POST/PUT/DELETE方法需要管理员权限（需要`X-API-Key`）

#### 修改公共知识点

```
PUT /api/knowledge?id=1
```

**认证**: 需要管理员权限（需要`X-API-Key`）

**查询参数**:
- `id`: 知识点ID（必填）

#### 删除公共知识点

```
DELETE /api/knowledge?id=1
```

**认证**: 需要管理员权限（需要`X-API-Key`）

**查询参数**:
- `id`: 知识点ID（必填）

### 从公共知识库拷贝知识点

```
POST /api/knowledge/copy
```

**描述**: 将公共知识点拷贝到个人知识库

**认证**: 需要 `X-API-Key`（未提供将返回401错误）

**请求体**:

```json
{
  "public_knowledge_id": 1,
  "notes": "我的笔记"  // 可选
}
```

**参数说明**:

- `public_knowledge_id`: 公共知识点ID
- `notes`: 用户添加的笔记（可选）

**响应示例**:

```json
{
  "status": "success",
  "message": "知识点拷贝成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "knowledge_id": 2,
    "original_knowledge_id": 1,
    "notes": "我的笔记",
    "is_edited": false,
    "created_at": "2026-01-01 13:00:00",
    "updated_at": "2026-01-01 13:00:00",
    "knowledge": {
      "id": 2,
      "topic": "Python 基础",
      "explanation": "Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言。",
      "example": [
        {
          "language": "python",
          "code": "print('Hello, World!')"
        }
      ],
      "is_public": false,
      "created_by": 1,
      "created_at": "2026-01-01 13:00:00",
      "updated_at": "2026-01-01 13:00:00"
    }
  }
}
```

### 同步从公共知识库拷贝的知识点

```
POST /api/knowledge/sync
```

**描述**: 同步更新从公共知识库拷贝的知识点

**认证**: 需要 `X-API-Key`

**请求体**:

```json
{
  "user_knowledge_id": 1
}
```

**参数说明**:

- `user_knowledge_id`: 用户知识点关联ID

### 用户个人知识库管理

```
GET /api/knowledge/user
POST /api/knowledge/user
PUT /api/knowledge/user
DELETE /api/knowledge/user
```

**认证**: 需要 `X-API-Key`（未提供将返回401错误）

#### 获取用户个人知识点

```
GET /api/knowledge/user
```

**查询参数**:

- `id`: 知识点ID（可选，获取特定知识点）
- `topic`: 知识点主题（可选，根据主题获取知识点）
- `limit`: 返回数量限制（可选，默认50）
- `offset`: 偏移量（可选，默认0）

**响应示例**:

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "knowledge_id": 2,
        "original_knowledge_id": 1,
        "notes": "我的笔记",
        "is_edited": false,
        "created_at": "2026-01-01 13:00:00",
        "updated_at": "2026-01-01 13:00:00",
        "knowledge": {
          "id": 2,
          "topic": "Python 基础",
          "explanation": "Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言。",
          "example": [
            {
              "language": "python",
              "code": "print('Hello, World!')"
            }
          ],
          "is_public": false,
          "created_by": 1,
          "created_at": "2026-01-01 13:00:00",
          "updated_at": "2026-01-01 13:00:00"
        }
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
}
```

#### 添加用户个人知识点

```
POST /api/knowledge/user
```

**请求体**:

```json
{
  "topic": "Python 列表",
  "explanation": "Python 列表是一种有序的可变序列类型。",
  "example": [
    {
      "language": "python",
      "code": "my_list = [1, 2, 3]\nprint(my_list)"
    }
  ],
  "notes": "重要的知识点"  // 可选
}
```

**参数说明**:

- `topic`: 知识点主题（必填）
- `explanation`: 知识点解释（必填）
- `example`: 示例代码列表（可选）
- `notes`: 用户笔记（可选）

**响应示例**:

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "user_id": 1,
    "knowledge_id": 3,
    "original_knowledge_id": null,
    "notes": "重要的知识点",
    "is_edited": false,
    "created_at": "2026-01-01 14:00:00",
    "updated_at": "2026-01-01 14:00:00",
    "knowledge": {
      "id": 3,
      "topic": "Python 列表",
      "explanation": "Python 列表是一种有序的可变序列类型。",
      "example": [
        {
          "language": "python",
          "code": "my_list = [1, 2, 3]\nprint(my_list)"
        }
      ],
      "is_public": false,
      "created_by": 1,
      "created_at": "2026-01-01 14:00:00",
      "updated_at": "2026-01-01 14:00:00"
    }
  }
}
```

#### 更新用户个人知识点

```
PUT /api/knowledge/user?id=3
```

**查询参数**:

- `id`: 知识点ID（必填）

**请求体**:

```json
{
  "topic": "Python 列表更新",
  "explanation": "Python 列表是一种有序的可变序列类型，可以随时添加、修改和删除元素。",
  "example": [
    {
      "language": "python",
      "code": "my_list = [1, 2, 3]\nmy_list.append(4)\nprint(my_list)"
    }
  ],
  "notes": "更新后的笔记"
}
```

**参数说明**:

- `topic`: 知识点主题（可选）
- `explanation`: 知识点解释（可选）
- `example`: 示例代码列表（可选）
- `notes`: 用户笔记（可选）

#### 删除用户个人知识点

```
DELETE /api/knowledge/user?id=3
```

**查询参数**:

- `id`: 知识点ID（必填）

**响应示例**:

```json
{
  "status": "success",
  "message": "知识点删除成功"
}
```

## AI 编程助手 API

### AI 代码解释

```
POST /api/ai/explain
```

**描述**: 使用 AI 解释代码（带数据库保存）

**请求体**:

```json
{
  "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    else:\n        return n * factorial(n-1)",
  "language": "python"  // 可选，默认为python
}
```

**参数说明**:

- `code`: 要解释的代码（必填）
- `language`: 编程语言（可选，默认为python）

### AI 代码生成

```
POST /api/ai/generate
```

**描述**: 使用 AI 生成代码（带数据库保存）

**请求体**:

```json
{
  "requirement": "编写一个冒泡排序算法",
  "language": "python"  // 可选，默认为python
}
```

**参数说明**:

- `requirement`: 需求描述（必填）
- `language`: 编程语言（可选，默认为python）

### AI 算法求解

```
POST /api/ai/solve
```

**描述**: 使用 AI 解决算法问题（带数据库保存）

**请求体**:

```json
{
  "problem": "两数之和：给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出 和为目标值 target  的那 两个 整数，并返回它们的数组下标。",
  "language": "python"  // 可选，默认为python
}
```

**参数说明**:

- `problem`: 问题描述（必填）
- `language`: 编程语言（可选，默认为python）

### AI 代码调试

```
POST /api/ai/debug
```

**描述**: 使用 AI 调试代码（带数据库保存）

**请求体**:

```json
{
  "code": "def divide(a, b):\n    return a / b\n\nresult = divide(10, 0)",
  "error": "ZeroDivisionError: division by zero",  // 可选
  "language": "python"  // 可选，默认为python
}
```

**参数说明**:

- `code`: 要调试的代码（必填）
- `error`: 错误信息（可选）
- `language`: 编程语言（可选，默认为python）

### 获取 AI 生成历史

```
GET /api/ai/history
```

**描述**: 获取 AI 生成的历史记录

**查询参数**:

- `function_type`: 函数类型（可选，explain/generate/solve/debug）
- `limit`: 返回数量限制（可选）

### 删除特定 AI 记录

```
DELETE /api/ai/history/<record_id>
```

**描述**: 删除指定的 AI 生成历史记录

**路径参数**:

- `record_id`: 记录 ID

## 代码分析 API

### 代码分析

```
POST /api/analyse
```

**描述**: 分析代码（语法检查 + 知识点映射）

**请求体**:

```json
{
  "code": "def hello():\n    print('Hello, World!')",
  "language": "python"  // 可选，默认为python
}
```

**参数说明**:

- `code`: 要分析的代码
- `language`: 编程语言（可选）

## 错误响应格式

所有 API 接口在发生错误时返回统一的错误响应格式：

```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

常见的错误码和场景：

- `400`: 请求参数错误（如缺少必要参数）
- `401`: 未授权访问（如未提供X-API-Key或API密钥无效）
- `403`: 禁止访问（如非管理员尝试修改公共知识点）
- `404`: 资源不存在
- `409`: 资源冲突（如用户名已存在）
- `500`: 服务器内部错误（如代码bug导致的异常）

**权限控制说明**:
- 未登录用户（无X-API-Key）无法使用个人知识点功能（返回401错误）
- 非管理员用户无法修改公共知识点（返回403错误）
- 管理员用户需要提供有效的API密钥才能执行管理操作

## 成功响应格式

大多数成功的 API 接口返回格式：

```json
{
  "status": "success",
  "message": "可选的成功描述",
  "data": {}
}
```

---

文档更新时间: 2024-01-18


