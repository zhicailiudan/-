# -*- coding: utf-8 -*-
"""
势力管理系统
"""

from dataclasses import dataclass, field
from typing import Optional, Callable
from .constants import *
from .data_structures import GameState


@dataclass
class FactionMember:
    """势力成员"""
    npc_id: str
    name: str
    role: str
    description: str
    trust_base: int = 0


@dataclass
class Faction:
    """势力定义"""
    faction_id: str
    name: str
    leader: str
    description: str
    join_conditions: dict
    privileges: list[str]
    members: list[FactionMember] = field(default_factory=list)
    quests: list[dict] = field(default_factory=list)


@dataclass
class FactionRelation:
    """势力间关系"""
    faction1: str
    faction2: str
    relation: str
    last_updated: int = 0


FACTION_DEFINITIONS = {
    FACTION_HEAVEN_GATE: Faction(
        faction_id=FACTION_HEAVEN_GATE,
        name="天堂口",
        leader="楚天秋",
        description="团结协作，共同逃离终焉之地",
        join_conditions={
            "progress_top_percent": 30,
            "help_others_count": 3
        },
        privileges=[
            "团队挑战资格（最多3人组队）",
            "天堂口知识库访问权",
            "每日道捐赠系统"
        ],
        members=[
            FactionMember("chutianqiu", "楚天秋", "领袖", "永远冷静的领袖，实际掌握逃离条件"),
            FactionMember("zhaoyongren", "赵庸人", "情报员", "情报收集者，知道很多隐藏信息"),
            FactionMember("linling", "林檎", "话事人", "负责新成员引导"),
            FactionMember("jojiajin", "乔家劲", "战斗员", "热情的年轻战士，天堂口成员"),
        ],
        quests=[
            {"quest_id": "heaven_gate_ch1", "title": "接纳", "description": "帮助3位新手学习者"},
            {"quest_id": "heaven_gate_ch2", "title": "信任", "description": "保守天堂口的秘密"},
            {"quest_id": "heaven_gate_ch3", "title": "裂痕", "description": "支持天堂口内部矛盾的选择"},
        ]
    ),

    FACTION_EXTREMIST: Faction(
        faction_id=FACTION_EXTREMIST,
        name="极道",
        leader="燕知春",
        description="以力量打破规则",
        join_conditions={
            "streak_wins": 5
        },
        privileges=[
            "强制挑战权（可以指定对手）",
            "暴力破解副本（消耗道直接通关）",
            "极道知识库访问权"
        ],
        members=[
            FactionMember("yanchunchun", "燕知春", "领袖", "相信力量是唯一出路"),
            FactionMember("hanwudao", "韩武道", "战斗狂人", "挑战他获得稀有知识"),
            FactionMember("wuming", "吴明", "谋士", "提供战术建议"),
        ],
        quests=[
            {"quest_id": "extremist_ch1", "title": "证明", "description": "连续击败3位人级生肖"},
            {"quest_id": "extremist_ch2", "title": "晋升", "description": "地下擂台的挑战"},
            {"quest_id": "extremist_ch3", "title": "背叛者", "description": "支持极道内部权力斗争"},
        ]
    ),

    FACTION_FORTUNE: Faction(
        faction_id=FACTION_FORTUNE,
        name="貔貅",
        leader="钱 Meck",
        description="智慧敛财，利益至上",
        join_conditions={
            "total_dao": 100
        },
        privileges=[
            "市场交易折扣",
            "情报购买（用道换取任何人的信息）",
            "貔貅知识库访问权"
        ],
        members=[
            FactionMember("qianmeck", "钱 Meck", "领袖", "精明的商人，任何东西都有价格"),
            FactionMember("sunzhqiong", "孙之琼", "黑市商人", "售卖违禁道具"),
            FactionMember("taojing", "陶净", "拍卖师", "主持特殊活动"),
        ],
        quests=[
            {"quest_id": "fortune_ch1", "title": "交易", "description": "用情报换取道"},
            {"quest_id": "fortune_ch2", "title": "投资", "description": "购买貔貅股份"},
            {"quest_id": "fortune_ch3", "title": "黑市", "description": "参与一次黑市交易"},
        ]
    ),

    FACTION_SHADOW: Faction(
        faction_id=FACTION_SHADOW,
        name="猫",
        leader="陈俊南",
        description="暗中行动，积蓄力量",
        join_conditions={
            "no_revealed_reverberation": True,
            "completed入会_test": True
        },
        privileges=[
            "隐藏行动（其他势力无法追踪）",
            "猫的知识库访问权",
            "策反其他势力成员的能力"
        ],
        members=[
            FactionMember("chennan", "陈俊南", "领袖", "唯一公开的回响者，猫的实际领袖"),
            FactionMember("hanpiyan", "韩片羽", "轮回者", "第27次轮回的幸存者，掌握关键信息"),
            FactionMember("cangque", "藏雀", "隐形者", "负责暗杀任务"),
        ],
        quests=[
            {"quest_id": "shadow_ch1", "title": "试探", "description": "不透露任何关于回响的信息"},
            {"quest_id": "shadow_ch2", "title": "任务", "description": "潜入某势力获取情报"},
            {"quest_id": "shadow_ch3", "title": "秘密", "description": "韩片羽的真实身份选择"},
        ]
    )
}


class FactionManager:
    """势力管理器"""

    def __init__(self, state: GameState):
        self.state = state
        self.factions = FACTION_DEFINITIONS
        self.relations: dict[str, FactionRelation] = {}
        self._init_default_relations()

    def _init_default_relations(self):
        """初始化默认势力关系"""
        for f1, f1_relations in FACTION_RELATIONS.items():
            for f2, relation in f1_relations.items():
                key = f"{f1}_{f2}"
                self.relations[key] = FactionRelation(f1, f2, relation)

    def get_faction(self, faction_id: str) -> Optional[Faction]:
        """获取势力信息"""
        return self.factions.get(faction_id)

    def get_player_faction(self) -> Optional[Faction]:
        """获取玩家所属势力"""
        if self.state.player.faction:
            return self.factions.get(self.state.player.faction)
        return None

    def check_join_conditions(self, faction_id: str) -> tuple[bool, list[str]]:
        """检查是否符合加入条件"""
        faction = self.factions.get(faction_id)
        if not faction:
            return False, ["势力不存在"]

        conditions = faction.join_conditions
        unmet = []

        if "progress_top_percent" in conditions:
            progress = self.state.knowledge_base.mastery * 100
            if progress < conditions["progress_top_percent"]:
                unmet.append(f"学习进度需达到{conditions['progress_top_percent']}%（当前：{progress:.1f}%）")

        if "help_others_count" in conditions:
            help_count = self.state.progression.story_flags.get("helped_others_count", 0)
            if help_count < conditions["help_others_count"]:
                unmet.append(f"需帮助{conditions['help_others_count']}位学习者（当前：{help_count}）")

        if "streak_wins" in conditions:
            streak = self.state.progression.story_flags.get("current_streak_wins", 0)
            if streak < conditions["streak_wins"]:
                unmet.append(f"需连续胜利{conditions['streak_wins']}场（当前：{streak}）")

        if "total_dao" in conditions:
            if self.state.player.dao < conditions["total_dao"]:
                unmet.append(f"需累计{conditions['total_dao']}道（当前：{self.state.player.dao}）")

        if "no_revealed_reverberation" in conditions:
            if self.state.progression.story_flags.get("revealed_reverberation"):
                unmet.append("不能透露过任何回响能力")

        return len(unmet) == 0, unmet

    def join_faction(self, faction_id: str) -> bool:
        """加入势力"""
        can_join, unmet = self.check_join_conditions(faction_id)
        if not can_join:
            return False

        old_faction = self.state.player.faction
        self.state.player.faction = faction_id
        self.state.player.faction_reputation[faction_id] = 30

        if old_faction:
            self.state.player.faction_reputation[old_faction] -= 20

        return True

    def leave_faction(self) -> bool:
        """离开势力"""
        if not self.state.player.faction:
            return False

        old_faction = self.state.player.faction
        self.state.player.faction = None
        self.state.player.faction_reputation[old_faction] = 0
        return True

    def change_reputation(self, faction_id: str, delta: int):
        """改变势力声望"""
        if faction_id in self.state.player.faction_reputation:
            self.state.player.faction_reputation[faction_id] += delta

    def get_reputation(self, faction_id: str) -> int:
        """获取势力声望"""
        return self.state.player.faction_reputation.get(faction_id, 0)

    def get_relation(self, faction1: str, faction2: str) -> str:
        """获取两个势力间的关系"""
        if faction1 == faction2:
            return "self"

        if faction1 > faction2:
            faction1, faction2 = faction2, faction1

        key = f"{faction1}_{faction2}"
        if key in self.relations:
            return self.relations[key].relation

        return "neutral"

    def update_relation(self, faction1: str, faction2: str, new_relation: str):
        """更新势力关系"""
        if faction1 > faction2:
            faction1, faction2 = faction2, faction1

        key = f"{faction1}_{faction2}"
        if key in self.relations:
            self.relations[key].relation = new_relation
            self.relations[key].last_updated = self.state.progression.current_day

    def get_faction_privileges(self, faction_id: str) -> list[str]:
        """获取势力特权"""
        faction = self.factions.get(faction_id)
        if faction:
            return faction.privileges
        return []

    def get_faction_quests(self, faction_id: str) -> list[dict]:
        """获取势力任务"""
        faction = self.factions.get(faction_id)
        if faction:
            return faction.quests
        return []

    def get_available_quests(self) -> list[dict]:
        """获取当前可接任务"""
        if not self.state.player.faction:
            return []

        quests = self.get_faction_quests(self.state.player.faction)
        available = []

        for quest in quests:
            quest_id = quest["quest_id"]
            if quest_id not in self.state.progression.completed_quests:
                available.append(quest)

        return available

    def complete_quest(self, quest_id: str) -> bool:
        """完成任务"""
        if quest_id in self.state.progression.completed_quests:
            return False

        self.state.progression.completed_quests.append(quest_id)
        self.change_reputation(self.state.player.faction, 10)
        return True

    def is_hostile(self, faction_id: str) -> bool:
        """判断是否敌对"""
        if not self.state.player.faction:
            return False
        return self.get_relation(self.state.player.faction, faction_id) == "hostile"

    def is_allied(self, faction_id: str) -> bool:
        """判断是否同盟"""
        if not self.state.player.faction:
            return False
        rel = self.get_relation(self.state.player.faction, faction_id)
        return rel in ["cooperate", "secret_alliance"]