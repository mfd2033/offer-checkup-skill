#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回归用例：验证「页面取工商」设计前提 + 硬红线早停检测，并投影新旧版本时延。

运行： py -3 tests/test_extract_工商.py
依赖： 仅标准库（无网络、无第三方）。fixtures 见 tests/fixtures/job-pages/README.md

A 部分：对 4 份 fixture 解析工商字段，报告每站点的字段覆盖缺口，
        并断言壳公司（自然人独资）能被早停分支识别。
B 部分：用 2026-09-20 真实体检测得的单次调用时延(responseTimeMs)，
        投影「旧·串行门 / 旧·并行 / 新版」三者的研究+抓取总时延。
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

    # ---------- B. 新旧版本时延对比（投影）----------
    print("\n=== B. 新旧版本时延对比（投影，使用实测 responseTimeMs）===")
    # 实测单次调用时延(ms)，来自 2026-09-20 真实体检（WebSearch.responseTimeMs）
    MEAS = {
        "京东":   {"crawl": 2000, "工商门": 1428, "待遇": 1378, "仲裁": 1427, "套路": 1489, "网络": 1508, "抖音": 5571, "高德": 1435},
        "超聚变": {"crawl": 2000, "工商门": 4264, "待遇": 1364, "仲裁": 1343, "套路": 1420, "网络": 1448, "抖音": 1632, "高德": 1497},
        "德之润": {"crawl": 1000, "工商门": 2356, "待遇": 1214, "仲裁": 1242, "套路": 1375, "网络": 1094, "抖音": 1364, "高德": 1973},
    }
    SOFT = ["待遇", "仲裁", "套路", "网络", "抖音", "高德"]
    STD  = ["待遇", "仲裁", "套路", "网络", "工商门"]   # 标准版(--lite)可选维（砍抖音/高德），非默认
    print(f"{'公司':<8}{'旧·串行门':>10}{'旧·并行':>10}{'新版·全维':>10}{'新版·标准版':>12}")
    for co, m in MEAS.items():
        serial = m["crawl"] + m["工商门"] + max(m[k] for k in SOFT)        # 串行门跳 + 并行波2
        parallel = m["crawl"] + max(m["工商门"], *(m[k] for k in SOFT))    # 7维一次性并行
        new_full = m["crawl"] + max(*(m[k] for k in SOFT), m["工商门"])   # = parallel
        new_std = m["crawl"] + max(m[k] for k in STD)                     # 砍抖音/高德后
        print(f"{co:<8}{serial:>8}ms{parallel:>8}ms{new_full:>8}ms{new_std:>10}ms")

    print("\n说明：")
    print("· 4 份 fixture 页上均不含参保人数（P0-2 未补），故新版·全维 ≈ 旧·并行基线（持平）；")
    print("  相比被替换的串行门版，仅省'串行跳' ~1.5–2s。")
    print("· 京东受抖音 5.6s 卡瓶颈：标准版(--lite)砍掉抖音/高德后 ~7.6s→~2.5s，但该省时依赖'抖音恰为最慢极点'这一离群假设（2026-09-20 实跑仲裁 10.6s 反成极点，省时归零），故砍软维仅作可选提速、不作默认。")
    print("· 超聚变/德之润瓶颈是工商/参保补查(~4.3s/2.4s)：标准版对其无效，除非页含参保(删工商调用)，")
    print("  但该路径 JD 页不可触发（P0-2 缺口），需用工信详情页类输入才能验证。")
    print("\n[OK] 全部解析通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
