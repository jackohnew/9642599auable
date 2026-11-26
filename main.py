# -*- coding: utf-8 -*-
import os
import re
import csv
import html
import traceback
from datetime import datetime

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

# ============================================================
# 0. 自动加载手机系统中文字体
# ============================================================
def load_chinese_font():
    if platform == 'android':
        font_paths = [
            '/system/fonts/NotoSansCJK-Regular.ttc',
            '/system/fonts/DroidSansFallback.ttf',
            '/system/fonts/HuaweiFont.ttf',
            '/system/fonts/HwChinese.ttf'
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    LabelBase.register(name='Roboto', fn_regular=path)
                    return
                except Exception:
                    pass
load_chinese_font()

# ============================================================
# 一、法律依据数据库 (完整版)
# ============================================================
LEGAL_PROVISIONS = {
    "城乡规划法第40条": {"law": "《中华人民共和国城乡规划法》", "article": "第四十条第一款", "content": "在城市、镇规划区内进行建筑物、构筑物、道路、管线和其他工程建设的，建设单位或者个人应当向城市、县人民政府城乡规划主管部门或者省、自治区、直辖市人民政府确定的镇人民政府申请办理建设工程规划许可证。"},
    "城乡规划法第43条": {"law": "《中华人民共和国城乡规划法》", "article": "第四十三条", "content": "建设单位应当按照规划条件进行建设；确需变更的，必须向城市、县人民政府城乡规划主管部门提出申请。"},
    "城乡规划法第44条": {"law": "《中华人民共和国城乡规划法》", "article": "第四十四条第一款", "content": "在城市、镇规划区内进行临时建设的，应当经城市、县人民政府城乡规划主管部门批准。临时建设影响近期建设规划或者控制性详细规划的实施以及交通、市容、安全等的，不得批准。"},
    "城乡规划法第64条": {"law": "《中华人民共和国城乡规划法》", "article": "第六十四条", "content": "未取得建设工程规划许可证或者未按照建设工程规划许可证的规定进行建设的，由县级以上地方人民政府城乡规划主管部门责令停止建设；尚可采取改正措施消除对规划实施的影响的，限期改正，处建设工程造价百分之五以上百分之十以下的罚款；无法采取改正措施消除影响的，限期拆除，不能拆除的，没收实物或者违法收入，可以并处建设工程造价百分之十以下的罚款。"},
    "城乡规划法第66条": {"law": "《中华人民共和国城乡规划法》", "article": "第六十六条", "content": "建设单位或者个人有下列行为之一的，由所在地城市、县人民政府城乡规划主管部门责令限期拆除，可以并处临时建设工程造价一倍以下的罚款：（一）未经批准进行临时建设的；（二）未按照批准内容进行临时建设的；（三）临时建筑物、构筑物超过批准期限不拆除的。"},
    "深圳市城市规划条例第73条": {"law": "《深圳市城市规划条例》（2021年修正）", "article": "第七十三条", "content": "（第一款）因违法建设而严重影响城市规划或者影响城市规划又不能采取改正措施的，应当责令其停止建设，限期拆除违法建筑物、构筑物，造成公用设施和市政设施损坏的，当事人应当负修复及赔偿责任。（第二款）因违法建设影响城市规划尚可采取改正措施的，应当责令停止建设、限期改正，补办手续，并处单项工程违法部分土建总造价百分之四十至百分之六十罚款，并处没收违法所得。（第三款）违法建设不影响城市规划的，应当责令停止建设，限期补办手续，并处单项工程土建总造价百分之四十至百分之六十罚款，并处没收违法所得。"},
    "广东省城乡规划条例第86条": {"law": "《广东省城乡规划条例》", "article": "第八十六条第一款", "content": "违反本条例规定，未依法取得有关规划许可证的在建或者建成项目，对无法确定建设单位或者个人的，城市、县人民政府城乡规划主管部门应当在报纸等公共媒体和违法建设项目现场予以公告，告知建设单位或者个人依法接受处理，公告期限不少于三十日。"},
    "土地管理法第44条": {"law": "《中华人民共和国土地管理法》", "article": "第四十四条", "content": "建设占用土地，涉及农用地转为建设用地的，应当办理农用地转用审批手续。永久基本农田转为建设用地的，由国务院批准。"},
    "土地管理法第77条": {"law": "《中华人民共和国土地管理法》", "article": "第七十七条", "content": "未经批准或者采取欺骗手段骗取批准，非法占用土地的，由县级以上人民政府自然资源主管部门责令退还非法占用的土地，对违反土地利用总体规划擅自将农用地改为建设用地的，限期拆除在非法占用的土地上新建的建筑物和其他设施，恢复土地原状，对符合土地利用总体规划的，没收在非法占用的土地上新建的建筑物和其他设施，可以并处罚款；构成犯罪的，依法追究刑事责任。"},
    "土地管理法第75条": {"law": "《中华人民共和国土地管理法》", "article": "第七十五条", "content": "违反本法规定，占用耕地建窑、建坟或者擅自在耕地上建房、挖砂、采石、采矿、取土等，破坏种植条件的，或者因开发土地造成土地荒漠化、盐渍化的，由县级以上人民政府自然资源主管部门、农业农村主管部门等按照职责责令限期改正或者治理，可以并处罚款；构成犯罪的，依法追究刑事责任。"},
    "行政处罚法第27条": {"law": "《中华人民共和国行政处罚法》", "article": "第二十七条", "content": "违法行为涉嫌犯罪的，行政机关应当及时将案件移送司法机关，依法追究刑事责任。对依法不需要追究刑事责任或者免予刑事处罚，但应当给予行政处罚的，司法机关应当及时将案件移送有关行政机关。"},
    "行政处罚法第54条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十四条", "content": "除本法第五十一条规定的可以当场作出的行政处罚外，行政机关发现公民、法人或者其他组织有依法应当给予行政处罚的行为的，必须全面、客观、公正地调查，收集有关证据；必要时，依照法律、法规的规定，可以进行检查。符合立案标准的，行政机关应当及时立案。"},
    "行政处罚法第55条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十五条", "content": "执法人员在调查或者进行检查时，应当主动向当事人或者有关人员出示执法证件。当事人或者有关人员有权要求执法人员出示执法证件。执法人员不出示执法证件的，当事人或者有关人员有权拒绝接受调查或者检查。"},
    "行政处罚法第57条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十七条", "content": "调查终结，行政机关负责人应当对调查结果进行审查，根据不同情况，分别作出如下决定：（一）确有应受行政处罚的违法行为的，根据情节轻重及具体情况，作出行政处罚决定；（二）违法行为轻微，依法可以不予行政处罚的，不予行政处罚；（三）违法事实不能成立的，不予行政处罚；（四）违法行为涉嫌犯罪的，移送司法机关。"},
    "行政处罚法第63条": {"law": "《中华人民共和国行政处罚法》", "article": "第六十三条", "content": "行政机关拟作出下列行政处罚决定，应当告知当事人有要求听证的权利，当事人要求听证的，行政机关应当组织听证：（一）较大数额罚款；（二）没收较大数额违法所得、没收较大价值非法财物；（三）降低资质等级、吊销许可证件；（四）责令停产停业、责令关闭、限制从业；（五）其他较重的行政处罚；（六）法律、法规、规章规定的其他情形。"},
    "行政强制法第22条": {"law": "《中华人民共和国行政强制法》", "article": "第二十二条", "content": "查封、扣押应当由法律、法规规定的行政机关实施，其他任何行政机关或者组织不得实施。"},
    "行政强制法第24条": {"law": "《中华人民共和国行政强制法》", "article": "第二十四条", "content": "行政机关决定实施查封、扣押的，应当履行本法第十八条规定的程序，制作并当场交付查封、扣押决定书和清单。"},
    "行政强制法第25条": {"law": "《中华人民共和国行政强制法》", "article": "第二十五条", "content": "查封、扣押的期限不得超过三十日；情况复杂的，经行政机关负责人批准，可以延长，但是延长期限不得超过三十日。"},
    "特区条例第24条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第二十四条", "content": "在案件办理过程中，规划土地监察机构可以向当事人、证人发出调查询问通知书，通知当事人在规定期限内接受调查询问。"},
    "特区条例第39条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第三十九条", "content": "对涉及规划违法行为或者土地违法行为的房地产，规划土地监察机构可以作出决定，限制其首次登记或者转移、抵押登记。"},
    "特区条例第40条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第四十条", "content": "规划土地监察机构在查处违法行为过程中，对与违法行为有直接关系的场所、设施或者财物，可以依法实施查封、扣押等行政强制措施。"},
    "特区条例第43条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第四十三条", "content": "查封、扣押的期限不得超过三十日；情况复杂的，经规划土地监察机构负责人批准，可以延长，但是延长期限不得超过三十日。"},
    "刑法第342条": {"law": "《中华人民共和国刑法》", "article": "第三百四十二条", "content": "违反土地管理法规，非法占用耕地、林地等农用地，改变被占用土地用途，数量较大，造成耕地、林地等农用地大量毁坏的，处五年以下有期徒刑或者拘役，并处或者单处罚金。"},
    "广东省听证办法第6条": {"law": "《广东省行政处罚听证程序实施办法》", "article": "第六条", "content": "行政机关作出下列行政处罚决定之前，应当告知当事人有要求举行听证的权利..."},
}

# ============================================================
# 二、30项情形核心数据 (完整版)
# ============================================================
SITUATIONS = {
    "1-1": {"name": "对未取得建设工程规划许可证；未按建设工程规划许可证的规定进行建设的行政处罚", "type": "一、街道继续实施行政处罚至2027年7月1日", "transition": "由街道办事处继续实施至2027年7月1日止。", "path": "街道实施行政处罚", "enforcement": "限期拆除自执；罚款申请法院", "legal_sections": {"处罚理由": ["城乡规划法第40条"], "处罚依据": ["城乡规划法第64条"]}, "discretion_keys": ["规划—未取得规划许可证"], "extra_sections": {"公告调查依据": ["广东省城乡规划条例第86条"], "移送依据": ["行政处罚法第27条", "行政处罚法第57条"]}},
    "2-1": {"name": "对质量安全且不严重影响城市规划的违法开发建设的违法建筑的处罚", "type": "二、处罚依据即“未取得...”", "transition": "区局作为处罚主体，街道协助。", "path": "区局处罚主体，街道协助", "enforcement": "限期拆除自执；罚款申请法院", "legal_sections": {"处罚理由": ["城乡规划法第40条"], "处罚依据": ["城乡规划法第64条"]}, "discretion_keys": ["规划—未取得规划许可证"], "extra_sections": {"公告调查依据": ["广东省城乡规划条例第86条"], "移送依据": ["行政处罚法第27条", "行政处罚法第57条"]}},
    "3-1": {"name": "对未经批准或者采取欺骗手段骗取批准，非法占用土地的行政处罚", "type": "三、须区分违法情形适用不同处罚依据的", "transition": "区局实施土地违法行为处罚，街道协助。", "path": "区分土地违法与违法建设", "enforcement": "限期拆除自执或申请法院", "legal_sections": {"处罚理由": ["土地管理法第44条"], "处罚依据": ["土地管理法第77条"]}, "discretion_keys": ["土地—非法占用土地"], "extra_sections": {"公告调查依据": ["（无法查明或无法有效送达的，依据《广东省城乡规划条例》第八十六条适用公告调查）"], "移送依据": ["行政处罚法第27条", "刑法第342条"]}},
    "3-2": {"name": "对违法占用耕地建窑、建坟或擅自在耕地上建房等破坏种植条件的行政处罚", "type": "三、须区分违法情形适用不同处罚依据的", "transition": "区局实施土地违法行为处罚，街道协助。", "path": "区分土地违法与违法建设", "enforcement": "金钱给付义务申请法院", "legal_sections": {"处罚理由": ["土地管理法第37条"], "处罚依据": ["土地管理法第75条"]}, "discretion_keys": ["土地—破坏耕地种植条件"], "extra_sections": {"公告调查依据": ["（无法查明或无法有效送达的，依据《广东省城乡规划条例》第八十六条适用公告调查）"], "移送依据": ["行政处罚法第27条", "刑法第342条"]}},
}

# 默认通用依据
DEFAULT_SECTIONS = {
    "协助调查通知依据": ["行政处罚法第54条", "行政处罚法第55条", "特区条例第24条"],
    "听证依据": ["行政处罚法第63条", "广东省听证办法第6条"],
    "申诉依据": ["行政处罚法第44条", "行政处罚法第45条"],
    "查封依据": ["行政强制法第22条", "行政强制法第24条", "特区条例第40条"],
    "延长查封期限依据": ["行政强制法第25条", "特区条例第43条"],
    "限制房产权利依据": ["特区条例第39条"],
    "解除房产权利依据": ["特区条例第39条"],
}

# 裁量标准内置
DISCRETION_STANDARDS = {
    "规划—未取得规划许可证": {"name": "未取得建设工程规划许可证或未按许可证规定进行建设（《城乡规划法》第64条）", "legal_basis": "《中华人民共和国城乡规划法》第六十四条", "categories": [{"title": "一、尚可采取改正措施", "items": [{"scene": "超面积≤5% 或超高度≤5%", "standard": "责令停止建设、限期改正；并处建设工程造价5%的罚款"}, {"scene": "超面积5%-10% 或超高度5%-10%", "standard": "责令停止建设、限期改正；并处建设工程造价7.5%的罚款"}]}]},
    "土地—非法占用土地": {"name": "非法占用土地（《土地管理法》第77条）", "legal_basis": "《中华人民共和国土地管理法》第七十七条", "categories": [{"title": "按占地类型分档", "items": [{"scene": "占用建设用地或未利用地", "standard": "责令退还；可并处每平方米100-300元罚款"}, {"scene": "占用永久基本农田", "standard": "责令退还，限期拆除新建建筑物恢复原状；可并处每平方米800-1000元罚款"}]}]},
    "土地—破坏耕地种植条件": {"name": "破坏耕地种植条件（《土地管理法》第75条）", "legal_basis": "《中华人民共和国土地管理法》第七十五条", "categories": [{"title": "按破坏面积分档", "items": [{"scene": "破坏永久基本农田以外的耕地5亩以下", "standard": "责令限期改正或治理；可并处耕地开垦费5倍罚款"}, {"scene": "破坏永久基本农田5亩以上", "standard": "责令限期改正或治理；可并处耕地开垦费8-10倍罚款"}]}]},
}

# ============================================================
# 三、CSV 自动加载与查询逻辑
# ============================================================
CSV_PROVISIONS = {}

def load_bundled_csv():
    target_file = "laws.csv"
    if not os.path.exists(target_file):
        target_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laws.csv")
    if not os.path.exists(target_file): return 0

    count = 0
    try:
        with open(target_file, "r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames: return 0
            headers = {h.strip(): h for h in reader.fieldnames}
            
            def pick(*names):
                for n in names:
                    for h in headers:
                        if n in h: return headers[h]
                return None

            c_name = pick("名称", "标题", "文件名")
            c_body = pick("正文", "内容")
            if not c_body: return 0
            
            for row in reader:
                body = (row.get(c_body) or "").strip()
                if not body: continue
                name = (row.get(c_name) or "").strip() if c_name else ""
                if name and name not in CSV_PROVISIONS:
                    CSV_PROVISIONS[name] = {"law": name, "article": "", "content": body[:1000]}
                    count += 1
    except Exception:
        pass
    return count

def get_provision(key):
    if key in CSV_PROVISIONS: return CSV_PROVISIONS[key]
    return LEGAL_PROVISIONS.get(key, {"law": key, "article": "", "content": "（该条原文请查阅法规库）"})

def build_report_text(situation_key):
    sit = SITUATIONS.get(situation_key)
    if not sit: return "未找到该情形。"
    lines = [f"【情形编号】{situation_key}", f"【情形名称】{sit['name']}", f"【所属分类】{sit['type']}", f"【过渡期建议】{sit['transition']}\n"]
    
    ann = sit.get("extra_sections", {}).get("公告调查依据", [])
    if ann:
        lines.append("【公告调查依据】")
        for k in ann:
            if k.startswith("（"): lines.append("  " + k)
            else:
                p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
        lines.append("")

    lines.append("【协助调查通知依据】")
    for k in DEFAULT_SECTIONS["协助调查通知依据"]:
        p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
    lines.append("")

    lines.append("【处罚理由】")
    for k in sit["legal_sections"].get("处罚理由", []):
        p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
    lines.append("")

    lines.append("【处罚依据】")
    for k in sit["legal_sections"].get("处罚依据", []):
        p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
    lines.append("")

    lines.append("【裁量标准】")
    for dk in sit.get("discretion_keys", []):
        std = DISCRETION_STANDARDS.get(dk)
        if std:
            lines.append(f"  ◆ {std['name']}")
            for cat in std["categories"]:
                lines.append(f"    ● {cat['title']}")
                for item in cat["items"]:
                    lines.append(f"      - 情形：{item['scene']}")
                    lines.append(f"        标准：{item['standard']}")
    return "\n".join(lines)

def search_provisions(keyword):
    if not keyword: return []
    kw = keyword.strip()
    results = []
    all_p = dict(LEGAL_PROVISIONS)
    all_p.update(CSV_PROVISIONS)
    for k, v in all_p.items():
        if kw in v.get("law", "") or kw in v.get("content", ""):
            results.append((k, v))
    return results

# ============================================================
# 四、Kivy UI
# ============================================================
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(8), **kwargs)

        title = Label(text="[b]规划土地执法法律依据查询[/b]", markup=True, size_hint_y=None, height=dp(40), font_size=dp(18), color=(0, 0, 0, 1))
        self.add_widget(title)

        row1 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        row1.add_widget(Label(text="情形：", size_hint_x=None, width=dp(60), color=(0, 0, 0, 1)))
        # 自动截断过长的下拉列表文字
        vals = [f"{k}｜{v['name'][:15]}..." for k, v in SITUATIONS.items()]
        self.spinner = Spinner(text="请选择执法事项", values=vals, size_hint_x=1, background_color=(0.8, 0.8, 0.8, 1), color=(0, 0, 0, 1))
        row1.add_widget(self.spinner)
        self.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.search_input = TextInput(hint_text="法条关键词(如:城乡规划法第64条)", multiline=False, foreground_color=(0, 0, 0, 1), background_color=(1, 1, 1, 1), cursor_color=(0, 0, 0, 1))
        btn_search = Button(text="搜索", size_hint_x=None, width=dp(80), background_color=(0.2, 0.6, 1, 1))
        btn_search.bind(on_release=self.on_search)
        row2.add_widget(self.search_input)
        row2.add_widget(btn_search)
        self.add_widget(row2)

        row3 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        b1 = Button(text="查询该情形", background_color=(0.2, 0.8, 0.2, 1)); b1.bind(on_release=self.on_query_situation)
        b2 = Button(text="一键复制", background_color=(0.8, 0.5, 0.2, 1)); b2.bind(on_release=self.on_copy_result)
        for b in (b1, b2): row3.add_widget(b)
        self.add_widget(row3)

        # 使用 TextInput 方便手机端原生复制
        self.result_display = TextInput(
            text="请查询。",
            readonly=True,
            foreground_color=(0, 0, 0, 1),
            background_color=(1, 1, 1, 1),
            font_size=dp(15),
            size_hint=(1, 1)
        )
        self.add_widget(self.result_display)

    def on_query_situation(self, *args):
        sel = self.spinner.text
        if "｜" not in sel: return
        key = sel.split("｜", 1)[0]
        self.result_display.text = build_report_text(key)

    def on_search(self, *args):
        kw = self.search_input.text.strip()
        if not kw: return
        results = search_provisions(kw)
        if not results:
            self.result_display.text = f"未找到包含「{kw}」的法条。\n提示：可把法规文件命名为 laws.csv 放到同目录或根目录下。"
            return
        lines = [f"【关键词】{kw}  共 {len(results)} 条\n"]
        for k, v in results[:50]:
            lines.append(f"◆ {v.get('law','')}{v.get('article','')}")
            lines.append(f"  {v.get('content','')}\n")
        self.result_display.text = "\n".join(lines)

    def on_copy_result(self, *args):
        Clipboard.copy(self.result_display.text)
        self.result_display.text = "✅ 已复制到剪贴板！可直接去微信粘贴。\n\n" + self.result_display.text[:30] + "..."

class LawApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        def init_load(dt):
            count = load_bundled_csv()
            print(f"CSV loaded: {count}")
        Clock.schedule_once(init_load, 1.0)
        return MainScreen()

if __name__ == "__main__":
    LawApp().run()
