# -*- coding: utf-8 -*-
"""
存档系统
"""

import json
import os
from datetime import datetime
from typing import Optional, List
from .data_structures import GameState
from .story_engine import StoryEngine


class GameSave:
    """存档管理"""

    SAVE_DIR = "data/saves"
    MAX_SAVES = 10

    def __init__(self):
        self._ensure_save_dir()

    def _ensure_save_dir(self):
        """确保存档目录存在"""
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)

    def _get_save_path(self, save_name: str) -> str:
        """获取存档路径"""
        return os.path.join(self.SAVE_DIR, f"{save_name}.json")

    def _get_index_path(self) -> str:
        """获取存档索引路径"""
        return os.path.join(self.SAVE_DIR, "index.json")

    def _get_save_index(self) -> dict:
        """获取存档索引"""
        index_path = self._get_index_path()
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"saves": []}

    def _save_index(self, index: dict):
        """保存存档索引"""
        index_path = self._get_index_path()
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def save(self, engine: StoryEngine, save_name: Optional[str] = None) -> str:
        """保存游戏"""
        if save_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"save_{timestamp}"

        save_path = self._get_save_path(save_name)
        save_data = {
            "save_name": save_name,
            "save_time": datetime.now().isoformat(),
            "game_state": engine.to_dict(),
            "version": "1.0.0"
        }

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        index = self._get_save_index()
        save_info = {
            "name": save_name,
            "time": save_data["save_time"],
            "day": engine.state.progression.current_day,
            "faction": engine.state.player.faction,
            "dao": engine.state.player.dao
        }

        existing = [i for i, s in enumerate(index["saves"]) if s["name"] == save_name]
        if existing:
            index["saves"][existing[0]] = save_info
        else:
            index["saves"].insert(0, save_info)

        if len(index["saves"]) > self.MAX_SAVES:
            to_delete = index["saves"][self.MAX_SAVES:]
            index["saves"] = index["saves"][:self.MAX_SAVES]
            for old_save in to_delete:
                path = self._get_save_path(old_save["name"])
                if os.path.exists(path):
                    os.remove(path)

        self._save_index(index)
        return save_name

    def load(self, save_name: str) -> Optional[StoryEngine]:
        """加载游戏"""
        save_path = self._get_save_path(save_name)
        if not os.path.exists(save_path):
            return None

        with open(save_path, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        engine = StoryEngine.from_dict(save_data["game_state"])
        return engine

    def list_saves(self) -> List[dict]:
        """列出所有存档"""
        index = self._get_save_index()
        return index["saves"]

    def delete_save(self, save_name: str) -> bool:
        """删除存档"""
        save_path = self._get_save_path(save_name)
        if not os.path.exists(save_path):
            return False

        os.remove(save_path)

        index = self._get_save_index()
        index["saves"] = [s for s in index["saves"] if s["name"] != save_name]
        self._save_index(index)
        return True

    def has_save(self, save_name: str) -> bool:
        """检查存档是否存在"""
        return os.path.exists(self._get_save_path(save_name))

    def get_save_count(self) -> int:
        """获取存档数量"""
        return len(self._get_save_index()["saves"])

    def quick_save(self, engine: StoryEngine) -> str:
        """快速存档"""
        return self.save(engine, "quicksave")

    def quick_load(self) -> Optional[StoryEngine]:
        """快速读档"""
        return self.load("quicksave")

    def has_quicksave(self) -> bool:
        """检查快速存档是否存在"""
        return self.has_save("quicksave")


class NewGame:
    """新游戏配置"""

    @staticmethod
    def create_initial_state(
        player_name: str = "觉醒者",
        knowledge_base_id: str = "python_basic"
    ) -> StoryEngine:
        """创建初始游戏状态"""
        from .data_structures import (
            Player, Progression, ZodiacProgress, KnowledgeBase
        )

        player = Player(
            name=player_name,
            level=1,
            exp=0,
            dao=50,
            resurrections=3,
            inventory=["复活币x1"]
        )

        progression = Progression(
            current_day=1,
            cycle_count=0,
            main_quest="day_1_interview",
            completed_quests=["day_1_interview"]
        )

        zodiac = ZodiacProgress(
            defeated=[],
            unlocked=["人级全部"]
        )

        knowledge_base = KnowledgeBase(
            kb_id=knowledge_base_id,
            mastery=0.0,
            weak_points=[]
        )

        state = GameState(
            player=player,
            progression=progression,
            zodiac=zodiac,
            knowledge_base=knowledge_base
        )

        engine = StoryEngine(state)

        from .main_story import STORY_DATA
        engine.load_story(STORY_DATA)

        return engine