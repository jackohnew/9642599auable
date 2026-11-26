# -*- coding: utf-8 -*-
"""
规划土地执法法律依据查询系统 —— Android / Kivy 版 (修复中文乱码和颜色)
"""
import os
import re
import csv
import html
import traceback
from datetime import datetime

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp
from kivy.core.text import LabelBase

# ============================================================
# 0. 自动加载手机系统自带的中文字体（解决乱码方块）
# ============================================================
def load_chinese_font():
    if platform == 'android':
        # 按优先级查找安卓系统常见中文字体
        font_paths = [
            '/system/fonts/NotoSansCJK-Regular.ttc',
            '/system/fonts/DroidSansFallback.ttf',
            '/system/fonts/HuaweiFont.ttf',
            '/system/fonts/HwChinese.ttf',
            '/system/fonts/NotoSansSC-Regular.otf'
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    # 强行把 Kivy 的默认字体替换成这个中文字体
                    LabelBase.register(name='Roboto', fn_regular=path)
                    print(f"成功加载中文字体: {path}")
                    return
                except Exception as e:
                    print(f"加载字体失败 {path}: {e}")

load_chinese_font()

# ============================================================
# 一、通用工具
# ============================================================
_WS_PATTERN = re.compile(r'[\s\u3000]+')

def strip_whitespace(s):
    if not isinstance(s, str):
        return ''
    return _WS_PATTERN.sub('', s)

# ============================================================
# 二、法律依据数据库（简略展示，保留核心）
# ============================================================
LEGAL_PROVISIONS = {
    "城乡规划法第40条": {"law": "《中华人民共和国城乡规划法》", "article": "第四十条第一款", "content": "在城市、镇规划区内进行建筑物、构筑物、道路、管线和其他工程建设的，建设单位或者个人应当向城市、县人民政府城乡规划主管部门或者省、自治区、直辖市人民政府确定的镇人民政府申请办理建设工程规划许可证。"},
    "城乡规划法第64条": {"law": "《中华人民共和国城乡规划法》", "article": "第六十四条", "content": "未取得建设工程规划许可证或者未按照建设工程规划许可证的规定进行建设的，由县级以上地方人民政府城乡规划主管部门责令停止建设；尚可采取改正措施消除对规划实施的影响的，限期改正，处建设工程造价百分之五以上百分之十以下的罚款；无法采取改正措施消除影响的，限期拆除，不能拆除的，没收实物或者违法收入，可以并处建设工程造价百分之十以下的罚款。"},
    "城乡规划法第66条": {"law": "《中华人民共和国城乡规划法》", "article": "第六十六条", "content": "建设单位或者个人有下列行为之一的，由所在地城市、县人民政府城乡规划主管部门责令限期拆除，可以并处临时建设工程造价一倍以下的罚款：（一）未经批准进行临时建设的；（二）未按照批准内容进行临时建设的；（三）临时建筑物、构筑物超过批准期限不拆除的。"},
    "土地管理法第77条": {"law": "《中华人民共和国土地管理法》", "article": "第七十七条", "content": "未经批准或者采取欺骗手段骗取批准，非法占用土地的，由县级以上人民政府自然资源主管部门责令退还非法占用的土地，对违反土地利用总体规划擅自将农用地改为建设用地的，限期拆除在非法占用的土地上新建的建筑物和其他设施，恢复土地原状，对符合土地利用总体规划的，没收在非法占用的土地上新建的建筑物和其他设施，可以并处罚款；构成犯罪的，依法追究刑事责任。"},
    "行政处罚法第27条": {"law": "《中华人民共和国行政处罚法》", "article": "第二十七条", "content": "违法行为涉嫌犯罪的，行政机关应当及时将案件移送司法机关，依法追究刑事责任。对依法不需要追究刑事责任或者免予刑事处罚，但应当给予行政处罚的，司法机关应当及时将案件移送有关行政机关。"},
    "行政处罚法第57条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十七条", "content": "调查终结，行政机关负责人应当对调查结果进行审查，根据不同情况，分别作出如下决定：（一）确有应受行政处罚的违法行为的，根据情节轻重及具体情况，作出行政处罚决定；（二）违法行为轻微，依法可以不予行政处罚的，不予行政处罚；（三）违法事实不能成立的，不予行政处罚；（四）违法行为涉嫌犯罪的，移送司法机关。"},
}

CSV_PROVISIONS = {}

# 简化测试用的 SITUATIONS
SITUATIONS = {
    "1-1": {
        "name": "对未取得建设工程规划许可证；未按建设工程规划许可证的规定进行建设的行政处罚",
        "type": "一、街道继续实施行政处罚至2027年7月1日",
        "criteria": "未取得或未按建设工程规划许可证进行建设。",
        "path": "街道实施行政处罚",
        "enforcement": "限期拆除自执；罚款申请法院",
        "restriction": "是（裁量）",
        "transition": "由街道办事处继续实施至2027年7月1日止。",
        "extra_sections": {"公告调查依据": ["广东省城乡规划条例第86条"], "移送依据": ["行政处罚法第27条", "行政处罚法第57条"]},
        "legal_sections": {"处罚理由": ["城乡规划法第40条"], "处罚依据": ["城乡规划法第64条"]},
        "discretion_keys": ["规划—未取得规划许可证"]
    }
}

# ============================================================
# 三、查询与生成逻辑
# ============================================================
def get_provision(key):
    if key in CSV_PROVISIONS:
        return CSV_PROVISIONS[key]
    return LEGAL_PROVISIONS.get(key, {"law": key, "article": "", "content": "（该条原文暂未内置，请查阅法规原文）"})

def build_report_text(situation_key):
    sit = SITUATIONS.get(situation_key)
    if not sit:
        return "未找到该情形。"
    lines = []
    lines.append(f"【情形编号】{situation_key}")
    lines.append(f"【情形名称】{sit['name']}")
    lines.append(f"【所属分类】{sit['type']}")
    lines.append(f"【适用条件】{sit['criteria']}")
    lines.append(f"【处罚主体路径】{sit['path']}")
    lines.append(f"【强制执行方式】{sit['enforcement']}")
    lines.append(f"【过渡期建议】{sit['transition']}\n")

    lines.append("【处罚理由（定性）】")
    for k in sit["legal_sections"].get("处罚理由", []):
        p = get_provision(k)
        lines.append(f"· {p['law']}{p['article']}：{p['content']}\n")

    lines.append("【处罚依据（罚则）】")
    for k in sit["legal_sections"].get("处罚依据", []):
        p = get_provision(k)
        lines.append(f"· {p['law']}{p['article']}：{p['content']}\n")

    return "\n".join(lines)

def search_provisions(keyword):
    if not keyword: return []
    kw = keyword.strip()
    results = []
    all_p = dict(LEGAL_PROVISIONS)
    all_p.update(CSV_PROVISIONS)
    for k, v in all_p.items():
        if kw in v.get("law", "") or kw in v.get("article", "") or kw in v.get("content", ""):
            results.append((k, v))
    return results

# ============================================================
# 四、Kivy 界面 (修复黑字、白底、点击问题)
# ============================================================
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(8), **kwargs)

        # 顶部标题 (黑字)
        title = Label(text="[b]规划土地执法法律依据查询系统[/b]", markup=True, size_hint_y=None, height=dp(40), font_size=dp(18), color=(0, 0, 0, 1))
        self.add_widget(title)

        # 情形选择行
        row1 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        row1.add_widget(Label(text="情形：", size_hint_x=None, width=dp(60), color=(0, 0, 0, 1)))
        self.spinner = Spinner(
            text="请选择执法事项",
            values=[f"{k}｜{v['name'][:15]}..." for k, v in SITUATIONS.items()],
            size_hint_x=1,
            background_color=(0.8, 0.8, 0.8, 1), # 按钮背景色
            color=(0, 0, 0, 1) # 文字颜色
        )
        row1.add_widget(self.spinner)
        self.add_widget(row1)

        # 搜索行
        row2 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.search_input = TextInput(
            hint_text="法条关键词（如：城乡规划法第64条）", 
            multiline=False,
            foreground_color=(0, 0, 0, 1), # 黑字
            background_color=(1, 1, 1, 1), # 白底
            cursor_color=(0, 0, 0, 1)
        )
        btn_search = Button(text="搜索", size_hint_x=None, width=dp(80), background_color=(0.2, 0.6, 1, 1))
        btn_search.bind(on_release=self.on_search)
        row2.add_widget(self.search_input)
        row2.add_widget(btn_search)
        self.add_widget(row2)

        # 操作按钮行
        row3 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        b1 = Button(text="查询该情形", background_color=(0.2, 0.8, 0.2, 1))
        b1.bind(on_release=self.on_query_situation)
        b2 = Button(text="导出HTML", background_color=(0.8, 0.5, 0.2, 1))
        b2.bind(on_release=self.on_export_html)
        b3 = Button(text="导入CSV", background_color=(0.5, 0.5, 0.8, 1))
        b3.bind(on_release=self.on_import_csv)
        for b in (b1, b2, b3):
            row3.add_widget(b)
        self.add_widget(row3)

        # 结果区 (黑底白字，或者白底黑字，这里使用白底黑字带个边框感)
        scroll = ScrollView(size_hint=(1, 1))
        self.result_label = Label(
            text="请选择情形或输入关键词后查询。",
            size_hint_y=None, markup=False,
            halign="left", valign="top",
            color=(0, 0, 0, 1) # 黑字！
        )
        self.result_label.bind(texture_size=self._update_label_height)
        # 让 text_size 随窗口变化
        self.result_label.text_size = (Window.width - dp(40), None)
        Window.bind(size=self._on_window_size)
        
        scroll.add_widget(self.result_label)
        self.add_widget(scroll)

    def _update_label_height(self, *args):
        self.result_label.height = self.result_label.texture_size[1] + dp(20)

    def _on_window_size(self, *args):
        self.result_label.text_size = (Window.width - dp(40), None)

    def show_text(self, txt):
        self.result_label.text = txt
        self.result_label.texture_update()
        self.result_label.height = self.result_label.texture_size[1] + dp(20)

    # ---------- 事件 ----------
    def on_query_situation(self, *args):
        sel = self.spinner.text
        if "｜" not in sel:
            self.show_text("请先选择一个执法事项。")
            return
        key = sel.split("｜", 1)[0]
        txt = build_report_text(key)
        self.show_text(txt)
        self._last_report = txt

    def on_search(self, *args):
        kw = self.search_input.text.strip()
        if not kw:
            self.show_text("请输入关键词。")
            return
        results = search_provisions(kw)
        if not results:
            self.show_text(f"未找到包含「{kw}」的法条。")
            return
        lines = [f"【关键词】{kw}  共 {len(results)} 条\n"]
        for k, v in results[:50]:
            lines.append(f"◆ {v.get('law','')}{v.get('article','')}")
            lines.append(f"  {v.get('content','')}\n")
        self.show_text("\n".join(lines))

    def on_import_csv(self, *args):
        self.show_text("该功能需在完整版中体验，当前测试版暂不支持文件选择器弹窗。")

    def on_export_html(self, *args):
        self.show_text("导出功能需在完整版中体验。")

class LawApp(App):
    title = "法律依据查询"
    def build(self):
        # 设置全局背景为浅灰色，避免纯白刺眼
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        return MainScreen()

if __name__ == "__main__":
    LawApp().run()
