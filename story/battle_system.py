# -*- coding: utf-8 -*-
"""
战斗系统
"""

from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum
from .constants import *
from .data_structures import GameState


@dataclass
class Question:
    """题目"""
    question_id: str
    content: str
    options: list[str] = field(default_factory=list)
    correct_answer: str = ""
    difficulty: int = 1
    topic: str = ""


@dataclass
class BattleResult:
    """战斗结果"""
    victory: bool
    correct_count: int
    total_questions: int
    rewards: dict = field(default_factory=dict)
    new_reverberation: Optional[str] = None
    perfect_clear: bool = False


class BattleSystem:
    """战斗系统"""

    def __init__(self, state: GameState):
        self.state = state
        self.current_battle: Optional[dict] = None
        self.questions: list[Question] = []
        self.current_question_index: int = 0
        self.correct_count: int = 0
        self._question_generator: Optional[Callable] = None

    def set_question_generator(self, generator_func: Callable):
        """设置题目生成器（对接RAG引擎）"""
        self._question_generator = generator_func

    def start_battle(self, zodiac_type: str, zodiac_level: str) -> dict:
        """开始战斗"""
        self.current_battle = {
            "zodiac_type": zodiac_type,
            "zodiac_level": zodiac_level,
            "started": True
        }
        self.questions = []
        self.current_question_index = 0
        self.correct_count = 0

        question_count = self._get_question_count(zodiac_level)
        if self._question_generator:
            self.questions = self._question_generator(
                zodiac_type=zodiac_type,
                count=question_count,
                difficulty=self._get_difficulty(zodiac_level)
            )
        else:
            self.questions = self._generate_mock_questions(question_count)

        return self.get_battle_info()

    def _get_question_count(self, level: str) -> int:
        """获取题目数量"""
        counts = {
            ZODIAC_HUMAN: 3,
            ZODIAC_EARTH: 5,
            ZODIAC_HEAVEN: 7
        }
        return counts.get(level, 3)

    def _get_difficulty(self, level: str) -> int:
        """获取难度等级"""
        difficulties = {
            ZODIAC_HUMAN: 1,
            ZODIAC_EARTH: 3,
            ZODIAC_HEAVEN: 5
        }
        return difficulties.get(level, 1)

    def _generate_mock_questions(self, count: int) -> list[Question]:
        """生成模拟题目"""
        questions = []
        for i in range(count):
            questions.append(Question(
                question_id=f"mock_q_{i+1}",
                content=f"这是第{i+1}道模拟题目。实际题目将由RAG引擎生成。",
                options=["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
                correct_answer="A",
                difficulty=1,
                topic="Python基础"
            ))
        return questions

    def get_current_question(self) -> Optional[Question]:
        """获取当前题目"""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def submit_answer(self, answer: str) -> dict:
        """提交答案"""
        question = self.get_current_question()
        if not question:
            return {"error": "没有待回答的题目"}

        is_correct = answer.upper() == question.correct_answer.upper()
        if is_correct:
            self.correct_count += 1

        result = {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "question_index": self.current_question_index,
            "total_questions": len(self.questions),
            "correct_count": self.correct_count
        }

        self.current_question_index += 1
        result["battle_ended"] = self.current_question_index >= len(self.questions)

        if result["battle_ended"]:
            result["battle_result"] = self._calculate_result()

        return result

    def _calculate_result(self) -> BattleResult:
        """计算战斗结果"""
        total = len(self.questions)
        rate = self.correct_count / total if total > 0 else 0

        level = self.current_battle["zodiac_level"]
        required_rate = {
            ZODIAC_HUMAN: 1.0,
            ZODIAC_EARTH: 0.8,
            ZODIAC_HEAVEN: 0.7
        }

        victory = rate >= required_rate.get(level, 1.0)
        perfect_clear = self.correct_count == total

        zodiac_id = f"{level}_{self.current_battle['zodiac_type']}"
        rewards = {}

        if victory:
            dao_reward = self._calculate_dao_reward(level, perfect_clear)
            rewards["dao"] = dao_reward
            rewards["exp"] = self._calculate_exp_reward(level)

            if zodiac_id not in self.state.zodiac.defeated:
                self.state.zodiac.defeated.append(zodiac_id)

            if perfect_clear:
                rewards["reverberation_fragment"] = True

        return BattleResult(
            victory=victory,
            correct_count=self.correct_count,
            total_questions=total,
            rewards=rewards,
            perfect_clear=perfect_clear
        )

    def _calculate_dao_reward(self, level: str, perfect: bool) -> int:
        """计算道奖励"""
        base_rewards = {
            ZODIAC_HUMAN: 15,
            ZODIAC_EARTH: 40,
            ZODIAC_HEAVEN: 80
        }
        reward = base_rewards.get(level, 15)
        if perfect:
            reward = int(reward * 1.5)
        return reward

    def _calculate_exp_reward(self, level: str) -> int:
        """计算经验奖励"""
        rewards = {
            ZODIAC_HUMAN: 30,
            ZODIAC_EARTH: 80,
            ZODIAC_HEAVEN: 150
        }
        return rewards.get(level, 30)

    def apply_rewards(self, result: BattleResult):
        """应用奖励到游戏状态"""
        if result.victory:
            if "dao" in result.rewards:
                self.state.player.dao += result.rewards["dao"]
            if "exp" in result.rewards:
                self.state.player.exp += result.rewards["exp"]
            if result.perfect_clear:
                self.state.progression.memory_fragments["battle"].append(
                    f"完美击败{self.current_battle['zodiac_level']}_{self.current_battle['zodiac_type']}"
                )

    def get_battle_info(self) -> dict:
        """获取战斗信息"""
        if not self.current_battle:
            return {}
        return {
            "zodiac_type": self.current_battle["zodiac_type"],
            "zodiac_level": self.current_battle["zodiac_level"],
            "total_questions": len(self.questions),
            "current_question": self.current_question_index + 1,
            "required_rate": {
                ZODIAC_HUMAN: "100%",
                ZODIAC_EARTH: "80%",
                ZODIAC_HEAVEN: "70%"
            }.get(self.current_battle["zodiac_level"], "100%")
        }

    def use_hint(self, cost: int = 5) -> Optional[str]:
        """使用提示"""
        if self.state.player.dao < cost:
            return None

        self.state.player.dao -= cost
        question = self.get_current_question()
        if question:
            return f"提示：正确答案是 {question.correct_answer}"
        return None

    def surrender(self) -> dict:
        """投降"""
        self.current_battle = None
        return {"surrendered": True}

    def get_remaining_questions(self) -> int:
        """获取剩余题目数"""
        return len(self.questions) - self.current_question_index


class GameType(Enum):
    """游戏类型"""
    TRUTH_TELLER = "说谎者"      # 找错误选项
    THREE_CHOICE = "三选一"       # 三选一
    SORTING = "排序"             # 排序
    GAMBLE = "赌命"              # 押道答题
    PRISONER = "囚徒困境"        # 双人答题
    CALENDAR = "朔望月"          # 日历规则
    BOX = "木盒"                # 随机箱子
    TIME_LIMIT = "天狗时刻"      # 限时递减
    DEATH = "死亡问答"           # 答错即死
    CYCLIC = "轮回试炼"          # 连续10轮


@dataclass
class GameRule:
    """游戏规则"""
    game_type: GameType
    name: str
    description: str
    difficulty: int
    special_rules: dict = field(default_factory=dict)


GAME_RULES = {
    "human": [
        GameRule(GameType.TRUTH_TELLER, "说谎者", "找出唯一的错误选项", 2),
        GameRule(GameType.THREE_CHOICE, "三选一", "三个选项选正确答案", 1),
        GameRule(GameType.SORTING, "排序", "按正确顺序排列", 3),
    ],
    "earth": [
        GameRule(GameType.GAMBLE, "赌命", "押上道进行答题，输则失去", 4),
        GameRule(GameType.PRISONER, "囚徒困境", "双人答题，对方错你才能对", 4),
        GameRule(GameType.CALENDAR, "朔望月", "日历规则下的答题", 3),
        GameRule(GameType.BOX, "木盒", "随机抽取题目箱", 3),
    ],
    "heaven": [
        GameRule(GameType.TIME_LIMIT, "天狗时刻", "限时答题，时间递减", 5),
        GameRule(GameType.DEATH, "死亡问答", "答错即死", 5),
        GameRule(GameType.CYCLIC, "轮回试炼", "连续10轮答对进入下一轮", 5),
    ]
}


def get_available_games(level: str) -> list[GameRule]:
    """获取可用的游戏"""
    return GAME_RULES.get(level, [])