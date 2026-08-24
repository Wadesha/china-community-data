# 中国城市小区数据体系 · 专题一

以"小区"为单元的中国城市住宅数据专题:先把数据世界里的每个概念说清楚(小区是什么、挂在哪里、价格和年份是什么数字),再做两个结构性分析视图。

## 页面结构

| 文件 | 内容 |
|---|---|
| `index.html` | 专题概述:概念框架与字段字典(小区本体 / 行政区划 / 价格概念 / 竣工年份 / 住房类型 / 字段字典 / 口径局限),全部注明官方来源 |
| `explorer.html` | 价格浏览器:省 → 城市 → 区县逐级下钻,区县级给出小区数、挂牌中位数、P25–P75、区内最高挂牌 |
| `age-price.html` | 年份 × 价格:按竣工年份段(5 年)统计城市挂牌中位数,SVG 曲线 + 分位带 + 明细表 |
| `data/communities.json` | 数据文件(当前为模拟数据,结构对齐真实抓取 schema) |
| `tools/generate_sim_data.py` | 模拟数据生成脚本 |

## 当前状态:模拟数据阶段

`data/communities.json` 目前是**结构对齐的模拟数据**(10 省 / 45 城市 / 约 3800 小区),用于固化框架:

- 层级对齐真实行政区划体系(含直辖市、省直辖县级市、县级市、直筒子市镇街等特殊形态)
- 小区命名按"专名 + 通名"体系生成(单位家属院 / 苑园 / 府湾 / 品牌系)
- 字段与缺失形态对齐真实抓取(约 30% 无竣工年份、挂牌均价口径)

真实数据接入后,只需替换 `communities.json` 为相同结构的文件,三个页面无需改版。

## 数据 schema

```
{ meta: { simulated, generated, note, fields },
  provinces: [ { name, type,
    cities: [ { name, tier,
      districts: [ { name, kind, kind_cn,
        communities: [ { name, year|null, biz, road, nearby,
                          second_hand, rent, price, price_change, fetch } ] } ] } ] } ] }
```

字段语义、口径与解读边界见 `index.html` §6 字段字典。

## 统计口径

- 聚合一律用**挂牌中位数**(挂牌价≠成交价,分布右偏,中位数稳健)
- 缺失即缺失,不插补:无竣工年份的小区不进入年份分析,"暂无均价"不计入价格统计
- 每行数据携带抓取日期,混合批次按快照区分

## 本地预览

```bash
cd site
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 发布(GitHub Pages)

本目录可作为独立仓库根目录:

```bash
git init && git add -A && git commit -m "init: 专题一 · 概念框架 + 模拟数据演示"
git remote add origin git@github.com:Wadesha/<repo>.git
git push -u origin main
# 仓库 Settings → Pages → Deploy from branch → main / root
```

## 口径与局限(摘录)

挂牌价非成交价;多数城市为平台头部样本;多批次时间快照;覆盖缺口如实标注;历史批次存在城市错标需按 URL 域名清洗。详见 `index.html` §8。

## 来源

概念框架的全部法律、标准、政府文件来源列于 `index.html` §9(共 28 项),包括 GB 50180-2018、《物业管理条例》及各省实施办法、《不动产登记暂行条例实施细则》、《地名管理条例》、《城市房地产管理法》、《民法典》第 359 条、民政部行政区划统计等。
