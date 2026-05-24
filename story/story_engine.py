# -*- coding: utf-8 -*-
"""
剧情引擎核心
"""

import json
import os
from typing import Optional, Callable, Any
from .data_structures import GameState, Player, Progression, ZodiacProgress, KnowledgeBase
from .story_nodes import Scene, Choice, DayStory, BranchingPoint
from .constants import *
from .dungeon_generator import DungeonManifest, SceneFrame


class StoryEngine:
    """剧情引擎"""

    def __init__(self, state: Optional[GameState] = None):
        self.state = state or GameState()
        self.days: dict[int, DayStory] = {}
        self.current_day: Optional[DayStory] = None
        self.current_scene: Optional[Scene] = None
        self._event_callbacks: dict[str, Callable] = {}

        # 副本支持
        self.current_dungeon: Optional[DungeonManifest] = None
        self.dungeon_scenes: list = []
        self.dungeon_scene_index: int = 0

    def register_event(self, event_name: str, callback: Callable):
        """注册事件回调"""
        self._event_callbacks[event_name] = callback

    def trigger_event(self, event_name: str, **kwargs):
        """触发事件"""
        if event_name in self._event_callbacks:
            self._event_callbacks[event_name](self.state, **kwargs)

    def load_story(self, story_data: dict):
        """加载剧情数据"""
        for day_data in story_data.get("days", []):
            day_story = DayStory(
                day=day_data["day"],
                title=day_data["title"],
                default_scene=day_data.get("default_scene", "start")
            )
            for scene_data in day_data.get("scenes", []):
                scene = Scene(
                    scene_id=scene_data["scene_id"],
                    title=scene_data["title"],
                    npcs=scene_data.get("npcs", []),
                    text=scene_data.get("text", ""),
                    background=scene_data.get("background", ""),
                    auto_advance=scene_data.get("auto_advance", False),
                    next_scene=scene_data.get("next_scene"),
                    choices=[
                        Choice(
                            choice_id=c["choice_id"],
                            text=c["text"],
                            next_scene=c.get("next_scene"),
                            effects=c.get("effects", {}),
                            condition=c.get("condition")
                        )
                        for c in scene_data.get("choices", [])
                    ]
                )
                day_story.scenes[scene.scene_id] = scene
            self.days[day_story.day] = day_story

    def start_day(self, day: int) -> Scene:
        """开始某日剧情"""
        if day not in self.days:
            raise ValueError(f"Day {day} not found in story data")
        self.state.progression.current_day = day
        self.current_day = self.days[day]
        default_scene_id = self.current_day.default_scene
        self.current_scene = self.current_day.scenes[default_scene_id]
        return self.current_scene

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """获取场景"""
        if self.current_day and scene_id in self.current_day.scenes:
            return self.current_day.scenes[scene_id]
        return None

    def go_to_scene(self, scene_id: str) -> Optional[Scene]:
        """跳转到场景"""
        scene = self.get_scene(scene_id)
        if scene:
            self.current_scene = scene
            self.trigger_event("scene_changed", scene=scene)
        return scene

    def make_choice(self, choice_id: str) -> Optional[Scene]:
        """做出选择"""
        if not self.current_scene:
            return None

        choice = None
        for c in self.current_scene.choices:
            if c.choice_id == choice_id:
                choice = c
                break

        if not choice:
            return None

        self._apply_effects(choice.effects)

        if choice.next_scene:
            return self.go_to_scene(choice.next_scene)
        elif self.current_scene.next_scene:
            return self.go_to_scene(self.current_scene.next_scene)
        elif self.current_scene.auto_advance:
            return self._advance_scene()
        return None

    def _apply_effects(self, effects: dict):
        """应用选择效果"""
        effects = effects or {}

        if "flags" in effects:
            self.state.progression.story_flags.update(effects["flags"])

        if "faction" in effects:
            self.state.player.faction = effects["faction"]
            self.trigger_event("faction_joined", faction=effects["faction"])

        if "faction_reputation" in effects:
            for faction, value in effects["faction_reputation"].items():
                if faction in self.state.player.faction_reputation:
                    self.state.player.faction_reputation[faction] += value

        if "dao" in effects:
            self.state.player.dao += effects["dao"]

        if "exp" in effects:
            self.state.player.exp += effects["exp"]

        if "memory_fragment" in effects:
            frag_type = effects["memory_fragment"].get("type", "choice")
            self.state.progression.memory_fragments[frag_type].append(
                effects["memory_fragment"]["content"]
            )

        if "add_quest" in effects:
            if effects["add_quest"] not in self.state.progression.completed_quests:
                self.state.progression.completed_quests.append(effects["add_quest"])

        if "trigger_event" in effects:
            self.trigger_event(effects["trigger_event"])

    def _advance_scene(self) -> Optional[Scene]:
        """自动推进场景"""
        if self.current_scene and self.current_scene.next_scene:
            return self.go_to_scene(self.current_scene.next_scene)
        return None

    def get_available_choices(self) -> list[Choice]:
        """获取可用选择（考虑条件）"""
        if not self.current_scene:
            return []
        available = []
        for choice in self.current_scene.choices:
            if choice.condition:
                if not self._check_condition(choice.condition):
                    continue
            available.append(choice)
        return available

    def _check_condition(self, condition: dict) -> bool:
        """检查条件是否满足"""
        if "faction" in condition:
            if self.state.player.faction != condition["faction"]:
                return False
        if "flags" in condition:
            for key, value in condition["flags"].items():
                if self.state.progression.story_flags.get(key) != value:
                    return False
        if "dao_gte" in condition:
            if self.state.player.dao < condition["dao_gte"]:
                return False
        if "dao_lte" in condition:
            if self.state.player.dao > condition["dao_lte"]:
                return False
        if "day_gte" in condition:
            if self.state.progression.current_day < condition["day_gte"]:
                return False
        return True

    # ===== 副本支持 =====

    def load_dungeon(self, manifest: DungeonManifest) -> Optional[SceneFrame]:
        """加载副本，返回第一个场景"""
        self.current_dungeon = manifest
        self.dungeon_scenes = manifest.scenes
        self.dungeon_scene_index = 0
        if self.dungeon_scenes:
            return self.dungeon_scenes[0]
        return None

    def get_current_dungeon_scene(self) -> Optional[SceneFrame]:
        """获取当前副本场景"""
        if not self.dungeon_scenes:
            return None
        if 0 <= self.dungeon_scene_index < len(self.dungeon_scenes):
            return self.dungeon_scenes[self.dungeon_scene_index]
        return None

    def advance_dungeon_scene(self) -> Optional[SceneFrame]:
        """推进到下一个场景"""
        if not self.dungeon_scenes:
            return None
        self.dungeon_scene_index += 1
        if self.dungeon_scene_index < len(self.dungeon_scenes):
            return self.dungeon_scenes[self.dungeon_scene_index]
        return None

    def is_dungeon_complete(self) -> bool:
        """副本是否全部走完"""
        return (len(self.dungeon_scenes) > 0
                and self.dungeon_scene_index >= len(self.dungeon_scenes))

    def has_active_dungeon(self) -> bool:
        """是否有进行中的副本"""
        return self.current_dungeon is not None and not self.is_dungeon_complete()

    def clear_dungeon(self):
        """清除副本状态"""
        self.current_dungeon = None
        self.dungeon_scenes = []
        self.dungeon_scene_index = 0

    def next_day(self) -> bool:
        """进入下一天"""
        next_day = self.state.progression.current_day + 1
        if next_day > 10:
            self.trigger_event("story_complete", ending=ENDING_CYCLE)
            return False
        self.trigger_event("day_ended", day=self.state.progression.current_day)
        self.start_day(next_day)
        return True

    def get_current_info(self) -> dict:
        """获取当前状态信息"""
        return {
            "day": self.state.progression.current_day,
            "cycle": self.state.progression.cycle_count,
            "scene": self.current_scene.scene_id if self.current_scene else None,
            "scene_title": self.current_scene.title if self.current_scene else None,
            "dao": self.state.player.dao,
            "exp": self.state.player.exp,
            "faction": self.state.player.faction,
        }

    def add_reverberation(self, rev_id: str, level: int = 1):
        """添加回响"""
        rev_str = f"{rev_id}_lv{level}"
        if rev_str not in self.state.player.reverberations:
            self.state.player.reverberations.append(rev_str)
            self.trigger_event("reverberation_gained", reverberation=rev_id)

    def check_ending_conditions(self, ending: dict) -> bool:
        """检查结局条件"""
        conditions = ending.get("conditions", {})
        if "zodiac_defeated" in conditions:
            if len(self.state.zodiac.defeated) < conditions["zodiac_defeated"]:
                return False
        if "dao" in conditions:
            if self.state.player.dao < conditions["dao"]:
                return False
        if "faction" in conditions:
            if self.state.player.faction != conditions["faction"]:
                return False
        if "reverberations" in conditions:
            for rev in conditions["reverberations"]:
                if not any(r.startswith(rev) for r in self.state.player.reverberations):
                    return False
        return True

    def to_dict(self) -> dict:
        """序列化状态"""
        return self.state.to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> "StoryEngine":
        """反序列化"""
        engine = cls(GameState.from_dict(data))
        return engine