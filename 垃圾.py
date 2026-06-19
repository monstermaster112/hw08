# -*- coding: utf-8 -*-
"""
垃圾分类智能识别系统 v1.0
支持：精确查询 / 模糊匹配 / 关键词规则识别 / 交互式查询
"""
import sys
import re
import os

CATEGORIES = {
    "recyclable": {"name": "可回收物", "color": "蓝", "icon": "\U0001F4E6",
                   "desc": "适宜回收循环利用的废弃物：废纸、塑料、金属、玻璃、织物等"},
    "hazardous":  {"name": "有害垃圾", "color": "红", "icon": "\u2623\ufe0f",
                   "desc": "含重金属/有毒物质的废弃物：电池、灯管、药品、油漆等"},
    "kitchen":    {"name": "厨余垃圾", "color": "绿", "icon": "\U0001F342",
                   "desc": "易腐烂的生物质废弃物：剩饭、果皮、菜叶、茶叶渣等"},
    "other":      {"name": "其他垃圾", "color": "灰", "icon": "\U0001F5F1\ufe0f",
                   "desc": "以上三类之外的废弃物：纸巾、烟蒂、陶瓷、尘土等"},
}
ITEMS = {
    "废纸":     ("recyclable", "旧报纸、书本纸、包装纸盒、纸箱、打印纸等未被污染的纸制品"),
    "纸箱":     ("recyclable", "快递纸箱、包装纸箱等，需清空内容物并压扁投放"),
    "报纸":     ("recyclable", "旧报纸、杂志、宣传单页等干净纸张"),
    "杂志":     ("recyclable", "旧杂志、画册、本子等纸质读物"),
    "书本":     ("recyclable", "旧课本、图书、笔记本等纸制品"),
    "书籍":     ("recyclable", "旧书籍、教材、工具书等"),
    "纸盒":     ("recyclable", "牛奶盒、饮料盒、快递盒等纸质包装盒"),
    "纸袋":     ("recyclable", "纸质购物袋、礼品袋等干净纸张"),
    "废纸板":   ("recyclable", "纸板箱、瓦楞纸板等纸质包装材料"),
    "牛奶盒":   ("recyclable", "牛奶包装盒，纸塑复合材质，需清空冲洗后投放"),
    "塑料瓶":   ("recyclable", "饮料瓶、矿泉水瓶、洗发水瓶等塑料容器，需清空冲洗后投放"),
    "废塑料":   ("recyclable", "废塑料制品：塑料瓶、塑料桶、塑料椅等"),
    "塑料桶":   ("recyclable", "塑料水桶、油桶等"),
    "塑料袋":   ("recyclable", "干净的塑料袋、购物袋等塑料薄膜制品"),
    "易拉罐":   ("recyclable", "铝制饮料罐、啤酒罐等金属罐体"),
    "废金属":   ("recyclable", "废铁、铜、铝等金属制品：易拉罐、金属瓶盖、罐头盒等"),
    "废铁":     ("recyclable", "铁制工具、铁罐、铁丝等"),
    "废铜":     ("recyclable", "铜线、铜管、铜制品等"),
    "旧衣服":   ("recyclable", "废弃衣物：T恤、裤子、外套等纺织品"),
    "旧鞋子":   ("recyclable", "废弃鞋子、拖鞋、运动鞋等"),
    "旧包包":   ("recyclable", "废弃背包、手提包、帆布袋等"),
    "旧床单":   ("recyclable", "废弃床单、被套、枕套等家用纺织品"),
    "旧毛巾":   ("recyclable", "废弃浴巾、毛巾、抹布等棉质织物"),
    "旧毛绒玩具":("recyclable", "废弃毛绒公仔、布偶等织物类玩具"),
    "玻璃瓶":   ("recyclable", "酒瓶、酱料瓶、化妆品瓶等玻璃容器"),
    "玻璃杯":   ("recyclable", "废弃玻璃水杯、酒杯等"),
    "旧手机":   ("recyclable", "废弃手机及配件，可回收贵金属"),
    "充电器":   ("recyclable", "废弃手机充电器、电源适配器等"),
    "充电宝":   ("recyclable", "充电宝含有锂电池，建议专门回收"),
    "破袜子":   ("recyclable", "废弃袜子，可回收的纺织品"),
    "废电池":   ("hazardous", "干电池、充电电池、纽扣电池、蓄电池等含重金属元素"),
    "锂电池":   ("hazardous", "手机锂电池、充电宝电池等可充电电池"),
    "纽扣电池": ("hazardous", "手表、计算器、遥控器中使用的纽扣式电池"),
    "废灯管":   ("hazardous", "荧光灯管、节能灯、汞灯等含汞光源"),
    "节能灯":   ("hazardous", "节能灯泡，含微量汞"),
    "废药品":   ("hazardous", "过期药品、变质药品、未清洗的药瓶"),
    "过期药":   ("hazardous", "过期的片剂、胶囊、口服液等药品"),
    "废农药":   ("hazardous", "杀虫剂、除草剂、农药瓶及包装物"),
    "废油漆":   ("hazardous", "油漆、涂料、稀释剂及其容器"),
    "废机油":   ("hazardous", "发动机油、齿轮油等矿物油"),
    "指甲油":   ("hazardous", "指甲油、洗甲水等含化学溶剂的化妆品"),
    "废温度计": ("hazardous", "水银温度计，含重金属汞"),
    "杀虫剂":   ("hazardous", "杀虫气雾剂、蚊香片、蟑螂药等"),
    "过期化妆品":("hazardous", "过期护肤品、彩妆等含化学成分"),
    "老鼠药":   ("hazardous", "鼠药、蟑螂药等有毒杀虫剂"),
    "剩菜":     ("kitchen", "吃剩的饭菜、汤渣等餐厨剩余物"),
    "剩饭":     ("kitchen", "吃剩的米饭、面条、馒头等主食残余"),
    "米饭":     ("kitchen", "吃剩或变质的米饭、粥等谷物制品"),
    "面条":     ("kitchen", "吃剩的面条、米粉、河粉等面食"),
    "面包":     ("kitchen", "过期或变质的面包、蛋糕、饼干等烘焙食品"),
    "果皮":     ("kitchen", "苹果皮、梨皮、香蕉皮、橘子皮等水果表皮"),
    "苹果核":   ("kitchen", "吃剩的苹果核、梨核等果核"),
    "香蕉皮":   ("kitchen", "香蕉外皮，易腐烂的生物质废弃物"),
    "橘子皮":   ("kitchen", "橘子、橙子、柚子的外皮"),
    "西瓜皮":   ("kitchen", "西瓜皮、哈密瓜皮等瓜类果皮"),
    "茶叶渣":   ("kitchen", "泡过的茶叶渣、茶包内容物"),
    "咖啡渣":   ("kitchen", "冲泡过的咖啡粉末、咖啡滤渣"),
    "菜叶":     ("kitchen", "摘剩的青菜叶、白菜叶、菠菜叶等蔬菜残余"),
    "蛋壳":     ("kitchen", "鸡蛋壳、鸭蛋壳、鹅蛋壳等禽蛋外壳"),
    "骨头":     ("kitchen", "鸡骨、鱼骨、猪骨等小型动物骨骼"),
    "鱼骨":     ("kitchen", "鱼刺、鱼骨等"),
    "鸡骨头":   ("kitchen", "鸡骨、鸭骨等禽类骨骼"),
    "虾壳":     ("kitchen", "虾头、虾壳等虾类废弃部分"),
    "蟹壳":     ("kitchen", "螃蟹壳、蟹脚等蟹类外壳"),
    "花生壳":   ("kitchen", "花生外壳、瓜子壳、核桃壳等坚果外壳"),
    "瓜子壳":   ("kitchen", "葵花籽壳、南瓜子壳等"),
    "中药渣":   ("kitchen", "熬煮过的中药残渣"),
    "过期食品": ("kitchen", "过期的糕点、熟食等食品"),
    "玉米芯":   ("kitchen", "吃完玉米后的玉米棒芯"),
    "豆渣":     ("kitchen", "制作豆浆后剩下的豆渣"),
    "花草":     ("kitchen", "枯萎盆栽植物、花园剪下的枝叶"),
    "龙虾壳":   ("kitchen", "小龙虾、龙虾的壳属于厨余垃圾"),
    "卫生纸":   ("other", "使用过的卫生纸、纸巾、湿纸巾等，遇水即溶不宜回收"),
    "餐巾纸":   ("other", "使用过的餐巾纸、厨房用纸、纸手帕等"),
    "纸尿裤":   ("other", "婴儿纸尿裤、成人纸尿裤等一次性卫生用品"),
    "卫生巾":   ("other", "卫生巾、护垫等女性卫生用品"),
    "湿纸巾":   ("other", "使用过的湿巾、消毒湿巾等"),
    "一次性餐具":("other", "一次性筷子、塑料勺叉、打包餐盒等，沾染油污不宜回收"),
    "一次性筷子":("other", "使用过的一次性竹筷、木筷"),
    "快餐盒":   ("other", "沾有油污的外卖塑料餐盒、泡沫餐盒"),
    "保鲜膜":   ("other", "使用过的保鲜膜、保鲜袋等塑料薄膜"),
    "烟蒂":     ("other", "香烟过滤嘴、烟灰等烟草废弃物"),
    "烟头":     ("other", "吸完的香烟烟蒂"),
    "尘土":     ("other", "扫地收集的灰尘、尘埃、碎屑等"),
    "陶瓷碎片": ("other", "破碎的碗碟、花瓶、瓷砖等陶瓷制品"),
    "陶瓷碗":   ("other", "废弃陶瓷碗、盘、杯等餐具"),
    "渣土":     ("other", "装修产生的渣土、碎石等建筑废弃物"),
    "灰烬":     ("other", "炭灰、煤灰、香灰等燃烧残余物"),
    "头发":     ("other", "剪下的头发、掉落的毛发"),
    "创可贴":   ("other", "使用过的创可贴、医用胶带等"),
    "口罩":     ("other", "使用过的一次性口罩、医用口罩等"),
    "棉签":     ("other", "使用过的棉签、棉球等"),
    "尿不湿":   ("other", "使用过的婴儿纸尿裤、成人护理垫等"),
    "宠物粪便": ("other", "猫砂、宠物排泄物等动物废弃物"),
    "猫砂":     ("other", "使用过的猫砂、宠物垫料"),
    "牙签":     ("other", "使用过的牙签、棉线等口腔清洁用品"),
    "吸管":     ("other", "使用过的塑料吸管、纸吸管等"),
    "一次性纸杯":("other", "使用过的一次性纸杯，有塑料涂层不易回收"),
    "脏抹布":   ("other", "被油污污染的抹布，属于其他垃圾"),
    "大棒骨":   ("other", "猪大腿骨、牛棒骨等大型骨骼，不易粉碎"),
    "贝壳":     ("other", "蛤蜊壳、扇贝壳、牡蛎壳等海鲜硬壳"),
    "椰子壳":   ("other", "椰子坚硬外壳，不易腐烂"),
    "榴莲壳":   ("other", "榴莲硬壳，质地坚硬不易处理"),
    "粽叶":     ("other", "包裹粽子的粽叶，因质地较硬不易腐烂"),
}
RULES = [
    # 可回收物
    (r"纸",       "recyclable", "含纸类成分，属于可回收物"),
    (r"书",       "recyclable", "书本杂志属于可回收物"),
    (r"瓶",       "recyclable", "瓶类容器通常属于可回收物"),
    (r"塑料",     "recyclable", "塑料制品属于可回收物"),
    (r"玻璃",     "recyclable", "玻璃制品属于可回收物"),
    (r"金属|铁|铜|铝|不锈钢", "recyclable", "金属制品属于可回收物"),
    (r"衣服|衣物|鞋|包|布|纺织|毛巾|床单|袜", "recyclable", "织物类属于可回收物"),
    (r"家电|手机|充电|电脑|电器", "recyclable", "电子电器产品可回收利用"),
    (r"衣架",     "recyclable", "衣架属于可回收物"),
    (r"光盘",     "recyclable", "光盘属于可回收物"),
    (r"钥匙|剪刀", "recyclable", "金属制品属于可回收物"),
    (r"易拉罐|罐", "recyclable", "金属罐体属于可回收物"),
    (r"盒|包装",   "recyclable", "纸盒/包装盒属于可回收物"),

    # 有害垃圾
    (r"电池|充电宝", "hazardous", "电池类含重金属，属于有害垃圾"),
    (r"灯管|灯泡|灯", "hazardous", "灯管类含汞，属于有害垃圾"),
    (r"药|药品",  "hazardous", "药品属于有害垃圾"),
    (r"农药|杀虫剂|除草", "hazardous", "农药类属于有害垃圾"),
    (r"油漆|涂料|稀释|溶剂", "hazardous", "化学溶剂属于有害垃圾"),
    (r"机油|油墨|矿物油", "hazardous", "矿物油类属于有害垃圾"),
    (r"胶片|相纸", "hazardous", "感光材料属于有害垃圾"),
    (r"指甲油|洗甲水", "hazardous", "含化学溶剂，属于有害垃圾"),
    (r"温度计|血压计", "hazardous", "含汞仪器属于有害垃圾"),
    (r"水银|汞",  "hazardous", "含汞物质属于有害垃圾"),
    (r"化妆品",   "hazardous", "过期化妆品含化学成分"),
    (r"鼠药|老鼠药|蟑螂", "hazardous", "有毒杀虫剂属于有害垃圾"),

    # 厨余垃圾
    (r"饭|米饭|粥|剩饭", "kitchen", "主食剩余属于厨余垃圾"),
    (r"菜|蔬菜|青菜|白菜", "kitchen", "蔬菜类属于厨余垃圾"),
    (r"果皮|果核|果壳|水果|苹果|香蕉|橘子|西瓜", "kitchen", "果皮果核属于厨余垃圾"),
    (r"茶|咖啡|豆浆", "kitchen", "饮品残渣属于厨余垃圾"),
    (r"蛋壳|鸡蛋", "kitchen", "蛋壳属于厨余垃圾"),
    (r"骨头|骨|鱼刺|鱼骨", "kitchen", "小型骨骼属于厨余垃圾"),
    (r"虾壳|蟹壳|虾", "kitchen", "水产外壳属于厨余垃圾"),
    (r"花生|瓜子|核桃|坚果", "kitchen", "坚果壳属于厨余垃圾"),
    (r"中药|药渣", "kitchen", "中药渣属于厨余垃圾"),
    (r"花草|花|叶|落叶|树枝", "kitchen", "植物残体属于厨余垃圾"),
    (r"面包|蛋糕|饼干|点心", "kitchen", "烘焙食品属于厨余垃圾"),
    (r"面条|面|粉|米粉", "kitchen", "面食类属于厨余垃圾"),
    (r"玉米|甘蔗", "kitchen", "植物残余属于厨余垃圾"),
    (r"剩菜|剩饭|剩菜剩饭|食物残渣", "kitchen", "食物残余属于厨余垃圾"),
    (r"过期食品",  "kitchen", "过期食品属于厨余垃圾"),

    # 其他垃圾
    (r"纸巾|卫生纸|餐巾纸|手帕纸", "other", "纸巾类遇水即溶，属于其他垃圾"),
    (r"纸尿裤|尿不湿|卫生巾|护垫", "other", "一次性卫生用品属于其他垃圾"),
    (r"湿巾|湿纸巾", "other", "湿纸巾属于其他垃圾"),
    (r"筷子|餐具|饭盒|快餐盒|打包盒", "other", "被污染的一次性餐具属于其他垃圾"),
    (r"保鲜膜|保鲜袋", "other", "保鲜膜属于其他垃圾"),
    (r"烟蒂|烟头|香烟|烟灰", "other", "烟草废弃物属于其他垃圾"),
    (r"尘土|灰尘|渣土|灰烬|煤渣", "other", "尘土类属于其他垃圾"),
    (r"陶瓷|瓦片|砖|瓷砖|碗", "other", "陶瓷类属于其他垃圾"),
    (r"头发|指甲", "other", "毛发指甲属于其他垃圾"),
    (r"创可贴|口罩|棉签|膏药", "other", "医疗卫生物品属于其他垃圾"),
    (r"笔|橡皮|尺子|胶带|便利贴|修正", "other", "文具类属于其他垃圾"),
    (r"宠物|猫砂|粪便", "other", "宠物废物属于其他垃圾"),
    (r"牙签|牙线|吸管", "other", "一次性口腔用品属于其他垃圾"),
    (r"纸杯|一次性纸杯", "other", "有塑料涂层的一次性纸杯属于其他垃圾"),
    (r"气球",     "other", "橡胶气球属于其他垃圾"),
    (r"化妆棉|面膜", "other", "化妆耗材属于其他垃圾"),
    (r"泡沫",     "other", "被污染的泡沫属于其他垃圾"),
    (r"粽叶|玉米皮", "other", "质地坚硬的植物外皮属于其他垃圾"),
    (r"大棒骨|大骨|牛骨|猪骨", "other", "大型骨骼难粉碎，属于其他垃圾"),
    (r"贝壳|蛤蜊|扇贝|牡蛎|花甲", "other", "贝壳类坚硬不易处理，属于其他垃圾"),
    (r"椰子|榴莲", "other", "坚硬果壳属于其他垃圾"),
    (r"抹布|脏布|脏衣服", "other", "被污染的织物属于其他垃圾"),
]
def exact_search(name):
    name = name.strip()
    if name in ITEMS:
        return ITEMS[name]
    return None

def fuzzy_search(name):
    name = name.strip()
    if not name:
        return None
    for key, val in ITEMS.items():
        if name in key or key in name:
            return val
    return None

def rule_match(name):
    name = name.strip()
    if not name:
        return None
    for pattern, cat, reason in RULES:
        if re.search(pattern, name):
            return cat, "【规则匹配】" + reason
    return None

def classify(name):
    name = name.strip()
    if not name:
        return None, None, "请输入物品名称"
    result = exact_search(name)
    if result:
        return result[0], result[1], None
    result = fuzzy_search(name)
    if result:
        return result[0], result[1], None
    result = rule_match(name)
    if result:
        return result[0], None, result[1]
    return None, None, None

def get_suggestions(name, top=5):
    name = name.strip().lower()
    if not name:
        return []
    scored = []
    for key in ITEMS:
        kl = key.lower()
        if name == kl:
            score = 100
        elif kl.startswith(name):
            score = 80
        elif name in kl:
            score = 60
        else:
            continue
        scored.append((score, key))
    scored.sort(reverse=True)
    return [k for _, k in scored[:top]]

def print_result(cat_key, desc, note):
    if not cat_key:
        print("\n  \u274c 未能识别\n")
        return
    c = CATEGORIES[cat_key]
    icon = c["icon"]
    print(f"\n  {icon} 识别结果：{c['name']}（{c['color']}色）")
    print(f"  {c['desc']}")
    if desc:
        print(f"  > {desc}")
    if note:
        print(f"  > {note}")
    examples = [k for k, v in ITEMS.items() if v[0] == cat_key][:6]
    if examples:
        print(f"  同类物品：{' / '.join(examples)}")
    print()

def interactive_mode():
    print("=" * 50)
    print("   垃圾分类智能识别系统 v1.0")
    print("=" * 50)
    for k, c in CATEGORIES.items():
        print(f"  {c['icon']} {c['name']}（{c['color']}色）")
    print("=" * 50)
    print("输入物品名查询，多个用逗号/空格分隔，输入 q 退出\n")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw.lower() in ("q", "quit", "exit"):
            break
        import re as re_mod
        names = [n.strip() for n in re_mod.split(r"[,，、\s]+", raw) if n.strip()]
        for name in names:
            cat_key, desc, note = classify(name)
            print_result(cat_key, desc, note)

def main():
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            cat_key, desc, note = classify(name)
            if cat_key:
                print(f"{name} -> {CATEGORIES[cat_key]['name']}")
            else:
                print(f"{name} -> 未知")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()