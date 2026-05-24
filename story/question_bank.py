# -*- coding: utf-8 -*-
"""
题库管理系统 - 支持上传文件生成题目
"""

from dataclasses import dataclass, field
from typing import Optional, List, Literal
from datetime import datetime
import uuid
import json
import os
import config


@dataclass
class Question:
    question_id: str
    question_text: str
    correct_answer: str
    options: List[str] = field(default_factory=list)
    topic: str = ""
    difficulty: int = 1
    source_chunk: str = ""
    zodiac_type: str = ""
    created_at: str = ""


@dataclass
class QuestionBank:
    """题库"""
    bank_id: str
    name: str
    kb_id: str
    description: str = ""
    questions: List[Question] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    total_questions: int = 0
    created_at: str = ""


class QuestionBankManager:
    """题库管理器"""

    def __init__(self):
        self.banks: dict[str, QuestionBank] = {}
        self.data_file = config.DB_DIR / "question_banks.json"
        self.load()

    def create_bank(self, name: str, kb_id: str, description: str = "") -> str:
        """创建题库"""
        bank_id = str(uuid.uuid4())[:8]
        bank = QuestionBank(
            bank_id=bank_id,
            name=name,
            kb_id=kb_id,
            description=description,
            created_at=datetime.now().isoformat()
        )
        self.banks[bank_id] = bank
        self.save()
        return bank_id

    def get_bank(self, bank_id: str) -> Optional[QuestionBank]:
        return self.banks.get(bank_id)

    def get_bank_by_kb(self, kb_id: str) -> Optional[QuestionBank]:
        for bank in self.banks.values():
            if bank.kb_id == kb_id:
                return bank
        return None

    def delete_bank(self, bank_id: str):
        if bank_id in self.banks:
            del self.banks[bank_id]
            self.save()

    def add_questions(self, bank_id: str, questions: List[Question]):
        """添加题目到题库"""
        bank = self.get_bank(bank_id)
        if not bank:
            return False

        for q in questions:
            q.question_id = f"q_{len(bank.questions) + 1}"
            bank.questions.append(q)
            if q.topic and q.topic not in bank.topics:
                bank.topics.append(q.topic)

        bank.total_questions = len(bank.questions)
        self.save()
        return True

    def get_questions_by_topic(self, bank_id: str, topic: str, count: int = 3) -> List[Question]:
        """按主题获取题目"""
        bank = self.get_bank(bank_id)
        if not bank:
            return []

        topic_questions = [q for q in bank.questions if q.topic == topic]
        return topic_questions[:count]

    def get_random_questions(self, bank_id: str, count: int = 3, difficulty: int = 1) -> List[Question]:
        """随机获取题目"""
        import random
        bank = self.get_bank(bank_id)
        if not bank:
            return []

        filtered = [q for q in bank.questions if q.difficulty == difficulty]
        if not filtered:
            filtered = bank.questions

        return random.sample(filtered, min(count, len(filtered)))

    def get_questions_for_zodiac(
        self,
        bank_id: str,
        zodiac_type: str,
        count: int = 3,
        difficulty: int = 1
    ) -> List[Question]:
        """为生肖获取题目"""
        bank = self.get_bank(bank_id)
        if not bank:
            return []

        matching = [q for q in bank.questions
                   if q.zodiac_type == zodiac_type and q.difficulty <= difficulty]
        if not matching:
            matching = [q for q in bank.questions if q.difficulty <= difficulty]

        import random
        return random.sample(matching, min(count, len(matching)))

    def get_all_topics(self, bank_id: str) -> List[str]:
        """获取题库所有主题"""
        bank = self.get_bank(bank_id)
        return bank.topics if bank else []

    def get_bank_stats(self, bank_id: str) -> dict:
        """获取题库统计"""
        bank = self.get_bank(bank_id)
        if not bank:
            return {}

        by_difficulty = {}
        for q in bank.questions:
            by_difficulty[q.difficulty] = by_difficulty.get(q.difficulty, 0) + 1

        return {
            "total": len(bank.questions),
            "by_difficulty": by_difficulty,
            "topics": len(bank.topics),
            "name": bank.name
        }

    def save(self):
        """保存到文件"""
        data = {}
        for bid, bank in self.banks.items():
            data[bid] = {
                "bank_id": bank.bank_id,
                "name": bank.name,
                "kb_id": bank.kb_id,
                "description": bank.description,
                "topics": bank.topics,
                "total_questions": bank.total_questions,
                "created_at": bank.created_at,
                "questions": [
                    {
                        "question_id": q.question_id,
                        "question_text": q.question_text,
                        "options": q.options,
                        "correct_answer": q.correct_answer,
                        "topic": q.topic,
                        "difficulty": q.difficulty,
                        "source_chunk": q.source_chunk,
                        "zodiac_type": q.zodiac_type,
                        "created_at": q.created_at
                    }
                    for q in bank.questions
                ]
            }

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        """从文件加载"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for bid, bank_data in data.items():
                        questions = [
                            Question(
                                question_id=q["question_id"],
                                question_text=q["question_text"],
                                options=q.get("options", []),
                                correct_answer=q["correct_answer"],
                                topic=q.get("topic", ""),
                                difficulty=q.get("difficulty", 1),
                                source_chunk=q.get("source_chunk", ""),
                                zodiac_type=q.get("zodiac_type", ""),
                                created_at=q.get("created_at", "")
                            )
                            for q in bank_data.get("questions", [])
                        ]
                        bank = QuestionBank(
                            bank_id=bank_data["bank_id"],
                            name=bank_data["name"],
                            kb_id=bank_data["kb_id"],
                            description=bank_data.get("description", ""),
                            topics=bank_data.get("topics", []),
                            total_questions=bank_data.get("total_questions", 0),
                            created_at=bank_data.get("created_at", "")
                        )
                        bank.questions = questions
                        self.banks[bid] = bank
            except Exception as e:
                print(f"加载题库失败: {e}")


class QuestionGenerator:
    """题目生成器 - 使用LLM从文档生成题目"""

    def __init__(self, llm=None):
        self.llm = llm

    def set_llm(self, llm):
        self.llm = llm

    def generate_from_chunk(self, chunk_text: str, topic: str = "", difficulty: int = 1) -> List[Question]:
        """从文本块生成题目"""
        if not self.llm:
            return self._generate_mock_questions(chunk_text, topic, difficulty)

        prompt = f"""基于以下内容生成3道选择题（难度{difficulty}）：
要求：每道题要有4个选项(A/B/C/D)，并标明正确答案。

内容：
{chunk_text}

请用JSON格式返回，格式如下：
[
  {{"question": "题目内容", "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"], "answer": "A", "topic": "主题"}},
  ...
]"""

        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=prompt)]

        try:
            response = self.llm.invoke(messages)
            return self._parse_questions(response.content, topic, difficulty, chunk_text)
        except Exception as e:
            print(f"生成题目失败: {e}")
            return self._generate_mock_questions(chunk_text, topic, difficulty)

    def generate_from_chunks(self, chunks: List[dict], kb_id: str) -> List[Question]:
        """从多个文本块批量生成题目"""
        questions = []
        for i, chunk in enumerate(chunks):
            topic = chunk.get("topic", f"知识点{i+1}")
            text = chunk.get("text", "")
            difficulty = chunk.get("difficulty", 1)

            if text and len(text) > 50:
                chunk_questions = self.generate_from_chunk(text, topic, difficulty)
                questions.extend(chunk_questions)

        return questions

    def _parse_questions(self, content: str, topic: str, difficulty: int, source: str) -> List[Question]:
        """解析LLM返回的题目"""
        import re
        questions = []

        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                for item in data:
                    q = Question(
                        question_id=f"q_{uuid.uuid4().hex[:8]}",
                        question_text=item.get("question", ""),
                        options=item.get("options", []),
                        correct_answer=item.get("answer", "A"),
                        topic=topic or item.get("topic", ""),
                        difficulty=difficulty,
                        source_chunk=source[:100],
                        created_at=datetime.now().isoformat()
                    )
                    questions.append(q)
            except json.JSONDecodeError:
                pass

        return questions

    def _generate_mock_questions(self, chunk_text: str, topic: str, difficulty: int) -> List[Question]:
        """生成模拟题目（无LLM时）"""
        questions = []

        for i in range(3):
            q = Question(
                question_id=f"q_{uuid.uuid4().hex[:8]}",
                question_text=f"关于\"{topic}\"的第{i+1}题：从以下选项中选择正确答案。",
                options=[
                    f"A. 第一个选项（正确答案）",
                    "B. 第二个选项",
                    "C. 第三个选项",
                    "D. 第四个选项"
                ],
                correct_answer="A",
                topic=topic,
                difficulty=difficulty,
                source_chunk=chunk_text[:100],
                created_at=datetime.now().isoformat()
            )
            questions.append(q)

        return questions