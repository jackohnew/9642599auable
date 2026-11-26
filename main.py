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
# 一、法律依据核心库（全量无省略号）
# ============================================================
LEGAL_PROVISIONS = {
    "城乡规划法第40条": {"law": "《中华人民共和国城乡规划法》", "article": "第四十条第一款", "content": "在城市、镇规划区内进行建筑物、构筑物、道路、管线和其他工程建设的，建设单位或者个人应当向城市、县人民政府城乡规划主管部门或者省、自治区、直辖市人民政府确定的镇人民政府申请办理建设工程规划许可证。"},
    "城乡规划法第64条": {"law": "《中华人民共和国城乡规划法》", "article": "第六十四条", "content": "未取得建设工程规划许可证或者未按照建设工程规划许可证的规定进行建设的，由县级以上地方人民政府城乡规划主管部门责令停止建设；尚可采取改正措施消除对规划实施的影响的，限期改正，处建设工程造价百分之五以上百分之十以下的罚款；无法采取改正措施消除影响的，限期拆除，不能拆除的，没收实物或者违法收入，可以并处建设工程造价百分之十以下的罚款。"},
    "城乡规划法第66条": {"law": "《中华人民共和国城乡规划法》", "article": "第六十六条", "content": "建设单位或者个人有下列行为之一的，由所在地城市、县人民政府城乡规划主管部门责令限期拆除，可以并处临时建设工程造价一倍以下的罚款：（一）未经批准进行临时建设的；（二）未按照批准内容进行临时建设的；（三）临时建筑物、构筑物超过批准期限不拆除的。"},
    "城市蓝线管理办法第10条": {"law": "《城市蓝线管理办法》", "article": "第十条", "content": "在城市蓝线内禁止进行下列活动：（一）违反城市蓝线保护和控制要求的建设活动；（二）擅自填埋、占用城市蓝线内水域；（三）影响水系安全的爆破、采石、取土；（四）擅自建设各类排污设施；（五）其它对城市水系保护构成破坏的活动。"},
    "城市紫线管理办法第2条": {"law": "《城市紫线管理办法》", "article": "第二条", "content": "本办法所称城市紫线，是指国家历史文化名城内的历史文化街区和省、自治区、直辖市人民政府公布的历史文化街区的保护范围界线，以及历史文化街区外经县级以上人民政府公布保护的历史建筑的保护范围界线。"},
    "城市黄线管理办法第2条": {"law": "《城市黄线管理办法》", "article": "第二条", "content": "本办法所称城市黄线，是指对城市发展全局有影响的、城市规划中确定的、必须控制的城市基础设施用地的控制界线。"},
    "住宅室内装饰装修管理办法第6条": {"law": "《住宅室内装饰装修管理办法》", "article": "第六条", "content": "装修人从事住宅室内装饰装修活动，未经批准，不得有下列行为：（一）搭建建筑物、构筑物；（二）改变住宅外立面，在非承重外墙上开门、窗；（三）拆改供暖管道和设施；（四）拆改燃气管道和设施。本条所列第（一）项、第（二）项行为，应当经城市规划行政主管部门批准。"},
    "土地管理法第77条": {"law": "《中华人民共和国土地管理法》", "article": "第七十七条", "content": "未经批准或者采取欺骗手段骗取批准，非法占用土地的，由县级以上人民政府自然资源主管部门责令退还非法占用的土地，对违反土地利用总体规划擅自将农用地改为建设用地的，限期拆除在非法占用的土地上新建的建筑物和其他设施，恢复土地原状，对符合土地利用总体规划的，没收在非法占用的土地上新建的建筑物和其他设施，可以并处罚款；构成犯罪的，依法追究刑事责任。"},
    "土地管理法第75条": {"law": "《中华人民共和国土地管理法》", "article": "第七十五条", "content": "违反本法规定，占用耕地建窑、建坟或者擅自在耕地上建房、挖砂、采石、采矿、取土等，破坏种植条件的，或者因开发土地造成土地荒漠化、盐渍化的，由县级以上人民政府自然资源主管部门、农业农村主管部门等按照职责责令限期改正或者治理，可以并处罚款；构成犯罪的，依法追究刑事责任。"},
    "行政处罚法第27条": {"law": "《中华人民共和国行政处罚法》", "article": "第二十七条", "content": "违法行为涉嫌犯罪的，行政机关应当及时将案件移送司法机关，依法追究刑事责任。对依法不需要追究刑事责任或者免予刑事处罚，但应当给予行政处罚的，司法机关应当及时将案件移送有关行政机关。"},
    "行政处罚法第44条": {"law": "《中华人民共和国行政处罚法》", "article": "第四十四条", "content": "行政机关在作出行政处罚决定之前，应当告知当事人拟作出的行政处罚内容及事实、理由、依据，并告知当事人依法享有的陈述、申辩、要求听证等权利。"},
    "行政处罚法第45条": {"law": "《中华人民共和国行政处罚法》", "article": "第四十五条", "content": "当事人有权进行陈述和申辩。行政机关必须充分听取当事人的意见，对当事人提出的事实、理由和证据，应当进行复核；当事人提出的事实、理由或者证据成立的，行政机关应当采纳。行政机关不得因当事人陈述、申辩而给予更重的处罚。"},
    "行政处罚法第54条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十四条", "content": "除本法第五十一条规定的可以当场作出的行政处罚外，行政机关发现公民、法人或者其他组织有依法应当给予行政处罚的行为的，必须全面、客观、公正地调查，收集有关证据；必要时，依照法律、法规的规定，可以进行检查。符合立案标准的，行政机关应当及时立案。"},
    "行政处罚法第55条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十五条", "content": "执法人员在调查或者进行检查时，应当主动向当事人或者有关人员出示执法证件。当事人或者有关人员有权要求执法人员出示执法证件。执法人员不出示执法证件的，当事人或者有关人员有权拒绝接受调查或者检查。"},
    "行政处罚法第57条": {"law": "《中华人民共和国行政处罚法》", "article": "第五十七条", "content": "调查终结，行政机关负责人应当对调查结果进行审查，根据不同情况，分别作出如下决定：（一）确有应受行政处罚的违法行为的，根据情节轻重及具体情况，作出行政处罚决定；（二）违法行为轻微，依法可以不予行政处罚的，不予行政处罚；（三）违法事实不能成立的，不予行政处罚；（四）违法行为涉嫌犯罪的，移送司法机关。"},
    "行政处罚法第63条": {"law": "《中华人民共和国行政处罚法》", "article": "第六十三条", "content": "行政机关拟作出下列行政处罚决定，应当告知当事人有要求听证的权利，当事人要求听证的，行政机关应当组织听证：（一）较大数额罚款；（二）没收较大数额违法所得、没收较大价值非法财物；（三）降低资质等级、吊销许可证件；（四）责令停产停业、责令关闭、限制从业；（五）其他较重的行政处罚；（六）法律、法规、规章规定的其他情形。"},
    "行政强制法第22条": {"law": "《中华人民共和国行政强制法》", "article": "第二十二条", "content": "查封、扣押应当由法律、法规规定的行政机关实施，其他任何行政机关或者组织不得实施。"},
    "行政强制法第24条": {"law": "《中华人民共和国行政强制法》", "article": "第二十四条", "content": "行政机关决定实施查封、扣押的，应当履行本法第十八条规定的程序，制作并当场交付查封、扣押决定书和清单。"},
    "行政强制法第25条": {"law": "《中华人民共和国行政强制法》", "article": "第二十五条", "content": "查封、扣押的期限不得超过三十日；情况复杂的，经行政机关负责人批准，可以延长，但是延长期限不得超过三十日。法律、行政法规另有规定的除外。"},
    "行政强制法第44条": {"law": "《中华人民共和国行政强制法》", "article": "第四十四条", "content": "对违法的建筑物、构筑物、设施等需要强制拆除的，应当由行政机关予以公告，限期当事人自行拆除。当事人在法定期限内不申请行政复议或者提起行政诉讼，又不拆除的，行政机关可以依法强制拆除。"},
    "行政强制法第53条": {"law": "《中华人民共和国行政强制法》", "article": "第五十三条", "content": "当事人在法定期限内不申请行政复议或者提起行政诉讼，又不履行行政决定的，没有行政强制执行权的行政机关可以自期限届满之日起三个月内，依照本章规定申请人民法院强制执行。"},
    "特区条例第24条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第二十四条", "content": "在案件办理过程中，规划土地监察机构可以向当事人、证人发出调查询问通知书，通知当事人在规定期限内接受调查询问。监察人员可以询问案件当事人、证人，并制作笔录。笔录经核对无误后由监察人员和被询问人员分别签名或者盖章；被询问人拒绝签名或者盖章的，监察人员应当在笔录上予以注明。"},
    "特区条例第39条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第三十九条", "content": "对涉及规划违法行为或者土地违法行为的房地产，规划土地监察机构可以作出决定，限制其首次登记或者转移、抵押登记。不动产登记机构收到规划土地监察机构限制房地产权利的决定后应当及时办理。违法状态消除或者当事人履行有关行政处罚决定后，规划土地监察机构应当作出决定，并及时通知不动产登记机构解除对有关房地产的权利限制。"},
    "特区条例第40条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第四十条", "content": "规划土地监察机构在查处违法行为过程中，对与违法行为有直接关系的场所、设施或者财物，可以依法实施查封、扣押等行政强制措施。"},
    "特区条例第43条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第四十三条", "content": "查封、扣押的期限不得超过三十日；情况复杂的，经规划土地监察机构负责人批准，可以延长，但是延长期限不得超过三十日。法律、行政法规另有规定的除外。"},
    "特区条例第44条": {"law": "《深圳经济特区规划土地监察条例》", "article": "第四十四条", "content": "当事人对行政处罚决定逾期不履行的，规划土地监察机构应当依法催告当事人履行义务。经催告，当事人仍不履行，且未在法定期限内申请行政复议或者提起行政诉讼的，按照下列方式分别处理：（一）依照城市规划法律、法规、规章作出的限期拆除行政处罚，由违法建筑物、构筑物、设施所在区的规划土地监察机构作出行政强制执行决定予以拆除；依照土地管理法律、法规、规章作出的限期拆除行政处罚，由作出处罚决定的规划土地监察机构申请人民法院强制执行。（二）其他行政处罚，由作出处罚决定的规划土地监察机构申请人民法院强制执行。规划土地监察机构应当在申请行政复议的法定期限或者提起行政诉讼的法定期限届满之日起三个月内申请人民法院强制执行；当事人对行政处罚决定提起行政复议或者行政诉讼的，规划土地监察机构应当在行政复议决定或者人民法院裁判文书生效之日起三个月内申请人民法院强制执行。"},
    "广东省听证办法第6条": {"law": "《广东省行政处罚听证程序实施办法》", "article": "第六条", "content": "行政机关作出下列行政处罚决定之前，应当告知当事人有要求举行听证的权利；当事人要求听证的，行政机关应当组织听证：（一）较大数额罚款；（二）没收较大数额违法所得、没收较大价值非法财物；（三）降低资质等级、吊销许可证件；（四）责令停产停业、责令关闭、限制从业；（五）其他较重的行政处罚；（六）法律、法规、规章规定的其他情形。"},
    "广东省听证办法第7条": {"law": "《广东省行政处罚听证程序实施办法》", "article": "第七条", "content": "第六条所称较大数额罚款、较大数额违法所得、较大价值非法财物，是指对公民的违法行为处以5000元以上罚款（等价值违法所得或者非法财物），对法人或者其他组织的违法行为处以10万元以上罚款（等价值违法所得或者非法财物）。部门规章对前款规定的数额有更低规定的，从其规定。"},
    "广东省城乡规划条例第86条": {"law": "《广东省城乡规划条例》", "article": "第八十六条第一款", "content": "违反本条例规定，未依法取得有关规划许可证的在建或者建成项目，对无法确定建设单位或者个人的，城市、县人民政府城乡规划主管部门应当在报纸等公共媒体和违法建设项目现场予以公告，告知建设单位或者个人依法接受处理，公告期限不少于三十日。无法确定建设单位或者个人的违法建设项目不及时拆除可能影响安全、交通等的，可以在向公证机关办理证据保全手续后予以强制拆除。"}
}

# ============================================================
# 二、30项完整情形
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
    "规划—地下空间": {"name": "违法建设地下建筑物/擅改地下空间", "categories": [{"title": "按危害后果", "items": [{"scene": "造成安全隐患", "standard": "责令停止建设，限期改正，并处造价7.5%罚款"}, {"scene": "造成他人人身财产损失", "standard": "责令停止建设，限期改正，并处造价10%罚款"}]}]},
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

DEFAULT_SECTIONS = {
    "协助调查通知依据": ["行政处罚法第54条", "行政处罚法第55条", "特区条例第24条"],
    "听证依据": ["行政处罚法第63条", "广东省听证办法第6条", "广东省听证办法第7条"],
    "申诉依据": ["行政处罚法第44条", "行政处罚法第45条"],
    "查封依据": ["行政强制法第22条", "行政强制法第24条", "特区条例第40条"],
    "延长查封期限依据": ["行政强制法第25条", "特区条例第43条"],
    "限制房产权利依据": ["特区条例第39条"],
    "解除房产权利依据": ["特区条例第39条"],
    "强制执行依据": ["行政强制法第44条", "行政强制法第53条", "特区条例第44条"]
}

NO_SEIZURE = {"4-2", "4-5", "4-7", "4-8", "4-9", "4-11", "4-12", "4-13", "4-15", "4-17", "4-18", "4-19"}
NO_PROP = {"4-2", "4-5", "4-7", "4-8", "4-9", "4-10", "4-11", "4-12", "4-13", "4-15", "4-17", "4-18", "4-19"}

# ============================================================
# 三、文本切分与CSV加载引擎
# ============================================================
CSV_DATA = []
CSV_HEADERS = []

def clean_html(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.replace('&nbsp;', ' ').strip()

def splitIntoSegments(text):
    if not text: return []
    pattern = re.compile(r'第[零一二三四五六七八九十百千万\d]+条')
    starts = [m.start() for m in pattern.finditer(text)]
    if not starts: return [text]
    segments = []
    if starts[0] > 0: segments.append(text[:starts[0]])
    for i in range(len(starts)):
        end = starts[i+1] if i+1 < len(starts) else len(text)
        segments.append(text[starts[i]:end])
    return segments

def extractContextBlocks(text, kw):
    blocks = []
    segs = splitIntoSegments(text)
    for seg in segs:
        if kw in seg: blocks.append(seg.strip())
    if not blocks: 
        parts = re.split(r'[。！？；\n]', text)
        for p in parts:
            if kw in p: blocks.append(p.strip())
    return blocks

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
                global CSV_HEADERS
                CSV_HEADERS = [h.strip() for h in reader.fieldnames]
                count = 0
                CSV_DATA.clear()
                for row in reader:
                    clean_row = {k.strip(): clean_html(v) for k, v in row.items() if k and v}
                    if clean_row: CSV_DATA.append(clean_row); count += 1
                return count, f"OK ({enc})"
        except Exception: continue
    return 0, "解析失败"

def get_provision(key):
    if key in LEGAL_PROVISIONS: return LEGAL_PROVISIONS[key]
    return {"law": key, "article": "", "content": "（原文请在搜索框检索）"}

# ============================================================
# 四、逻辑查询与拼装
# ============================================================
def query_situation_text(key):
    sit = SITUATIONS.get(key)
    if not sit: return "未找到该情形。"
    
    lines = [f"【情形编号】{key}", f"【情形名称】{sit['name']}", f"【所属分类】{sit['type']}", f"【过渡期建议】{sit['transition']}\n"]
    
    if sit["extra_sections"].get("公告调查依据"):
        lines.append("【公告调查依据】")
        for k in sit["extra_sections"]["公告调查依据"]:
            if k.startswith("（"): lines.append(f"  {k}")
            else:
                p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
        lines.append("")

    for sec in ["协助调查通知依据", "处罚理由", "处罚依据", "听证依据", "申诉依据"]:
        lines.append(f"【{sec}】")
        if sec in ["处罚理由", "处罚依据"]:
            keys = sit["legal_sections"].get(sec, [])
        else:
            keys = DEFAULT_SECTIONS.get(sec, [])
        for k in keys:
            if k.startswith("（"): lines.append(f"  {k}"); continue
            p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
        lines.append("")

    if key not in NO_SEIZURE:
        for sec in ["查封依据", "延长查封期限依据"]:
            lines.append(f"【{sec}】")
            for k in DEFAULT_SECTIONS[sec]:
                p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
            lines.append("")

    if key not in NO_PROP:
        for sec in ["限制房产权利依据", "解除房产权利依据"]:
            lines.append(f"【{sec}】")
            for k in DEFAULT_SECTIONS[sec]:
                p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
            lines.append("")

    lines.append("【强制执行依据】")
    for k in DEFAULT_SECTIONS["强制执行依据"]:
        p = get_provision(k); lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
    lines.append("")

    if sit["extra_sections"].get("移送依据"):
        lines.append("【移送依据】")
        for k in sit["extra_sections"]["移送依据"]: 
            p = get_provision(k)
            if "未内置" not in p["content"]: lines.append(f"  · {p['law']}{p['article']}：{p['content']}")
            else: lines.append(f"  · {k}")
        lines.append("")

    lines.append("【裁量标准（简略版内置）】")
    for dk in sit.get("discretion_keys", []):
        std = DISCRETION_STANDARDS.get(dk)
        if std:
            lines.append(f"  ◆ {std['name']}")
            for cat in std["categories"]:
                lines.append(f"    ● {cat['title']}")
                for item in cat["items"]:
                    lines.append(f"      - 情形：{item['scene']} -> {item['standard']}")
                    
    # 【核心联动】：去CSV里把详尽的裁量基准、违法情节挖出来
    sit_name = sit["name"]
    search_terms = []
    if "未取得" in sit_name or "未按" in sit_name:
        search_terms = ["未取得建设工程规划许可证", "未按照建设工程规划许可证", "未取得规划许可证", "未按照规划许可证"]
    elif "装饰装修" in sit_name: search_terms = ["装饰装修", "外立面"]
    elif "非法占用" in sit_name: search_terms = ["非法占用土地"]
    elif "临时用地" in sit_name: search_terms = ["临时用地"]
    elif "复垦" in sit_name: search_terms = ["复垦"]
    elif "买卖" in sit_name or "转让" in sit_name: search_terms = ["买卖", "非法转让"]
    else: search_terms = [sit_name[:6]]

    hit_rows = []
    for r in CSV_DATA:
        row_text = "".join([str(v) for v in r.values()])
        if any(term in row_text for term in search_terms):
            # 加上这个判断，确保抓取到的是裁量基准表里的数据，而不是整部法规原文
            if "裁量基准" in row_text or "违法情节" in row_text or "裁量档次" in row_text:
                # 简单去重
                if not any(hr.get("序号") == r.get("序号") and hr.get("违法违规行为") == r.get("违法违规行为") for hr in hit_rows):
                    hit_rows.append(r)
            
    if hit_rows:
        lines.append("\n【来自政策库的详尽裁量基准与情节】")
        for i, r in enumerate(hit_rows[:5]): # 最多抓5条详表
            lines.append(f"◆ 详细记录 {i+1}")
            if r.get("序号"): lines.append(f"序号：{r['序号']}")
            if r.get("名称"): lines.append(f"来源：{r['名称']}")
            if r.get("发布日期"): lines.append(f"发布日期：{r['发布日期']}")
            if r.get("文号"): lines.append(f"文号：{r['文号']}")
            if r.get("网址"): lines.append(f"网址：{r['网址']}")
            
            for k, v in r.items():
                if k in ["序号", "名称", "发布日期", "文号", "网址"]: continue
                if not v: continue
                if len(v) > 3000: continue # 过滤过长的法律原文
                
                if len(v) > 50 and "第" in v and "条" in v:
                    blocks = splitIntoSegments(v)
                    lines.append(f"  {k}：")
                    for b in blocks:
                        lines.append(f"    {b}")
                else:
                    lines.append(f"  {k}：{v}")
            lines.append("")
            
    return "\n".join(lines)

def search_all_text(keyword):
    kw = keyword.strip()
    if not kw: return "请输入关键词。"
    raw_results = []
    
    # 1. 搜 CSV 数据库 (优先展示详细数据)
    for row in CSV_DATA:
        row_text = "".join([str(v) for v in row.values()])
        if kw in row_text:
            text = ""
            # 优先展示元数据
            if row.get("序号"): text += f"序号：{row['序号']}\n"
            if row.get("名称"): text += f"名称：{row['名称']}\n"
            if row.get("发布日期"): text += f"发布日期：{row['发布日期']}\n"
            if row.get("文号"): text += f"文号：{row['文号']}\n"
            if row.get("网址"): text += f"网址：{row['网址']}\n"
            
            # 遍历其他列
            for k, v in row.items():
                if k in ["序号", "名称", "发布日期", "文号", "网址"]: continue
                if not v: continue
                
                # 命中的长文本进行切段
                if kw in v and len(v) > 50:
                    blocks = extractContextBlocks(v, kw)
                    if blocks:
                        text += f"{k}：\n"
                        for b in blocks: text += f"  {b}\n"
                    else:
                        text += f"{k}：{v}\n"
                else:
                    text += f"{k}：{v}\n"
            raw_results.append(text + "\n")

    # 2. 搜内置法条
    for k, v in LEGAL_PROVISIONS.items():
        if kw in k or kw in v['content']:
            raw_results.append(f"📄【内置法条】{v['law']}{v['article']}\n{v['content']}\n")

    if not raw_results:
        return f"未找到包含「{kw}」的内容。"
        
    final_text = f"【搜索关键词】{kw} (共匹配 {len(raw_results)} 条)\n\n"
    final_text += "\n".join(raw_results[:50])
    return final_text

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
        b2 = Button(text="复制全部", background_color=(0.8, 0.5, 0.2, 1)); b2.bind(on_release=self.on_copy_result)
        row3.add_widget(b1)
        row3.add_widget(b2)
        self.add_widget(row3)

        # 使用 TextInput 显示，支持手指滑动
        self.result_display = TextInput(
            text="正在初始化数据...",
            readonly=True,
            multiline=True,
            foreground_color=(0, 0, 0, 1),
            background_color=(1, 1, 1, 1),
            font_size=dp(14), # 稍微调小字号，一屏显示更多
            size_hint=(1, 1)
        )
        self.add_widget(self.result_display)

    def on_query_situation(self, *args):
        sel = self.spinner.text
        if "｜" not in sel: return
        key = sel.split("｜", 1)[0]
        self.result_display.text = query_situation_text(key)

    def on_search(self, *args):
        kw = self.search_input.text.strip()
        if not kw: return
        self.result_display.text = search_all_text(kw)

    def on_copy_result(self, *args):
        Clipboard.copy(self.result_display.text)
        self.result_display.text = "✅ 已复制到剪贴板！\n\n" + self.result_display.text[:100] + "..."

class LawApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        def init_load(dt):
            count, status = load_bundled_csv()
            msg = f"系统初始化完成！\n已加载 {len(SITUATIONS)} 项完整情形。\nCSV状态：{status}，共 {count} 条。\n\n如果CSV为0条，请检查文件是否上传。"
            self.root.result_display.text = msg
        Clock.schedule_once(init_load, 0.5)
        return MainScreen()

if __name__ == "__main__":
    LawApp().run()
