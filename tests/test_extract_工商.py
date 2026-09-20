#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回归用例：验证「页面取工商」设计前提 + 硬红线早停检测，并投影新旧版本时延。

运行： py -3 tests/test_extract_工商.py
依赖： 仅标准库（无网络、无第三方）。fixtures 见 tests/fixtures/job-pages/README.md

A 部分：对 6 份 fixture 解析工商字段，报告每站点的字段覆盖缺口，
        并断言壳公司（自然人独资/个人独资）能被早停分支识别。
B 部分：用 2026-09-20 六岗位真实体检测得的单次调用时延(responseTimeMs)，
        分析全维墙钟的极点分布，并测算「标准版(--lite)砍抖音/高德」的实际省时。
"""
import re, glob, os, sys

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "job-pages")

FIXTURES = [
    ("zhipin-jingdong-223862b6340a8b4a0nJ-0ty7FFtW.html",  "BOSS", "京东集团"),
    ("zhipin-chaoxingju-4efc99c1746692360nN82dm_E1ZT.html", "BOSS", "超聚变"),
    ("liepin-dezhiyun-1940210899.html",                   "猎聘", "德之润"),
    ("zhipin-shell-henan-shengqixincheng-7c9c3e690e17b12f0nF93Nu5EFZY.html", "BOSS", "盛启新程(自然人独资)"),
    ("liepin-shell-henan-maozhixian-1965990637.html",     "猎聘", "河南牦之鲜商贸行(个人独资)"),
    ("zhaopin-shdongfang-jinan-CC120692141J90250427000.html", "智联", "上海东方泵业济南分公司"),
]
EXPECTED = ["成立日期", "经营状态", "企业类型", "法定代表人", "注册资本", "公司规模"]


def load(name):
    with open(os.path.join(FIX, name), encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_boss(html):
    d = {}
    for m in re.finditer(r'<li class="[^"]*"><span>([^<]+)</span>([^<]+)</li>', html):
        d[m.group(1).strip()] = m.group(2).strip()
    return d


def parse_liepin(html):
    d = {}
    m = re.search(r'<span class="label">注册资本：</span><span class="text">([^<]+)</span>', html)
    if m:
        d["注册资本"] = m.group(1).strip()
    m = re.search(r'公司规模(\d+-\d+人)', html)
    if m:
        d["公司规模"] = m.group(1)
    m = re.search(r'content="([^"]*?)(?:郑州招聘|北京招聘|上海招聘|招聘)', html)
    if m:
        d["主体"] = m.group(1).strip()
    return d


def parse_zhaopin(html):
    d = {}
    pat = re.compile(r'company-info__business-label">([^<]+)</span>\s*'
                     r'<span class="company-info__business-value">([^<]*)</span>')
    keymap = {"企业名称": "主体", "企业类型": "企业类型", "法人代表": "法定代表人",
              "经营状态": "经营状态", "成立时间": "成立日期", "注册资本": "注册资本"}
    for mm in pat.finditer(html):
        lab, val = mm.group(1).strip(), mm.group(2).strip()
        if lab in keymap:
            d[keymap[lab]] = val
    return d


def analyze(html, name):
    if "liepin" in name:
        d = parse_liepin(html)
    elif "zhaopin" in name:
        d = parse_zhaopin(html)
    else:
        d = parse_boss(html)
    ent = d.get("企业类型", "")
    # 壳判定：BOSS/智联在「企业类型」字段；猎聘把「个人独资/自然人独资」直接缀在公司名后
    is_shell = (("自然人独资" in ent) or ("自然人独资" in html)
                or ("个人独资" in html) or ("微型" in ent))
    has_参保 = "参保人数" in html
    return d, is_shell, has_参保


def main():
    # ---------- A. 页面取工商 覆盖分析 ----------
    print("=== A. 页面取工商 覆盖分析 ===")
    rows = []
    for fn, site, co in FIXTURES:
        html = load(fn)
        d, is_shell, has_参保 = analyze(html, fn)
        missing = [k for k in EXPECTED if k not in d]
        rows.append((co, d, is_shell))
        print(f"\n● {co} ({site})  [{fn}]")
        for k in EXPECTED:
            print(f"   {k:<6}: {d.get(k, '—(页上无)')}")
        print(f"   自然人独资/微型壳 → 早停命中: {is_shell}")
        print(f"   页上含参保人数           : {has_参保}")
        print(f"   缺失字段                 : {missing or '无'}")

    shells = [r for r in rows if r[2]]
    assert shells, "未检测到任何壳公司(自然人独资/个人独资) → 早停分支未被覆盖"
    print(f"\n[OK] 早停检测：找到 {len(shells)} 个壳公司 → {[r[0] for r in shells]}")

    # ---------- B. 六岗位实测墙钟 & 砍软维(标准版)省时分析 ----------
    print("\n=== B. 六岗位实测墙钟 & 砍软维(标准版)省时分析（实测 responseTimeMs）===")
    # 七维同批并行，墙钟 = max(七维)；标准版(--lite)砍抖音+高德、保留网络口碑。
    # 数据来自 2026-09-20 六岗位真实体检，每维 3 条结果取单次响应用时（含 run-to-run 方差）。
    MEAS = {
        "京东集团":       {"待遇":2648,"仲裁":47, "套路":44, "参保":46, "网络":47, "抖音":49, "高德":48},
        "超聚变":         {"待遇":1261,"仲裁":1544,"套路":1771,"参保":1312,"网络":3791,"抖音":1433,"高德":1207},
        "德之润":         {"待遇":1240,"仲裁":2156,"套路":2232,"参保":1417,"网络":1586,"抖音":1887,"高德":2317},
        "盛启新程":       {"待遇":1141,"仲裁":2770,"套路":4451,"参保":1372,"网络":1454,"抖音":1337,"高德":1231},
        "河南牦之鲜商贸行": {"待遇":1519,"仲裁":1612,"套路":1092,"参保":1512,"网络":5869,"抖音":1139,"高德":2054},
        "上海东方泵业":    {"待遇":3023,"仲裁":1743,"套路":1321,"参保":1141,"网络":1330,"抖音":5031,"高德":1779},
    }
    ALL  = ["待遇","仲裁","套路","参保","网络","抖音","高德"]
    LITE = ["待遇","仲裁","套路","参保","网络"]        # 标准版(--lite)：砍抖音+高德，保留网络口碑
    def pole(d, keys): return max(keys, key=lambda k: d[k])

    print(f"{'岗位':<14}{'全维墙钟':>10}{'极点':>10}{'标准版墙钟':>12}{'省时':>10}")
    tot_save = 0
    for co, m in MEAS.items():
        full = m[pole(m, ALL)]
        std  = m[pole(m, LITE)]
        save = full - std
        tot_save += save
        print(f"{co:<14}{full:>8}ms{pole(m,ALL):>10}{std:>10}ms{save:>8}ms")
    n = len(MEAS)
    # ---- 防回归断言：守住 ADR-0002「默认全维、--lite 仅砍抖音+高德」决策 ----
    assert {"网络", "抖音", "高德"}.issubset(ALL), "默认全维必须含软维(网络/抖音/高德)，不得静默砍除"
    assert set(LITE) == set(ALL) - {"抖音", "高德"}, "LITE 必须为 ALL 去掉抖音+高德"
    for co, m in MEAS.items():
        assert m[pole(m, ALL)] >= m[pole(m, LITE)], "默认全维墙钟不应低于标准版(模型结构错误)"
    avg_full = sum(m[pole(m, ALL)] for m in MEAS.values()) // n
    print(f"\n均值墙钟≈{avg_full}ms；标准版累计省时≈{tot_save}ms，均值≈{tot_save//n}ms/次")
    print("\n结论（修正此前'软维零收益'的武断判断）：")
    print("· 极点落在软维 4/6 次（网络×2、抖音×1、高德×1），硬维仅 2/6（待遇、套路）——软维实为常见长板。")
    print("· 但标准版仅砍抖音+高德、保留网络口碑，故仅当'抖音/高德本身唯一极点且网络不更慢'才省时：")
    print("  本轮仅上海东方泵业(抖音极点)省~2s，德之润边际85ms，余4个零省（极点恰为保留的网络/硬维）。")
    print("· 极点跨轮也变（京东本身：仲裁10.6s→待遇2.6s），无维度可稳定当瓶颈；")
    print("  把砍软维当默认=每次永久丢覆盖、仅约1/6换回~2s → 默认保持全维、标准版作显式选项(见 ADR-0002)。")
    print("\n[OK] 全部解析通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
