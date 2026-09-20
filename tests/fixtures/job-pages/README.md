# 对比测试 fixtures · 职位页原始 HTML

用于回归对比「降延迟版」体检流程的时延与页面工商解析。抓取方式：browser-skill `get-html --out`（BOSS 需登录态），猎聘/智联可用 `WebFetch`。

| 文件 | 站点 | 公司 | 职位 | 原始链接 | 抓取法 | 大小 |
|---|---|---|---|---|---|---|
| `zhipin-jingdong-223862b6340a8b4a0nJ-0ty7FFtW.html` | BOSS | 京东集团 | 体检销售团队负责人（北京） | https://www.zhipin.com/job_detail/223862b6340a8b4a0nJ-0ty7FFtW.html | bsk get-html | 467KB |
| `zhipin-chaoxingju-4efc99c1746692360nN82dm_E1ZT.html` | BOSS | 超聚变技术有限公司 | 交付项目经理 | https://www.zhipin.com/job_detail/4efc99c1746692360nN82dm_E1ZT.html | bsk get-html | 161KB |
| `liepin-dezhiyun-1940210899.html` | 猎聘 | 德之润 | — | https://www.liepin.com/job/1940210899.shtml | bsk get-html | 173KB |
| `zhipin-shell-henan-shengqixincheng-7c9c3e690e17b12f0nF93Nu5EFZY.html` | BOSS | 河南盛启新程信息技术有限公司（自然人独资） | — | https://www.zhipin.com/job_detail/7c9c3e690e17b12f0nF93Nu5EFZY.html | bsk get-html | 167KB |
| `liepin-shell-henan-maozhixian-1965990637.html` | 猎聘 | 河南牦之鲜商贸行（个人独资） | 销售代表（郑州） | https://www.liepin.com/job/1965990637.shtml | bsk get-html | 312KB |
| `zhaopin-shdongfang-jinan-CC120692141J90250427000.html` | 智联 | 上海东方泵业(集团)有限公司济南分公司 | 销售代表（济南） | https://www.zhaopin.com/jobdetail/CC120692141J90250427000.htm | bsk get-html | 3061KB |

> 郑州琛署（微型壳/主体混淆样例）按需求**不纳入**本 fixtures 集。
> 页面内已自带工商信息（主体/企业类型/规模/成立/注册资本/经营状态），验证「页面取工商、免独立串行工商门」设计的关键依据。
> 壳公司样本（盛启新程，企业类型=有限责任公司（自然人独资））用于覆盖**硬红线早停分支**：页面取工商应识别为自然人独资壳 → 报告中省略网络口碑/抖音/高德三段。
> **猎聘也暴露企业类型**：猎聘职位页把「个人独资/自然人独资」直接缀在公司名后（如"河南牦之鲜商贸行(个人独资)"），故页面取工商对猎聘壳**可检**——修正了"猎聘无企业类型"的早期假设（结构化"企业类型"字段仍缺失，但公司名后缀足够触发早停）。
> **智联结构化工商块**：标签为 `企业名称/企业类型/法人代表/经营状态/成立时间/注册资本`，需做映射（成立时间→成立日期、法人代表→法定代表人）；注册资本对分公司常显示 `--`。
> **P0-2 未补**：招聘职位页（含以上全部样本）均**不含"参保人数"**（参保在工商年报/国家公示系统，不在 JD 页）。故"页面含参保→删工商门调用→跑赢并行基线"这条路径在 JD 页上基本不可触发，本 fixtures 集未含此类样本；若需验证，须用企业工商详情页（非职位页）或智联企业主页等会显示参保人数的页面。
