# -*- coding: utf-8 -*-
"""
战斗系统与RAG/题库集成
"""

from typing import Optional, Callable, List
from .battle_system import BattleSystem, Question
from .question_bank import QuestionBankManager, QuestionGenerator, QuestionBank
from .data_structures import GameState
from .constants import *


class BattleIntegrator:
    """战斗系统集成器"""

    def __init__(self, state: GameState):
        self.state = state
        self.battle = BattleSystem(state)
        self.qb_manager = QuestionBankManager()
        self.qb_generator = QuestionGenerator()

    def set_llm(self, llm):
        """设置LLM用于题目生成"""
        self.qb_generator.set_llm(llm)

    def connect_to_rag(self, rag_engine):
        """连接到RAG引擎"""
        self.rag_engine = rag_engine

    def start_battle_with_bank(
        self,
        zodiac_type: str,
        zodiac_level: str,
        kb_id: str = None
    ) -> dict:
        """使用题库开始战斗"""
        bank = None

        if kb_id:
            bank = self.qb_manager.get_bank_by_kb(kb_id)

        if not bank and self.state.knowledge_base.kb_id != "python_basic":
            bank = self.qb_manager.get_bank_by_kb(self.state.knowledge_base.kb_id)

        if bank and bank.questions:
            questions = self.qb_manager.get_questions_for_zodiac(
                bank.bank_id,
                zodiac_type,
                count=self._get_question_count(zodiac_level),
                difficulty=self._get_difficulty_num(zodiac_level)
            )

            if questions:
                return self._start_battle_with_questions(zodiac_type, zodiac_level, questions)

        return self.start_battle_with_rag(zodiac_type, zodiac_level)

    def _start_battle_with_questions(
        self,
        zodiac_type: str,
        zodiac_level: str,
        questions: List[Question]
    ) -> dict:
        """使用指定题目开始战斗"""
        battle_questions = []
        for q in questions:
            battle_questions.append(Question(
                question_id=q.question_id,
                content=q.question_text if hasattr(q, 'question_text') else q.content,
                options=q.options,
                correct_answer=q.correct_answer,
                difficulty=q.difficulty,
                topic=q.topic
            ))

        self.battle.questions = battle_questions
        self.battle.current_question_index = 0
        self.battle.correct_count = 0
        self.battle.current_battle = {
            "zodiac_type": zodiac_type,
            "zodiac_level": zodiac_level,
            "started": True,
            "source": "question_bank"
        }

        return self.battle.get_battle_info()

    def start_battle_with_rag(
        self,
        zodiac_type: str,
        zodiac_level: str,
        topic: str = None
    ) -> dict:
        """使用RAG生成题目开始战斗"""
        question_count = self._get_question_count(zodiac_level)
        difficulty = self._get_difficulty_num(zodiac_level)

        if hasattr(self, 'rag_engine') and self.rag_engine:
            questions = self._generate_questions_from_rag(
                topic or zodiac_type,
                question_count,
                difficulty
            )
        else:
            questions = self._generate_mock_questions(question_count, difficulty)

        return self._start_battle_with_questions(zodiac_type, zodiac_level, questions)

    def _generate_questions_from_rag(
        self,
        query: str,
        count: int,
        difficulty: int
    ) -> List[Question]:
        """从RAG生成题目"""
        docs = self.rag_engine.get_relevant_docs(query, k=5)

        if not docs:
            return self._generate_mock_questions(count, difficulty)

        chunks = [
            {"text": d.page_content, "topic": d.metadata.get("topic", query), "difficulty": difficulty}
            for d in docs
        ]

        generated = self.qb_generator.generate_from_chunks(chunks, self.state.knowledge_base.kb_id)

        if len(generated) < count:
            extra = self._generate_mock_questions(count - len(generated), difficulty)
            generated.extend(extra)

        return generated[:count]

    def _generate_mock_questions(self, count: int, difficulty: int) -> List[Question]:
        """生成模拟题目"""
        questions = []
        for i in range(count):
            questions.append(Question(
                question_id=f"mock_{i+1}",
                content=f"这是第{i+1}道模拟题目（难度{difficulty}）。",
                options=["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
                correct_answer="A",
                difficulty=difficulty,
                topic="基础"
            ))
        return questions

    def _get_question_count(self, level: str) -> int:
        counts = {ZODIAC_HUMAN: 3, ZODIAC_EARTH: 5, ZODIAC_HEAVEN: 7}
        return counts.get(level, 3)

    def _get_difficulty_num(self, level: str) -> int:
        difficulties = {ZODIAC_HUMAN: 1, ZODIAC_EARTH: 3, ZODIAC_HEAVEN: 5}
        return difficulties.get(level, 1)

    def submit_answer(self, answer: str) -> dict:
        """提交答案"""
        return self.battle.submit_answer(answer)

    def get_current_question(self) -> Optional[dict]:
        """获取当前题目"""
        question = self.battle.get_current_question()
        if not question:
            return None

        return {
            "question_id": question.question_id,
            "content": question.content,
            "options": question.options,
            "topic": question.topic,
            "difficulty": question.difficulty,
            "remaining": self.battle.get_remaining_questions(),
            "correct_count": self.battle.correct_count
        }

    def get_battle_info(self) -> dict:
        """获取战斗信息"""
        return self.battle.get_battle_info()

    def use_hint(self, cost: int = 5) -> Optional[str]:
        """使用提示"""
        return self.battle.use_hint(cost)

    def surrender(self) -> dict:
        """投降"""
        return self.battle.surrender()


class QuestionBankUI:
    """题库管理界面"""

    def __init__(self):
        self.qb_manager = QuestionBankManager()

    def create_bank(self, name: str, kb_id: str, description: str = "") -> str:
        """创建题库"""
        return self.qb_manager.create_bank(name, kb_id, description)

    def upload_and_generate(
        self,
        bank_id: str,
        file_path: str,
        file_content: bytes,
        generator: QuestionGenerator
    ) -> dict:
        """上传文件并生成题目"""
        import tempfile
        from core.document_parser import DocumentParser

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_path)[1]) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            parser = DocumentParser()
            chunks = parser.parse(tmp_path)

            questions = []
            for i, chunk in enumerate(chunks):
                topic = f"第{i+1}节"
                chunk_questions = generator.generate_from_chunk(
                    chunk.get("content", ""),
                    topic,
                    difficulty=1
                )
                for q in chunk_questions:
                    q.zodiac_type = "rat"
                questions.extend(chunk_questions)

            self.qb_manager.add_questions(bank_id, questions)

            return {
                "success": True,
                "questions_generated": len(questions),
                "chunks_processed": len(chunks)
            }
        finally:
            os.unlink(tmp_path)

    def get_bank_info(self, bank_id: str) -> Optional[dict]:
        """获取题库信息"""
        bank = self.qb_manager.get_bank(bank_id)
        if not bank:
            return None

        return {
            "bank_id": bank.bank_id,
            "name": bank.name,
            "kb_id": bank.kb_id,
            "description": bank.description,
            "total_questions": bank.total_questions,
            "topics": bank.topics,
            "stats": self.qb_manager.get_bank_stats(bank_id)
        }

    def list_banks(self) -> List[dict]:
        """列出所有题库"""
        return [
            {
                "bank_id": bid,
                "name": bank.name,
                "kb_id": bank.kb_id,
                "total_questions": bank.total_questions
            }
            for bid, bank in self.qb_manager.banks.items()
        ]

    def delete_bank(self, bank_id: str) -> bool:
        """删除题库"""
        self.qb_manager.delete_bank(bank_id)
        return True


import os