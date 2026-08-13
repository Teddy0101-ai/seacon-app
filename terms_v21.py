# -*- coding: utf-8 -*-
"""白皮书 v2.1 术语补丁。

保留原始 terms_v2.json 作为白皮书快照，在 App 构建时：
1. 合并语义重复项；2. 补正文/附录中缺失的核心术语；3. 加入搜索别名；
4. 把少量 Markdown 标记转换为卡片可直接显示的 HTML。
"""

import re


PATCHES = {
    "船级社": {
        "en": "Class Society",
        "a": ["DNV", "LR", "Lloyd's Register", "BV", "Bureau Veritas", "ABS", "CCS", "IACS"],
    },
    "有效运力": {
        "en": "Effective Supply / Effective Capacity",
        "a": ["有效运力供给", "动态运力", "实际运力"],
    },
    "Kidnap & Ransom / Piracy Cover": {
        "a": ["K&R", "K&R Insurance", "海盗绑架险", "绑架勒索险"],
    },
    "DP1 / DP2 / DP3": {
        "a": ["DP", "Dynamic Positioning", "动态定位", "DP1/DP2", "DP2/DP3", "DP2 / DP3"],
    },
    "SS / DD": {
        "a": ["SS/DD", "Special Survey", "Dry Dock", "特别检验", "坞修"],
    },
    "油耗": {
        "a": ["FO Cons.", "FOC", "燃油消耗", "油耗"],
    },
    "MARPOL": {
        "a": ["MARPOL Annex VI", "MARPOL 附则 VI", "防污公约"],
    },
    "OFAC": {"a": ["Office of Foreign Assets Control", "美国海外资产控制办公室"]},
    "BCI / BPI / BSI": {
        "a": ["BCI", "BPI", "BSI", "BCI/BPI/BSI", "Baltic Capesize Index", "Baltic Panamax Index", "Baltic Supramax Index"],
    },
    "OPEX / CAPEX": {
        "a": ["OPEX", "CAPEX", "Operating Expenditure", "Capital Expenditure", "运营支出", "资本支出"],
    },
    "Innocent Owners' Interest / Additional Perils Insurance / IOI & IOAP": {
        "a": ["IOI", "IOAP", "IOI/IOAP", "IOI / IOAP Policy", "无过错船东权益险"],
    },
    "Hull & Machinery / H&M": {"a": ["H&M", "HM Policy", "船壳险", "船壳机器险"]},
    "Protection & Indemnity / P&I": {"a": ["P&I", "PNI Policy", "保赔险", "保赔协会"]},
    "Sub-charter Assignment": {"a": ["Assignment of Sub-Charter", "转租权益转让"]},
    "Acknowledgement": {"a": ["Acknowledgment", "转让确认回执"]},
    "MOA": {"a": ["MOA（Memorandum of Agreement）", "Memorandum of Agreement", "船舶买卖合同"]},
    "GT": {"a": ["GT/NT", "GT / NT", "Gross Tonnage", "总吨"]},
    "SHINC / SHEX": {"a": ["SHINC/SHEX"]},
    "WIBON / WIPON": {"a": ["WIBON/WIPON"]},
    "Ex-yard": {"a": ["EXW", "Ex Works", "船厂交货"]},
    "SBC": {"a": ["SBC/MOA", "Shipbuilding Contract", "造船合同"]},
}


# 被合并项仍作为别名进入搜索，不损失可发现性。
MERGE_INTO = {
    "CII (Carbon Intensity Indicator)": "CII",
    "DP2 / DP3": "DP1 / DP2 / DP3",
    "HM Policy（Hull & Machinery）": "Hull & Machinery / H&M",
    "PNI Policy（Protection & Indemnity）": "Protection & Indemnity / P&I",
    "IOI / IOAP Policy": "Innocent Owners' Interest / Additional Perils Insurance / IOI & IOAP",
    "Assignment of Sub-Charter": "Sub-charter Assignment",
    "Acknowledgment": "Acknowledgement",
    "MOA（Memorandum of Agreement）": "MOA",
}


EXTRAS = [
    {"t": "Registered Owner", "c": "基础·角色地图", "cn": "登记船东", "d": "登记在船旗国船舶登记册上的法律所有人，登记证书上写谁，法律上首先就找谁。", "n": "登记船东不一定是最终出资和享有经济利益的人；融资租赁中常由出租人或其 SPV 担任。", "a": ["Legal Owner", "注册船东"]},
    {"t": "Beneficial Owner", "c": "基础·角色地图", "cn": "实益所有人", "d": "最终控制船舶并享有经济利益的人或实体，可能隐藏在多层 SPV 和股权结构之后。", "n": "KYC、制裁筛查和关联交易判断必须穿透到实益所有人。", "a": ["UBO", "Ultimate Beneficial Owner", "最终受益人"]},
    {"t": "Bareboat Charterer", "c": "基础·角色地图", "cn": "光船承租人", "d": "通过光船租赁取得船舶占有和控制，自行配员、管理、维修和运营的一方。", "n": "它像经营上的船东，但并不当然取得船舶所有权。", "a": ["Demise Charterer", "光租承租人"]},
    {"t": "Ship Manager", "c": "基础·角色地图", "cn": "船舶管理公司", "d": "受船东委托提供技术管理或商业管理的公司。TM 负责船员、维修、证书等，CM 负责租船和商业运营。", "a": ["TM", "CM", "Technical Manager", "Commercial Manager", "TM/CM"]},
    {"t": "Surveyor", "c": "基础·角色地图", "cn": "验船师 / 检验人", "d": "代表船级社、保险人、买卖双方或融资方进行检验并出具事实记录或报告的专业人员。", "n": "先确认其委托方和检验范围；同一次上船，不同委托方的责任并不相同。", "a": ["验船师", "监造组", "Superintendent"]},
    {"t": "BIMCO", "c": "交易·标准合同", "en": "Baltic and International Maritime Council", "cn": "波罗的海国际航运公会", "d": "维护大量航运标准合同和条款的国际行业组织，常见范本包括 BARECON、SHIPMAN、NEWBUILDCON 和 DEMOLISHCON。", "n": "使用范本不等于风险已解决；附加条款和逐项修改往往决定真正的风险分配。"},
    {"t": "Fixture Recap", "c": "租约·成交确认", "cn": "成交确认 / 成交摘要", "d": "租船谈判达成主要商业条件后形成的成交确认，集中记录船舶、租期、租金、航区、交还船和 subjects 等核心条款。", "n": "先逐项消除 subjects，再确认与长式租约一致；任何缩写、附件或优先顺序不清都可能改变交易。", "a": ["Recap", "Fixture Note", "成交电文"]},
    {"t": "NEWBUILDCON", "c": "交易·标准合同", "cn": "BIMCO 新造船合同范本", "d": "BIMCO 发布的新造船合同标准格式，用于约定规格、价格、付款节点、延期、性能、交付和解约等事项。", "n": "项目仍须结合船厂版本、技术规格书、退款保函和适用法逐条谈判。"},
    {"t": "SHIPMAN", "c": "交易·标准合同", "cn": "BIMCO 船舶管理合同范本", "d": "用于委托技术、船员或商业管理的标准合同，界定管理范围、费用、责任、保险和终止机制。", "n": "要把管理权限、费用上限、关联交易、报告义务和重大事项审批写清。"},
    {"t": "DEMOLISHCON", "c": "交易·标准合同", "cn": "BIMCO 拆船买卖合同范本", "d": "用于船舶出售拆解的标准合同，覆盖价格、交付、风险转移、环保合规和违约等事项。", "n": "拆解地点、现金买家、香港公约及当地环保要求都要独立核验。"},
    {"t": "S&P", "c": "交易·二手船", "en": "Sale and Purchase", "cn": "船舶买卖", "d": "航运语境下通常指二手船买卖市场或成交，而不是股票指数。", "n": "成交船价必须连同船龄、船型、船级、坞修状态、租约和交割日期一起比较。", "a": ["Sale & Purchase", "二手船买卖"]},
    {"t": "Due Diligence", "c": "交易·二手船", "cn": "尽职调查", "d": "签约或放款前对船舶技术、法律权属、财务、运营、保险、合规和对手方进行系统核验。", "n": "尽调不是收文件；每个结论都要能回到文件、检验或可靠数据源。", "a": ["DD", "尽调"]},
    {"t": "LDT", "c": "核心参数", "en": "Light Displacement Tonnage", "cn": "轻吨 / 空船重量吨", "d": "船舶不含货物、燃油、淡水、人员和物料时的结构及设备重量，拆船通常按 LDT × 每轻吨废钢价估值。", "n": "LDT 是拆解计价口径，不是 DWT，也不等于证书上的 GT。", "a": ["Lightweight Tonnage", "轻载排水量"]},
    {"t": "LBP", "c": "核心参数", "en": "Length Between Perpendiculars", "cn": "垂线间长", "d": "夏季载重水线前后垂线之间的长度，主要用于船舶设计、稳性和规则计算。", "n": "LBP 通常比总长 LOA 短；Q88 上两者相邻，抄错会让泊位、船闸和航线适配分析失效。", "a": ["LPP", "垂线间长度"]},
    {"t": "MCR", "c": "核心参数", "en": "Maximum Continuous Rating", "cn": "最大持续功率", "d": "主机在规定条件下允许长期连续输出的最大功率，是设备能力上限。", "n": "不要把 MCR 当成日常运营档位或直接用来承诺服务航速。"},
    {"t": "NCR", "c": "核心参数", "en": "Normal Continuous Rating", "cn": "常用持续功率", "d": "主机日常连续运行采用的功率水平，通常低于 MCR，常见约为 MCR 的 85%—90%。", "n": "航速和油耗保证必须确认对应的功率、吃水、海况和测量方法。"},
    {"t": "Bollard Pull", "c": "核心参数", "cn": "系柱拉力", "d": "拖轮系在固定系柱上全功率工作时测得的持续拉力，通常以吨计，是 AHTS 和拖轮能力的核心指标。", "n": "它衡量拖力，不是 DWT，也不能代表动态定位等级。", "a": ["BP", "系柱拖力"]},
    {"t": "SCNT", "c": "核心参数", "en": "Suez Canal Net Tonnage", "cn": "苏伊士运河净吨", "d": "苏伊士运河按专门规则计算的计费吨位，用于确定运河通行费。", "n": "SCNT 与国际吨位证书上的 NT 不是同一个口径。"},
    {"t": "PC/UMS", "c": "核心参数", "en": "Panama Canal Universal Measurement System", "cn": "巴拿马运河通用计量体系", "d": "巴拿马运河采用的专用船舶计量和收费口径。", "n": "运河费测算应使用运河当期规则和专用吨位，不能直接套 GT 或 NT。", "a": ["PC-UMS", "Panama Canal Tonnage"]},
    {"t": "FWA", "c": "核心参数", "en": "Fresh Water Allowance", "cn": "淡水增吃水量", "d": "船舶由海水进入密度较低的淡水时，在同一排水量下增加的吃水量。常用近似式为满载排水量 ÷（4 × TPC）。", "n": "受淡水港或运河吃水限制时，必须先扣除 FWA，再计算可装货量。"},
    {"t": "TPC", "c": "核心参数", "en": "Tonnes per Centimetre Immersion", "cn": "每厘米吃水吨数", "d": "船舶平均吃水每变化 1 厘米所对应的排水量变化吨数，用于快速估算减载或增载量。", "n": "TPC 会随吃水变化；精确计算应查静水力表，不能对大幅吃水变化始终使用同一个常数。"},
    {"t": "Kamsarmax", "c": "船型·干散货", "cn": "卡姆萨尔型散货船", "d": "约 8.0—8.5 万 DWT、船长通常控制在约 229 米的散货船，尺度源自几内亚 Kamsar 港限制。", "n": "常跑粮食、铝土矿和煤炭，是现代 Panamax 市场的重要主力船型。"},
    {"t": "Newcastlemax", "c": "船型·干散货", "cn": "纽卡斯尔型散货船", "d": "约 20—21 万 DWT、长度通常控制在约 300 米的大型散货船，尺度源自澳大利亚 Newcastle 港。", "n": "不要只凭吨位名称判断港口适配，仍须逐港核对长、宽、吃水和装卸限制。"},
    {"t": "Post-Panamax", "c": "船型·集装箱", "cn": "超巴拿马型集装箱船", "d": "泛指尺度超过老巴拿马船闸限制、不能通过老船闸的集装箱船。", "n": "Post-Panamax 是宽泛类别；Neo-Panamax 特指按新船闸尺度优化的船，两者不能完全等同。"},
    {"t": "PLV", "c": "船型·气体与特种", "en": "Pipe-Laying Vessel", "cn": "铺管船", "d": "用于铺设海底油气管道或电缆的工程船，核心能力包括铺设系统、张紧器、起重、DP 和水下作业支持。", "n": "评价 PLV 要看管径、水深、铺设方式和 DP 能力，不能只看船舶吨位。"},
    {"t": "Crane Vessel", "c": "船型·气体与特种", "cn": "起重船", "d": "装备大型海上起重机，用于吊装平台模块、海上风机和其他重型构件的工程船。", "a": ["CV", "Heavy Lift Vessel", "起重工程船"]},
    {"t": "Floatel", "c": "船型·气体与特种", "cn": "海上居住船", "d": "为海上工程、平台或风电项目人员提供住宿、生活、办公和转运支持的船舶或浮式设施。", "n": "关键能力通常包括床位、gangway、DP、直升机甲板和恶劣海况可用率。"},
    {"t": "ITC", "c": "船舶保险", "en": "Institute Time Clauses—Hulls", "cn": "协会船舶定期保险条款", "d": "伦敦市场船壳险常用条款体系，规定承保风险、除外责任、碰撞责任和索赔义务。", "n": "白皮书所述常见结构下，H&M 承担对被碰船碰撞责任的 3/4，剩余部分通常由 P&I 衔接；具体仍以保单文本为准。"},
    {"t": "CTL", "c": "船舶保险", "en": "Constructive Total Loss", "cn": "推定全损", "d": "船舶仍存在，但预计修复、救助和恢复费用达到保单约定阈值，经济上不值得修复时按全损处理的状态。", "n": "CTL 通常涉及及时发出委付通知和严格的费用证明，程序比实际全损复杂。", "a": ["Constructive Total Loss", "委付"]},
    {"t": "ECA", "c": "环保与合规", "en": "Emission Control Area", "cn": "排放控制区", "d": "对船舶硫氧化物、氮氧化物或颗粒物排放实施更严格限制的指定海域。", "n": "进入 ECA 前要确认燃油切换、设备状态、记录和当地规则；合规成本会改变航线经济性。", "a": ["SECA", "NECA", "排放控制区"]},
    {"t": "BWM Convention", "c": "环保与合规", "en": "Ballast Water Management Convention", "cn": "压载水管理公约", "d": "要求船舶管理压载水和沉积物，降低外来水生生物跨区域传播风险的 IMO 公约。", "n": "多数船舶通过安装 BWTS 满足排放标准，但设备型式认可、港口国执行和维护记录都可能影响合规。", "a": ["BWM", "Ballast Water Convention", "压载水公约"]},
    {"t": "SEEMP", "c": "环保与合规", "en": "Ship Energy Efficiency Management Plan", "cn": "船舶能效管理计划", "d": "船舶持续改进能效和管理营运碳强度的计划文件。CII 适用船需在 SEEMP 第三部分记录目标和执行机制。", "n": "单年 E 或连续三年 D 时须提交纠正行动计划。"},
    {"t": "AER", "c": "环保与合规", "en": "Annual Efficiency Ratio", "cn": "年度效率比", "d": "常用于 CII 的营运碳强度指标，以年度 CO₂ 排放量除以载重吨与航行距离的乘积。", "n": "短程、多港、等待时间长的船，即使设备不差，也可能因航行距离分母偏小而评级恶化。"},
    {"t": "SDN", "c": "环保与合规", "en": "Specially Designated Nationals and Blocked Persons List", "cn": "特别指定国民和被封锁人员名单", "d": "美国 OFAC 维护的制裁名单，可能覆盖个人、企业、船舶和其他财产权益。", "n": "筛查不能只搜船名，还要核对 IMO 号、所有权、控制关系、货物、航线和交易对手。", "a": ["SDN List", "OFAC SDN"]},
    {"t": "STS", "c": "环保与合规", "en": "Ship-to-Ship Transfer", "cn": "船对船过驳", "d": "两条船在海上或锚地直接转移货物、燃油或物料的作业。", "n": "STS 本身是正常作业，但与关闭 AIS、异常绕航、文件不一致同时出现时，是制裁规避和货源真实性的重要红旗。", "a": ["Ship to Ship", "过驳"]},
    {"t": "Shadow Fleet", "c": "环保与合规", "cn": "影子船队", "d": "通常指船龄偏高、所有权和运营结构不透明、保险安排非主流，并参与受制裁或高风险油品运输的船队。", "n": "它会扭曲老龄油轮价格和拆解节奏；估值时必须识别买家池是否依赖不可持续的制裁套利。", "a": ["Dark Fleet", "灰色船队"]},
    {"t": "BHSI", "c": "市场与周期", "en": "Baltic Handysize Index", "cn": "波罗的海灵便型散货船指数", "d": "反映灵便型散货船市场运价或期租等价水平的波罗的海交易所指数。", "n": "2018 年起不再计入 BDI，但仍用于观察 Handysize 子市场。"},
    {"t": "BDTI", "c": "市场与周期", "en": "Baltic Dirty Tanker Index", "cn": "波罗的海原油及脏油轮指数", "d": "反映原油和其他脏油品航线即期运价的波罗的海交易所综合指数。", "n": "它不是干散货 BDI，也不能直接替代具体航线、船型和 Worldscale 点位。"},
    {"t": "BCTI", "c": "市场与周期", "en": "Baltic Clean Tanker Index", "cn": "波罗的海成品油轮指数", "d": "反映成品油及其他清洁油品航线即期运价的波罗的海交易所综合指数。", "n": "分析 MR、LR1、LR2 时还要下钻到对应航线，综合指数可能掩盖区域分化。"},
    {"t": "Orderbook", "c": "市场与周期", "cn": "手持订单 / 订单簿", "d": "船厂已签约但尚未交付的新船订单集合，常以艘数、DWT、CGT 或占现有船队比例衡量。", "n": "订单簿是未来供给，不是今天的有效运力；必须结合交付节奏、延期、撤单和拆解量判断。", "a": ["Orderbook-to-Fleet", "订单占船队比"]},
    {"t": "Scrapping", "c": "市场与周期", "cn": "拆船 / 船舶拆解", "d": "船舶退出营运并出售给拆船设施回收钢材和设备的过程，是船队供给收缩的主要出口。", "n": "拆解决策受船龄、运价、坞修成本、环保规则和废钢价共同影响。", "a": ["Demolition", "Recycling", "拆解"]},
    {"t": "Cash Waterfall", "c": "融资·利率与契约", "cn": "现金流瀑布", "d": "把项目账户现金按预先约定的优先顺序分配，例如先付运营费用，再付本息、补足储备，最后才允许分红。", "n": "它是账户控制和分红限制真正落地的机制；建模时要按文件顺序逐层扣减。"},
    {"t": "PMT", "c": "融资·测算指标", "en": "Payment", "cn": "每期等额本息付款额函数", "d": "Excel 中按固定利率、固定期数和现值计算每期固定还本付息额的函数。", "n": "输入利率与期数必须使用同一周期；现金流正负号方向要一致。"},
    {"t": "PPMT", "c": "融资·测算指标", "en": "Principal Payment", "cn": "每期本金函数", "d": "Excel 中计算等额本息结构某一期本金偿还额的函数。", "n": "PPMT 与 IPMT 相加等于该期 PMT；核对期数起点和现金流符号。"},
    {"t": "IPMT", "c": "融资·测算指标", "en": "Interest Payment", "cn": "每期利息函数", "d": "Excel 中计算等额本息结构某一期利息支出的函数。", "n": "前期 IPMT 通常较高，随着剩余本金下降而减少。"},
    {"t": "Voyage Cost", "c": "投资测算", "cn": "航次成本", "d": "随具体航次发生的燃油、港口、运河、代理和装卸相关成本，通常由航次租船下的船东承担。", "n": "不要把 Voyage Cost 混进日常 OPEX；租约类型不同，成本承担方会改变。"},
    {"t": "Operating Days", "c": "投资测算", "cn": "可运营天数", "d": "日历天数扣除计划坞修、非计划停租、租约衔接空档等不赚钱天数后的实际营运天数。", "n": "收入模型不能默认 365 天全部赚租金；可运营天数是假设敏感度很高的变量。"},
    {"t": "SIW", "c": "研究·数据口径", "en": "Shipping Intelligence Weekly", "cn": "Clarksons 航运情报周刊", "d": "Clarksons 每周发布的市场资料，涵盖收益、运价、成交、船价、燃油和主要指数等。", "n": "复现周报时以具体期号和出版日为口径，不要用其他日期的实时值替换刊内数据。", "a": ["Clarksons SIW"]},
    {"t": "ClarkSea Index", "c": "研究·数据口径", "cn": "Clarksons 综合船舶收益指数", "d": "Clarksons 编制的跨主要商船板块综合日收益指标，用于观察整体航运市场收益水平。", "n": "综合指数适合看大盘，具体项目仍要回到对应船型、航线和租约期限。", "a": ["Clarksea", "ClarkSea"]},
    {"t": "VLSFO", "c": "研究·数据口径", "en": "Very Low Sulphur Fuel Oil", "cn": "极低硫燃料油", "d": "硫含量通常不高于 0.50% m/m 的船用燃料油，是 IMO 2020 后常见的合规燃油基准。", "n": "燃油价格比较必须注明港口、日期、币种、单位和燃油规格。"},
    {"t": "HFO / LSFO / MGO", "c": "核心参数", "cn": "重油 / 低硫燃油 / 船用轻柴油", "d": "船舶航速油耗表常分列的燃油种类：HFO 为重质燃料油，LSFO 为低硫燃油，MGO 为船用轻柴油。", "n": "不同燃油不能只比较吨数；价格、硫含量、设备适配和 ECA 使用要求都不同。", "a": ["HFO", "LSFO", "MGO", "HFO/LSFO/MGO", "Marine Gas Oil"]},
    {"t": "VLGC", "c": "船型·气体与特种", "en": "Very Large Gas Carrier", "cn": "超大型液化气船", "d": "通常指约 8 万立方米级、以 LPG、氨等货物为主的远洋大型气体运输船。", "n": "VLGC 以舱容而非 DWT 作为核心运力口径；还要区分货物体系、制冷方式和码头适配。"},
    {"t": "GDP", "c": "市场与周期", "en": "Gross Domestic Product", "cn": "国内生产总值", "d": "衡量经济体最终产品和服务产出的宏观指标，增速影响贸易总量和航运需求基线。", "n": "航运需求还取决于贸易结构和运输距离；GDP 同向不等于吨海里同比例变化。"},
    {"t": "PMI", "c": "市场与周期", "en": "Purchasing Managers' Index", "cn": "采购经理指数", "d": "反映制造业或服务业景气变化的扩散指数，常用于观察贸易与工业活动的领先方向。", "n": "PMI 是方向指标，不应直接代入船型运量预测；需结合订单、库存、商品和区域数据。"},
    {"t": "CSPI", "c": "研究·数据口径", "cn": "中国航运景气指数", "d": "上海国际航运研究中心发布的航运景气调查指标，用于观察企业经营景气和预期。", "n": "引用时注明发布机构、季度和具体分指数，避免与船价指数或运价指数混淆。"},
    {"t": "SOx / NOx", "c": "环保与合规", "cn": "硫氧化物 / 氮氧化物", "d": "船舶燃料和发动机燃烧产生的主要空气污染物。SOx 主要由燃油硫含量控制，NOx 主要由发动机技术标准和排放区要求控制。", "n": "两者规则、技术路径和适用边界不同；不要把低硫燃油当成解决 NOx 的措施。", "a": ["SOx", "NOx", "Sulphur Oxides", "Nitrogen Oxides"]},
]


def _aliases(value):
    if not value:
        return []
    return value if isinstance(value, list) else [value]


def _unique(values):
    out = []
    seen = set()
    for value in values:
        value = str(value).strip()
        key = value.casefold()
        if value and key not in seen:
            seen.add(key)
            out.append(value)
    return out


def _rich(value):
    """原始内容是受信任的静态数据，只转换遗留 Markdown 记号。"""
    if not value:
        return value
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", str(value))
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    return value


def apply_terms_v21(source):
    """返回适合 App 的完整、去重术语列表。"""
    records = [dict(item) for item in source]
    by_title = {item["t"]: item for item in records}

    for old_title, canonical_title in MERGE_INTO.items():
        old = by_title.get(old_title)
        canonical = by_title.get(canonical_title)
        if not old or not canonical:
            continue
        canonical["a"] = _unique(
            _aliases(canonical.get("a"))
            + [old_title, old.get("en", ""), old.get("cn", "")]
            + _aliases(old.get("a"))
        )
        for key in ("en", "cn", "d", "n", "u"):
            if not canonical.get(key) and old.get(key):
                canonical[key] = old[key]
        records.remove(old)
        by_title.pop(old_title, None)

    for title, patch in PATCHES.items():
        item = by_title.get(title)
        if not item:
            continue
        for key, value in patch.items():
            if key == "a":
                item["a"] = _unique(_aliases(item.get("a")) + _aliases(value))
            else:
                item[key] = value

    for extra in EXTRAS:
        if extra["t"] in by_title:
            raise ValueError("术语补丁重复：%s" % extra["t"])
        item = dict(extra)
        records.append(item)
        by_title[item["t"]] = item

    for item in records:
        if not item.get("d"):
            item["d"] = item.get("cn") or item.get("u") or item.get("n") or "术语释义待补充。"
        for key in ("d", "n", "u"):
            if item.get(key):
                item[key] = _rich(item[key])
        if item.get("n"):
            item["n"] = re.sub(r"^\s*⚑\s*", "", item["n"])
        item["a"] = _unique(_aliases(item.get("a")))
        if not item["a"]:
            item.pop("a", None)

    return records
