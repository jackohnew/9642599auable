# -*- coding: utf-8 -*-
import os
import re
import csv
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.resources import resource_find

# ============================================================
# 0. 自动加载手机系统中文字体
# ============================================================
def load_chinese_font():
    if platform == 'android':
        font_paths = ['/system/fonts/NotoSansCJK-Regular.ttc', '/system/fonts/DroidSansFallback.ttf', '/system/fonts/HuaweiFont.ttf']
        for path in font_paths:
            if os.path.exists(path):
                try:
                    LabelBase.register(name='Roboto', fn_regular=path)
                    return
                except Exception: pass
load_chinese_font()

# ============================================================
# 一、法律依据核心库（补全蓝线、紫线、室内装修等）
# ============================================================
LEGAL_PROVISIONS = {
    "城乡规划法第40条": {"law": "《中华人民共和国城乡规划法》", "article": "第四十条第一款", "content": "在城市、镇规划区内进行建筑物、构筑物、道路、管线和其他工程建设的，建设单位或者个人应当向城市、县人民政府城乡规划主管部门或者省、自治区、直辖市人民政府确定的镇人民政府申请办理建设工程规划许可证。"},
    "城乡规划法第64条": {"law": "《中华人民共和国城乡规划法》", "article": "第六十四条", "content": "未取得建设工程规划许可证或者未按照建设工程规划许可证的规定进行建设的，由县级以上地方人民政府城乡规划主管部门责令停止建设；尚可采取改正措施消除对规划实施的影响的，限期改正，处建设工程造价百分之五以上百分之十以下的罚款；无法采取改正措施消除影响的，限期拆除，不能拆除的，没收实物或者违法收入，可以并处建设工程造价百分之十以下的罚款。"},
    "城乡规划法第66条": {"law": "《中华人民共和国城乡规划法》", "article": "第六十六条", "content": "建设单位或者个人有下列行为之一的，由所在地城市、县人民政府城乡规划主管部门责令限期拆除，可以并处临时建设工程造价一倍以下的罚款：（一）未经批准进行临时建设的；（二）未按照批准内容进行临时建设的；（三）临时建筑物、构筑物超过批准期限不拆除的。"},
    "城市蓝线管理办法第10条": {"law": "《城市蓝线管理办法》", "article": "第十条", "content": "在城市蓝线内禁止进行下列活动：（一）违反城市蓝线保护和控制要求的建设活动；（二）擅自填埋、占用城市蓝线内水域；（三）影响水系安全的爆破、采石、取土；（四）擅自建设各类排污设施；（五）其它对城市水系保护构成破坏的活动。"},
    "城市紫线管理办法第2条": {"law": "《城市紫线管理办法》", "article": "第二条", "content": "本办法所称城市紫线，是指国家历史文化名城内的历史文化街区和省、自治区、直辖市人民政府公布的历史文化街区的保护范围界线..."},
    "城市黄线管理办法第2条": {"law": "《城市黄线管理办法》", "article": "第二条", "content": "本办法所称城市黄线，是指对城市发展全局有影响的、城市规划中确定的、必须控制的城市基础设施用地的控制界线。"},
    "住宅室内装饰装修管理办法第6条": {"law": "《住宅室内装饰装修管理办法》", "article": "第六条", "content": "装修人从事住宅室内装饰装修活动，未经批准，不得有下列行为：（一）搭建建筑物、构筑物；（二）改变住宅外立面，在非承重外墙上开门、窗；（三）拆改供暖管道和设施；（四）拆改燃气管道和设施。本条所列第（一）项、第（二）项行为，应当经城市规划行政主管部门批准。"},
    "土地管理法第77条": {"law": "《中华人民共和国土地管理法》", "article": "第七十七条", "content": "未经批准或者采取欺骗手段骗取批准，非法占用土地的，由县级以上人民政府自然资源主管部门责令退还非法占用的土地..."},
    "土地管理法第75条": {"law": "《中华人民共和国土地管理法》", "article": "第七十五条", "content": "违反本法规定，占用耕地建窑、建坟或者擅自在耕地上建房、挖砂、采石、采矿、取土等，破坏种植条件的..."},
    "行政处罚法第27条": {"law": "《中华人民共和国行政处罚法》", "article": "第二十七条", "content": "违法行为涉嫌犯罪的，行政机关应当及时将案件移送司法机关，依法追究刑事责任。"},
    "行政处罚法第54条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十四条", "content": "除本法第五十一条规定的可以当场作出的行政处罚外，行政机关发现公民、法人或者其他组织有依法应当给予行政处罚的行为的，必须全面、客观、公正地调查..."},
    "行政处罚法第55条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十五条", "content": "执法人员在调查或者进行检查时，应当主动向当事人或者有关人员出示执法证件..."},
    "行政处罚法第57条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十七条", "content": "调查终结，行政机关负责人应当对调查结果进行审查..."},
    "行政处罚法第63条": {"law": "《中华人民共和国行政处罚法》", "article": "第六十三条", "content": "行政机关拟作出下列行政处罚决定，应当告知当事人有要求听证的权利..."},
    "行政强制法第22条": {"law": "《中华人民共和国行政强制法》", "article": "第二十二条", "content": "查封、扣押应当由法律、法规规定的行政机关实施..."},
    "行政强制法第24条": {"law": "《中华人民共和国行政强制法》", "article": "第二十四条", "content": "行政机关决定实施查封、扣押的，应当履行本法第十八条规定的程序..."},
    "行政强制法第25条": {"law": "《中华人民共和国行政强制法》", "article": "第二十五条", "content": "查封、扣押的期限不得超过三十日..."},
    "特区条例第24条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第二十四条", "content": "在案件办理过程中，规划土地监察机构可以向当事人、证人发出调查询问通知书..."},
    "特区条例第39条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第三十九条", "content": "对涉及规划违法行为或者土地违法行为的房地产，规划土地监察机构可以作出决定，限制其首次登记..."},
    "特区条例第40条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第四十条", "content": "规划土地监察机构在查处违法行为过程中，对与违法行为有直接关系的场所、设施或者财物，可以依法实施查封、扣押等行政强制措施。"},
    "特区条例第43条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第四十三条", "content": "查封、扣押的期限不得超过三十日..."},
    "广东省城乡规划条例第86条": {"law": "《广东省城乡规划条例》", "article": "第八十六条第一款", "content": "违反本条例规定，未依法取得有关规划许可证的在建或者建成项目，对无法确定建设单位或者个人的..."}
}

# ============================================================
# 二、30项完整情形底层数据
# ============================================================
RECYCLED_ITEMS = [
    {"key": "1-1", "name": "对未取得建设工程规划许可证；未按建设工程规划许可证的规定进行建设的行政处罚", "type": "一、街道继续实施至2027年7月1日", "transition": "由街道办事处继续实施至2027年7月1日止。", "discretion_keys": ["规划—未取得规划许可证"]},
    {"key": "2-1", "name": "对质量安全且不严重影响城市规划的违法开发建设的违法建筑的处罚", "type": "二、处罚依据即“未取得...”", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—未取得规划许可证"]},
    {"key": "2-2", "name": "对严重违反控制性详细规划的建筑物、构筑物的行政处罚", "type": "二、处罚依据即“未取得...”", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—未取得规划许可证"]},
    {"key": "2-3", "name": "对未经批准在城市紫线范围内进行建设活动的行政处罚", "type": "二、处罚依据即“未取得...”", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—未取得规划许可证"]},
    {"key": "2-4", "name": "对在城市蓝线范围内进行各类建设活动的行政处罚", "type": "二、处罚依据即“未取得...”", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—未取得规划许可证"]},
    {"key": "2-5", "name": "对未经批准在住宅室内装饰装修中搭建建筑物、构筑物，或擅自改变外立面的行政处罚", "type": "二、处罚依据即“未取得...”", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—未取得规划许可证"]},
    {"key": "2-6", "name": "对未经批准在城市黄线范围内进行建设活动；擅自改变土地用途的行政处罚", "type": "二、处罚依据即“未取得...”", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—未取得规划许可证"]},
    {"key": "2-7", "name": "对固定消纳场未按规定办理规划许可手续的行政处罚", "type": "二、处罚依据即“未取得...”", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—未取得规划许可证"]},
    {"key": "3-1", "name": "对未经批准或者采取欺骗手段骗取批准，非法占用土地的行政处罚", "type": "三、须区分违法情形", "transition": "区局实施土地违法处罚，存在违建的街道协助。", "discretion_keys": ["土地—非法占用土地"]},
    {"key": "3-2", "name": "对违法占用耕地建窑、建坟或擅自在耕地上建房等破坏种植条件的行政处罚", "type": "三、须区分违法情形", "transition": "区局实施土地违法处罚，存在违建的街道协助。", "discretion_keys": ["土地—破坏耕地种植条件"]},
    {"key": "3-3", "name": "对未经批准进行临时建设；未按批准内容进行临时建设；临时建筑超期不拆除的行政处罚", "type": "三、须区分违法情形", "transition": "无法取得合法手续的按未取得规划许可处罚，街道实施。", "discretion_keys": ["规划—临时建设"]},
    {"key": "4-1", "name": "对建设单位和使用单位违反城市地下空间规划及法定实施管理程序规定的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—地下空间"]},
    {"key": "4-2", "name": "对土地复垦义务人未按规定补充编制土地复垦方案的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—未补充编制复垦方案"]},
    {"key": "4-3", "name": "对个人未办理规划许可审批手续建设地下建筑物、构筑物的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—地下空间"]},
    {"key": "4-4", "name": "对在土地利用总体规划制定前已建的不符合规划用途的建筑物重建、扩建的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—规划前已建建筑物重建扩建"]},
    {"key": "4-5", "name": "对土地复垦义务人未按规定报告土地损毁等情况的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—未报告复垦情况"]},
    {"key": "4-6", "name": "对在临时用地上修建永久性建筑物、构筑物的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—临时用地修永久建筑"]},
    {"key": "4-7", "name": "对土地复垦义务人拒绝、阻碍监督检查或弄虚作假的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—拒绝监督检查"]},
    {"key": "4-8", "name": "对破坏或者擅自改变基本农田保护区标志的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—基本农田标志"]},
    {"key": "4-9", "name": "对依法收回国有土地使用权当事人拒不交出土地，临时使用土地期满拒不归还的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—拒不交还土地"]},
    {"key": "4-10", "name": "对买卖或者以其他形式非法转让土地的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—买卖或非法转让"]},
    {"key": "4-11", "name": "对土地复垦义务人未按规定将土地复垦费用列入生产成本的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—复垦费用未列入成本"]},
    {"key": "4-12", "name": "对土地复垦义务人未按规定对拟损毁的耕地等进行表土剥离的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—未表土剥离"]},
    {"key": "4-13", "name": "对拒不履行土地复垦义务的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—拒不履行复垦义务"]},
    {"key": "4-14", "name": "对非法占用已完成征转地补偿手续的国有土地，建筑物使用功能不违反规划的处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["法定—历史遗留违建没收"]},
    {"key": "4-15", "name": "对建设项目施工和地质勘查临时占用耕地，逾期不恢复种植条件的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—临时用地期满未复垦"]},
    {"key": "4-16", "name": "对建设单位未办理规划许可审批手续建设地下建筑物、构筑物的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["规划—地下空间"]},
    {"key": "4-17", "name": "对土地复垦义务人应当缴纳土地复垦费而不缴纳的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—应缴复垦费不缴"]},
    {"key": "4-18", "name": "对违法在土地利用总体规划确定的禁止开垦区内进行开垦的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—禁止开垦区开发"]},
    {"key": "4-19", "name": "对擅自将农民集体所有土地使用权出让、转让或出租用于非农业建设的行政处罚", "type": "四、区局处罚主体", "transition": "区局处罚主体，街道协助。", "discretion_keys": ["土地—集体土地擅自用于非农"]},
]

LEGAL_SPLIT_MAP = {
    "1-1": {"reason": ["城乡规划法第40条"], "penalty": ["城乡规划法第64条"]},
    "2-1": {"reason": ["城乡规划法第40条"], "penalty": ["城乡规划法第64条"]},
    "2-2": {"reason": ["城乡规划法第40条"], "penalty": ["城乡规划法第64条"]},
    "2-3": {"reason": ["城市紫线管理办法第2条"], "penalty": ["城乡规划法第64条"]},
    "2-4": {"reason": ["城市蓝线管理办法第10条"], "penalty": ["城乡规划法第64条"]},
    "2-5": {"reason": ["住宅室内装饰装修管理办法第6条"], "penalty": ["城乡规划法第64条"]},
    "2-6": {"reason": ["城市黄线管理办法第2条"], "penalty": ["城乡规划法第64条"]},
    "2-7": {"reason": ["深圳市建筑废弃物管理办法第31条"], "penalty": ["城乡规划法第64条"]},
    "3-1": {"reason": ["土地管理法第44条"], "penalty": ["土地管理法第77条"]},
    "3-2": {"reason": ["土地管理法第37条"], "penalty": ["土地管理法第75条"]},
    "3-3": {"reason": ["城乡规划法第40条", "城乡规划法第44条"], "penalty": ["城乡规划法第64条", "城乡规划法第66条"]},
    "4-1": {"reason": ["城市地下空间开发利用管理规定第30条"], "penalty": ["城乡规划法第64条"]},
    "4-2": {"reason": ["土地复垦条例第13条"], "penalty": ["土地复垦条例第37条"]},
    "4-3": {"reason": ["城市地下空间开发利用管理规定第30条"], "penalty": ["城乡规划法第64条"]},
    "4-4": {"reason": ["土地管理法第65条"], "penalty": ["土地管理法实施条例第53条"]},
    "4-5": {"reason": ["土地复垦条例第17条"], "penalty": ["土地复垦条例第41条"]},
    "4-6": {"reason": ["土地管理法第57条"], "penalty": ["土地管理法实施条例第52条"]},
    "4-7": {"reason": ["土地复垦条例第8条"], "penalty": ["土地复垦条例第43条"]},
    "4-8": {"reason": ["基本农田保护条例第11条"], "penalty": ["基本农田保护条例第32条"]},
    "4-9": {"reason": ["土地管理法第56条"], "penalty": ["土地管理法第81条"]},
    "4-10": {"reason": ["（《土地管理法》第七十四条已含定性）"], "penalty": ["土地管理法第74条"]},
    "4-11": {"reason": ["土地复垦条例第15条"], "penalty": ["土地复垦条例第38条"]},
    "4-12": {"reason": ["土地复垦条例第16条"], "penalty": ["土地复垦条例第39条"]},
    "4-13": {"reason": ["土地管理法第43条"], "penalty": ["土地管理法第76条"]},
    "4-14": {"reason": ["（深圳历史遗留违建处理决定已含情形）"], "penalty": ["深圳历史遗留违法建筑处理决定第10条"]},
    "4-15": {"reason": ["土地管理法第43条"], "penalty": ["土地管理法第76条"]},
    "4-16": {"reason": ["城市地下空间开发利用管理规定第30条"], "penalty": ["城乡规划法第64条"]},
    "4-17": {"reason": ["土地复垦条例第18条"], "penalty": ["土地复垦条例第42条"]},
    "4-18": {"reason": ["土地管理法实施条例第9条"], "penalty": ["土地管理法实施条例第57条"]},
    "4-19": {"reason": ["土地管理法第63条"], "penalty": ["土地管理法第82条"]},
}

_ANN_GUIDE = ["广东省城乡规划条例第86条"]
_ANN_LAND = ["（当事人能够查明并直接送达的，不适用公告调查；无法查明的，依据《广东省城乡规划条例》第八十六条适用公告调查）"]
_ANN_RECORD = ["（义务人已在册，可直接送达；确无法送达的，参照《广东省城乡规划条例》第八十六条适用公告调查）"]
_MOVE_DEFAULT = ["行政处罚法第27条", "行政处罚法第57条"]

EXTRA_SECTIONS_MAP = {
    "1-1": (_ANN_GUIDE, _MOVE_DEFAULT), "2-1": (_ANN_GUIDE, _MOVE_DEFAULT), "2-2": (_ANN_GUIDE, _MOVE_DEFAULT), "2-3": (_ANN_GUIDE, _MOVE_DEFAULT), "2-4": (_ANN_GUIDE, _MOVE_DEFAULT), "2-5": (_ANN_GUIDE, _MOVE_DEFAULT), "2-6": (_ANN_GUIDE, _MOVE_DEFAULT), "2-7": (_ANN_GUIDE, _MOVE_DEFAULT),
    "3-1": (_ANN_LAND, ["行政处罚法第27条", "行政处罚法第57条", "刑法第342条"]), "3-2": (_ANN_LAND, ["行政处罚法第27条", "行政处罚法第57条", "刑法第342条"]), "3-3": (_ANN_GUIDE, _MOVE_DEFAULT),
    "4-1": (_ANN_GUIDE, _MOVE_DEFAULT), "4-2": (_ANN_RECORD, _MOVE_DEFAULT), "4-3": (_ANN_GUIDE, _MOVE_DEFAULT), "4-4": (_ANN_LAND, _MOVE_DEFAULT), "4-5": (_ANN_RECORD, _MOVE_DEFAULT), "4-6": (_ANN_LAND, _MOVE_DEFAULT), "4-7": (_ANN_RECORD, _MOVE_DEFAULT), "4-8": (_ANN_LAND, _MOVE_DEFAULT), "4-9": (_ANN_RECORD, _MOVE_DEFAULT), "4-10": (_ANN_LAND, ["行政处罚法第27条", "行政处罚法第57条", "刑法第228条"]),
    "4-11": (_ANN_RECORD, _MOVE_DEFAULT), "4-12": (_ANN_RECORD, _MOVE_DEFAULT), "4-13": (_ANN_RECORD, _MOVE_DEFAULT), "4-14": (_ANN_GUIDE, _MOVE_DEFAULT), "4-15": (_ANN_RECORD, _MOVE_DEFAULT), "4-16": (_ANN_GUIDE, _MOVE_DEFAULT), "4-17": (_ANN_RECORD, _MOVE_DEFAULT), "4-18": (_ANN_LAND, ["行政处罚法第27条", "行政处罚法第57条", "刑法第342条"]), "4-19": (_ANN_LAND, ["行政处罚法第27条", "行政处罚法第57条", "刑法第228条"]),
}

DISCRETION_STANDARDS = {
    "规划—未取得规划许可证": {"name": "未取得建设工程规划许可证或未按许可证规定进行建设（《城乡规划法》第64条）", "categories": [{"title": "一、尚可采取改正措施", "items": [{"scene": "超面积≤5% 或超高度≤5%", "standard": "责令停止建设、限期改正；并处建设工程造价5%的罚款"}, {"scene": "超面积5%-10%", "standard": "责令停止建设、限期改正；并处建设工程造价7.5%的罚款"}]}, {"title": "二、无法采取改正措施", "items": [{"scene": "违反强制性技术规定或侵占公共用地", "standard": "责令停止建设；限期拆除；不能拆除的，没收实物，可并处10%以下罚款"}]}]},
    "规划—临时建设": {"name": "未经批准/未按内容临时建设/超期不拆（第66条）", "categories": [{"title": "情节较重", "items": [{"scene": "影响规划实施或超期3个月以上", "standard": "责令限期拆除；可并处临时造价1倍罚款"}]}]},
    "规划—地下空间": {"name": "违法建设地下建筑物/擅改地下空间（《广东省城乡规划条例》第79条）", "categories": [{"title": "按危害后果", "items": [{"scene": "造成安全隐患", "standard": "责令停止建设，限期改正，并处造价7.5%罚款"}, {"scene": "造成他人人身财产损失", "standard": "责令停止建设，限期改正，并处造价10%罚款"}]}]},
    "土地—破坏耕地种植条件": {"name": "违法占用耕地破坏种植条件（第75条）", "categories": [{"title": "按破坏面积", "items": [{"scene": "破坏永久基本农田以外的耕地5亩以下", "standard": "责令限期改正或治理；可并处耕地开垦费5倍罚款"}, {"scene": "破坏永久基本农田5亩以上", "standard": "责令限期改正或治理；可并处耕地开垦费8-10倍罚款"}]}]},
    "土地—非法占用土地": {"name": "非法占用土地（第77条）", "categories": [{"title": "按占地类型", "items": [{"scene": "占用建设用地", "standard": "责令退还；可并处100-300元/平米罚款"}, {"scene": "占用永久基本农田", "standard": "责令退还，限期拆除新建建筑物；可并处800-1000元/平米罚款"}]}]},
    "土地—拒不交还土地": {"name": "拒不交还土地/期满不归还（第81条）", "categories": [{"title": "按面积", "items": [{"scene": "不涉及永久基本农田面积不足10亩", "standard": "责令交还；处100-300元/平米罚款"}, {"scene": "涉及永久基本农田5亩以上", "standard": "责令交还；处300-500元/平米罚款"}]}]},
    "土地—买卖或非法转让": {"name": "买卖或以其他形式非法转让土地（第74条）", "categories": [{"title": "按违法所得", "items": [{"scene": "违法所得30万元以下", "standard": "没收违法所得；可并处10%-20%罚款"}, {"scene": "违法所得50万元以上", "standard": "没收违法所得；可并处40%-50%罚款"}]}]},
    "土地—临时用地修永久建筑": {"name": "临时用地上修建永久性建筑（实施条例第52条）", "categories": [{"title": "按占地类型", "items": [{"scene": "占用建设用地", "standard": "责令限期拆除；按面积处复垦费5-6倍罚款"}, {"scene": "占用耕地", "standard": "责令限期拆除；按面积处复垦费8-10倍罚款"}]}]},
}

SITUATIONS = {}
for item in RECYCLED_ITEMS:
    _k = item["key"]
    _split = LEGAL_SPLIT_MAP.get(_k, {})
    _extra = EXTRA_SECTIONS_MAP.get(_k, ([], []))
    SITUATIONS[_k] = {
        "name": item["name"], "type": item["type"], "transition": item["transition"],
        "discretion_keys": item.get("discretion_keys", []),
        "legal_sections": {"处罚理由": _split.get("reason", []), "处罚依据": _split.get("penalty", [])},
        "extra_sections": {"公告调查依据": _extra[0], "移送依据": _extra[1]}
    }

DEFAULT_SECTIONS = {"协助调查通知依据": ["行政处罚法第54条", "行政处罚法第55条"]}

# ============================================================
# 三、文本切分与引用提取引擎（完美复刻电脑端）
# ============================================================
ARTICLE_PATTERN = re.compile(r'第([零一二三四五六七八九十百千万\d]+)条')
ARTICLE_REF_PATTERN = re.compile(r'第[零一二三四五六七八九十百千万\d]+条(?:第[零一二三四五六七八九十百千万\d]+款)?(?:第[零一二三四五六七八九十百千万\d]+项)?')
TOP_LEVEL_ITEM_PATTERN = re.compile(r'(?:^|\n)([\s\u3000]*[零一二三四五六七八九十百]+、)')

REF_PREFIXES = ['违反本条例', '违反本例', '违反本法', '违反本规定', '违反本办法', '根据本条例', '根据本例', '根据本法', '根据本规定', '根据本办法', '依照本条例', '依照本法', '依照本规定', '依照本办法', '按照本条例', '按照本法', '按照本规定', '按照本办法', '符合本条例', '依据本条例', '依据本法', '本条例', '本法', '本规定', '本办法', '该条例', '该法', '该规定', '该办法', '违反']
PARALLEL_REF_PATTERN = re.compile(r'第[零一二三四五六七八九十百千万\d]+条[、,，]$')
_MOD_PREFIX_WORDS = ['将', '作为', '修改', '删去', '删除', '改为', '增加']
_MOD_SUFFIX_WORDS = ['修改为', '修改', '删去', '删除', '改为', '作以下', '进行修改']
_MOD_SUFFIX_STRICT = ['增加一条', '增加一款', '增加一项', '增加规定', '增加以下']
_SEP_CHARS = set('。！？；，、：:.,;!?"\'《》（）()【】[]{}\n\r\t \u3000')

def strip_whitespace(s):
    if not isinstance(s, str): return ''
    return re.sub(r'[\s\u3000]+', '', s)

def is_likely_reference(text, match_start):
    if match_start < 1: return False
    prev_char = text[match_start - 1]
    if prev_char and not prev_char.isspace() and prev_char not in _SEP_CHARS: return True
    lookbehind = text[max(0, match_start - 60):match_start]
    lookbehind_stripped = strip_whitespace(lookbehind)
    for p in REF_PREFIXES:
        if lookbehind_stripped.endswith(p): return True
    if PARALLEL_REF_PATTERN.search(lookbehind_stripped): return True
    if '》' in lookbehind_stripped:
        last_close = lookbehind_stripped.rfind('》')
        between = lookbehind_stripped[last_close + 1:]
        if not any(ch in between for ch in '。！？；，,、'): return True
    return False

def _looks_like_modification_ref(text, pos):
    before = strip_whitespace(text[max(0, pos - 8):pos])
    if any(w in before for w in _MOD_PREFIX_WORDS): return True
    after = strip_whitespace(text[pos:pos + 40])
    for w in _MOD_SUFFIX_WORDS:
        if w in after: return True
    for w in _MOD_SUFFIX_STRICT:
        if w in after: return True
    return False

def _is_inline_article_ref(text, curr_start, prev_end):
    if prev_end < 0: return False
    between = text[prev_end:curr_start]
    return strip_whitespace(between) == ''

def get_segment_boundaries(text):
    if not isinstance(text, str) or not text: return []
    boundaries = set()
    for m in TOP_LEVEL_ITEM_PATTERN.finditer(text): boundaries.add(m.start(1))
    for m in ARTICLE_PATTERN.finditer(text):
        if is_likely_reference(text, m.start()): continue
        if _looks_like_modification_ref(text, m.start()): continue
        boundaries.add(m.start())
    return sorted(boundaries)

def split_into_segments(text):
    if not isinstance(text, str) or not text: return [text] if isinstance(text, str) else []
    boundaries = get_segment_boundaries(text)
    if not boundaries: return [text]
    segments = []
    if boundaries[0] > 0:
        head = text[:boundaries[0]]
        if head.strip(): segments.append(head)
    for i, b in enumerate(boundaries):
        end = boundaries[i + 1] if i + 1 < len(boundaries) else len(text)
        seg = text[b:end]
        if seg.strip(): segments.append(seg)
    return segments

def find_article_definitions(text, article_ref, max_results=3):
    if not isinstance(text, str) or not text or not article_ref: return []
    m = re.match(r'第([零一二三四五六七八九十百千万\d]+)条', article_ref)
    if not m: return []
    target_num_str = m.group(1)
    
    all_matches = list(ARTICLE_PATTERN.finditer(text))
    candidates = [mm for mm in all_matches if not is_likely_reference(text, mm.start()) and not _looks_like_modification_ref(text, mm.start())]
    article_starts = []
    prev_end = -1
    for mm in candidates:
        if _is_inline_article_ref(text, mm.start(), prev_end): continue
        article_starts.append(mm)
        prev_end = mm.end()
        
    results = []
    for i, match in enumerate(article_starts):
        num_str = match.group(1)
        if num_str != target_num_str: continue
        start = match.start()
        end = article_starts[i + 1].start() if i + 1 < len(article_starts) else len(text)
        article_text = text[start:end].strip()
        if article_text:
            results.append(article_text)
            if len(results) >= max_results: break
    return results

def find_referenced_articles_in_hit(text, keyword):
    if not isinstance(text, str) or not text: return []
    kw = strip_whitespace(keyword).lower()
    if not kw: return []
    segments = split_into_segments(text)
    refs = []
    seen_nums = set()
    for seg in segments:
        if kw not in strip_whitespace(seg).lower(): continue
        for rm in ARTICLE_REF_PATTERN.finditer(seg):
            if not is_likely_reference(seg, rm.start()): continue
            base_m = re.match(r'第([零一二三四五六七八九十百千万\d]+)条', rm.group(0))
            if not base_m: continue
            base_num_str = base_m.group(1)
            if base_num_str in seen_nums: continue
            seen_nums.add(base_num_str)
            refs.append(f"第{base_num_str}条")
    return refs

def extract_context_blocks_fallback(text, keyword):
    parts = re.split(r'(。|！|？|；|\n)', text)
    sentences = []
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and parts[i + 1] in '。！？；\n':
            sentences.append((parts[i] + parts[i + 1]).strip())
            i += 2
        else:
            sentences.append(parts[i].strip())
            i += 1
    sentences = [s for s in sentences if s]
    blocks = []
    kw = keyword.lower()
    for sent in sentences:
        if kw in sent.lower():
            blocks.append(sent)
    return blocks

def extract_matching_articles(text, keyword, max_items=20):
    if not isinstance(text, str): return []
    kw = strip_whitespace(keyword).lower()
    if not kw: return []
    segments = split_into_segments(text)
    if not segments: return extract_context_blocks_fallback(text, keyword)
    items = []
    for seg in segments:
        if kw in strip_whitespace(seg).lower():
            items.append(seg.strip())
            if len(items) >= max_items: break
    if not items: return extract_context_blocks_fallback(text, keyword)
    return items

# ============================================================
# 四、安全文本处理、高亮与搜索逻辑
# ============================================================
CSV_DATA = []

def escape_markup(text):
    if not text: return ""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text.replace('[', '&#91;').replace(']', '&#93;')

def highlight_text(text, keyword):
    """绝对安全的关键词高亮：先用不可见字符包裹，再统一转义"""
    if not keyword or not text: return text
    # 用特殊标记包住关键词
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    marked = pattern.sub(f"__HL_START__{keyword}__HL_END__", text)
    
    # 统一转义特殊字符
    safe_text = escape_markup(marked)
    
    # 替换标记为 Kivy 颜色标签
    safe_text = safe_text.replace("__HL_START__", "[color=#d93025][b]")
    safe_text = safe_text.replace("__HL_END__", "[/b][/color]")
    
    return safe_text

def clean_html(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.replace('&nbsp;', ' ').strip()

def load_bundled_csv():
    target_file = "laws.csv"
    if not os.path.exists(target_file):
        found = resource_find("laws.csv")
        if found: target_file = found
        else: target_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laws.csv")
    if not os.path.exists(target_file): return 0, "未找到 laws.csv"

    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb18030']
    for enc in encodings:
        try:
            with open(target_file, "r", encoding=enc, errors="ignore") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames: continue
                col_map = {}
                for col in reader.fieldnames:
                    col_clean = col.strip()
                    if '序号' in col_clean: col_map['序号'] = col
                    elif '网址' in col_clean: col_map['网址'] = col
                    elif '名称' in col_clean and '名称' not in col_map: col_map['名称'] = col
                    elif '发布日期' in col_clean: col_map['发布日期'] = col
                    elif '文号' in col_clean: col_map['文号'] = col
                    elif '正文' in col_clean or '内容' in col_clean: col_map['正文'] = col
                
                if '正文' not in col_map: continue

                count = 0
                CSV_DATA.clear()
                for row in reader:
                    body = clean_html(row.get(col_map['正文'], ''))
                    if not body: continue
                    CSV_DATA.append({
                        '序号': row.get(col_map.get('序号', ''), '').strip(),
                        '名称': row.get(col_map.get('名称', ''), '').strip(),
                        '文号': row.get(col_map.get('文号', ''), '').strip(),
                        '发布日期': row.get(col_map.get('发布日期', ''), '').strip(),
                        '网址': row.get(col_map.get('网址', ''), '').strip(),
                        '正文': body
                    })
                    count += 1
                return count, f"OK ({enc})"
        except Exception: continue
    return 0, "解析失败"

def get_provision(key):
    if key in LEGAL_PROVISIONS: return LEGAL_PROVISIONS[key]
    return {"law": key, "article": "", "content": "（原文请使用搜索功能查法规库）"}

def build_report_text(situation_key, keyword=""):
    sit = SITUATIONS.get(situation_key)
    if not sit: return "未找到该情形。"
    
    lines = [f"【情形编号】{situation_key}", f"【情形名称】{sit['name']}", f"【所属分类】{sit['type']}", f"【过渡期建议】{sit['transition']}\n"]
    
    ann = sit["extra_sections"].get("公告调查依据", [])
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
        if k.startswith("（"): lines.append("  " + k); continue
        p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
    lines.append("")

    lines.append("【处罚依据】")
    for k in sit["legal_sections"].get("处罚依据", []):
        p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
    lines.append("")

    move = sit["extra_sections"].get("移送依据", [])
    if move:
        lines.append("【移送依据】")
        for k in move: 
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
                    lines.append(f"      - 情形：{item['scene']} -> {item['standard']}")
                    
    raw_text = "\n".join(lines)
    return highlight_text(raw_text, keyword)

def search_all(keyword):
    kw = keyword.strip()
    if not kw: return "请输入关键词。"
    raw_results = []
    
    for k, v in LEGAL_PROVISIONS.items():
        if kw in k or kw in v['content']:
            raw_results.append(f"📄【内置法条】{v['law']}{v['article']}\n{v['content']}\n")
            
    kw_stripped = strip_whitespace(kw).lower()
    for row in CSV_DATA:
        name = row.get('名称', '')
        doc_no = row.get('文号', '')
        content = row.get('正文', '')
        
        if kw_stripped in strip_whitespace(name).lower() or kw_stripped in strip_whitespace(doc_no).lower() or kw_stripped in strip_whitespace(content).lower():
            # 提取整段！而不是被切断的句子
            blocks = extract_matching_articles(content, kw)
            if not blocks:
                continue
                
            refs = find_referenced_articles_in_hit(content, kw)
            ref_contents = []
            for ref in refs:
                contents = find_article_definitions(content, ref, max_results=3)
                if contents:
                    ref_contents.append({'ref': ref, 'contents': [{'content': c} for c in contents]})
            
            text = ""
            if row.get('序号'): text += f"序号：{row['序号']}　"
            if name: text += f"名称：{name}　"
            if doc_no: text += f"文号：{doc_no}　"
            if row.get('发布日期'): text += f"发布日期：{row['发布日期']}\n"
            if row.get('网址'): text += f"网址：{row['网址']}\n"
            
            for i, b in enumerate(blocks):
                text += f"  {i+1}. {b}\n"
                
            if ref_contents:
                text += "【引用条款内容】\n"
                for r in ref_contents:
                    text += f"▶ {r['ref']}\n"
                    for c in r['contents']:
                        text += f"{c['content']}\n"
            
            raw_results.append(text + "\n")

    if not raw_results:
        return f"未找到包含「{kw}」的法条或政策文件。"
    
    limit = 50
    final_text = f"【搜索关键词】{kw} (共匹配 {len(raw_results)} 条)\n\n"
    final_text += "\n".join(raw_results[:limit])
    if len(raw_results) > limit:
        final_text += f"\n\n... (仅显示前{limit}条)"
        
    return highlight_text(final_text, keyword)

# ============================================================
# 五、UI 界面
# ============================================================
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(8), **kwargs)
        self.add_widget(Label(text="[b]规划土地执法法律依据查询[/b]", markup=True, size_hint_y=None, height=dp(40), font_size=dp(18), color=(0, 0, 0, 1)))

        row1 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        row1.add_widget(Label(text="情形：", size_hint_x=None, width=dp(60), color=(0, 0, 0, 1)))
        vals = [f"{k}｜{v['name'][:15]}..." for k, v in SITUATIONS.items()]
        self.spinner = Spinner(text="请选择执法事项", values=vals, size_hint_x=1, background_color=(0.8, 0.8, 0.8, 1), color=(0, 0, 0, 1))
        row1.add_widget(self.spinner)
        self.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.search_input = TextInput(hint_text="搜法条或CSV政策(如:搭建)", multiline=False, foreground_color=(0, 0, 0, 1), background_color=(1, 1, 1, 1))
        btn_search = Button(text="搜索", size_hint_x=None, width=dp(80), background_color=(0.2, 0.6, 1, 1))
        btn_search.bind(on_release=self.on_search)
        row2.add_widget(self.search_input)
        row2.add_widget(btn_search)
        self.add_widget(row2)

        row3 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        b1 = Button(text="查询该情形", background_color=(0.2, 0.8, 0.2, 1)); b1.bind(on_release=self.on_query_situation)
        b2 = Button(text="一键复制全部", background_color=(0.8, 0.5, 0.2, 1)); b2.bind(on_release=self.on_copy_result)
        row3.add_widget(b1)
        row3.add_widget(b2)
        self.add_widget(row3)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.result_label = Label(text="正在初始化数据，请稍候...", size_hint_y=None, markup=True, halign="left", valign="top", color=(0, 0, 0, 1))
        self.result_label.bind(texture_size=self._update_label_height)
        self.result_label.text_size = (Window.width - dp(40), None)
        Window.bind(size=self._on_window_size)
        self.scroll.add_widget(self.result_label)
        self.add_widget(self.scroll)
        
        self.current_raw_text = "" 

    def _update_label_height(self, *args):
        self.result_label.height = self.result_label.texture_size[1] + dp(20)

    def _on_window_size(self, *args):
        self.result_label.text_size = (Window.width - dp(40), None)
        self._update_label_height()

    def show_text(self, txt, raw_txt):
        self.result_label.text = txt
        self.current_raw_text = raw_txt
        self.result_label.texture_update()
        self.result_label.height = self.result_label.texture_size[1] + dp(20)
        self.scroll.scroll_y = 1

    def on_query_situation(self, *args):
        sel = self.spinner.text
        if "｜" not in sel: return
        kw = self.search_input.text.strip()
        key = sel.split("｜", 1)[0]
        
        # 纯文本用于复制（无格式）
        sit = SITUATIONS.get(key)
        raw_lines = [f"【情形编号】{key}", f"【情形名称】{sit['name']}"]
        for k in sit["legal_sections"].get("处罚理由", []):
            p = get_provision(k); raw_lines.append(f"· {p['law']}{p['article']}：{p['content']}")
        self.current_raw_text = "\n".join(raw_lines)
        
        # 带高亮的富文本用于显示
        highlighted = build_report_text(key, kw)
        self.result_label.text = highlighted
        self.result_label.texture_update()
        self.result_label.height = self.result_label.texture_size[1] + dp(20)
        self.scroll.scroll_y = 1

    def on_search(self, *args):
        kw = self.search_input.text.strip()
        if not kw: return
        
        # 获取纯文本用于复制（移除高亮标签）
        raw_text = search_all(kw).replace("[color=#d93025][b]", "").replace("[/b][/color]", "")
        # 获取带高亮的富文本用于显示
        display_text = search_all(kw)
        
        self.show_text(display_text, raw_text)

    def on_copy_result(self, *args):
        Clipboard.copy(self.current_raw_text)
        self.result_label.text = "[color=#008000][b]✅ 已复制到剪贴板！[/b][/color]\n\n" + self.result_label.text
        self.current_raw_text = "✅ 已复制到剪贴板！\n\n" + self.current_raw_text

class LawApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        def init_load(dt):
            count, status = load_bundled_csv()
            msg = f"系统初始化完成！\n已加载 {len(SITUATIONS)} 项完整执法情形。\nCSV数据加载状态：{status}\n共加载 {count} 条政策法规数据。\n\n请在上方选择情形或输入关键词搜索。"
            self.root.show_text(msg, msg)
        Clock.schedule_once(init_load, 0.5)
        return MainScreen()

if __name__ == "__main__":
    LawApp().run()
