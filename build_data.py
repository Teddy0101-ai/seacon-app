# -*- coding: utf-8 -*-
"""生成已清空题目的课程路径骨架。

旧题库已于 2026-08-14 全部删除。这里仅保留 11 个单元、56 节课的标题和顺序，
方便后续从零重建内容，不允许旧题通过构建脚本重新混回来。
"""

import io
import json
import os


HERE = os.path.dirname(os.path.abspath(__file__))


def lessons(*titles):
    return [{"t": title, "q": []} for title in titles]


COURSE = [
    {"id": "u1", "t": "先认人", "s": "角色 · 钱怎么流", "c": "#2a9d8f", "i": "👥", "L": lessons(
        "三个基本角色", "谁在管这条船", "钱从哪来到哪去", "五把不通用的尺子", "一条船的一生")},
    {"id": "u2", "t": "八大船型", "s": "分清赛道", "c": "#2a78d6", "i": "🚢", "L": lessons(
        "八个族", "名字的由来", "油轮那条线", "干散货与集装箱尺度", "剖开船体看结构", "OSV 按能力分级")},
    {"id": "u3", "t": "参数与吨位", "s": "数字就是钱", "c": "#eb6834", "i": "📐", "L": lessons(
        "六个「吨」", "三面红旗", "十一项参数都挂着钱")},
    {"id": "u4", "t": "租约三分法", "s": "谁付油钱", "c": "#8a4fbd", "i": "📋", "L": lessons(
        "TC / VC / BBC", "停租那些事", "航次租的黑话", "一年到底赚多少", "把 Recap 里的雷找出来")},
    {"id": "u5", "t": "交易与文件", "s": "同一天发生", "c": "#c9722f", "i": "📄", "L": lessons(
        "两种结构", "交船那一天", "谈判桌上", "二手船六步", "尽调不是收文件", "红线与交割日")},
    {"id": "u6", "t": "保险九宫格", "s": "谁赔、赔多少", "c": "#c0392b", "i": "🛟", "L": lessons(
        "九张保单", "为什么必须有 IOI", "环保合规", "九宫格的另外五格", "风险审批与环保分层", "制裁会让项目归零")},
    {"id": "u7", "t": "市场与周期", "s": "什么时候出手", "c": "#1baf7a", "i": "📈", "L": lessons(
        "需求是个乘法", "剪刀差", "周期时钟", "看哪个指数", "有效供给不是船队总数", "指数与研究纪律")},
    {"id": "u8", "t": "测算与融资", "s": "算得清", "c": "#4a3aa7", "i": "🧮", "L": lessons(
        "四个指标", "DSCR 是开关", "融资那些坑", "先过四道门", "银行控制的是现金流")},
    {"id": "u9", "t": "数量级直觉", "s": "这个数正常吗", "c": "#e67e22", "i": "🎯", "L": lessons(
        "船价与租金", "融资那几个比率", "市场与周期的标尺")},
    {"id": "u10", "t": "实战情景", "s": "换你会怎么做", "c": "#c0392b", "i": "🧭", "L": lessons(
        "交船日出事了", "租家来提索赔", "融资顾问的漂亮方案", "流程排序", "项目初筛先问什么", "看征兆，省谈判子弹")},
    {"id": "u11", "t": "说得出来", "s": "白纸默写 · 不给选项", "c": "#8a4fbd", "i": "🗣", "L": lessons(
        "角色与租约", "保险与交船文件", "算给我看 · 三条线", "算给我看 · 船与货", "说清机制")},
]


unit_count = len(COURSE)
lesson_count = sum(len(unit["L"]) for unit in COURSE)
question_count = sum(len(lesson["q"]) for unit in COURSE for lesson in unit["L"])
assert unit_count == 11
assert lesson_count == 56
assert question_count == 0, "题库清空版本不得包含任何题目"

js = "window.COURSE=" + json.dumps(COURSE, ensure_ascii=False, separators=(",", ":")) + ";"
io.open(os.path.join(HERE, "data.js"), "w", encoding="utf-8").write(js)
print("单元 %d 个 / 路径 %d 节 / 题目 %d 道 / data.js %.1f KB"
      % (unit_count, lesson_count, question_count, len(js.encode("utf-8")) / 1024))
