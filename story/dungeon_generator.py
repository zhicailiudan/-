# -*- coding: utf-8 -*-
"""
副本场景生成器 — 将知识内容转换为终焉之地风格剧情副本
"""

import json
import os
import re
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime

import config


@dataclass
class SceneFrame:
    """单个场景框架（LLM 预生成，不含角色发言）"""
    scene_id: str = ""
    title: str = ""
    location: str = ""
    prop: str = ""
    atmosphere: str = ""
    knowledge_seed: str = ""


@dataclass
class DungeonManifest:
    """副本清单"""
    dungeon_id: str = ""
    dungeon_name: str = ""
    kb_id: str = ""
    kb_name: str = ""
    atmosphere: str = ""
    introduction: str = ""
    scene_count: int = 0
    scenes: List[SceneFrame] = field(default_factory=list)
    created_at: str = ""
    cycle_count: int = 1


DUNGEON_SYSTEM_PROMPT = """你是「终焉之地·知识觉醒」的副本场景生成器。
你的任务是将用户提供的知识内容转换为沉浸式的终焉之地剧情场景。

世界观：
终焉之地是由「天龙」创造的试炼空间。觉醒者（玩家）意外进入此地，
需要通过知识学习获得力量。有一座知识城池「道城」，城中有十二生肖守护者。
四大势力：天堂口（团结协作）、极道（力量至上）、貔貅（利益交换）、猫（暗中行动）。

三个助手角色的人格：
- 齐夏：极度理性、稳定、克制。他只做一件事：让问题收敛。
- 楚天秋：逻辑严密、条理清晰，擅长构建框架和体系。
- 乔家劲：行动派，信奉「干就完了」，直接粗暴有效。

输出要求：只输出合法的 JSON，不要包含任何其他文字或 markdown 标记。
场景数量 = 知识点数，最少1个最多5个。"""


class DungeonGenerator:
    """副本场景生成器"""

    def __init__(self, llm=None):
        self.llm = llm
        self._manifest_cache = {}

    def generate(
        self,
        kb_text: str,
        kb_id: str,
        kb_name: str,
        cycle_count: int = 1,
        main_stage: str = "降临"
    ) -> DungeonManifest:
        """核心入口：文本 → LLM → 存储 → 返回"""
        # 尝试 LLM 生成
        manifest = self._try_llm_generate(kb_text, kb_id, kb_name, cycle_count, main_stage)
        if manifest is None:
            manifest = self._mock_generate(kb_text, kb_id, kb_name, cycle_count)

        # 生成唯一 ID
        raw = f"{kb_id}_{time.time()}"
        manifest.dungeon_id = hashlib.sha256(raw.encode()).hexdigest()[:8]
        manifest.created_at = datetime.now().isoformat()

        # 存储到文件
        self._save_manifest(manifest)
        return manifest

    def _try_llm_generate(self, kb_text, kb_id, kb_name, cycle_count, main_stage) -> Optional[DungeonManifest]:
        """尝试用 LLM 生成副本清单"""
        if not self.llm:
            return None

        # 截断知识文本防止超长
        truncated = kb_text[:3000] if len(kb_text) > 3000 else kb_text

        stage_map = {1: "降临", 2: "裂痕", 3: "逼近真相", 4: "超越轮回"}
        stage = stage_map.get(cycle_count, "降临")

        prompt = f"""{DUNGEON_SYSTEM_PROMPT}

用户输入格式：
【当前轮回数】第 {cycle_count} 次轮回
【当前主线阶段】{stage}
【任务】
将以下知识内容转换为终焉之地风格的副本场景。每个场景对应一个独立知识点，
场景需要包装在终焉之地世界观（地点/道具/氛围）下，且 knowledge_seed 必须
用叙事语言呈现知识核心。

【输出JSON格式】
{{
  "dungeon_name": "终焉之地风格的副本名称",
  "atmosphere": "副本整体氛围一句话",
  "introduction": "副本引言2-3句",
  "scenes": [
    {{
      "title": "场景标题",
      "location": "终焉之地地点",
      "prop": "承载知识的道具",
      "atmosphere": "该场景氛围",
      "knowledge_seed": "叙事化的知识引子"
    }}
  ]
}}

场景数量 = 知识点数，最少1个最多5个。

知识内容：
{truncated}"""

        from langchain_core.messages import HumanMessage
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            return self._parse_llm_response(content, kb_id, kb_name, cycle_count)
        except Exception:
            return None

    def _parse_llm_response(self, content: str, kb_id, kb_name, cycle_count) -> Optional[DungeonManifest]:
        """解析 LLM 返回的 JSON"""
        # 尝试提取 JSON（可能被 markdown 包裹）
        json_match = re.search(r'\{[\s\S]*\}', content)
        if not json_match:
            return None
        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError:
            return None

        scenes = []
        for i, s in enumerate(data.get("scenes", [])):
            scenes.append(SceneFrame(
                scene_id=f"s{i + 1}",
                title=s.get("title", f"场景{i + 1}"),
                location=s.get("location", "未知地点"),
                prop=s.get("prop", ""),
                atmosphere=s.get("atmosphere", ""),
                knowledge_seed=s.get("knowledge_seed", ""),
            ))

        return DungeonManifest(
            dungeon_name=data.get("dungeon_name", "知识副本"),
            kb_id=kb_id,
            kb_name=kb_name,
            atmosphere=data.get("atmosphere", ""),
            introduction=data.get("introduction", ""),
            scene_count=len(scenes),
            scenes=scenes,
            cycle_count=cycle_count,
        )

    def _mock_generate(self, kb_text, kb_id, kb_name, cycle_count) -> DungeonManifest:
        """LLM 不可用时的 mock 回退生成"""
        # 按分段拆成场景
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', kb_text) if p.strip()]
        scenes = []
        for i, p in enumerate(paragraphs[:5]):
            # 取段落前 30 字作为引子
            seed = p[:60] + "……" if len(p) > 60 else p
            scenes.append(SceneFrame(
                scene_id=f"s{i + 1}",
                title=f"第{'一二三四五'[i]}层回廊",
                location=f"知识迷宫·{['东','南','西','北','中'][i]}翼",
                prop="一本泛着微光的古籍",
                atmosphere="尘埃在光束中浮动，空气中弥漫着旧纸张的味道",
                knowledge_seed=seed,
            ))
        if not scenes:
            scenes.append(SceneFrame(
                scene_id="s1",
                title="知识回廊",
                location="遗忘图书馆·东翼",
                prop="一本泛黄的手册",
                atmosphere="寂静笼罩着这座尘封的图书馆",
                knowledge_seed=kb_text[:80] + "……" if len(kb_text) > 80 else kb_text,
            ))

        return DungeonManifest(
            dungeon_name=f"知识回廊·{kb_name[:8] if kb_name else '未知'}",
            kb_id=kb_id,
            kb_name=kb_name,
            atmosphere="知识的力量在空气中流动，等待着被唤醒",
            introduction=f"你踏入了一座由知识构建的迷宫。{kb_name}的奥秘隐藏在这里，等待你去发掘。",
            scene_count=len(scenes),
            scenes=scenes,
            cycle_count=cycle_count,
        )

    def _save_manifest(self, manifest: DungeonManifest):
        """存储副本到文件"""
        dungeon_dir = config.DATA_DIR / "dungeons"
        os.makedirs(dungeon_dir, exist_ok=True)
        path = dungeon_dir / f"{manifest.dungeon_id}.json"

        data = asdict(manifest)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_manifest(self, dungeon_id: str) -> Optional[DungeonManifest]:
        """从 data/dungeons/{id}.json 加载"""
        # 先查缓存
        if dungeon_id in self._manifest_cache:
            return self._manifest_cache[dungeon_id]

        path = config.DATA_DIR / "dungeons" / f"{dungeon_id}.json"
        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenes = [SceneFrame(**s) for s in data.get("scenes", [])]
        manifest = DungeonManifest(
            dungeon_id=data["dungeon_id"],
            dungeon_name=data["dungeon_name"],
            kb_id=data["kb_id"],
            kb_name=data["kb_name"],
            atmosphere=data.get("atmosphere", ""),
            introduction=data.get("introduction", ""),
            scene_count=data.get("scene_count", 0),
            scenes=scenes,
            created_at=data.get("created_at", ""),
            cycle_count=data.get("cycle_count", 1),
        )
        self._manifest_cache[dungeon_id] = manifest
        return manifest
