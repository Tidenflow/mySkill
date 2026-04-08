# Template File Code Example

This file shows the complete implementation with TODO markers and ANSWER blocks.

## File Naming

`xxx.template.ts` where xxx is the feature name.

## Code Structure

```typescript
// 📁 src/utils/jwt.ts
import jwt from "jsonwebtoken"

const secret = process.env.JWT_SECRET || "your-secret-key"

interface TokenPayload {
  userId: number
  username: string
  role: string
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

// ============================================
// TODO: Extract Token from Authorization Header
// ============================================
export function extractToken(authHeader: string | undefined): string | null {
  // Task:
  // 1. Check if authHeader exists and starts with "Bearer "
  // 2. Extract and return the token string
  // 3. Return null if header is invalid
  
  // ===== ANSWER ===== //
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return null
  }
  return authHeader.slice(7)
  // ===== ANSWER ===== //
}
```

## Key Patterns

1. **TODO marker format**:
   ```typescript
   // ============================================
   // TODO: Function Name
   // ============================================
   ```

2. **Task description**: Include clear instructions inside the TODO block

3. **ANSWER block**:
   ```typescript
   // ===== ANSWER ===== //
   // actual working code here
   // ===== ANSWER ===== //
   ```

4. **Placeholder return**: Commented out or replaced by actual answer
   - ❌ `return "" // TODO: Implement this`
   - ✅ Answer block replaces the TODO placeholder