# AGENTS.md — offer体检 技能

## 技能概况
- 名称:`offer体检`（固定，勿改 `SKILL.md` frontmatter 的 `name`）
- 作用:招聘 / 公司入职前体检,交叉核验待遇、参保、劳动仲裁、招聘套路、网络/抖音/高德口碑,输出 1–5 星推荐指数的单文件 HTML 报告
- 源码仓库:当前目录（技能仓库根）

## 技能安装位置
以「用户级 skills 目录」加载（各机路径不同，本机具体位置见项目记忆）。`use_skill` 列出的 `offer体检` 即指向该目录下的 `SKILL.md`。

## 更新流程（源码 → 安装目录）
交付集 / 排除集 / 同步命令全在 **`docs/sync-guide.md`**，本文件不重复。要点：只同步交付集，切忌 `robocopy /MIR`。

## 本机维护信息（本地，未跟踪，不进版本库）
安装路径、环境陷阱（safe-delete shim 拦截、`$env:` 内联吞字符等）、ADR 时延优化、对比测试 fixtures 清单 → 见本地未跟踪文件 `.scratch/local-maintenance.md`。
- 该文件被 `.gitignore` 排除，不出现在技能交付集 / skills 安装目录；缺失即表示当前环境无需这些本机信息。
