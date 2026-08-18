# -*- coding: utf-8 -*-
"""Seacon Academy v3 课程作者 DSL。

这里的函数只负责保存结构，不生成题干、选项或解析。所有学习目标、题目、
干扰项和解析均由课程作者逐条撰写，避免用字符串模板伪造题库规模。
"""


def mc(stem, options, answer, analysis, context=""):
    return {"k": "mc", "q": stem, "o": list(options), "a": answer,
            "w": analysis, "pre": context}


def tf(stem, answer, analysis, context=""):
    return {"k": "tf", "q": stem, "o": ["正确", "错误"],
            "a": "正确" if answer else "错误", "w": analysis, "pre": context}


def multi(stem, options, answers, analysis, context=""):
    return {"k": "multi", "q": stem, "o": list(options), "a": list(answers),
            "w": analysis, "pre": context}


def order(stem, items, analysis, context=""):
    return {"k": "order", "q": stem, "o": list(items), "a": list(items),
            "w": analysis, "pre": context}


def prod(stem, model, analysis, context=""):
    return {"k": "prod", "q": stem, "model": model, "a": model,
            "w": analysis, "pre": context}


def num(stem, options, answer, analysis, context=""):
    return {"k": "num", "q": stem, "o": list(options), "a": answer,
            "w": analysis, "pre": context}


def lesson(title, goal, intro, keys, trap, source, questions, kind="skill", difficulty=1):
    return {
        "t": title, "goal": goal, "intro": intro, "keys": list(keys),
        "trap": trap, "source": source, "kind": kind,
        "difficulty": difficulty, "q": list(questions),
    }


def unit(uid, title, subtitle, color, icon, guide, outcomes, lessons):
    return {
        "id": uid, "t": title, "s": subtitle, "c": color, "i": icon,
        "guide": guide, "outcomes": list(outcomes), "L": list(lessons),
    }
