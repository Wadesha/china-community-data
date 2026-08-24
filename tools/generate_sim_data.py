#!/usr/bin/env python3
# 生成模拟小区数据:结构对齐真实 schema(城市/小区名/竣工年份/区县/商圈/道路/配套/二手/租房/挂牌均价/涨跌/抓取日期)
# 层级与命名遵循真实概念体系:行政区划四级、专名+通名、单位家属院、分期大盘等
import json, random, os

random.seed(20260824)

# (省, 类型, [(城市, 能级, 挂牌基准价, [(区县, 类型)]), ...])
# 区县类型: core核心区 / sub次核心 / urban主城普通 / near近郊 / far远郊 / county县 / cl县级市(代管) / town街道(县级市或直筒子市下)
DATA = [
    ("北京", "直辖市", [
        ("北京", "一线", 58000, [("东城","core"),("西城","core"),("朝阳","urban"),("海淀","sub"),("丰台","urban"),("石景山","urban"),("通州","near"),("昌平","near"),("大兴","near"),("密云","county")])
    ]),
    ("上海", "直辖市", [
        ("上海", "一线", 56000, [("黄浦","core"),("徐汇","core"),("静安","core"),("浦东","urban"),("闵行","urban"),("宝山","near"),("嘉定","near"),("崇明","county")])
    ]),
    ("广东", "省", [
        ("深圳", "一线", 60000, [("福田","core"),("罗湖","sub"),("南山","core"),("宝安","urban"),("龙岗","urban"),("龙华","near"),("坪山","far")]),
        ("广州", "一线", 33000, [("天河","core"),("越秀","core"),("海珠","sub"),("荔湾","urban"),("白云","urban"),("黄埔","near"),("番禺","near"),("增城","far")]),
        ("佛山", "二线", 13500, [("禅城","core"),("南海","urban"),("顺德","urban"),("三水","near"),("高明","far")]),
        ("东莞", "二线", 15000, [("南城","core"),("东城","sub"),("莞城","urban"),("松山湖","near"),("虎门","town"),("长安","town")]),
        ("汕头", "三线", 8500, [("金平","core"),("龙湖","sub"),("澄海","near"),("潮阳","far"),("潮南","far")])
    ]),
    ("江苏", "省", [
        ("南京", "二线", 29000, [("玄武","core"),("秦淮","core"),("鼓楼","sub"),("建邺","sub"),("江宁","near"),("浦口","near"),("六合","far"),("溧水","far")]),
        ("苏州", "二线", 27000, [("姑苏","core"),("虎丘","sub"),("吴中","urban"),("相城","near"),("吴江","near"),("常熟","cl"),("昆山","cl")]),
        ("无锡", "二线", 19000, [("梁溪","core"),("锡山","urban"),("惠山","urban"),("滨湖","sub"),("新吴","near"),("江阴","cl")]),
        ("南通", "三线", 10000, [("崇川","core"),("通州","near"),("如皋","cl"),("启东","cl")]),
        ("昆山", "县级市", 18000, [("玉山","town"),("花桥","town"),("周市","town"),("张浦","town")])
    ]),
    ("浙江", "省", [
        ("杭州", "二线", 32000, [("上城","core"),("拱墅","sub"),("西湖","sub"),("滨江","urban"),("萧山","near"),("余杭","near"),("临平","far"),("富阳","far")]),
        ("宁波", "二线", 21000, [("海曙","core"),("鄞州","sub"),("江北","urban"),("镇海","near"),("北仑","near"),("慈溪","cl")]),
        ("温州", "三线", 12000, [("鹿城","core"),("龙湾","urban"),("瓯海","urban"),("乐清","cl")]),
        ("义乌", "县级市", 17500, [("稠城","town"),("福田","town"),("江东","town"),("北苑","town")])
    ]),
    ("山东", "省", [
        ("济南", "二线", 15000, [("历下","core"),("市中","sub"),("槐荫","urban"),("天桥","urban"),("历城","near"),("长清","far"),("章丘","cl")]),
        ("青岛", "二线", 14000, [("市南","core"),("市北","sub"),("李沧","urban"),("崂山","sub"),("城阳","near"),("黄岛","near"),("即墨","cl")]),
        ("烟台", "三线", 9000, [("芝罘","core"),("福山","urban"),("牟平","far"),("莱山","sub"),("龙口","cl")]),
        ("临沂", "三线", 8000, [("兰山","core"),("罗庄","near"),("河东","near"),("沂水","county")])
    ]),
    ("河南", "省", [
        ("郑州", "二线", 13500, [("中原","urban"),("二七","sub"),("金水","core"),("管城","urban"),("惠济","near"),("新郑","cl")]),
        ("洛阳", "三线", 8200, [("老城","core"),("西工","sub"),("瀍河","urban"),("涧西","urban"),("洛龙","near"),("偃师","cl")]),
        ("南阳", "三线", 6800, [("卧龙","core"),("宛城","sub"),("镇平","county")]),
        ("济源", "省直辖县级市", 5800, [("沁园","town"),("济水","town"),("北海","town"),("天坛","town")])
    ]),
    ("四川", "省", [
        ("成都", "二线", 16000, [("锦江","core"),("青羊","core"),("金牛","urban"),("武侯","sub"),("成华","urban"),("龙泉驿","near"),("双流","near"),("郫都","near")]),
        ("绵阳", "三线", 7000, [("涪城","core"),("游仙","urban"),("安州","far"),("江油","cl")]),
        ("宜宾", "三线", 6800, [("翠屏","core"),("南溪","near"),("叙州","urban")])
    ]),
    ("湖北", "省", [
        ("武汉", "二线", 15500, [("江岸","core"),("江汉","core"),("硚口","urban"),("汉阳","sub"),("武昌","core"),("青山","urban"),("洪山","sub"),("东西湖","near"),("黄陂","far")]),
        ("宜昌", "三线", 7000, [("西陵","core"),("伍家岗","sub"),("点军","far"),("猇亭","far"),("夷陵","near")]),
        ("仙桃", "省直辖县级市", 5600, [("干河","town"),("龙华山","town"),("沙嘴","town")])
    ]),
    ("陕西", "省", [
        ("西安", "二线", 14500, [("新城","core"),("碑林","core"),("莲湖","sub"),("雁塔","sub"),("未央","urban"),("灞桥","near"),("长安","near")]),
        ("宝鸡", "三线", 6000, [("渭滨","core"),("金台","sub"),("陈仓","near")])
    ]),
]

DIST_MULT = {"core":1.35,"sub":1.15,"urban":1.00,"near":0.80,"far":0.65,"county":0.60,"cl":0.72,"town":1.00}
DIST_KIND_CN = {"core":"核心区","sub":"次核心区","urban":"主城区","near":"近郊区","far":"远郊区","county":"县","cl":"县级市(代管)","town":"街道/镇"}
# 各类型区县的小区数量区间
DIST_COUNT = {"core":(26,40),"sub":(20,32),"urban":(16,28),"near":(10,20),"far":(8,15),"county":(8,14),"cl":(10,18),"town":(8,16)}

ZHUAAN = ["翠湖","金色","阳光","望江","临江","锦绣","翡翠","梧桐","紫金","龙潭","滨河","学府","幸福","和平","明珠","星河","云顶","江湾","春晓","御景","中央","东方","南山","北岸","天鹅","凤凰","玉兰","丹桂","香樟","水岸","桃源","上城","天悦","国宾","青秀","丹霞","白鹭","紫薇","迎泽"]
TONGMING_OLD = ["苑","园","小区","花园","家园","新村","嘉园","名邸","公寓"]
TONGMING_MID = ["华庭","公馆","湾","府","城","郡","上城","天地"]
TONGMING_NEW = ["云筑","天著","壹号","九里","印","序","玖著","青云台"]
BRAND = ["万科","保利","龙湖","华润","绿城","中海","融创","金地","招商","越秀"]
UNIT = ["纺织厂","机械厂","铁路","邮电","电力","化肥厂","食品厂","运输公司","棉纺厂","钢厂","自来水公司","粮食局","人民医院","一中","工商银行"]

BIZZ = ["广场","公园","大学城","步行街","老街","CBD","站","码头","桥","体育场","会展中心","湖","古城"]
ROAD = ["建设路","人民路","中山路","解放路","和平路","光明街","育才街","工业路","滨河路","长江路","黄河路","昆仑路","学府街","朝阳街","永安街","长虹路"]
NEARBY = ["地铁1号线","地铁2号线","地铁3号线","配套齐全","小户型居多","二环以内","三环以外","近学校","近公园","临江","临湖","近商圈","次新房","满五唯一多"]

def year_mult(y):
    if y <= 1985: base = 0.50
    elif y <= 1995: base = 0.50 + (y-1985)/10*0.15
    elif y <= 2005: base = 0.65 + (y-1995)/10*0.15
    elif y <= 2015: base = 0.80 + (y-2005)/10*0.25
    elif y <= 2020: base = 1.05 + (y-2015)/5*0.10
    else: base = 1.15 + min((y-2020)/5*0.08, 0.08)
    return base

def make_name(year, rng):
    r = rng.random()
    if year <= 1998 and r < 0.55:
        return rng.choice(UNIT) + rng.choice(["家属院","宿舍","生活区"])
    if year <= 2010:
        return rng.choice(ZHUAAN) + rng.choice(TONGMING_OLD)
    if year <= 2018:
        return rng.choice(ZHUAAN) + rng.choice(TONGMING_MID)
    if r < 0.6:
        return rng.choice(BRAND) + rng.choice(["·",""]) + rng.choice(ZHUAAN) + rng.choice(TONGMING_NEW)
    return rng.choice(ZHUAAN) + rng.choice(TONGMING_MID)

def gen_district(prov, city, dist_name, kind, base, rng, city_note):
    lo, hi = DIST_COUNT[kind]
    n = rng.randint(lo, hi)
    # 商圈:每区县 3-5 个
    biz = rng.sample(BIZZ, rng.randint(3,5))
    biz = [dist_name + b for b in biz]
    names = set()
    comms = []
    while len(comms) < n:
        year = rng.choices([rng.randint(1980,1998), rng.randint(1999,2010), rng.randint(2011,2018), rng.randint(2019,2025)], weights=[22,30,28,20])[0]
        name = make_name(year, rng)
        if name in names: continue
        names.add(name)
        mult = DIST_MULT[kind]
        # 核心区老房价格韧性(地段/学区)
        if kind in ("core","sub") and year < 2000:
            mult *= rng.uniform(1.10, 1.35)
        price = base * mult * year_mult(year) * rng.uniform(0.82, 1.18)
        price = max(1800, int(round(price/50.0)*50))
        sh = max(0, int(rng.gauss(18, 12)))
        rent = max(0, int(sh * rng.uniform(0.2, 0.7)))
        chg = round(rng.gauss(-0.35, 0.65), 2)
        nb = "、".join(rng.sample(NEARBY, rng.randint(1,3)))
        road = rng.choice(ROAD) + str(rng.randint(1, 399)) + "号"
        has_year = rng.random() > 0.30  # 30% 缺竣工年份,对齐真实数据形态
        comms.append({
            "name": name,
            "year": year if has_year else None,
            "biz": rng.choice(biz),
            "road": road,
            "nearby": nb,
            "second_hand": sh,
            "rent": rent,
            "price": price,
            "price_change": chg,
            "fetch": "2026-08-24"
        })
    return {"name": dist_name, "kind": kind, "kind_cn": DIST_KIND_CN[kind], "communities": comms}

def main():
    out = {"meta": {
        "simulated": True,
        "generated": "2026-08-24",
        "note": "模拟数据:用于专题框架演示。层级、命名、字段结构对齐真实抓取 schema,数值为模拟生成,不代表任何真实小区。",
        "fields": "name=小区名 year=竣工年份(可为空) biz=商圈 road=道路 nearby=配套标签 second_hand=二手挂牌量 rent=租房挂牌量 price=挂牌均价(元/m²) price_change=价格变动 fetch=抓取日期"
    }, "provinces": []}
    total = 0
    for prov, ptype, cities in DATA:
        p = {"name": prov, "type": ptype, "cities": []}
        for city, tier, base, districts in cities:
            c = {"name": city, "tier": tier, "districts": []}
            for dname, kind in districts:
                d = gen_district(prov, city, dname, kind, base, random, tier)
                total += len(d["communities"])
                c["districts"].append(d)
            p["cities"].append(c)
        out["provinces"].append(p)
    path = os.path.join(os.path.dirname(__file__), "..", "data", "communities.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"provinces={len(out['provinces'])} communities={total} size={os.path.getsize(path)//1024}KB")

if __name__ == "__main__":
    main()
