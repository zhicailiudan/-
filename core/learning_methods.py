from enum import Enum
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid
import json
import os
import config


class LearningMethodType(Enum):
    SPACED_REPETITION = "spaced_repetition"
    FEYNMAN = "feynman"
    HEURISTIC = "heuristic"
    QUIZ = "quiz"
    RECALL = "recall"


@dataclass
class LearningRecord:
    chunk_id: str
    method: LearningMethodType
    timestamp: datetime
    quality: int = 0
    next_review: Optional[datetime] = None
    interval_days: int = 1
    repetitions: int = 0
    ease_factor: float = 2.5


@dataclass
class LearningProgress:
    total_chunks: int
    mastered: int = 0
    learning: int = 0
    new: int = 0
    records: Dict[str, LearningRecord] = field(default_factory=dict)


class SpacedRepetition:
    """
    艾宾浩斯遗忘曲线复习系统
    基于SM-2算法，根据记忆质量调整复习间隔
    """
    
    MIN_EASE_FACTOR = 1.3
    DEFAULT_EASE_FACTOR = 2.5
    
    @staticmethod
    def calculate_next_review(record: LearningRecord, quality: int) -> tuple[datetime, int, float]:
        """
        计算下一次复习时间和间隔
        quality: 0-5 (0=完全忘记, 5=完美记住)
        """
        if quality < 3:
            record.repetitions = 0
            interval_days = 1
        else:
            if record.repetitions == 0:
                interval_days = 1
            elif record.repetitions == 1:
                interval_days = 6
            else:
                interval_days = int(record.interval_days * record.ease_factor)
            
            record.repetitions += 1
        
        interval_days = min(interval_days, 365)
        
        new_ease_factor = record.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(new_ease_factor, SpacedRepetition.MIN_EASE_FACTOR)
        
        next_review = datetime.now() + timedelta(days=interval_days)
        
        return next_review, interval_days, new_ease_factor
    
    @staticmethod
    def get_review_priority(records: Dict[str, LearningRecord]) -> List[str]:
        """获取需要复习的chunk优先级"""
        now = datetime.now()
        priority = []
        
        for chunk_id, record in records.items():
            if record.next_review and record.next_review <= now:
                priority.append(chunk_id)
            elif record.next_review:
                days_until = (record.next_review - now).days
                priority.append((days_until, chunk_id))
        
        priority.sort(key=lambda x: x[0] if isinstance(x, tuple) else 0)
        return [x[1] if isinstance(x, tuple) else x for x in priority]


class FeynmanMethod:
    """
    费曼学习法 - 通过讲解来学习
    核心：用自己的话讲清楚 = 真正的理解
    """
    
    @staticmethod
    def generate_teaching_task(knowledge_point: str, context: str) -> str:
        """生成费曼教学任务"""
        return f"""请选择一个知识点，用简洁易懂的语言向一个完全没有基础的人解释。
        
知识点：{knowledge_point}
背景：{context}

要求：
- 用最简单直白的语言，不使用专业术语
- 用生活中的例子类比
- 检查对方是否真正理解
- 一句话总结核心"""
    
    @staticmethod
    def evaluate_explanation(explanation: str, knowledge_point: str) -> dict:
        """评估用户的讲解质量"""
        evaluation_steps = [
            "是否用通俗语言解释了概念？",
            "是否消除了所有专业术语？",
            "是否提供了生活中的例子？",
            "能否让外行听懂？",
            "核心要点是否准确？"
        ]
        
        has_simple = len(explanation) < 200 and "因为" in explanation
        has_example = any(word in explanation for word in ["比如", "像", "相当于", "就像", "例如"])
        
        return {
            "length_check": "简洁" if len(explanation) < 300 else "过长，建议精简",
            "example_check": "有例子" if has_example else "建议添加生活化的例子",
            "terminology_check": "已简化" if has_simple else "注意用通俗语言",
            "suggestion": "很好，继续用它来解释其他概念" if has_simple and has_example else "尝试用身边的事物来类比"
        }


class HeuristicMethod:
    """
    启发式学习 - 通过提问引导思考
    苏格拉底式提问法
    """
    
    @staticmethod
    def generate_socratic_questions(knowledge_point: str) -> List[str]:
        """生成苏格拉底式提问"""
        return [
            f"这个{knowledge_point}的核心是什么？",
            f"你能用自己的话描述吗？",
            f"它和什么有关联？",
            f"如果没有会发生什么？",
            f"和已知知识有什么联系？"
        ]
    
    @staticmethod
    def guide_discovery(knowledge_point: str, user_answer: str, history: List[dict]) -> str:
        """根据用户回答，引导发现新问题"""
        return f"""基于用户的回答：「{user_answer}」
        
请引导他发现更深的层面：
- 追问"为什么"
- 追问"如果...会怎样"
- 引导联系其他知识点"""
    
    @staticmethod
    def should_trigger(user_input: str, progress: LearningProgress) -> bool:
        """判断是否触发启发式引导时机"""
        confusion_signals = ["不懂", "疑惑", "为什么", "什么意思", "不太明白", "卡住了"]
        return any(signal in user_input for signal in confusion_signals)


class LearningScheduler:
    """
    学习调度器 - 根据上下文選擇合适的学习方法
    """
    
    @staticmethod
    def select_method(
        user_input: str,
        method: LearningMethodType,
        progress: LearningProgress
    ) -> tuple[LearningMethodType, str]:
        """选择最合适的学习方法"""
        
        user_lower = user_input.lower()
        
        if "复习" in user_input or "记得" in user_input:
            method_type = LearningMethodType.SPACED_REPETITION
            prompt = "让我们来复习一下之前学过的内容..."
        
        elif "教我" in user_input or "讲讲" in user_input or "解释" in user_input:
            method_type = LearningMethodType.FEYNMAN
            prompt = "换你来讲，我来听，看看你是否真正掌握..."
        
        elif any(word in user_input for word in ["不懂", "为什么", "疑惑", "卡住", "迷茫"]):
            method_type = LearningMethodType.HEURISTIC
            prompt = "让我们一步步来想..."
        
        elif "考我" in user_input or "抽查" in user_input:
            method_type = LearningMethodType.QUIZ
            prompt = "好，让我来考考你..."
        
        else:
            method_type = method
            prompt = ""
        
        return method_type, prompt
    
    @staticmethod
    def get_learning_tip(method: LearningMethodType) -> str:
        """获取学习方法提示"""
        tips = {
            LearningMethodType.SPACED_REPETITION: "📅 复习的最佳时机是在遗忘之前",
            LearningMethodType.FEYNMAN: "📢 教是最好的学",
            LearningMethodType.HEURISTIC: "❓ 好问题比好答案更重要",
            LearningMethodType.QUIZ: "🎯 测试是最好的巩固",
            LearningMethodType.RECALL: "🧠 回忆是记忆的母亲"
        }
        return tips.get(method, "")


class LearningManager:
    """学习进度管理器"""
    
    def __init__(self):
        self.data_file = config.DB_DIR / "learning_progress.json"
        self.progress: Dict[str, LearningProgress] = {}
        self.load()
    
    def get_progress(self, kb_id: str) -> LearningProgress:
        if kb_id not in self.progress:
            self.progress[kb_id] = LearningProgress(total_chunks=0)
        return self.progress[kb_id]
    
    def record_learning(self, kb_id: str, chunk_id: str, method: LearningMethodType, quality: int = 3):
        progress = self.get_progress(kb_id)
        
        if chunk_id not in progress.records:
            progress.records[chunk_id] = LearningRecord(
                chunk_id=chunk_id,
                method=method,
                timestamp=datetime.now()
            )
        
        record = progress.records[chunk_id]
        record.quality = quality
        
        if method == LearningMethodType.SPACED_REPETITION:
            next_review, interval, ease = SpacedRepetition.calculate_next_review(record, quality)
            record.next_review = next_review
            record.interval_days = interval
            record.ease_factor = ease
    
    def get_due_chunks(self, kb_id: str) -> List[str]:
        progress = self.get_progress(kb_id)
        return SpacedRepetition.get_review_priority(progress.records)
    
    def update_chunk_count(self, kb_id: str, count: int):
        """更新知识块总数"""
        progress = self.get_progress(kb_id)
        progress.total_chunks = count
        new_count = count - (progress.mastered + progress.learning + progress.new)
        if new_count > 0:
            progress.new += new_count
    
    def get_mastery_rate(self, kb_id: str) -> float:
        progress = self.get_progress(kb_id)
        if progress.total_chunks == 0:
            return 0.0
        return progress.mastered / progress.total_chunks
    
    def save(self):
        data = {}
        for kb_id, prog in self.progress.items():
            data[kb_id] = {
                "total_chunks": prog.total_chunks,
                "mastered": prog.mastered,
                "learning": prog.learning,
                "new": prog.new,
                "records": {
                    chunk_id: {
                        "chunk_id": r.chunk_id,
                        "method": r.method.value,
                        "timestamp": r.timestamp.isoformat(),
                        "quality": r.quality,
                        "next_review": r.next_review.isoformat() if r.next_review else None,
                        "interval_days": r.interval_days,
                        "repetitions": r.repetitions,
                        "ease_factor": r.ease_factor
                    }
                    for chunk_id, r in prog.records.items()
                }
            }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.progress = {}
                for kb_id, prog_data in data.items():
                    records = {}
                    for chunk_id, r_data in prog_data.get("records", {}).items():
                        records[chunk_id] = LearningRecord(
                            chunk_id=r_data["chunk_id"],
                            method=LearningMethodType(r_data["method"]),
                            timestamp=datetime.fromisoformat(r_data["timestamp"]),
                            quality=r_data.get("quality", 0),
                            next_review=datetime.fromisoformat(r_data["next_review"]) if r_data.get("next_review") else None,
                            interval_days=r_data.get("interval_days", 1),
                            repetitions=r_data.get("repetitions", 0),
                            ease_factor=r_data.get("ease_factor", 2.5)
                        )
                    
                    self.progress[kb_id] = LearningProgress(
                        total_chunks=prog_data.get("total_chunks", 0),
                        mastered=prog_data.get("mastered", 0),
                        learning=prog_data.get("learning", 0),
                        new=prog_data.get("new", 0),
                        records=records
                    )