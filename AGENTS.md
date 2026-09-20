# AGENTS.md — offer体检 技能

## 技能概况
- 名称:`offer体检`(`SKILL.md` frontmatter 的 `name`,不要改)
- 作用:招聘 / 公司入职前体检,交叉核验待遇、参保、劳动仲裁、招聘套路、网络/抖音/高德口碑,输出 1–5 星推荐指数的单文件 HTML 报告
- 源码仓库:当前目录(即本技能仓库根)

## 技能安装位置
技能以「用户级 skills 目录」加载(各机器路径不同,本机具体位置见项目记忆)。`use_skill` 列出的 `offer体检` 即指向该目录下的 `SKILL.md`。

## 更新流程(源码仓库 → 技能安装目录)
只同步「技能交付集」,**不要把仓库的开发 / 产物文件带进去**(否则加载的是带杂质的目录,且增大体积)。

### 交付集(必须同步,保持与源码一致)
- `SKILL.md`(主体)
- `README.md`、`LICENSE`
- `assets/`(报告模板 `report_template.html`,被 SKILL 引用)
- `examples/`(样例报告)
- `references/`(仅 `SKILL.md` 实际引用的运行时参考,如 `scoring.md`)

### 排除集(不同步进安装目录)
- `.git`、`.gitignore`、`.workbuddy/`(IDE 元数据)
- `*.zip`(打包产物)
- `docs/`、`tests/`(开发 ADR 与测试 fixtures,含大体积 HTML)
- `reports/`(运行产出的示例报告)
- `.scratch/`、`todo-list/`(本地开发笔记 / 待办)
- `references/adr/`、`references/glossary.md`:虽位于 `references/` 下,但**未被 `SKILL.md` 引用**,属开发决策 / 术语文档,不要同步(与排除 `docs/adr` 保持一致)

### 同步命令(通用)
用 `robocopy /E` 逐目录镜像交付集(只复制新增 / 更新,**不删**目标已有文件),**切忌 `/MIR`**(`/MIR` 会删除目标中源没有的文件,可能误伤)。以 `<REPO>` 表示仓库根、`<SKILLS_DIR>` 表示安装目录,典型步骤:
```powershell
robocopy "<REPO>" "<SKILLS_DIR>" SKILL.md LICENSE README.md /R:1 /W:1
robocopy "<REPO>\assets" "<SKILLS_DIR>\assets" /E /R:1 /W:1
robocopy "<REPO>\examples" "<SKILLS_DIR>\examples" /E /R:1 /W:1
robocopy "<REPO>\references" "<SKILLS_DIR>\references" /E /R:1 /W:1
```
> ⚠️ 用 `/E` 整目录镜像 `references/` 时,若源码新增了 `adr/`、`glossary.md` 等未被引用文件,会被一并带入。同步后核对安装目录 `references/`,手动删掉被意外带入的 `references/adr/` 与 `references/glossary.md`。最稳妥是只复制 `SKILL.md` 实际引用的 `references/scoring.md`。

## 生效
同步完成后,重载 / 重启会话,`offer体检` 技能即加载新版本。
