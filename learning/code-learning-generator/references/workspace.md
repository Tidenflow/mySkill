# Workspace File Code Example

This file contains ONLY TODO markers - no answers. For reference, use the corresponding template file.

## File Naming

`xxx.workspace.ts` where xxx is the feature name.

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

// ============================================
// TODO: Extract Token from Authorization Header
// ============================================
export function extractToken(authHeader: string | undefined): string | null {
  // Task:
  // 1. Check if authHeader exists and starts with "Bearer "
  // 2. Extract and return the token string
  // 3. Return null if header is invalid
  
  return null // TODO: Implement this
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

3. **Placeholder return**: Empty value with TODO comment
   - Primitive types: `return ""`, `return null`, `return 0`
   - Objects: `return {}`
   - Arrays: `return []`

4. **NO ANSWER blocks**: This file is for your practice only