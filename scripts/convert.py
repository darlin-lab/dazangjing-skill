#!/usr/bin/env python3
"""CBETA XML P5 -> 干净繁体纯文本转换器
- 去掉校勘(app保留lem正文)、注释(note)、脚注锚(ref/anchor)
- 生僻字(g) 按 cbeta_gaiji.csv 官方对照还原
- 一部经一个 txt，输出到 经文/<部>/<经号>.txt
- 生成 catalog.tsv 总目录
"""
import csv, os, re, sys, time
import xml.etree.ElementTree as ET

BASE = os.environ.get("CBETA_HOME", os.path.expanduser("~/佛经库"))
SRC = os.path.join(BASE, "cbeta-xml")
OUT = os.path.join(BASE, "经文")
GAJIJI_CSV = os.path.join(BASE, "工具/cbeta_gaiji/cbeta_gaiji.csv")
CATALOG = os.path.join(BASE, "catalog.tsv")

TEI = "{http://www.tei-c.org/ns/1.0}"
CB = "{http://www.cbeta.org/ns/1.0}"

# ---------- gaiji mapping ----------
gaiji = {}
with open(GAJIJI_CSV, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        ch = row.get("uni_char") or row.get("norm_uni_char") or row.get("norm_big5_char") or ""
        gaiji[row["ID"]] = ch or "□"

SKIP_TAGS = {"note", "ref", "anchor", "listWit", "rdg", "wit", "cb:note", "figure", "graphic", "milestone"}
BLOCK_TAGS = {"p", "head", "lg", "l", "div", "trailer", "byline", "docTitle", "titlePage", "epigraph", "argument", "seg"}


def local(tag):
    t = tag
    for ns in (TEI, CB):
        if t.startswith(ns):
            return t[len(ns):]
    return t


def render(elem, out):
    name = local(elem.tag)
    if name in SKIP_TAGS:
        return
    if name == "app":  # 校勘异文：只取正文(lem)
        lem = elem.find(f"{TEI}lem")
        if lem is not None:
            render(lem, out)
        else:
            # 无lem时取第一个子元素文本
            for ch in elem:
                render(ch, out)
        return
    if name == "g":  # 缺字
        ref = elem.get("ref") or ""
        cid = ref.lstrip("#").split()[0] if ref else ""
        out.append(gaiji.get(cid, "□"))
        return
    if name == "lb":
        return
    if elem.text:
        out.append(elem.text)
    for ch in elem:
        render(ch, out)
        if ch.tail:
            out.append(ch.tail)
    if name in ("l",):  # 偈颂一行一断
        out.append("\n")
    if name in BLOCK_TAGS:
        out.append("\n")


def clean(text):
    text = re.sub(r"[ \t\u3000]+", " ", text)  # 压缩空白（保留空格分隔）
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


canon_names = {
    "T": "大正新脩大藏經", "X": "卍新纂續藏經", "J": "嘉興藏", "K": "高麗藏",
    "A": "國家圖書館善本佛典", "B": "佛教大藏經", "C": "中華藏", "D": "道教文獻",
    "F": "房山石經", "G": "趙城金藏", "GA": "中國佛寺志(GA)", "GB": "中國佛寺志(GB)",
    "I": "藏外佛教文獻", "L": "嘉興藏補", "LC": "龍藏補", "M": "明清佛教文獻",
    "N": "南傳大藏經", "P": "永樂北藏", "S": "事匯部外", "TX": "大正藏圖像",
    "U": "漢譯南傳補", "Y": "印順法師著作", "YP": "太虛大師全書", "ZS": "正史佛教資料",
    "ZW": "大藏經補編", "CC": "補續高僧傳", "M1": "呂澂著作",
}

start = time.time()
rows = []
canons = sorted(d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d)))
total = sum(len(files) for c in canons
            for _, _, files in os.walk(os.path.join(SRC, c)))
done = 0
errors = []

for canon in canons:
    cdir = os.path.join(SRC, canon)
    if not os.path.isdir(cdir):
        continue
    odir = os.path.join(OUT, canon)
    os.makedirs(odir, exist_ok=True)
    for root, _, files in os.walk(cdir):
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            path = os.path.join(root, fn)
            sid = fn[:-4]  # e.g. T01n0001
            try:
                tree = ET.parse(path)
                rootel = tree.getroot()
                header = rootel.find(f"{TEI}teiHeader")
                title, author, extent, source = "", "", "", ""
                if header is not None:
                    ts = header.find(f"{TEI}fileDesc/{TEI}titleStmt")
                    if ts is not None:
                        for t in ts.findall(f"{TEI}title"):
                            if t.get("level") == "m" and (t.text or "").strip():
                                title = t.text.strip()
                                break
                        if not title:
                            for t in ts.findall(f"{TEI}title"):
                                if (t.text or "").strip() and "No." in t.text:
                                    m = re.search(r"No\.\s*\d+\s*(.+)", t.text)
                                    title = m.group(1).strip() if m else t.text.strip()
                                    break
                        a = ts.find(f"{TEI}author")
                        if a is not None and a.text:
                            author = a.text.strip()
                    ext = header.find(f"{TEI}fileDesc/{TEI}extent")
                    if ext is not None and ext.text:
                        extent = ext.text.strip()
                    bibl = header.find(f"{TEI}fileDesc/{TEI}sourceDesc/{TEI}bibl")
                    if bibl is not None and bibl.text:
                        source = bibl.text.strip()
                body = rootel.find(f"{TEI}text/{TEI}body")
                out = []
                if body is not None:
                    render(body, out)
                text = clean("".join(out))
                if not text:
                    done += 1
                    continue
                # 标题兜底
                if not title:
                    title = sid
                fname = f"{sid}_{re.sub(r'[\\/:*?\"<>|]', '', title)[:40]}.txt"
                fpath = os.path.join(odir, fname)
                canon_full = canon_names.get(canon, canon)
                with open(fpath, "w", encoding="utf-8") as w:
                    w.write(f"《{title}》\n")
                    w.write(f"出處：{canon_full}（{sid}）\n")
                    if author:
                        w.write(f"譯著：{author}\n")
                    if extent:
                        w.write(f"卷數：{extent}\n")
                    w.write("────────────────────\n\n")
                    w.write(text + "\n\n")
                    w.write("────────────────────\n")
                    w.write("資料來源：CBETA 中華電子佛典基金會（XML P5），非商業使用\n")
                rows.append((canon, canon_full, sid, title, author, extent,
                             f"经文/{canon}/{fname}", len(text)))
            except Exception as e:
                errors.append((sid, str(e)))
            done += 1
            if done % 500 == 0:
                print(f"[{time.time()-start:6.0f}s] {done}/{total}", flush=True)

with open(CATALOG, "w", encoding="utf-8") as w:
    w.write("部類\t部類名\t經號\t經名\t譯著\t卷數\t文件\t正文字數\n")
    for r in rows:
        w.write("\t".join(r) + "\n")

print(f"DONE {done} files, {len(rows)} sutras, {len(errors)} errors, {time.time()-start:.0f}s")
if errors:
    print("ERRORS:", errors[:10])
