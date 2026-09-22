#!/usr/bin/env python3
"""从已生成的 经文/*.txt 文件头重建 catalog.tsv"""
import os, re, time

BASE = os.environ.get("CBETA_HOME", os.path.expanduser("~/佛经库"))
OUT = os.path.join(BASE, "经文")
CAT = os.path.join(BASE, "catalog.tsv")

canon_names = {"T": "大正新脩大藏經", "X": "卍新纂續藏經", "J": "嘉興藏", "K": "高麗藏",
    "A": "國家圖書館善本佛典", "B": "佛教大藏經", "C": "中華藏", "D": "道教文獻",
    "F": "房山石經", "G": "趙城金藏", "GA": "中國佛寺志(GA)", "GB": "中國佛寺志(GB)",
    "I": "藏外佛教文獻", "L": "嘉興藏補", "LC": "龍藏補", "M": "明清佛教文獻",
    "N": "南傳大藏經", "P": "永樂北藏", "S": "事匯部外", "TX": "大正藏圖像",
    "U": "漢譯南傳補", "Y": "印順法師著作", "YP": "太虛大師全書", "ZS": "正史佛教資料",
    "ZW": "大藏經補編", "CC": "補續高僧傳"}

rows = []
t0 = time.time()
for canon in sorted(os.listdir(OUT)):
    cdir = os.path.join(OUT, canon)
    if not os.path.isdir(cdir):
        continue
    for fn in sorted(os.listdir(cdir)):
        fp = os.path.join(cdir, fn)
        try:
            with open(fp, encoding="utf-8") as f:
                head = [f.readline() for _ in range(4)]
            m = re.match(r"《(.+)》", head[0])
            title = m.group(1) if m else fn
            m = re.search(r"（(\w+)）", head[1])
            sid = m.group(1) if m else fn[:8]
            author, extent = "", ""
            for line in head[2:4]:
                mm = re.match(r"譯著：(.*)", line)
                if mm:
                    author = mm.group(1).strip()
                mm = re.match(r"卷數：(.*)", line)
                if mm:
                    extent = mm.group(1).strip()
            size = os.path.getsize(fp)
            rows.append((canon, canon_names.get(canon, canon), sid, title,
                         author, extent, f"经文/{canon}/{fn}", str(size)))
        except Exception as e:
            print("ERR", fn, e, flush=True)

with open(CAT, "w", encoding="utf-8") as w:
    w.write("部類\t部類名\t經號\t經名\t譯著\t卷數\t文件\t文件字節數\n")
    for r in rows:
        w.write("\t".join(r) + "\n")
print(f"catalog: {len(rows)} sutras in {time.time()-t0:.0f}s")
