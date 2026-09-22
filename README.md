# 大正藏 · 本地佛经检索 Skill

一个 [WorkBuddy](https://www.workbuddy.ai) AI 助手技能：把 **CBETA 中华电子佛典**全套 5017 部经装进你的电脑，之后对 AI 随口说"这句出自哪部经""《金刚经》怎么讲"，AI 直接检索本地经库，**逐字引用原文、注明出处**，不凭记忆瞎编。

数据全部来自 [CBETA 官方开源仓库](https://github.com/cbeta-org/xml-p5)（法鼓文理学院维护，繁体中文），本仓库只提供"下载 → 转文本 → 检索"的工具链，不含任何经文数据。

## 功能

- 📚 **5017 部经**全文：大正藏(T)、卍续藏(X)、嘉兴藏(J)、高丽藏(K)、南传大藏经(N)、太虚大师全书(YP)、印顺法师著作(Y) 等 26 个部类
- 🔍 **逐字原文检索**：任一句经文，全库定位命中经名 + 上下文
- 📖 **经名目录检索**：按经名查出处、译者、卷数、文件路径
- ✍️ **生僻佛字自动还原**：31661 个 CBETA 缺字按官方对照表转回通用汉字
- 🈶 **繁体原样保存**：经文一字不动，引文保持繁体

## 安装

### 1. 下载 CBETA 官方数据（约 2.5G）

```bash
mkdir -p ~/佛经库 && cd ~/佛经库
git clone --depth 1 https://github.com/cbeta-org/xml-p5.git cbeta-xml
```

### 2. 下载生僻字对照表

```bash
cd ~/佛经库 && mkdir -p 工具
git clone --depth 1 https://github.com/cbeta-org/cbeta_gaiji.git 工具/cbeta_gaiji
```

### 3. 转成干净文本（约 10 分钟）

```bash
cd ~/佛经库
python3 scripts/convert.py        # 从本仓库复制 scripts/ 目录
python3 scripts/build_catalog.py  # 生成总目录 catalog.tsv
```

完成后得到：

```
~/佛经库/
├── cbeta-xml/    CBETA 官方原始数据（底本，保留可支持日后更新）
├── 经文/         干净繁体文本，一部经一个 txt
├── catalog.tsv   全库总目录
└── 工具/         转换脚本与对照表
```

### 4. 安装 Skill 到 WorkBuddy

把本仓库整个目录复制到 WorkBuddy 技能目录：

```bash
cp -r . ~/.workbuddy/skills/dazangjing/
```

如果你的经库不在 `~/佛经库`，设置环境变量（可写入 shell 配置）：

```bash
export CBETA_HOME="/你的/经库/路径"
```

## 使用

装好后对 WorkBuddy AI 说：

- "查佛经：这句'應無所住而生其心'出自哪部经？"
- "《地藏经》原文怎么讲孝顺？"
- "大正藏里有没有讲临终念佛的？"

AI 会自动进入本技能：先检索本地经库 → 逐字引用 → 注明出处（部类+经号）→ 再讲义理。

也可以直接用命令行：

```bash
python3 scripts/search.py "應無所住而生其心"   # 全文检索
python3 scripts/search.py 金剛經 --name        # 按经名查目录
```

## 更新经库

CBETA 有新版时：

```bash
cd ~/佛经库/cbeta-xml && git pull
python3 scripts/convert.py && python3 scripts/build_catalog.py
```

## 目录结构

```
├── SKILL.md                  WorkBuddy 技能定义（触发词、回答规范）
├── scripts/
│   ├── search.py             检索工具（全文/经名）
│   ├── convert.py            CBETA XML → 干净文本转换器
│   └── build_catalog.py      总目录生成器
└── README.md
```

## 许可

- 本仓库代码：MIT
- 佛经数据版权归 [CBETA 中华电子佛典基金会](https://www.cbeta.org) 所有，依其版权宣告**非商业使用**，请遵守

## 致谢

- [CBETA 中华电子佛典基金会](https://www.cbeta.org) —— 数十年的校勘与数字化心血
- [法鼓文理学院 DILA](https://www.dila.edu.tw) —— CBETA Online 与开源数据维护
