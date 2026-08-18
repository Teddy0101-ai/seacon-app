# -*- coding: utf-8 -*-
"""编译并审计 Seacon Academy v3 课程数据。"""

import io
import hashlib
import json
import os
from collections import Counter

from course_v3_01 import UNITS as U01
from course_v3_02 import UNITS as U02
from course_v3_03 import UNITS as U03
from course_v3_04 import UNITS as U04
from course_v3_05 import UNITS as U05
from course_v3_06 import UNITS as U06
from course_v3_07 import UNITS as U07
from course_v3_08 import UNITS as U08

HERE = os.path.dirname(os.path.abspath(__file__))
COURSE = U01 + U02 + U03 + U04 + U05 + U06 + U07 + U08
META = {
    "version": "3.0.0", "title": "Seacon 航运学院",
    "basis": "《主流船型必须搞懂的知识白皮书》v2.1",
    "authorship": "LLM 逐题综合白皮书知识点、真实误区与实务场景后编写；构建期静态打包，离线不调用外部 API。",
    "unitCount": 16, "lessonCount": 80, "questionCount": 448,
}


def fail(message):
    raise ValueError(message)


def validate():
    if len(COURSE) != META["unitCount"]:
        fail("单元数错误: %s" % len(COURSE))
    if len({u["id"] for u in COURSE}) != len(COURSE):
        fail("单元 ID 重复")
    ids, stems, kinds, positions, tf_answers = set(), set(), Counter(), Counter(), Counter()
    total_lessons = total_questions = 0
    for unit in COURSE:
        if len(unit["L"]) != 5:
            fail("%s 不是 5 节" % unit["id"])
        if not unit.get("guide") or len(unit.get("outcomes", [])) < 3:
            fail("%s 缺少导读或成果" % unit["id"])
        total_lessons += len(unit["L"])
        for li, lesson_obj in enumerate(unit["L"], 1):
            expected = 8 if lesson_obj.get("kind") == "checkpoint" else 5
            if len(lesson_obj["q"]) != expected:
                fail("%s 第 %s 节题量 %s != %s" % (unit["id"], li, len(lesson_obj["q"]), expected))
            for key in ("goal", "intro", "keys", "trap", "source"):
                if not lesson_obj.get(key):
                    fail("%s 第 %s 节缺少 %s" % (unit["id"], li, key))
            for qi, question in enumerate(lesson_obj["q"], 1):
                qid = "%s-l%02d-q%02d" % (unit["id"], li, qi)
                if qid in ids:
                    fail("重复题目 ID: %s" % qid)
                ids.add(qid)
                question["id"] = qid
                question["source"] = question.get("source") or lesson_obj["source"]
                if not question.get("q") or not question.get("w"):
                    fail("%s 缺题干或解析" % qid)
                normalized_stem = "".join(question["q"].split())
                if normalized_stem in stems:
                    fail("重复题干: %s" % question["q"])
                stems.add(normalized_stem)
                if len(question["w"]) < 10:
                    fail("%s 解析过短，未解释判断机制" % qid)
                kind = question.get("k")
                kinds[kind] += 1
                # 题目正文和干扰项由作者逐条撰写；这里仅按稳定 ID 轮换展示顺序，
                # 避免作者源码习惯让正确答案长期出现在第一个位置。
                if kind in ("mc", "num", "multi") and question.get("o"):
                    opts0 = list(question["o"])
                    shift = int(hashlib.sha256(qid.encode("ascii")).hexdigest()[:8], 16) % len(opts0)
                    question["o"] = opts0[shift:] + opts0[:shift]
                if kind in ("mc", "tf", "num"):
                    opts = question.get("o", [])
                    if len(opts) < 2 or len(opts) != len(set(opts)):
                        fail("%s 选项不足或重复" % qid)
                    if question.get("a") not in opts:
                        fail("%s 答案不在选项中" % qid)
                    if kind in ("mc", "num"):
                        positions[opts.index(question["a"])] += 1
                    if kind == "tf":
                        tf_answers[question["a"]] += 1
                elif kind == "multi":
                    opts, answers = question.get("o", []), question.get("a", [])
                    if len(opts) != len(set(opts)) or not answers or not set(answers).issubset(set(opts)):
                        fail("%s 多选答案非法" % qid)
                elif kind == "order":
                    if len(question.get("o", [])) < 3 or question.get("o") != question.get("a"):
                        fail("%s 排序结构非法" % qid)
                elif kind == "prod":
                    if not question.get("model"):
                        fail("%s 缺参考表达" % qid)
                else:
                    fail("%s 未知题型 %s" % (qid, kind))
                total_questions += 1
    if total_lessons != META["lessonCount"] or total_questions != META["questionCount"]:
        fail("规模错误: %s 节 / %s 题" % (total_lessons, total_questions))
    required = {"mc", "tf", "multi", "order", "prod", "num"}
    if not required.issubset(kinds):
        fail("题型缺失: %s" % (required - set(kinds)))
    if positions and max(positions.values()) / sum(positions.values()) > 0.48:
        fail("单选答案位置偏置过强: %s" % dict(positions))
    if tf_answers and max(tf_answers.values()) / sum(tf_answers.values()) > 0.75:
        fail("判断题方向偏置过强: %s" % dict(tf_answers))
    return total_lessons, total_questions, kinds, positions, tf_answers


lessons, questions, kinds, positions, tf_answers = validate()
payload = "window.COURSE_META=" + json.dumps(META, ensure_ascii=False, separators=(",", ":")) + ";\n"
payload += "window.COURSE=" + json.dumps(COURSE, ensure_ascii=False, separators=(",", ":")) + ";\n"
with io.open(os.path.join(HERE, "data.js"), "w", encoding="utf-8") as handle:
    handle.write(payload)
print("PASS Seacon Academy v3")
print("单元 %d / 课程 %d / 题目 %d / %.1f KB" %
      (len(COURSE), lessons, questions, len(payload.encode("utf-8")) / 1024.0))
print("题型 " + json.dumps(kinds, ensure_ascii=False, sort_keys=True))
print("答案位置 " + json.dumps(positions, ensure_ascii=False, sort_keys=True))
print("判断方向 " + json.dumps(tf_answers, ensure_ascii=False, sort_keys=True))
