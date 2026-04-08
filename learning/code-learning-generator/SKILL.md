---
name: code-learning-generator
description: Creates minimal code learning repositories from technical markdown documents. Generates dual-file structure: xxx.template.ts (with answers) + xxx.workspace.ts (TODO only, for practice). Supports TypeScript, JavaScript, Python, C++, Go, Rust, etc. Use when: building learning project scaffolds, generating practice code from docs, setting up tech practice environments.
---

# Code Learning Generator

Creates code learning repositories from technical documentation with dual-file structure for effective learning.

## Workflow

### Step 1: Collect User Requirements

User provides:
1. **Learning doc path** - Full path to the technical markdown document
2. **Target directory** - Where to create the repo (optional, defaults to tech name folder in current dir)

### Step 2: Analyze Document

Read the md document, extract:
- Code examples (```typescript, ```javascript, ```python, etc.)
- Project structure (directory trees)
- Key technical concepts (JWT, Auth, Database, etc.)
- API endpoint definitions
- Environment setup instructions

### Step 3: Create Project Structure

Build minimal project based on doc analysis:

```
target-dir/
├── README.md                 # Learning guide (with TODO checklist & order)
├── backend/                  # Backend code
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.example
│   └── src/
│       ├── index.ts          # Entry (complete)
│       ├── utils/
│       │   ├── jwt.template.ts   # Complete code with TODO markers
│       │   └── jwt.workspace.ts  # TODO only, no answers
│       ├── middleware/
│       │   ├── auth.template.ts
│       │   └── auth.workspace.ts
│       └── routes/
│           ├── auth.template.ts
│           └── auth.workspace.ts
└── frontend/                 # Frontend code (if needed)
    ├── package.json
    ├── index.template.html
    └── index.workspace.html
```

### Step 4: Write Dual TODO Code

For each TODO file, create TWO versions:

#### Template File (xxx.template.ts)

Contains complete answer with TODO markers for key parts:

```typescript
// 📁 src/utils/jwt.ts
import jwt from "jsonwebtoken"

const secret = process.env.JWT_SECRET || "your-secret-key"

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
  
  // return "" // TODO: Implement this
}
```

#### Workspace File (xxx.workspace.ts)

Only TODO markers, NO answers:

```typescript
// 📁 src/utils/jwt.ts
import jwt from "jsonwebtoken"

const secret = process.env.JWT_SECRET || "your-secret-key"

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
```

### Step 5: Write README.md

Include:
- Project structure
- Startup commands
- TODO task checklist (order + file + description)
- Which file to use (template for reference, workspace for practice)

## Example

User: "I want to learn JWT, doc is at E:\Github\Gains-Summary\skill_stack\jwt_guide.md, create repo at E:\Github\TS_study\JWT"

→ Creates complete JWT learning repo with frontend + backend, 4 TODO file pairs (8 files total), complete README.md.

## Multi-Language Support

The skill supports any programming language. Adjust file extensions accordingly:

| Language | Template File | Workspace File |
|----------|--------------|----------------|
| TypeScript | `xxx.template.ts` | `xxx.workspace.ts` |
| JavaScript | `xxx.template.js` | `xxx.workspace.js` |
| Python | `xxx.template.py` | `xxx.workspace.py` |
| C++ | `xxx.template.cpp` / `.h` | `xxx.workspace.cpp` / `.h` |
| Go | `xxx.template.go` | `xxx.workspace.go` |
| Rust | `xxx.template.rs` | `xxx.workspace.rs` |
| Java | `xxx.template.java` | `xxx.workspace.java` |
| C# | `xxx.template.cs` | `xxx.workspace.cs` |

Project structure adapts to language:

```
# Python project
target-dir/
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── main.py           # Entry (complete)
│   └── utils/
│       ├── jwt.template.py
│       └── jwt.workspace.py

# C++ project
target-dir/
├── README.md
├── src/
│   ├── main.cpp          # Entry (complete)
│   └── utils/
│       ├── jwt.template.cpp
│       └── jwt.workspace.cpp
├── include/
│   ├── jwt.template.h
│   └── jwt.workspace.h
└── CMakeLists.txt
```

## Reference

- See [references/template.md](references/template.md) for template file format
- See [references/workspace.md](references/workspace.md) for workspace file format
- See [references/jwt_example.md](references/jwt_example.md) for complete example output

## Principles

- Create minimal, runnable project structure only
- Entry files remain complete, TODO only on core logic
- ALWAYS create dual files: template (with answers) + workspace (TODO only)
- Template file uses `// ===== ANSWER ===== //` comment blocks to show correct implementation
- Workspace file has NO answers, only empty TODO placeholders
- README.md must include complete startup commands and task order