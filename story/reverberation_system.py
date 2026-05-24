# -*- coding: utf-8 -*-
"""
回响系统
"""

from dataclasses import dataclass, field
from typing import Optional
from .constants import *
from .data_structures import GameState


@dataclass
class Reverberation:
    rev_id: str
    name: str
    description: str
    awakening_condition: str
    max_level: int = 4
    effects: dict = field(default_factory=dict)


REVERBERATION_DEFINITIONS = {
    REVERBERATION_LIFE: Reverberation(
        rev_id=REVERBERATION_LIFE,
        name="生生不息",
        description="连续复习同一知识点3次后觉醒",
        awakening_condition="连续3次复习同一知识点",
        effects={
            1: {"review_efficiency": 0.5},
            2: {"review_efficiency": 0.7, "bonus_questions": 1},
            3: {"review_efficiency": 0.9, "bonus_questions": 2, "auto_review": True},
            4: {"review_efficiency": 1.0, "bonus_questions": 3, "auto_review": True}
        }
    ),

    REVERBERATION_BREAK_ALL: Reverberation(
        rev_id=REVERBERATION_BREAK_ALL,
        name="破万法",
        description="连续解出3道难题后觉醒",
        awakening_condition="连续解出3道难题",
        effects={
            1: {"hard_question_bonus": 0.3},
            2: {"hard_question_bonus": 0.5, "hint_free": True},
            3: {"hard_question_bonus": 0.7, "hint_free": True, "critical_hit": True},
            4: {"hard_question_bonus": 1.0, "hint_free": True, "critical_hit": True}
        }
    ),

    REVERBERATION_LUCK: Reverberation(
        rev_id=REVERBERATION_LUCK,
        name="强运",
        description="考试连续3次满分后觉醒",
        awakening_condition="考试连续3次满分",
        effects={
            1: {"random_guess_bonus": 0.2},
            2: {"random_guess_bonus": 0.35, "dao_bonus": 0.1},
            3: {"random_guess_bonus": 0.5, "dao_bonus": 0.2, "perfect_protection": True},
            4: {"random_guess_bonus": 0.7, "dao_bonus": 0.3, "perfect_protection": True}
        }
    ),

    REVERBERATION_CAT: Reverberation(
        rev_id=REVERBERATION_CAT,
        name="猫",
        description="连续学习7天后觉醒",
        awakening_condition="连续学习7天",
        effects={
            1: {"hidden_learning_time": True},
            2: {"hidden_learning_time": True, "stealth_bonus": 0.2},
            3: {"hidden_learning_time": True, "stealth_bonus": 0.4, "untraceable": True},
            4: {"hidden_learning_time": True, "stealth_bonus": 0.6, "untraceable": True}
        }
    ),

    REVERBERATION_DREAM: Reverberation(
        rev_id=REVERBERATION_DREAM,
        name="入梦",
        description="理解达到100%后觉醒",
        awakening_condition="理解达到100%",
        effects={
            1: {"deep_knowledge": True},
            2: {"deep_knowledge": True, "comprehension_speed": 0.3},
            3: {"deep_knowledge": True, "comprehension_speed": 0.5, "unlock_hidden": True},
            4: {"deep_knowledge": True, "comprehension_speed": 0.7, "unlock_hidden": True}
        }
    ),

    REVERBERATION_ANALYZE: Reverberation(
        rev_id=REVERBERATION_ANALYZE,
        name="离析",
        description="连续正确50道题后觉醒",
        awakening_condition="连续正确50道题",
        effects={
            1: {"knowledge_breakdown": True},
            2: {"knowledge_breakdown": True, "analyze_enemy": True},
            3: {"knowledge_breakdown": True, "analyze_enemy": True, "predict_question": True},
            4: {"knowledge_breakdown": True, "analyze_enemy": True, "predict_question": True}
        }
    ),

    REVERBERATION_DISASTER: Reverberation(
        rev_id=REVERBERATION_DISASTER,
        name="招灾",
        description="答错10道题后觉醒",
        awakening_condition="答错10道题",
        effects={
            1: {"disaster_sense": True},
            2: {"disaster_sense": True, "danger_warning": True},
            3: {"disaster_sense": True, "danger_warning": True, "disaster_immunity": 0.3},
            4: {"disaster_sense": True, "danger_warning": True, "disaster_immunity": 0.6}
        }
    ),

    REVERBERATION_TIME_REWIND: Reverberation(
        rev_id=REVERBERATION_TIME_REWIND,
        name="时间回溯",
        description="掌握所有基础知识后觉醒",
        awakening_condition="掌握所有基础",
        effects={
            1: {"rewind_question": True},
            2: {"rewind_question": True, "time_pause": True},
            3: {"rewind_question": True, "time_pause": True, "slow_time": True},
            4: {"rewind_question": True, "time_pause": True, "slow_time": True, "time_stop": True}
        }
    )
}


class ReverberationSystem:
    def __init__(self, state: GameState):
        self.state = state
        self.reverberations = REVERBERATION_DEFINITIONS
        self.progress_trackers: dict = {}
        self._init_trackers()

    def _init_trackers(self):
        self.progress_trackers = {
            "review_streak": 0,
            "hard_question_streak": 0,
            "perfect_exam_streak": 0,
            "learning_day_streak": 0,
            "comprehension_total": 0.0,
            "correct_answer_streak": 0,
            "wrong_answer_total": 0,
            "basic_mastered_count": 0
        }

    def get_reverberation(self, rev_id: str) -> Optional[Reverberation]:
        return self.reverberations.get(rev_id)

    def has_reverberation(self, rev_id: str) -> bool:
        return any(r.startswith(rev_id) for r in self.state.player.reverberations)

    def get_reverberation_level(self, rev_id: str) -> int:
        for r in self.state.player.reverberations:
            if r.startswith(rev_id):
                try:
                    return int(r.split("_lv")[1])
                except (IndexError, ValueError):
                    return 1
        return 0

    def get_effect(self, rev_id: str) -> dict:
        level = self.get_reverberation_level(rev_id)
        if level == 0:
            return {}
        rev = self.reverberations.get(rev_id)
        if not rev:
            return {}
        return rev.effects.get(level, {})

    def gain_reverberation(self, rev_id: str) -> bool:
        if self.has_reverberation(rev_id):
            level = self.get_reverberation_level(rev_id)
            if level < REVERBERATION_DEFINITIONS[rev_id].max_level:
                self._upgrade_reverberation(rev_id)
                return True
            return False
        rev_str = f"{rev_id}_lv1"
        self.state.player.reverberations.append(rev_str)
        self.state.progression.memory_fragments["discovery"].append(f"awakened: {rev_id}")
        return True

    def _upgrade_reverberation(self, rev_id: str):
        current_level = self.get_reverberation_level(rev_id)
        for i, r in enumerate(self.state.player.reverberations):
            if r.startswith(rev_id):
                self.state.player.reverberations[i] = f"{rev_id}_lv{current_level + 1}"
                break

    def can_upgrade(self, rev_id: str) -> tuple[bool, str]:
        if not self.has_reverberation(rev_id):
            return False, "not awakened"
        level = self.get_reverberation_level(rev_id)
        rev = REVERBERATION_DEFINITIONS.get(rev_id)
        if level >= rev.max_level:
            return False, "max level"
        return True, f"continue to upgrade (current: {level})"

    def track_event(self, event_type: str, **kwargs):
        if event_type == "review":
            self.progress_trackers["review_streak"] += 1
            if self.progress_trackers["review_streak"] >= 3:
                self._check_awakening(REVERBERATION_LIFE)
        elif event_type == "hard_question_correct":
            self.progress_trackers["hard_question_streak"] += 1
            if self.progress_trackers["hard_question_streak"] >= 3:
                self._check_awakening(REVERBERATION_BREAK_ALL)
        elif event_type == "perfect_exam":
            self.progress_trackers["perfect_exam_streak"] += 1
            if self.progress_trackers["perfect_exam_streak"] >= 3:
                self._check_awakening(REVERBERATION_LUCK)
        elif event_type == "daily_learning":
            self.progress_trackers["learning_day_streak"] += 1
            if self.progress_trackers["learning_day_streak"] >= 7:
                self._check_awakening(REVERBERATION_CAT)
        elif event_type == "comprehension":
            amount = kwargs.get("amount", 0)
            self.progress_trackers["comprehension_total"] += amount
            if self.progress_trackers["comprehension_total"] >= 100:
                self._check_awakening(REVERBERATION_DREAM)
        elif event_type == "correct_answer":
            self.progress_trackers["correct_answer_streak"] += 1
            if self.progress_trackers["correct_answer_streak"] >= 50:
                self._check_awakening(REVERBERATION_ANALYZE)
        elif event_type == "wrong_answer":
            self.progress_trackers["wrong_answer_total"] += 1
            if self.progress_trackers["wrong_answer_total"] >= 10:
                self._check_awakening(REVERBERATION_DISASTER)
        elif event_type == "basic_mastered":
            self.progress_trackers["basic_mastered_count"] += 1
            if self.progress_trackers["basic_mastered_count"] >= 10:
                self._check_awakening(REVERBERATION_TIME_REWIND)

    def _check_awakening(self, rev_id: str):
        if not self.has_reverberation(rev_id):
            self.gain_reverberation(rev_id)
            return True
        return False

    def use_reverberation(self, rev_id: str, target: Optional[str] = None) -> tuple[bool, str]:
        if not self.has_reverberation(rev_id):
            return False, "not awakened"
        level = self.get_reverberation_level(rev_id)
        rev = self.reverberations.get(rev_id)
        if rev_id == REVERBERATION_LIFE:
            progress = self.progress_trackers.get("review_count", 0)
            self.progress_trackers["review_count"] = progress + 1
            return True, f"efficiency +{rev.effects[level].get('review_efficiency', 0)*100}%"
        elif rev_id == REVERBERATION_TIME_REWIND:
            if target == "rewind":
                return True, "can rewind previous question"
        return True, f"{rev.name} activated"

    def get_all_progress(self) -> dict:
        return {
            "reverberations": [
                {
                    "id": rev_id,
                    "name": rev.name,
                    "level": self.get_reverberation_level(rev_id),
                    "max_level": rev.max_level,
                    "effects": self.get_effect(rev_id),
                    "description": rev.description
                }
                for rev_id, rev in self.reverberations.items()
            ],
            "trackers": self.progress_trackers.copy()
        }

    def can_trigger_hidden_ending(self) -> bool:
        required_revs = [REVERBERATION_TIME_REWIND, REVERBERATION_DREAM]
        return all(self.has_reverberation(rev_id) for rev_id in required_revs)