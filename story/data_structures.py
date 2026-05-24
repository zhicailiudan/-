# -*- coding: utf-8 -*-
"""
数据结构定义
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum


@dataclass
class Player:
    """玩家数据"""
    name: str = "觉醒者"
    level: int = 1
    exp: int = 0
    dao: int = 50
    faction: Optional[str] = None
    faction_reputation: dict = field(default_factory=lambda: {
        "heaven_gate": 0,
        "extremist": 0,
        "fortune": 0,
        "shadow": 0
    })
    resurrections: int = 3
    reverberations: list = field(default_factory=list)
    inventory: list = field(default_factory=list)


@dataclass
class Progression:
    """进度数据"""
    current_day: int = 1
    cycle_count: int = 0
    main_quest: str = "day_1_interview"
    completed_quests: list = field(default_factory=list)
    story_flags: dict = field(default_factory=dict)
    memory_fragments: dict = field(default_factory=lambda: {
        "dialogue": [],
        "battle": [],
        "choice": [],
        "discovery": []
    })


@dataclass
class ZodiacProgress:
    """生肖进度"""
    defeated: list = field(default_factory=list)
    unlocked: list = field(default_factory=list)


@dataclass
class KnowledgeBase:
    """知识库进度"""
    kb_id: str = "python_basic"
    mastery: float = 0.0
    weak_points: list = field(default_factory=list)


@dataclass
class NPCRelationship:
    """NPC关系"""
    trust: int = 0
    shared_secrets: list = field(default_factory=list)
    is_betrayed: bool = False


@dataclass
class FactionWar:
    """势力战争"""
    active_war: Optional[str] = None
    war_progress: int = 0


@dataclass
class CrossCycleMemory:
    """跨轮回记忆（轮回重置时保留的部分）"""
    milestones: list = field(default_factory=list)
    mastered_kbs: list = field(default_factory=list)
    permanent_reverberations: list = field(default_factory=list)


@dataclass
class DungeonState:
    """副本状态"""
    dungeon_id: str = ""
    kb_id: str = ""
    kb_name: str = ""
    scene_count: int = 0
    current_index: int = 0
    is_completed: bool = False
    compressed_summary: str = ""


@dataclass
class MilestoneNode:
    """关键节点记录"""
    milestone_id: str = ""
    scene_id: str = ""
    title: str = ""
    summary: str = ""
    cycle_created: int = 0
    linked_kb_id: str = ""
    is_permanent: bool = False


@dataclass
class GameState:
    """完整游戏状态"""
    player: Player = field(default_factory=Player)
    progression: Progression = field(default_factory=Progression)
    zodiac: ZodiacProgress = field(default_factory=ZodiacProgress)
    knowledge_base: KnowledgeBase = field(default_factory=KnowledgeBase)
    npc_relationships: dict = field(default_factory=dict)
    faction_war: FactionWar = field(default_factory=FactionWar)
    cross_cycle_memory: CrossCycleMemory = field(default_factory=CrossCycleMemory)
    dungeon_state: DungeonState = field(default_factory=DungeonState)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "player": {
                "name": self.player.name,
                "level": self.player.level,
                "exp": self.player.exp,
                "dao": self.player.dao,
                "faction": self.player.faction,
                "faction_reputation": self.player.faction_reputation,
                "resurrections": self.player.resurrections,
                "reverberations": self.player.reverberations,
                "inventory": self.player.inventory,
            },
            "progression": {
                "current_day": self.progression.current_day,
                "cycle_count": self.progression.cycle_count,
                "main_quest": self.progression.main_quest,
                "completed_quests": self.progression.completed_quests,
                "story_flags": self.progression.story_flags,
                "memory_fragments": self.progression.memory_fragments,
            },
            "zodiac_defeated": self.zodiac.defeated,
            "zodiac_unlocked": self.zodiac.unlocked,
            "knowledge_base": {
                "kb_id": self.knowledge_base.kb_id,
                "mastery": self.knowledge_base.mastery,
                "weak_points": self.knowledge_base.weak_points,
            },
            "relationships": {
                npc_id: {
                    "trust": rel.trust,
                    "shared_secrets": rel.shared_secrets,
                    "is_betrayed": rel.is_betrayed
                }
                for npc_id, rel in self.npc_relationships.items()
            },
            "faction_war": {
                "active_war": self.faction_war.active_war,
                "war_progress": self.faction_war.war_progress,
            },
            "cross_cycle_memory": {
                "milestones": self.cross_cycle_memory.milestones,
                "mastered_kbs": self.cross_cycle_memory.mastered_kbs,
                "permanent_reverberations": self.cross_cycle_memory.permanent_reverberations,
            },
            "dungeon_state": {
                "dungeon_id": self.dungeon_state.dungeon_id,
                "kb_id": self.dungeon_state.kb_id,
                "kb_name": self.dungeon_state.kb_name,
                "scene_count": self.dungeon_state.scene_count,
                "current_index": self.dungeon_state.current_index,
                "is_completed": self.dungeon_state.is_completed,
                "compressed_summary": self.dungeon_state.compressed_summary,
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """从字典创建"""
        state = cls()
        if "player" in data:
            p = data["player"]
            state.player = Player(
                name=p.get("name", "觉醒者"),
                level=p.get("level", 1),
                exp=p.get("exp", 0),
                dao=p.get("dao", 50),
                faction=p.get("faction"),
                faction_reputation=p.get("faction_reputation", {}),
                resurrections=p.get("resurrections", 3),
                reverberations=p.get("reverberations", []),
                inventory=p.get("inventory", []),
            )
        if "progression" in data:
            pg = data["progression"]
            state.progression = Progression(
                current_day=pg.get("current_day", 1),
                cycle_count=pg.get("cycle_count", 0),
                main_quest=pg.get("main_quest", "day_1_interview"),
                completed_quests=pg.get("completed_quests", []),
                story_flags=pg.get("story_flags", {}),
                memory_fragments=pg.get("memory_fragments", {}),
            )
        if "zodiac_defeated" in data:
            state.zodiac.defeated = data["zodiac_defeated"]
        if "zodiac_unlocked" in data:
            state.zodiac.unlocked = data["zodiac_unlocked"]
        if "knowledge_base" in data:
            kb = data["knowledge_base"]
            state.knowledge_base = KnowledgeBase(
                kb_id=kb.get("kb_id", "python_basic"),
                mastery=kb.get("mastery", 0.0),
                weak_points=kb.get("weak_points", []),
            )
        if "relationships" in data:
            for npc_id, rel_data in data["relationships"].items():
                state.npc_relationships[npc_id] = NPCRelationship(
                    trust=rel_data.get("trust", 0),
                    shared_secrets=rel_data.get("shared_secrets", []),
                    is_betrayed=rel_data.get("is_betrayed", False),
                )
        if "faction_war" in data:
            state.faction_war = FactionWar(
                active_war=data["faction_war"].get("active_war"),
                war_progress=data["faction_war"].get("war_progress", 0),
            )
        if "cross_cycle_memory" in data:
            ccm = data["cross_cycle_memory"]
            state.cross_cycle_memory = CrossCycleMemory(
                milestones=ccm.get("milestones", []),
                mastered_kbs=ccm.get("mastered_kbs", []),
                permanent_reverberations=ccm.get("permanent_reverberations", []),
            )
        if "dungeon_state" in data:
            ds = data["dungeon_state"]
            state.dungeon_state = DungeonState(
                dungeon_id=ds.get("dungeon_id", ""),
                kb_id=ds.get("kb_id", ""),
                kb_name=ds.get("kb_name", ""),
                scene_count=ds.get("scene_count", 0),
                current_index=ds.get("current_index", 0),
                is_completed=ds.get("is_completed", False),
                compressed_summary=ds.get("compressed_summary", ""),
            )
        return state