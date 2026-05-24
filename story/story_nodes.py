# -*- coding: utf-8 -*-
"""
剧情节点定义
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Choice:
    """选择选项"""
    choice_id: str
    text: str
    next_scene: Optional[str] = None
    effects: dict = field(default_factory=dict)
    condition: Optional[dict] = None


@dataclass
class Scene:
    """场景"""
    scene_id: str
    title: str
    npcs: list = field(default_factory=list)
    text: str = ""
    background: str = ""
    choices: list = field(default_factory=list)
    auto_advance: bool = False
    next_scene: Optional[str] = None


@dataclass
class DayStory:
    """单日剧情"""
    day: int
    title: str
    scenes: dict = field(default_factory=dict)
    default_scene: str = "start"


@dataclass
class BranchingPoint:
    """分支点"""
    day: int
    condition: str
    branches: dict
    default_branch: str = "independent"


@dataclass
class Ending:
    """结局"""
    ending_id: str
    title: str
    description: str
    conditions: dict
    final_battle: Optional[str] = None