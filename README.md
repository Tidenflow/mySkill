# mySkill 🧰

我自己在用的 Skill 仓库，记录已经实际使用和验证过的工作流。

## 📦 现有 Skills

| Skill | 用途 |
|-------|------|
| [upstream-imagegen](dev-tools/upstream-imagegen/) | 复用 Codex/CC Switch 当前中转站，通过 `/images/generations` 生成并保存图片 |
| [quick-get](learning/quick-get/) | 快速整理一份中文技术概念文档，包含对比、项目结构和代码示例 |
| [code-learning-generator](learning/code-learning-generator/) | 把技术文档转换成答案版与练习版代码项目 |
| [skill-creator](skill-creator/) | 创建、校验和打包新的 Skill |

## 📁 目录

```text
mySkill/
├── dev-tools/
│   └── upstream-imagegen/
├── learning/
│   ├── quick-get/
│   └── code-learning-generator/
└── skill-creator/
```

## 🚀 使用

每个 Skill 的具体触发条件和使用方式都写在对应的 `SKILL.md` 中。

以 Codex 为例，将需要的 Skill 目录复制到：

```text
~/.codex/skills/
```

重新打开会话后即可调用，例如：

```text
使用 $upstream-imagegen 生成一张宣传图
```

Windows、Linux 和 CC Switch 的详细配置见 [upstream-imagegen 跨平台说明](dev-tools/upstream-imagegen/references/platform-setup.md)。
