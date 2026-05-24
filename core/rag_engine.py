from typing import List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import os
import config
from agents.role_manager import AgentRole, get_role_prompt
from core.learning_methods import (
    LearningMethodType,
    LearningManager,
    FeynmanMethod,
    HeuristicMethod,
    SpacedRepetition,
    LearningScheduler
)
from core.conversation_memory import MemoryManager


class Document(BaseModel):
    page_content: str
    metadata: dict = {}


class RAGEngine:
    def __init__(self, knowledge_base_id: str = "default", agent_role: AgentRole = AgentRole.QIXIA):
        self.knowledge_base_id = knowledge_base_id
        self.agent_role = agent_role
        self.persist_directory = str(config.CHROMA_DIR / knowledge_base_id)
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
        )
        self.vectorstore = None
        self.llm = ChatOpenAI(
            model="qwen-plus",
            openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.7
        )
        self.learning_manager = LearningManager()
        self.current_method = LearningMethodType.SPACED_REPETITION
        self.memory = MemoryManager.get_memory(knowledge_base_id, agent_role.value, use_mempalace=True)
        self._load_vectorstore()

    def _load_vectorstore(self):
        if os.path.exists(self.persist_directory):
            try:
                files = os.listdir(self.persist_directory)
                if any(f.endswith('.sqlite3') for f in files):
                    self.vectorstore = Chroma(
                        persist_directory=self.persist_directory,
                        embedding_function=self.embeddings
                    )
            except Exception:
                self.vectorstore = None

    def switch_role(self, role: AgentRole):
        self.agent_role = role
        self.memory = MemoryManager.get_memory(self.knowledge_base_id, role.value, use_mempalace=True)

    def add_documents(self, texts: List[str], metadata: List[dict] = None, doc_name: str = None):
        docs = []
        for i, text in enumerate(texts):
            meta = metadata[i] if metadata else {}
            meta["index"] = i
            if doc_name:
                meta["doc_name"] = doc_name
            docs.append(Document(page_content=text, metadata=meta))

        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
        else:
            self.vectorstore.add_documents(docs)
        
        self.vectorstore.persist()
        
        self.learning_manager.update_chunk_count(self.knowledge_base_id, len(texts))

    def query(self, question: str, k: int = 3):
        if not self.vectorstore:
            yield "请先上传文档"
            return

        docs = self.vectorstore.similarity_search(question, k=k)
        context = "\n\n".join([d.page_content for d in docs])

        role_prompt = get_role_prompt(self.agent_role)
        
        memory_context = self.memory.get_context_for_query(question)

        prompt = f"""{role_prompt}

基于以下参考内容和语义记忆回答用户的问题。如果你不知道答案，直接说明不知道。

语义记忆（相关历史对话）:
{memory_context}

参考内容:
{context}

问题: {question}

回答:"""

        messages = [HumanMessage(content=prompt)]
        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield chunk.content

    def query_with_history(self, question: str, history: List[dict], k: int = 3):
        if not self.vectorstore:
            yield "请先上传文档"
            return

        docs = self.vectorstore.similarity_search(question, k=k)
        context = "\n\n".join([d.page_content for d in docs])

        role_prompt = get_role_prompt(self.agent_role)

        memory_context = self.memory.get_context_for_query(question)
        
        conversation = ""
        for msg in history:
            role = "用户" if msg["role"] == "user" else "助手"
            conversation += f"{role}: {msg['content']}\n"

        prompt = f"""{role_prompt}

基于以下参考内容、语义记忆和对话历史回答用户的问题。

语义记忆（相关历史对话）:
{memory_context}

参考内容:
{context}

对话历史:
{conversation}

当前问题: {question}

回答:"""

        messages = [HumanMessage(content=prompt)]
        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield chunk.content

    def query_and_save(self, question: str, history: List[dict], assistant_response: str, k: int = 3):
        """带记忆保存的查询"""
        self.memory.add_turn(question, assistant_response)
        return self.query_with_history(question, history, k)

    def get_relevant_docs(self, question: str, k: int = 5) -> List[Document]:
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search(question, k=k)

    def query_with_learning(self, question: str, history: List[dict], k: int = 3):
        """带学习方法感知的查询 - MemPalace分层记忆优化"""
        if not self.vectorstore:
            yield "请先上传文档"
            return

        method_type, method_prompt = LearningScheduler.select_method(
            question,
            self.current_method,
            self.learning_manager.get_progress(self.knowledge_base_id)
        )
        self.current_method = method_type
        
        docs = self.vectorstore.similarity_search(question, k=k)
        context = "\n\n".join([d.page_content for d in docs])
        
        role_prompt = get_role_prompt(self.agent_role)
        
        learning_instruction = self._get_learning_instruction(method_type, docs)
        
        wake_up_context = self.memory.get_l0_l1()

        memory_context = self.memory.get_context_for_query(question)

        # 获取已加载的文档列表
        loaded_docs = self.get_loaded_docs()
        docs_context = f"【已解析文档】{', '.join(loaded_docs)}" if loaded_docs else ""

        conversation = ""
        for msg in history[-5:]:
            role = "用户" if msg["role"] == "user" else "助手"
            conversation += f"{role}: {msg['content'][:100]}\n"

        prompt = f"""{role_prompt}

{learning_instruction}

当前学习方法: {method_type.value}
{method_prompt}

{wake_up_context}

语义记忆（相关历史对话）:
{memory_context}

{docs_context}

参考内容:
{context}

对话历史:
{conversation}

问题: {question}

回答:"""

        messages = [HumanMessage(content=prompt)]
        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield chunk.content

    def _get_learning_instruction(self, method_type: LearningMethodType, docs: List[Document]) -> str:
        """根据学习方法生成指导"""
        instructions = {
            LearningMethodType.SPACED_REPETITION: """【学习引导】这是一个复习相关的问题。
请用问题引导用户回忆，而不是直接给出答案。
当用户回答后，根据回答质量判断是否需要再次复习。
回答格式：提问 → 等待回答 → 判断质量 → 给出复习建议""",
            
            LearningMethodType.FEYNMAN: """【学习引导】这是一个费曼学习任务。
请让用户用自己的话讲解这个知识点。
不要直接给出完整答案，而是引导用户组织自己的语言。
评估标准：是否通俗易懂、是否有例子、是否去除专业术语""",
            
            LearningMethodType.HEURISTIC: """【学习引导】用户有疑惑，使用启发式学习。
使用苏格拉底式提问，引导用户自己思考。
通过追问"为什么"和"如果...会怎样"来深化理解。
不要直接给答案，而是引导用户发现答案""",
            
            LearningMethodType.QUIZ: """【学习引导】这是一个抽查测试。
先给一个具体问题或场景，让用户回答。
根据回答判断掌握程度。
不要解释答案，而是判断对错并给出反馈"""
        }
        return instructions.get(method_type, "")

    def get_learning_progress(self) -> dict:
        """获取学习进度"""
        progress = self.learning_manager.get_progress(self.knowledge_base_id)
        return {
            "total_chunks": progress.total_chunks,
            "mastered": progress.mastered,
            "learning": progress.learning,
            "new": progress.new,
            "mastery_rate": self.learning_manager.get_mastery_rate(self.knowledge_base_id),
            "due_reviews": len(self.learning_manager.get_due_chunks(self.knowledge_base_id))
        }

    def record_review(self, chunk_id: str, quality: int):
        """记录复习结果"""
        self.learning_manager.record_learning(
            self.knowledge_base_id,
            chunk_id,
            LearningMethodType.SPACED_REPETITION,
            quality
        )
        self.learning_manager.save()

    def get_chunk_content(self, chunk_id: str) -> str:
        """获取知识块内容"""
        if not self.vectorstore:
            return ""
        try:
            docs = self.vectorstore.get(where={"index": int(chunk_id.split('_')[-1]) if chunk_id.split('_')[-1].isdigit() else 0})
            if docs and docs.get('documents'):
                return docs['documents'][0]
        except Exception:
            pass
        return ""

    def get_due_chunks(self) -> List[str]:
        """获取待复习的知识块ID列表"""
        return self.learning_manager.get_due_chunks(self.knowledge_base_id)

    def get_loaded_docs(self) -> List[str]:
        """获取当前知识库已加载的文档名列表"""
        # 优先从 metadata 读取（新增文档）
        if self.vectorstore:
            try:
                result = self.vectorstore.get(include=["metadatas"])
                if result and result.get("metadatas"):
                    doc_names = set()
                    for meta in result["metadatas"]:
                        if meta.get("doc_name"):
                            doc_names.add(meta["doc_name"])
                    if doc_names:
                        return list(doc_names)
            except Exception:
                pass

        # 回退：从 knowledge_bases.json 读取
        from core.knowledge_base import KnowledgeBaseManager
        kb_manager = KnowledgeBaseManager()
        kb = kb_manager.get_kb(self.knowledge_base_id)
        if kb and kb.documents:
            return kb.documents

        return []