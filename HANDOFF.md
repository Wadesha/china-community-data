# 交接文档 HANDOFF

> 本文档面向后续接力的模型或开发者。读完即可独立完成:补数据、换真实数据上线、维护八个页面、续写五部百科卷、发布到 GitHub Pages。**先读 §8 项目哲学再动手**,那是本项目一切取舍的依据。

## 0. 一句话定位

以"小区"为单元的中国城市住宅数据体系:爬取全国安居客小区数据 → 清洗 → 发布为静态专题站点(数据视图 + 体系化概念文本)。**数据是模拟的阶段,框架是真实的阶段。**

两条工作线:

| 线 | 位置 | 状态 |
|---|---|---|
| 数据线(爬取/清洗) | `/Users/wade/Library/CloudStorage/OneDrive-个人/claw/anjuke/` | 真实数据 37.2 万行/333 城,有缺口待补 |
| 站点线(展示/文本) | 同上 `anjuke/site/`(**即本仓库根目录**) | 已上线,GitHub Pages,当前跑模拟数据 |

## 1. 路径速查

```
claw/anjuke/
├── data/
│   ├── anjuke_communities_multi.csv   # ★ 主数据文件(真实,72MB/38.1万行,清洗后37.2万行)
│   ├── 待补数据城市清单.md              # ★ 补数据优先级依据(错标清零城/缺口城/覆盖不足)
│   ├── coverage_assessment.csv         # 覆盖评估
│   └── *.bak_*                         # 各轮清洗的带时间戳备份(勿删)
├── scripts/
│   ├── anjuke_scraper_pw*.py           # Playwright 爬虫多轮版本(pw6 为最新)
│   ├── clear_mislabeled_cities.py      # 错标城市清除(幂等,/tmp 中转防 OneDrive 截断)
│   ├── normalize_city_names.py         # 城市名归一化
│   └── anjuke_pw4_progress.json        # 爬虫断点进度
├── 数据缺口清单.html                    # 缺口可视化报告
└── site/                              # ★ 本仓库(git 根,即 GitHub Pages 根)
    ├── index.html                     # 专题概述:概念框架+字段字典(28项官方来源)
    ├── explorer.html                  # 价格浏览器:省→市→区县下钻(读 communities.json)
    ├── age-price.html                 # 年份×价格:竣工年份段×挂牌中位数曲线(同上)
    ├── history.html                   # 《中国居住建筑史》第一卷:六编四附录(177KB,独立无依赖)
    ├── planning.html                  # 《中国城市规划与区域发展》第二卷:六编四附录(122KB,同体例,先秦—2026)
    ├── landscape.html                 # 《中国近现代城乡风貌》第三卷:六编四附录(125KB,同体例,1840—2026,含识别工具)
    ├── region.html                    # 《中国区域志》第四卷:六编四附录(208KB,同体例,六大区逐地实录,31 省全部地级政区逐省列表)
    ├── hotspot.html                   # 《中国城市热点片区》第五卷:六编四附录(189KB,同体例,2016—2026 被反复谈论的 36 个片区,每条三段式:能看到什么→近几年发生了什么→怎么来的)
    ├── data/communities.json          # ★ 站点数据文件(当前模拟,结构对齐真实 schema)
    ├── tools/generate_sim_data.py     # 模拟数据生成器(seed=20260824 可复现)
    └── README.md                      # 仓库门面(首行即站点链接)
```

## 2. 数据线:真实数据管线

### 2.1 原始 CSV schema(13 列,UTF-8-BOM)

```
City, Name (a), Year Built (b), District (c), Sub-district (d), Road (e),
Nearby (f), Second-hand (h), Rent (i), Other Links (j), Price (k),
Price Change (l), Fetch Date (m)
```

爬虫写入见 `scripts/anjuke_scraper_pw4.py` 第 287-298 行的 keys 映射。

### 2.2 已知数据质量问题(接力前必读)

1. **城市错标 bug(最重要)**:3 月批次中,蚌埠数据被同时写进了 合肥/宿州/常州/烟台/青岛 5 个城市名下(青岛保留 68 行真实数据)。假数据已由 `clear_mislabeled_cities.py` 清除,五城现为 0 或近 0 数据。**重新抓取前必须先排查爬虫的城市归属 bug,否则错误会重演。**
2. 从未抓到数据(只有导航垃圾行):佛山、宁波、温州、邯郸、金华、驻马店。
3. 大城市覆盖不足:上海 16%、重庆 25%、天津 31%;广州/济南/郑州等为"头部样本"(默认排序前约 1250 条)。
4. 完整缺口明细与补数顺序:见 `data/待补数据城市清单.md` 末节。

### 2.3 清洗约定(踩过的坑)

- **OneDrive 同步截断**:数据文件在 OneDrive 目录内,直接原地写大文件可能被同步进程截断。所有清洗脚本必须走 `/tmp` 中转 → `os.remove` 原文件 → `copy2` 回来。新写清洗脚本照抄 `clear_mislabeled_cities.py` 的模式。
- 每轮清洗前自动留 `*.bak_YYYYMMDD_HHMMSS` 备份。
- 清洗幂等:重复运行结果不变。
- CSV 读写必须 `encoding='utf-8-sig'` + `newline=''`。

## 3. 站点线:架构与数据流

### 3.1 架构决策(勿推翻)

- **零依赖纯静态**:无框架、无构建步骤、无 node_modules。七个 HTML + 一个 JSON,`python3 -m http.server` 即可本地预览。
- **history.html / planning.html / landscape.html / region.html / hotspot.html 完全自包含**:不读 JSON、无外部资源,单文件可独立打开。planning.html、landscape.html、region.html、hotspot.html 与 history.html 同体例(条目/定义段/技术档案/图版/参见),但**编号独立**——五卷的"图 n-n""档 n-n"互不相涉,校验脚本按文件分开跑。
- 数据页面(explorer/age-price)启动时 `fetch('data/communities.json')`,注意:本地直接双击打开会因 file:// 协议 CORS 失败,**必须起 http 服务**。
- 设计约束:**只用黑白灰、无图标、紧凑布局**(用户明确要求,见 §8)。

### 3.2 站点 JSON schema(explorer/age-price 的消费格式)

```json
{
  "meta": {
    "simulated": true,             // 换真实数据时改 false,并更新 note
    "generated": "2026-08-24",
    "note": "...",
    "fields": "name=小区名 year=竣工年份(可为null) biz=商圈 road=道路 nearby=配套标签 second_hand=二手挂牌量 rent=租房挂牌量 price=挂牌均价(元/m²) price_change=涨跌 fetch=抓取日期"
  },
  "provinces": [{
    "name": "江苏", "type": "省",   // type: 省|直辖市
    "cities": [{
      "name": "苏州", "tier": "二线", // tier: 一线|二线|三线|县级市|省直辖县级市
      "districts": [{
        "name": "姑苏", "kind": "core", "kind_cn": "核心区",
        // kind: core|sub|urban|near|far|county|cl(县级市代管)|town(街道/直筒子市)
        "communities": [{
          "name": "和平华庭", "year": 2011, "biz": "东城公园",
          "road": "中山路199号", "nearby": "三环以外、配套齐全",
          "second_hand": 5, "rent": 1, "price": 76700,
          "price_change": -0.2, "fetch": "2026-08-24"
        }]
      }]
    }]
  }]
}
```

聚合口径(两页面共用,勿改):**挂牌中位数**(挂牌价≠成交价,右偏分布,中位数稳健);缺失即缺失,**不插补**——无年份小区不进年份分析,无价格不计入价格统计。

### 3.3 换真实数据上线(标准接力任务)

写一个转换脚本(建议放 `tools/csv_to_json.py`,尚未创建):读 `../data/anjuke_communities_multi.csv` → 按上节 schema 聚合 → 覆盖 `data/communities.json`。要点:

1. `Price (k)` 为空或非数字 → `price: null`(不进统计);
2. `Year Built (b)` 空/非 4 位数字 → `year: null`;
3. District/Sub-district 两个粒度都有:当前 schema 只用 `District (c)`(区县级),Sub-district(商圈/街道)可进 `biz` 字段;
4. 城市归属以爬虫批次 fetch 日期 + 待补清单 §1 排查结果双重校验;
5. 生成后跑一遍三个页面人工抽查(错标 bug 的教训)。

数据量大时注意:全量 37 万小区的 JSON 会很大,GitHub Pages 单文件建议 <10MB。可按省拆分或先做城市级聚合(站点两个视图其实只需要区县级聚合 + 明细,评估后再定)。

## 4. 百科卷:体例与编号系统(history.html / planning.html / landscape.html / region.html / hotspot.html)

五卷均为单文件自包含百科体例:凡例 → 总纲(分期框架) → 六编 → 四附录(A 术语表 / B 参考来源 / C 总年表 / D 图版与档案目录)。卷一《中国居住建筑史》(177KB)回答"房子长什么样";卷二《中国城市规划与区域发展》(122KB,先秦—2026)回答"城市怎么被组织起来",以规划权归属/编制依据/规划对象三项制度变量断代;卷三《中国近现代城乡风貌》(125KB,1840—2026)回答"眼前这块风貌是什么时候、被谁、按什么规则造出来的",以建造主体/资金来源/规则依据三变量整体换代分四期,城市乡村双线并观,第六编与附录为识别工具(建筑年代五维鉴定、街道剖面法);卷四《中国区域志》(208KB)回答"具体的地方长什么样",按六大行政区(华北/东北/华东/中南/西南/西北)逐地实录,先现象后成因,不立新概念、只用现行通名与真实地名,每编结构固定为"直辖市与省会实录 → 地级市实录 → 县城实录 → 乡村实录",六张逐省实录表覆盖内地 31 个省级政区的全部地级政区;卷五《中国城市热点片区》(189KB,2016—2026)回答"近几年大家谈论的小地方是哪里、为什么是它们",收三十六个片区按驱动机制分六编(滨水更新/总部集聚/科学城/制度合作区/新中心/存量再生),每条固定三段式"能看到什么→近几年发生了什么→怎么来的",时间截至 2026 年 8 月,运营数据随文标注口径。维护前必读:

### 4.1 编号系统(增量维护的核心约束)

**五卷编号完全独立**:卷二的"图 1-1"与卷一的"图 1-1"互不相涉,卷三、卷四、卷五亦然。跨卷引用写明"→卷一 档 3-2"这类带卷号的形式,不能用裸编号。

| 编号 | 格式 | 卷一 history.html 分配 | 卷二 planning.html 分配 | 卷三 landscape.html 分配 | 卷四 region.html 分配 | 卷五 hotspot.html 分配 |
|---|---|---|---|---|---|
| 图版 | `图 n-n`(n=编次) | 图 1-1…1-2, 2-1, 3-1…3-2, 5-1…5-4,共 9 幅(第四编无图版) | 图 1-1…1-2, 2-1, 3-1, 4-1, 5-1…5-2, 6-1…6-2,共 9 幅 | 图 1-1…1-2, 2-1, 3-1…3-2, 4-1, 5-1, 6-1…6-2,共 9 幅 | 图 1-1…1-2, 2-1…2-2, 3-1…3-2, 4-1…4-2, 5-1, 6-1,共 10 幅 | 图 0-1(总纲)+ 1-1…1-2, 2-1, 3-1, 4-1…4-2, 5-1, 6-1…6-2,共 10 幅 |
| 技术档案 | `档 n-n` | 档 1-1…1-4, 2-1, 3-1…3-2, 6-1…6-7,共 14 卷(第五编无档案) | 档 1-1, 3-1, 4-1, 5-1…5-2, 6-1,共 6 卷(第二编无档案) | 档 1-1, 2-1, 3-1…3-2, 4-1, 5-1, 6-1,共 6 卷 | 档 1-1…1-2, 2-1, 3-1…3-2, 4-1…4-2, 5-1, 6-1…6-2,共 10 卷 | 档 1-1, 2-1, 3-1, 4-1…4-2, 5-1, 6-1,共 7 卷 |
| 正文引用 | `[n]` | 1–65 连续 | 1–11 连续(制度文本与通史著作为纲,多数无 URL) | 1–12 连续(保护名录、村落名录、普查统计、更新政策为纲) | 1–13 连续(区划简册、新区批复、开发区目录、城市群纲要为纲) | 1–43 连续(官方发布与主流媒体报道为纲,时间截至 2026-08) |

硬规则:**每条附录 B 来源必须有正文上标对应,不允许"只列不用"**。已验证:卷一 65/65、卷二 11/11、卷三 12/12、卷四 13/13、卷五 43/43 全部被引用。

### 4.2 术语表(附录 A)

按拼音序插入(`<div class="lemma">`),新词条须带交叉引用(→图/档/§)。五卷各 32 条。

### 4.3 目录(左侧 nav.toc)

新章节需同步:导航 `<a href="#id">` + 正文 `<div class="sec" id="...">` 或 `<div class="vol" id="...">`。滚动高亮脚本按 id 匹配。

### 4.4 修改后必跑的校验(三个都要过,五卷各跑一遍)

```bash
cd /Users/wade/Library/CloudStorage/OneDrive-个人/claw/anjuke/site
# 把下面三段里的 history.html 换成 planning.html / landscape.html / region.html / hotspot.html 再各跑一遍即为卷二至卷五校验

# 1. 标签配平
env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3 -c "
import re,io
s=io.open('history.html',encoding='utf-8').read()
ok=True
for t in ['div','table','tr','td','th','p','span','h2','h3','h4','ol','li','sup','b','footer','main','nav','body','html']:
    o=len(re.findall(r'<'+t+r'(?=[ >])',s)); c=len(re.findall(r'</'+t+r'>',s))
    if o!=c: print(f'{t}: MISMATCH {o}/{c}'); ok=False
print('配平:' , 'OK' if ok else 'FAIL')"

# 2. 引用完整性(每个来源都被正文引用,无缺号无超号)
env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3 -c "
import re,io
s=io.open('history.html',encoding='utf-8').read()
body=s[:s.find('<ol class=\"src\">')]
used=set()
for m in re.finditer(r'class=\"ref\">((?:\[[0-9]+\])+)<',body):
    for n in re.findall(r'\[([0-9]+)\]',m.group(1)): used.add(int(n))
nli=len(re.findall(r'<li>',s))
missing=[i for i in range(1,nli+1) if i not in used]
print('来源条数',nli,'未引用:',missing if missing else '无,OK')"

# 3. 页内锚点
env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3 -c "
import re,io
s=io.open('history.html',encoding='utf-8').read()
ids=set(re.findall(r'id=\"([a-z0-9]+)\"',s))
hrefs=set(re.findall(r'href=\"#([a-z0-9]+)\"',s))
print('未解析锚点:',hrefs-ids if hrefs-ids else '无,OK')"
```

### 4.5 内容红线

- **不写行情数据**("某年某城房价涨跌"一类)。价格随月失效,制度与建筑形态的演变不会——这是本卷的立卷理由,写在凡例里。
- 分期断代用"制度断代"(住房制度变革),不用政权更迭。
- 技术档案数值是"类型通行区间",非单案数值;图版均为示意,不按比例。

## 5. 发布流程

```bash
cd "/Users/wade/Library/CloudStorage/OneDrive-个人/claw/anjuke/site"
git add -A && git commit -m "<中文 commit,feat/docs 前缀>"
git push        # 凭据走 macOS 钥匙串(osxkeychain),无需配置
```

- 仓库:https://github.com/Wadesha/china-community-data(private=false)
- 站点:https://wadesha.github.io/china-community-data/(Pages: Deploy from branch → main/root)
- 部署约 1 分钟,验证:`curl -s -o /dev/null -w "%{http_code}" https://wadesha.github.io/china-community-data/`
- commit 信息风格沿用现有两条:中文短句 + feat:/docs: 前缀。
- **Token 注意**:GitHub 凭据存在钥匙串,remote URL 里**不放 token**。此前记忆里"token 存 remote URL"的说法已过时(那是另一个仓库 wadez.asia)。勿在任何文件中落盘 token。

## 6. 环境坑(macOS 12.7.6)

| 问题 | 解法 |
|---|---|
| 系统 python3 报 `Symbol not found: (_mkfifoat)` | 一律用 `env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3` |
| node 报 dyld Symbol not found | 不要用 node 做校验,用上面配平脚本 |
| 未装 gh CLI | GitHub API 用 curl + 钥匙串 token:`printf "protocol=https\nhost=github.com\n" \| git credential fill` |
| 本地双击 HTML 白屏 | file:// 下 fetch JSON 被 CORS 拦,`python3 -m http.server 8000` 起服务访问 |
| OneDrive 大文件写入截断 | 见 §2.3,/tmp 中转 |

## 7. 当前进度快照(2026-08-24)

- [x] 数据爬取 38.1 万行/333 城(真实,有缺口)
- [x] 错标五城清除(合肥/宿州/常州/烟台/青岛 → 0 数据,待重抓)
- [x] 站点八页面完成,模拟数据(10 省/32 城/3798 小区)
- [x] history.html 全卷完成:六编 + 术语表32条 + 来源65条 + 总年表44事 + 图版档案目录
- [x] planning.html 全卷完成(2026-08-24):六编(营国与里坊/近代市政转型/计划经济规划/恢复与土地革命/城市化加速/国土空间规划)+ 22 条目 + 图版9 + 档案6 + 术语32 + 来源11 + 总年表;六页 topnav 互链、index §8 三卷导览
- [x] landscape.html 全卷完成(2026-08-24):六编(近代输入/单位建造/市场建造/保护名录与管控/当代乡村/当代城市与识别谱系)+ 图版9 + 档案6 + 术语32 + 来源12 + 总年表;起点即 1840 不写古代,第六编与附录为识别工具(年代鉴定五维法、街道剖面法、乡村四代谱系)
- [x] region.html 全卷完成(2026-08-24):六编(华北/东北/华东/中南/西南/西北)+ 62 条目 + 图版10 + 档案10 + 术语32 + 来源13 + 总年表;六大区逐地实录、先现象后成因、只用现行通名与真实地名,六张逐省实录表覆盖 31 省级政区全部地级政区;张江/光谷/天府/西安高新四档案为"政策区"主线;七页 topnav 互链、index §8 四卷导览
- [x] hotspot.html 全卷完成(2026-08-25):六编(滨水更新/总部集聚/科学城/制度合作区/新中心/存量再生)+ 36 条目(徐汇滨江/杨浦滨江/北外滩/苏州河/世博文化公园/亮马河/白鹅潭/深超总/前滩/琶洲/交子/丽泽/张江/光谷/怀柔/松山湖/合肥滨湖/横琴/前海/河套/临港/南沙/海南/雄安/杭州奥体/骆岗/天府/济南起步区/张园/首钢园/隆福寺/永庆坊/东郊记忆/十八梯/南头古城/烟台山)+ 图版10(含图 0-1 总纲矩阵)+ 档案7 + 术语32 + 来源43 + 总年表;每条三段式"能看到什么→近几年发生了什么→怎么来的";八页 topnav 互链、index §8 五卷导览
- [x] 发布 GitHub Pages,入口 200 验证通过
- [ ] **补数据**:按待补清单优先级(错标五城 > 从未抓到六城 > 覆盖不足)
- [ ] **csv_to_json.py**:真实数据 → communities.json(§3.3)
- [ ] 重抓前排查爬虫城市归属 bug(§2.2.1)

## 8. 项目哲学与用户约束(接力模型必读)

1. **体系化 > 时效数据**:用户多次明确排斥行情统计/月度报告("过时了就没用了")。要回答的是"这个东西到底是什么":小区是什么、挂在哪、价格是什么数字、不同年代建的是什么、给谁建的。任何"最新数据/权威统计"倾向的产出都会被退回。
2. **叙述性 > 死板问答**:history.html 从叙事散文被推翻重写为百科全书体,但保留了故事性(样本、引语、观念史)。不要写成 Q&A 或数据报告。
3. **视觉与版式 = 四参照系**(用户明确定义,各管一层):
   - **DK 百科 → 信息密度**:图版是信息本体而非配图;注释引线直指图上部位;图文各半;每页自成完整信息单元
   - **大英百科 → 条目结构**:词条+学科归属+分层释义+交叉引用("参见")+术语表/附录体系;内容是可检索的知识组织,不是文章
   - **建筑事务所 → 版式纪律**:严格网格、编号文化(图版号/档案号/图纸号)、线稿图纸感、大开本留白与密排交替
   - **麦肯锡报告 → 叙述逻辑**:金字塔原理、结论先行、每节有 takeaway、结构化编号、图表驱动论证
   黑白灰、无图标、紧凑只是这四者蒸馏出的**表层约束**,不是风格的全部。任何新内容先问:这一层(密度/结构/版式/叙述)分别对标哪个参照系。
4. **不做 KPI、不设指标要求**。
5. 中文交流;用户语气直率,对齐需求即可,不必过度确认。

## 9. 常见接力任务速查

| 任务 | 步骤 |
|---|---|
| 补抓某城市 | 排查城市归属 bug → 跑 `anjuke_scraper_pw6.py`(先 update_cookie) → 数据追加主 CSV → 更新待补清单 |
| 真实数据上线 | 写 csv_to_json.py(§3.3)→ 替换 communities.json → meta.simulated=false → 三页抽查 → commit+push |
| 新增词条/图版/档案 | 按 §4.1 编号 → 附录 A/C/D 同步 → 跑三个校验 → push |
| 新页面 | 复制任一现有页的 header/topnav 结构 → topnav 七页互链同步更新 → README 表格补行 |
| 改聚合口径 | **不要改**。中位数+不插补是写进口径说明的约定,改了须同步三处口径文本 |
