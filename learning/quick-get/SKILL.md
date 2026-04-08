---
name: quick-get
description: Generates concise technical documentation for any technology concept. Creates structured docs covering: what it is, why we need it, comparison with alternatives, typical code location, and code organization structure with file layout. Use when user wants to quickly understand a technology or concept.
---

# Quick Get

Generate quick technical documentation for any technology concept.

## Workflow

### Step 1: Collect User Requirements

User provides:
1. **Technology name** - e.g., JWT, Session, WebSocket, Redis
2. **Language/Framework** (optional) - e.g., Node.js, Python, Java

### Step 2: Analyze the Technology

Based on the technology name, gather information about:
- What problem it solves
- How it works
- Common use cases
- Comparison with similar technologies

### Step 3: Generate Document Structure

Create a markdown document with these sections:

```markdown
# {Technology} 完全指南

> 一句话说明这个技术是什么

---

## 1. 为什么需要 {Technology}？

用实际场景说明痛点，对比没有这个技术时的麻烦

## 2. {Technology} 是什么？

解释核心概念，用图或流程说明

## 3. {Technology} 的核心特性/结构

## 4. 与其他技术对比

| 特性 | {Technology} | 替代方案 A | 替代方案 B |
|------|-------------|-----------|-----------|

## 5. 完整的项目结构示例

这是最重要的部分！展示代码组织结构：

```
my-app/
├── .env                          ← 【配置密钥】（不提交到 Git）
├── .env.example                  ← 【模板】（提交到 Git）
├── frontend/                     ← 【前端】
│   ├── src/
│   │   ├── utils/
│   │   │   └── {tech}.ts         ← 【{Technology} 相关工具】
│   │   ├── api/
│   │   │   └── axios.ts          ← 【请求拦截器】
│   │   └── stores/
│   │       └── user.ts           ← 【状态管理】
│   └── package.json
├── backend/                      ← 【后端】
│   ├── src/
│   │   ├── utils/
│   │   │   └── {tech}.ts         ← 【{Technology} 核心实现】
│   │   ├── middleware/
│   │   │   └── {tech}.ts         ← 【中间件/验证】
│   │   ├── routes/
│   │   │   ├── auth.ts           ← 【相关接口】
│   │   │   └── data.ts           ← 【业务接口】
│   │   └── index.ts              ← 【入口文件】
│   └── package.json
└── package.json                  ← 【根目录】（如有 monorepo）
```

### 5.1 核心代码实现

展示关键代码片段，带文件路径标注：

```typescript
// 📁 backend/src/utils/{tech}.ts
// 关键实现代码
```

### 5.2 中间件/工具函数（如适用）

```typescript
// 📁 backend/src/middleware/{tech}.ts
```

### 5.3 在路由中使用

```typescript
// 📁 backend/src/routes/auth.ts
```

## 6. 最佳实践 / 注意事项

## 7. 常见问题

### Q1：xxx?
> 回答

### Q2：xxx?
> 回答

## 8. 总结

| 概念 | 说明 |
|------|------|
| | |

**最佳实践**：
1. 
2. 
3. 
```

## Document Style

- **Language**: 中文（与用户语言一致）
- **Tone**: 简洁易懂，避免术语堆砌
- **Code examples**: 使用 `// 📁 file/path.ts` 标注文件路径
- **Structure**: 始终包含项目结构图（这是用户最关心的）

## Example

User: "给我讲讲 Redis" 或 "quick-get Redis"

→ Generates complete Redis guide with:
- Why Redis (use cases: cache, session store, pub/sub)
- What Redis is
- Comparison with Memcached, in-memory DB
- Full project structure showing Redis integration
- Code examples for common operations
- Best practices

## Reference

See [references/session_cookie_guide.md](references/session_cookie_guide.md) and [references/jwt_guide.md](references/jwt_guide.md) as output format reference.

## Principles

- Always include a project structure diagram - this is the most valuable part
- Use file path annotations `// 📁 path/file.ts` in code examples
- Keep explanations concise but complete
- Compare with similar technologies when relevant
- Include best practices and security notes
