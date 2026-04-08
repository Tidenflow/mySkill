# Session + Cookie 完全指南

> 解释 Session 和 Cookie 是什么，为什么需要它们，以及如何使用。

---

## 1. 为什么需要 Session 和 Cookie？

在开发 Web 应用时，你经常会遇到这样的场景：

```typescript
// 用户登录后，服务器需要知道"你是谁"
if (用户已登录) {
  return "你的私密数据"
}
```

HTTP 协议是**无状态**的：每次请求都是独立的，服务器不知道两次请求是否来自同一个用户。

```
服务器视角：
请求1 ──► 不知道是谁
请求2 ──► 不知道是谁  
请求3 ──► 不知道是谁
```

**Session 和 Cookie** 就是来解决这个问题的：让服务器记住用户身份。

---

## 2. Cookie 是什么？

**Cookie** 是浏览器（客户端）存储的一小段数据，每次向服务器发送请求时，浏览器会自动带上 Cookie。

```
浏览器                                            服务器
  │                                                  │
  │──── 首次访问 ──────────────────────────────────►│
  │◄─── 响应（Set-Cookie: session=abc123）──────────│   服务器生成 Session ID
  │                                                  │
  │──── 第二次访问（带 Cookie）────────────────────►│
  │     Cookie: session=abc123                       │
  │◄─── 响应 ──────────────────────────────────────│  服务器根据 ID 识别用户
```

### 2.1 Cookie 的特点

| 特性 | 说明 |
|------|------|
| **存储位置** | 浏览器 |
| **自动发送** | 每次请求自动带上同域名的 Cookie |
| **大小限制** | 约 4KB |
| **生命周期** | 可以设置过期时间 |

### 2.2 Cookie 的结构

```
Cookie: name1=value1; name2=value2; name3=value3
```

---

## 3. Session 是什么？

**Session** 是服务器端存储的用户会话信息。服务器为每个用户创建一个唯一的 Session ID，用这个 ID 来查找对应的会话数据。

```
服务器内存/数据库：

Session Store:
┌─────────────┬──────────────────────────┐
│ Session ID  │ 用户数据                  │
├─────────────┼──────────────────────────┤
│ abc123      │ { userId: 1, name: "Tom" }│
│ def456      │ { userId: 2, name: "Amy" }│
│ ghi789      │ { userId: 3, name: "Bob" }│
└─────────────┴──────────────────────────┘
```

### 3.1 Session 的特点

| 特性 | 说明 |
|------|------|
| **存储位置** | 服务器（内存/数据库/Redis） |
| **唯一标识** | 每个用户有唯一的 Session ID |
| **可存储更多数据** | 不像 Cookie 那样限制大小 |
| **需要清理** | 过期或登出后需要删除 |

---

## 4. Session + Cookie 的工作流程

```
┌─────────┐                              ┌─────────┐
│  浏览器  │                              │  服务器  │
└────┬────┘                              └────┬────┘
     │                                        │
     │──── 1. 登录请求（用户名密码） ─────────►│
     │                                        │
     │     服务器验证成功                     │
     │     创建 Session，存储用户信息         │
     │     生成 Session ID                    │
     │                                        │
     │◄─── 2. 响应（Set-Cookie: sid=abc123）──│
     │     （浏览器自动保存 Cookie）          │
     │                                        │
     │──── 3. 再次请求 ─────────────────────►│
     │     Cookie: sid=abc123                 │
     │                                        │
     │     服务器根据 sid 找到 Session        │
     │     获取用户信息                       │
     │                                        │
     │◄─── 4. 响应（带用户数据） ─────────────│
     │                                        │
```

---

## 5. 在代码中使用 Session + Cookie

### 5.1 使用 express-session（Node.js 后端）

#### 5.1.1 安装依赖

```bash
npm install express-session
npm install -D @types/express-session
```

#### 5.1.2 基本配置（后端）

```typescript
// 📁 backend/src/app.ts
import express from "express"
import session from "express-session"

const app = express()

app.use(session({
  secret: process.env.SESSION_SECRET || "your-secret-key",  // 用于签名 Session ID，重要！
  name: "sid",                                                  // Cookie 名称
  resave: false,                                               // 每次请求是否重新保存 Session
  saveUninitialized: false,                                    // 是否保存未初始化的 Session
  cookie: {
    maxAge: 1000 * 60 * 60 * 24,  // 24 小时（毫秒）
    httpOnly: true,               // 禁止 JavaScript 访问（安全）
    secure: false,                // HTTPS 才发送（生产环境设为 true）
    sameSite: "lax"               // CSRF 防护
  }
}))

app.listen(3000)
```

#### 5.1.3 登录时创建 Session（后端）

```typescript
// 📁 backend/src/routes/auth.ts
router.post("/login", (req, res) => {
  const { username, password } = req.body
  
  // 验证用户名密码（这里简化处理）
  if (username === "admin" && password === "123456") {
    // ✅ 登录成功，创建 Session
    req.session.userId = "123"
    req.session.username = username
    req.session.role = "admin"
    
    res.json({ message: "登录成功" })
  } else {
    res.status(401).json({ error: "用户名或密码错误" })
  }
})
```

#### 5.1.4 检查登录状态（后端）

```typescript
// 📁 backend/src/routes/auth.ts
router.get("/profile", (req, res) => {
  // 检查 Session 是否存在
  if (!req.session.userId) {
    return res.status(401).json({ error: "未登录" })
  }
  
  res.json({
    userId: req.session.userId,
    username: req.session.username,
    role: req.session.role
  })
})
```

#### 5.1.5 登出（销毁 Session）（后端）

```typescript
// 📁 backend/src/routes/auth.ts
router.post("/logout", (req, res) => {
  // 销毁 Session
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: "登出失败" })
    }
    
    // 清除 Cookie
    res.clearCookie("sid")
    res.json({ message: "登出成功" })
  })
})
```

### 5.2 使用 Redis 存储 Session（后端）

生产环境推荐用 Redis 存储 Session，压力大时也能保持性能。

```typescript
// 📁 backend/src/app.ts
import session from "express-session"
import RedisStore from "connect-redistore"

app.use(session({
  secret: process.env.SESSION_SECRET || "your-secret-key",
  store: new RedisStore({
    host: "localhost",
    port: 6379,
    prefix: "session:"
  }),
  cookie: {
    maxAge: 1000 * 60 * 60 * 24 * 7, // 7 天
    httpOnly: true,
    secure: true // 生产环境设为 true
  }
}))
```

---

## 6. Cookie 的属性详解

| 属性 | 说明 | 示例值 |
|------|------|--------|
| `name` | Cookie 名称 | `sessionId` |
| `value` | Cookie 值（Session ID） | `abc123xyz` |
| `maxAge` | 有效期（秒） | `86400`（24小时） |
| `expires` | 过期时间（日期） | `Sat, 01 Jan 2025 00:00:00 GMT` |
| `httpOnly` | 禁止 JS 访问 | `true`（安全） |
| `secure` | 仅 HTTPS 传输 | `true`（生产环境） |
| `sameSite` | CSRF 防护 | `strict` / `lax` / `none` |
| `path` | 作用路径 | `/` |
| `domain` | 作用域名 | `.example.com` |

### 6.1 httpOnly - 安全防护

```typescript
// 📁 backend/src/app.ts
// ✅ 安全：禁止 JavaScript 访问，无法通过 document.cookie 读取
cookie: {
  httpOnly: true
}

// ❌ 不安全：可以被 JavaScript 读取，容易被 XSS 攻击窃取
cookie: {
  httpOnly: false
}
```

### 6.2 sameSite - CSRF 防护

```typescript
// 📁 backend/src/app.ts
// 最严格：完全禁止跨站 Cookie
cookie: {
  sameSite: "strict"
}

// 较宽松：导航到目标网站时允许 Cookie
cookie: {
  sameSite: "lax"
}

// 允许跨站 Cookie（需要 secure=true）
cookie: {
  sameSite: "none",
  secure: true
}
```

---

## 7. Session 的安全问题

### 7.1 Session 劫持（Session Hijacking）

攻击者通过窃取用户的 Session ID 来冒充用户。

**防御措施**：

```typescript
// 📁 backend/src/app.ts
// 1. 设置 httpOnly，防止 XSS 窃取
cookie: {
  httpOnly: true
}

// 2. 定期刷新 Session ID
app.use((req, res, next) => {
  if (req.session.regenerate) {
    req.session.regenerate((err) => {
      next(err)
    })
  } else {
    next()
  }
})

// 3. 检查 User-Agent 或 IP 变化
if (req.session.userAgent !== req.headers["user-agent"]) {
  req.session.destroy()
}
```

### 7.2 Session 固定（Session Fixation）

攻击者先获取一个 Session ID，然后诱骗用户使用这个 ID 登录。

**防御措施**：

```typescript
// 📁 backend/src/routes/auth.ts
// 登录后重新生成 Session ID
router.post("/login", (req, res) => {
  // 验证成功后
  req.session.regenerate((err) => {
    req.session.userId = user.id
    res.json({ message: "登录成功" })
  })
})
```

### 7.3 Session 存储安全

```typescript
// 📁 backend/src/routes/auth.ts
// ❌ 错误：敏感信息存 Session（不安全）
req.session.password = user.password
req.session.creditCard = "1234-5678-9012-3456"

// ✅ 正确：只存 ID，通过 ID 去数据库查
req.session.userId = user.id
```

---

## 8. Session vs Cookie

| 特性 | Session | Cookie |
|------|---------|--------|
| **存储位置** | 服务器 | 浏览器 |
| **存储容量** | 较大 | 约 4KB |
| **安全性** | 高（不暴露给客户端） | 中（存在客户端） |
| **性能** | 需要查表 | 自动发送 |
| **生命周期** | 服务器控制 | 浏览器/代码控制 |

### 实际配合使用

```
Session（存服务器） + Cookie（存客户端，作为 Session ID 的载体）
```

---

## 9. 完整的项目结构示例

```
my-app/
├── .env                          ← 【Session 密钥】（不提交到 Git）
├── .env.example                  ← 【模板】（提交到 Git）
├── frontend/                     ← 【前端】（Session + Cookie 主要是后端，前端无感知）
│   ├── src/
│   │   ├── views/
│   │   │   └── Login.vue         ← 【登录页面】
│   │   └── App.vue
│   └── package.json
├── backend/                      ← 【后端】
│   ├── src/
│   │   ├── app.ts               ← 【主应用，配置 Session】
│   │   ├── routes/
│   │   │   ├── auth.ts          ← 【登录、登出、用户接口】
│   │   │   └── data.ts          ← 【业务接口】
│   │   └── middleware/
│   │       └── auth.ts           ← 【登录验证中间件】
│   └── package.json
└── package.json                  ← 【根目录】（如有 monorepo）
```

### 9.1 配置 Session 中间件（后端）

```typescript
// 📁 backend/src/app.ts
import express from "express"
import session from "express-session"

const app = express()

app.use(express.json())

// Session 配置
app.use(session({
  secret: process.env.SESSION_SECRET || "default-secret",
  name: "sid",
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 1000 * 60 * 60 * 24 * 7, // 7 天
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax"
  }
}))

// 引入路由
import authRouter from "./routes/auth"
app.use("/", authRouter)

app.listen(3000, () => {
  console.log("服务器启动在 3000 端口")
})
```

### 9.2 登录验证中间件（后端）

```typescript
// 📁 backend/src/middleware/auth.ts
import { Request, Response, NextFunction } from "express"

export function isAuthenticated(
  req: Request,
  res: Response,
  next: NextFunction
) {
  if (req.session && req.session.userId) {
    next()
  } else {
    res.status(401).json({ error: "未登录，请先登录" })
  }
}
```

### 9.3 路由实现（后端）

```typescript
// 📁 backend/src/routes/auth.ts
import { Router } from "express"
import { isAuthenticated } from "../middleware/auth"

const router = Router()

// 登录
router.post("/login", (req, res) => {
  const { username, password } = req.body
  
  // 验证逻辑（这里简化）
  if (username === "admin" && password === "123456") {
    // ✅ 创建 Session
    req.session.userId = "123"
    req.session.username = username
    req.session.role = "admin"
    
    res.json({ 
      message: "登录成功",
      username 
    })
  } else {
    res.status(401).json({ error: "用户名或密码错误" })
  }
})

// 登出
router.post("/logout", (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: "登出失败" })
    }
    res.clearCookie("sid")
    res.json({ message: "登出成功" })
  })
})

// 获取当前用户（需要登录）
router.get("/me", isAuthenticated, (req, res) => {
  res.json({
    userId: req.session.userId,
    username: req.session.username,
    role: req.session.role
  })
})

// 修改资料（需要登录）
router.put("/profile", isAuthenticated, (req, res) => {
  // 可以更新 Session 中的信息
  if (req.body.nickname) {
    req.session.nickname = req.body.nickname
  }
  res.json({ message: "更新成功" })
})

export default router
```

### 9.4 业务接口示例（后端）

```typescript
// 📁 backend/src/routes/data.ts
import { Router } from "express"
import { isAuthenticated } from "../middleware/auth"

const router = Router()

// 需要登录的接口
router.get("/orders", isAuthenticated, (req, res) => {
  // 可以通过 req.session 获取用户信息
  const userId = req.session.userId
  
  res.json({
    userId,
    orders: [
      { id: 1, name: "商品 A" },
      { id: 2, name: "商品 B" }
    ]
  })
})

export default router
```

---

## 10. 常见问题

### Q1：Session 和 Cookie 有什么区别？
> - **Cookie**：浏览器存储的小数据，每次请求自动发送
> - **Session**：服务器存储的会话信息，通过 Cookie 中的 Session ID 关联

### Q2：Session 存在哪里？
> - **内存**：开发环境，简单但重启丢失
> - **Redis**：生产环境推荐，性能好，支持多实例共享
> - **数据库**：如 MySQL、MongoDB

### Q3：Session 过期了怎么办？
> - 用户重新登录
> - 使用"记住我"功能（延长 Cookie 有效期）
> - 实现刷新令牌机制

### Q4：Cookie 被禁用怎么办？
> - URL 重写（把 Session ID 放在 URL 参数里）
> - 移动端通常使用 Token（JWT）方案

### Q5：Session 和 JWT 选哪个？
> | 场景 | 推荐 |
> |------|------|
> | 传统 Web 应用，后端渲染 | Session + Cookie |
> | 前后端分离、移动端 | JWT |
> | 需要跨域、分布式 | JWT |
> | 需要高安全性，简单实现 | Session（Redis） |

---

## 11. 总结

| 概念 | 说明 |
|------|------|
| Cookie | 浏览器存储的键值对，每次请求自动发送 |
| Session | 服务器存储的用户会话信息 |
| Session ID | 唯一标识，存放在 Cookie 中 |
| express-session | Node.js 常用的 Session 中间件 |
| httpOnly | 禁止 JS 访问，防止 XSS |
| sameSite | CSRF 防护 |
| secure | 仅 HTTPS 发送 |

**最佳实践**：
1. Session 密钥从环境变量读取，不要硬编码
2. 生产环境使用 Redis 存储 Session
3. Cookie 设置 `httpOnly: true` 安全标志
4. 生产环境设置 `secure: true`（HTTPS）
5. 登录后调用 `regenerate()` 防止 Session 固定攻击
6. 设置合理的过期时间