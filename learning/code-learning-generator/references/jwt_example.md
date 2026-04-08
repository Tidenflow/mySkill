# JWT Learning Repo Example

This is a complete example of a code learning repository generated from the JWT guide document.

## Project Structure

```
JWT/
├── README.md
├── backend/
│   ├── src/
│   │   ├── utils/
│   │   │   ├── jwt.template.ts       # Complete code with TODO + ANSWER
│   │   │   └── jwt.workspace.ts     # TODO only, no answers
│   │   ├── middleware/
│   │   │   ├── auth.template.ts
│   │   │   └── auth.workspace.ts
│   │   ├── routes/
│   │   │   ├── auth.template.ts
│   │   │   ├── auth.workspace.ts
│   │   │   ├── data.template.ts
│   │   │   └── data.workspace.ts
│   │   └── index.ts          # Entry file (complete)
│   ├── .env.example
│   ├── package.json
│   └── tsconfig.json
└── frontend/
    ├── index.template.html    # Complete code with TODO + ANSWER
    ├── index.workspace.html  # TODO only, no answers
    ├── vite.config.js
    └── package.json
```

## How to Use

### For Practice (Recommended)
Use **workspace** files - they contain only TODO markers, forcing you to think and implement the solution yourself.

### For Reference
Use **template** files - they contain the complete answer within `// ===== ANSWER ===== //` blocks. Check here if you're stuck.

## Startup Commands

### 1. Start Backend

```bash
cd backend
npm install
cp .env.example .env
npm run dev
```

### 2. Start Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

## TODO Tasks

### Backend (complete first)

| Order | File | Task |
|-------|------|------|
| 1 | `backend/src/utils/jwt.workspace.ts` | Implement generateToken, verifyToken, decodeToken |
| 2 | `backend/src/middleware/auth.workspace.ts` | Implement auth middleware |
| 3 | `backend/src/routes/auth.workspace.ts` | Implement login endpoint |
| 4 | `backend/src/routes/data.workspace.ts` | Implement protected endpoints |

### Frontend

| Order | File | Task |
|-------|------|------|
| 1 | `frontend/index.workspace.html` | Implement saveToken, getStoredToken, clearStoredToken |
| 2 | `frontend/index.workspace.html` | Implement makeAuthRequest (requests with Token) |
| 3 | `frontend/index.workspace.html` | Complete login() function |

## Test

1. Open frontend http://localhost:5173
2. Click "Login" (admin / 123456)
3. Test "Get Profile", "Get Secret Data" (require auth)
4. Test "Get Public Data" (no auth required)

## Example: Dual Files

### jwt.template.ts (with answers)

```typescript
import jwt from "jsonwebtoken"

const secret = process.env.JWT_SECRET || "your-secret-key"

interface TokenPayload {
  userId: number
  username: string
}

// ============================================
// TODO: Generate JWT Token
// ============================================
export function generateToken(payload: TokenPayload): string {
  // Task:
  // 1. Use jwt.sign() to generate token
  // 2. Set expiresIn: "7d"
  // 3. Return generated token
  
  // ===== ANSWER ===== //
  return jwt.sign(payload, secret, { expiresIn: "7d" })
  // ===== ANSWER ===== //
}

// ============================================
// TODO: Verify JWT Token
// ============================================
export function verifyToken(token: string): TokenPayload | null {
  // Task:
  // 1. Use jwt.verify() to verify token
  // 2. Return decoded payload or null if invalid
  
  // ===== ANSWER ===== //
  try {
    return jwt.verify(token, secret) as TokenPayload
  } catch {
    return null
  }
  // ===== ANSWER ===== //
}

// ============================================
// TODO: Decode JWT Token (without verification)
// ============================================
export function decodeToken(token: string): TokenPayload | null {
  // Task:
  // 1. Use jwt.decode() to decode token (no verification)
  // 2. Return decoded payload or null if failed
  
  // ===== ANSWER ===== //
  const decoded = jwt.decode(token)
  return decoded as TokenPayload | null
  // ===== ANSWER ===== //
}
```

### jwt.workspace.ts (TODO only)

```typescript
import jwt from "jsonwebtoken"

const secret = process.env.JWT_SECRET || "your-secret-key"

interface TokenPayload {
  userId: number
  username: string
}

// ============================================
// TODO: Generate JWT Token
// ============================================
export function generateToken(payload: TokenPayload): string {
  // Task:
  // 1. Use jwt.sign() to generate token
  // 2. Set expiresIn: "7d"
  // 3. Return generated token
  
  return "" // TODO: Implement this
}

// ============================================
// TODO: Verify JWT Token
// ============================================
export function verifyToken(token: string): TokenPayload | null {
  // Task:
  // 1. Use jwt.verify() to verify token
  // 2. Return decoded payload or null if invalid
  
  return null // TODO: Implement this
}

// ============================================
// TODO: Decode JWT Token (without verification)
// ============================================
export function decodeToken(token: string): TokenPayload | null {
  // Task:
  // 1. Use jwt.decode() to decode token (no verification)
  // 2. Return decoded payload or null if failed
  
  return null // TODO: Implement this
}
```

## Reference

Original JWT guide: `E:\Github\Gains-Summary\skill_stack\jwt_guide.md`