# -*- coding: utf-8 -*-
"""
常量定义
"""

# 势力ID
FACTION_HEAVEN_GATE = "heaven_gate"
FACTION_EXTREMIST = "extremist"
FACTION_FORTUNE = "fortune"
FACTION_SHADOW = "shadow"
FACTION_NONE = None

FACTION_NAMES = {
    FACTION_HEAVEN_GATE: "天堂口",
    FACTION_EXTREMIST: "极道",
    FACTION_FORTUNE: "貔貅",
    FACTION_SHADOW: "猫",
}

# 势力关系
FACTION_RELATIONS = {
    FACTION_HEAVEN_GATE: {
        FACTION_EXTREMIST: "cooperate",
        FACTION_FORTUNE: "compete",
        FACTION_SHADOW: "secret_alliance",
    },
    FACTION_EXTREMIST: {
        FACTION_HEAVEN_GATE: "cooperate",
        FACTION_FORTUNE: "hostile",
        FACTION_SHADOW: "unknown",
    },
    FACTION_FORTUNE: {
        FACTION_HEAVEN_GATE: "compete",
        FACTION_EXTREMIST: "hostile",
        FACTION_SHADOW: "trade",
    },
    FACTION_SHADOW: {
        FACTION_HEAVEN_GATE: "secret_alliance",
        FACTION_EXTREMIST: "unknown",
        FACTION_FORTUNE: "trade",
    },
}

# 结局ID
ENDING_REBEL = "rebel"
ENDING_NEW_TIANLONG = "new_tianlong"
ENDING_WALL_BREAKER = "wall_breaker"
ENDING_ACCOMPLICE = "accomplice"
ENDING_CYCLE = "cycle"
ENDING_FORGETTER = "forgetter"

# 生肖等级
ZODIAC_HUMAN = "human"
ZODIAC_EARTH = "earth"
ZODIAC_HEAVEN = "heaven"

# 回响ID
REVERBERATION_LIFE = "life"
REVERBERATION_BREAK_ALL = "break_all"
REVERBERATION_LUCK = "luck"
REVERBERATION_CAT = "cat"
REVERBERATION_DREAM = "dream"
REVERBERATION_ANALYZE = "analyze"
REVERBERATION_DISASTER = "disaster"
REVERBERATION_TIME_REWIND = "time_rewind"

# 记忆碎片类型
FRAGMENT_DIALOGUE = "dialogue"
FRAGMENT_BATTLE = "battle"
FRAGMENT_CHOICE = "choice"
FRAGMENT_DISCOVERY = "discovery"