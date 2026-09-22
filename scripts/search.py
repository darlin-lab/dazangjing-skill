#!/usr/bin/env python3
"""大正藏经文检索工具
用法:
  python3 search.py "應無所住而生其心"        # 全文检索（原文逐字）
  python3 search.py --name 金剛經             # 按经名查目录
输出: 命中的经号/经名/文件路径 + 上下文
"""
import subprocess, sys, os, argparse

BASE = os.environ.get("CBETA_HOME", os.path.expanduser("~/佛经库"))
TXT = os.path.join(BASE, "经文")
CAT = os.path.join(BASE, "catalog.tsv")


def find_files(pattern):
    r = subprocess.run(["grep", "-rF", "-l", "--include=*.txt", pattern, TXT],
                       capture_output=True, text=True, timeout=600)
    return [l for l in r.stdout.splitlines() if l]


def show(path, phrase, ctx=160, maxhits=5):
    try:
        text = open(path, encoding="utf-8").read()
    except Exception as e:
        print(f"  (读取失败: {e})")
        return
    name = os.path.basename(path)
    n = 0
    start = 0
    while n < maxhits:
        i = text.find(phrase, start)
        if i < 0:
            break
        lo, hi = max(0, i - ctx), min(len(text), i + len(phrase) + ctx)
        snippet = text[lo:hi].replace("\n", " ")
        print(f"\n【{name}】…{snippet}…")
        start = i + len(phrase)
        n += 1
    if n == 0:
        print(f"\n【{name}】(命中但未定位，文件: {path})")


def by_name(name):
    hits = []
    with open(CAT, encoding="utf-8") as f:
        for line in f:
            if name in line:
                hits.append(line.rstrip("\n"))
    for h in hits[:30]:
        print("\t".join(h.split("\t")[:6]))
    print(f"\n共 {len(hits)} 条（显示前30）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="要检索的原文词句")
    ap.add_argument("--name", action="store_true", help="按经名检索目录")
    ap.add_argument("--max-files", type=int, default=8)
    args = ap.parse_args()
    if not (args.query or ""):
        print(__doc__)
        return
    if args.name:
        by_name(args.query)
        return
    files = find_files(args.query)
    print(f"『{args.query}』命中 {len(files)} 部经")
    for p in files[:args.max_files]:
        show(p, args.query)
    if len(files) > args.max_files:
        print(f"\n……其余 {len(files)-args.max_files} 部: ")
        for p in files[args.max_files:args.max_files+15]:
            print("  ", p)


if __name__ == "__main__":
    main()
