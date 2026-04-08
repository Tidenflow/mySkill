# JWT 完全指南

> 解释 JWT 是什么，为什么需要它，以及如何使用。

---

## 1. 为什么需要 JWT？

在开发 Web 应用时，你经常会遇到这样的场景：

```typescript
// 用户登录后，服务器需要知道"你是谁"
if (用户已登录) {
  return "你的私密数据"
}
```

传统的解决方案是**Session**（会话）：

```
浏览器                    服务器
  │                         │
  │──── 登录请求 ──────────►│
  │◄─── 设置 Cookie ────────│
  │                         │
  │──── 请求（带 Cookie）─►│ 服务器读取 Session
  │◄─── 返回数据 ──────────│
```

**Session 的问题**：
1. **服务器压力大**：每个登录用户都要在服务器存储 Session
2. **分布式困难**：多台服务器需要共享 Session
3. **移动端不友好**：移动端处理 Cookie 不方便

**JWT** 就是来解决这些问题的。

---

## 2. JWT 是什么？

**JWT（JSON Web Token）** 是一种**令牌格式**，可以把用户信息编码成一个字符串，服务器生成后交给客户端，客户端每次请求带上这个令牌，服务器解析后就知道"你是谁"了。

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

这个字符串分为三部分，用 `.` 分隔：
- **Header**（头部）：声明令牌类型和签名算法
- **Payload**（载荷）：存放实际数据
- **Signature**（签名）：验证令牌是否被篡改

---

## 3. JWT 的结构

```
Header.Payload.Signature
```

### 3.1 Header（头部）

```json
{
  "alg": "HS256",  // 签名算法：HMAC SHA-256
  "typ": "JWT"     // 类型
}
```

Base64 编码后：`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`

### 3.2 Payload（载荷）

存放实际需要传递的数据，**标准声明**（可选）：

| 声明 | 含义 |
|------|------|
| `iss` | 签发者 |
| `sub` | 主题（用户 ID） |
| `aud` | 受众 |
| `exp` | 过期时间 |
| `nbf` | 生效时间 |
| `iat` | 签发时间 |
| `jti` | JWT ID（唯一标识） |

**自定义声明**（想放什么放什么）：

```json
{
  "sub": "1234567890",      // 用户 ID
  "name": "John Doe",       // 用户名
  "role": "admin",          // 角色
  "iat": 1516239022         // 签发时间
}
```

Base64 编码后：`eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ`

### 3.3 Signature（签名）

对 Header 和 Payload 进行签名，防止数据被篡改：

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

---

## 4. 在代码中使用 JWT

### 4.1 安装依赖

```bash
npm install jsonwebtoken
npm install -D @types/jsonwebtoken
```

### 4.2 生成 JWT（后端）

```typescript
// 📁 backend/src/utils/jwt.ts
import jwt from "jsonwebtoken"

const secret = process.env.JWT_SECRET || "your-secret-key"  // 密钥，要保管好！

// 生成令牌
const token = jwt.sign(
  {
    sub: "1234567890",     // 用户 ID
    name: "John Doe",      // 用户名
    role: "admin"          // 角色
  },
  secret,
  {
    expiresIn: "7d"        // 有效期：7 天
  }
)

console.log(token)
// eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzA0...（后续省略）
```

### 4.3 验证 JWT（后端）

```typescript
// 📁 backend/src/utils/jwt.ts
import jwt from "jsonwebtoken"

const secret = process.env.JWT_SECRET || "your-secret-key"

try {
  const decoded = jwt.verify(token, secret)
  
  console.log(decoded)
  // {
  //   sub: '1234567890',
  //   name: 'John Doe',
  //   role: 'admin',
  //   iat: 1704...,
  //   exp: 1704...
  // }
} catch (err) {
  // 令牌无效（过期、被篡改）
  console.log("验证失败:", err.message)
}
```

### 4.4 提取 Payload（不验证）

```typescript
// 📁 backend/src/utils/jwt.ts
// 只提取 Payload，不验证签名（不安全，仅用于调试）
const payload = jwt.decode(token)

console.log(payload.sub)   // 1234567890
console.log(payload.name)  // John Doe
```

---

## 5. JWT 的使用流程

```
┌─────────┐                              ┌─────────┐
│  客户端  │                              │  服务器  │
└────┬────┘                              └────┬────┘
     │                                        │
     │──── 1. 登录请求（用户名密码） ─────────►│
     │◄─── 2. 返回 JWT 令牌 ──────────────────│
     │                                        │
     │──── 3. 请求（带 JWT） ────────────────►│
     │     Authorization: Bearer <token>     │
     │◄─── 4. 返回数据 ──────────────────────│
     │                                        │
     │──── 5. 请求（带 JWT） ────────────────►│
     │◄─── 6. 返回数据 ──────────────────────│
```

### 5.1 客户端存储 JWT（前端）

**方式一：localStorage**

```typescript
// 📁 frontend/src/utils/auth.ts
// 登录成功后存储
localStorage.setItem("token", token)

// 发送请求时带上
const token = localStorage.getItem("token")
fetch("/api/data", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
})
```

**方式二：Cookie（更安全）**

```typescript
// 📁 frontend/src/api/axios.ts
// 服务器设置 HttpOnly Cookie
// 客户端自动发送，无需手动处理
```

### 5.2 服务器验证 JWT（后端）

```typescript
// 📁 backend/src/routes/data.ts
import express from "express"
import jwt from "jsonwebtoken"

const router = express.Router()
const secret = process.env.JWT_SECRET || "your-secret-key"

router.get("/data", (req, res) => {
  const authHeader = req.headers.authorization
  
  if (!authHeader) {
    return res.status(401).json({ error: "未登录" })
  }
  
  const token = authHeader.replace("Bearer ", "")
  
  try {
    const decoded = jwt.verify(token, secret)
    // 验证通过，获取用户信息
    res.json({ 
      userId: decoded.sub,
      name: decoded.name,
      data: "你的私密数据"
    })
  } catch (err) {
    res.status(401).json({ error: "令牌无效" })
  }
})

export default router
```

---

## 6. JWT 的优势

| 特性 | 说明 |
|------|------|
| **无状态** | 服务器不需要存储 Session，只验证令牌即可 |
| **跨域支持** | 适合前后端分离、移动端、分布式系统 |
| **标准格式** | JSON 格式，跨语言兼容 |
| **可验证** | 签名机制保证不被篡改 |

---

## 7. JWT 的安全问题

### 7.1 不要在 Payload 存放敏感信息

```typescript
// 📁 backend/src/utils/jwt.ts
// ❌ 错误：密码放在 JWT 里
jwt.sign({ userId: 1, password: "123456" }, secret)

// ✅ 正确：只放不敏感的信息
jwt.sign({ userId: 1 }, secret)
```

### 7.2 密钥要保管好

```typescript
// 📁 backend/src/utils/jwt.ts
// ❌ 错误：硬编码在代码里
const secret = "my-secret-key"

// ✅ 正确：从环境变量读取
const secret = process.env.JWT_SECRET
```

### 7.3 设置合理的过期时间

```typescript
// 📁 backend/src/utils/jwt.ts
// ✅ 合理：7 天
jwt.sign(payload, secret, { expiresIn: "7d" })

// ✅ 更安全：访问令牌短一些，刷新令牌长一些
jwt.sign(payload, secret, { expiresIn: "1h" })  // 访问令牌 1 小时
```

### 7.4 使用 HTTPS

生产环境必须使用 HTTPS，防止令牌被截获。

---

## 8. 完整的项目结构示例

```
my-app/
├── .env                          ← 【JWT 密钥】（不提交到 Git）
├── .env.example                  ← 【模板】（提交到 Git）
├── frontend/                     ← 【前端】
│   ├── src/
│   │   ├── utils/
│   │   │   └── auth.ts           ← 【登录、存取 Token】
│   │   ├── api/
│   │   │   └── axios.ts          ← 【请求拦截器】
│   │   └── stores/
│   │       └── user.ts           ← 【Pinia Store】
│   └── package.json
├── backend/                      ← 【后端】
│   ├── src/
│   │   ├── utils/
│   │   │   └── jwt.ts            ← 【JWT 工具函数】
│   │   ├── middleware/
│   │   │   └── auth.ts           ← 【验证中间件】
│   │   ├── routes/
│   │   │   ├── auth.ts           ← 【登录接口】
│   │   │   └── data.ts           ← 【需要验证的接口】
│   │   └── index.ts              ← 【入口文件】
│   └── package.json
└── package.json                  ← 【根目录】（如有 monorepo）
```

### 8.1 封装 JWT 工具（后端）

```typescript
// 📁 backend/src/utils/jwt.ts
import jwt from "jsonwebtoken"

const secret = process.env.JWT_SECRET || "default-secret"

export interface TokenPayload {
  sub: string      // 用户 ID
  name: string     // 用户名
  role: string     // 角色
}

export function generateToken(payload: TokenPayload): string {
  return jwt.sign(payload, secret, { expiresIn: "7d" })
}

export function verifyToken(token: string): TokenPayload {
  return jwt.verify(token, secret) as TokenPayload
}
```

### 8.2 封装验证中间件（后端）

```typescript
// 📁 backend/src/middleware/auth.ts
import { Request, Response, NextFunction } from "express"
import { verifyToken } from "../utils/jwt"

export function authMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
) {
  const authHeader = req.headers.authorization
  
  if (!authHeader) {
    return res.status(401).json({ error: "未提供令牌" })
  }
  
  const token = authHeader.replace("Bearer ", "")
  
  try {
    const decoded = verifyToken(token)
    ;(req as any).user = decoded  // 挂载到请求对象上
    next()
  } catch (err) {
    return res.status(401).json({ error: "令牌无效或已过期" })
  }
}
```

### 8.3 在路由中使用（后端）

```typescript
// 📁 backend/src/routes/auth.ts
import express from "express"
import { generateToken } from "../utils/jwt"

const router = express.Router()

// 登录
router.post("/login", (req, res) => {
  const { username, password } = req.body
  
  // 这里应该验证用户名密码
  const user = { id: "123", name: username, role: "user" }
  
  const token = generateToken({
    sub: user.id,
    name: user.name,
    role: user.role
  })
  
  res.json({ token })
})

export default router
```

```typescript
// 📁 backend/src/routes/data.ts
import express from "express"
import { authMiddleware } from "../middleware/auth"

const router = express.Router()

// 需要登录的接口
router.get("/profile", authMiddleware, (req, res) => {
  const user = (req as any).user
  res.json({ 
    id: user.sub,
    name: user.name,
    role: user.role
  })
})

export default router
```

### 8.4 前端存储 Token（前端）

```typescript
// 📁 frontend/src/utils/auth.ts
// 登录成功后存储
export function saveToken(token: string) {
  localStorage.setItem("token", token)
}

// 获取 Token
export function getToken(): string | null {
  return localStorage.getItem("token")
}

// 清除 Token（登出）
export function clearToken() {
  localStorage.removeItem("token")
}
```

```typescript
// 📁 frontend/src/api/axios.ts
import axios from "axios"
import { getToken } from "../utils/auth"

const api = axios.create({
  baseURL: "/api"
})

// 请求拦截器：自动带上 Token
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

```typescript
// 📁 frontend/src/stores/user.ts
import { defineStore } from "pinia"
import { saveToken, getToken, clearToken } from "../utils/auth"

export const useUserStore = defineStore("user", {
  state: () => ({
    token: getToken() || "",
    userInfo: null as any
  }),
  actions: {
    setToken(token: string) {
      this.token = token
      saveToken(token)
    },
    logout() {
      this.token = ""
      this.userInfo = null
      clearToken()
    }
  }
})
```

---

## 9. 常见问题

### Q1：JWT 令牌存在哪里？
> - **localStorage**：方便，但容易受到 XSS 攻击
> - **Cookie（HttpOnly）**：更安全，但需要服务器支持
> - 移动端通常存在本地存储

### Q2：JWT 令牌过期了怎么办？
> - **方案一**：刷新令牌（Refresh Token）
> - **方案二**：让用户重新登录

### Q3：JWT 可以登出/失效吗？
> JWT 是无状态的，服务器不存储。**解决方案**：
> - 使用黑名单（Redis）存储已失效的 JWT
> - 使用短期令牌 + 刷新机制
> - 颁发时间 `iat` + 服务端记录用户最近活跃时间

### Q4：JWT 和 Session 选哪个？
> | 场景 | 推荐 |
> |------|------|
> | 前后端分离、移动端 | JWT |
> | 传统 Web 应用 | Session |
> | 需要跨域、分布式 | JWT |

---

## 10. 总结

| 概念 | 说明 |
|------|------|
| JWT | JSON Web Token，一种令牌格式 |
| Header | 头部，声明算法和类型 |
| Payload | 载荷，存放实际数据 |
| Signature | 签名，验证令牌完整性 |
| sign() | 生成 JWT |
| verify() | 验证 JWT |
| expiresIn | 设置过期时间 |

**最佳实践**：
1. JWT 存在 Cookie（HttpOnly）里，更安全
2. 密钥从环境变量读取，不要硬编码
3. 设置合理的过期时间
4. 不要在 Payload 里放敏感信息
5. 生产环境务必使用 HTTPS