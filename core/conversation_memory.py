import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass, field
import config
import json
from pathlib import Path


@dataclass
class KeyMemory:
    memory_type: str
    content: str
    timestamp: str
    relevance: float = 0.0


@dataclass
class L0Identity:
    content: str
    last_updated: str = ""


@dataclass
class L1Essential:
    wing: str
    room: str
    facts: List[str] = field(default_factory=list)
    last_updated: str = ""


class WingRoomClassifier:
    """Wing和Room分类器 - 基于关键词的简单分类"""
    
    WINGS = {
        "技术": ["代码", "编程", "python", "bug", "实现", "开发", "技术", "api", "函数", "变量"],
        "学习": ["学习", "知识", "理解", "概念", "教程", "复习", "费曼", "艾宾浩斯"],
        "项目": ["项目", "任务", "目标", "计划", "进度", "完成"],
        "个人": ["我", "我的", "喜欢", "习惯", "偏好", "决定", "选择"]
    }
    
    ROOMS = {
        "代码开发": ["代码", "编程", "python", "实现", "函数", "变量", "bug"],
        "知识理解": ["概念", "理解", "原理", "为什么", "解释"],
        "任务规划": ["计划", "目标", "任务", "完成", "进度"],
        "经验总结": ["经验", "总结", "教训", "心得", "成功", "失败"]
    }
    
    @classmethod
    def classify(cls, text: str) -> tuple[str, str]:
        text_lower = text.lower()
        
        wing = "个人"
        for w, keywords in cls.WINGS.items():
            if any(kw in text_lower for kw in keywords):
                wing = w
                break
        
        room = "经验总结"
        for r, keywords in cls.ROOMS.items():
            if any(kw in text_lower for kw in keywords):
                room = r
                break
                
        return wing, room


class MemoryExtractor:
    """关键记忆提取器"""

    @staticmethod
    def extract(text: str) -> List[KeyMemory]:
        memories = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:
                continue
            
            mem_type = MemoryExtractor._classify(line)
            if mem_type:
                memories.append(KeyMemory(
                    memory_type=mem_type,
                    content=line[:200],
                    timestamp=datetime.now().isoformat(),
                    relevance=1.0
                ))
        
        return memories
    
    @staticmethod
    def _classify(text: str) -> Optional[str]:
        text_lower = text.lower()
        
        decision_markers = ["决定", "选用", "采用", "因为", "最终", "选择", "用了"]
        pref_markers = ["喜欢", "习惯", "总是", "从来", "偏好", " prefer"]
        milestone_markers = ["成功", "解决", "完成", "突破", "works", "fixed"]
        problem_markers = ["问题", "错误", "bug", "失败", "error"]
        
        if any(m in text_lower for m in decision_markers):
            return "DECISION"
        if any(m in text_lower for m in pref_markers):
            return "PREFERENCE"
        if any(m in text_lower for m in milestone_markers):
            return "MILESTONE"
        if any(m in text_lower for m in problem_markers):
            return "PROBLEM"
        
        return None


class MemPalaceMemory:
    """
    MemPalace风格的分层记忆系统
    
    L0: Identity - 固定身份信息 (~50-100 tokens)
    L1: Essential - 核心事实摘要 (~120 tokens)  
    L2: Room - 按需加载的主题记忆 (~200-500/topic)
    L3: Deep Search - 完整语义搜索 (按需)
    
    目标: 最小化wake-up token消耗
    """
    
    L0_FILE = "l0_identity.json"
    L1_FILE = "l1_essential.json"
    
    def __init__(self, kb_id: str, agent_role: str):
        self.kb_id = kb_id
        self.agent_role = agent_role
        self.collection_name = f"key_mem_{kb_id}_{agent_role}"
        self.persist_dir = str(config.DB_DIR / "memories" / self.collection_name)
        
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.client = None
        self.collection = None
        self._init_chroma()
        
        self.extractor = MemoryExtractor()
        self.classifier = WingRoomClassifier()
        
        self._l0: Optional[L0Identity] = self._load_l0()
        self._l1: Optional[L1Essential] = self._load_l1()
    
    def _init_chroma(self):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            
            existing = self.client.list_collections()
            if self.collection_name in [c.name for c in existing]:
                self.collection = self.client.get_collection(self.collection_name)
            else:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": f"MemPalace memory for {self.kb_id}/{self.agent_role}"}
                )
        except Exception as e:
            print(f"Warning: Memory init failed: {e}")
    
    def _load_l0(self) -> Optional[L0Identity]:
        path = Path(self.persist_dir) / self.L0_FILE
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return L0Identity(
                        content=data.get("content", ""),
                        last_updated=data.get("last_updated", "")
                    )
            except:
                pass
        return None
    
    def _save_l0(self, l0: L0Identity):
        path = Path(self.persist_dir) / self.L0_FILE
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "content": l0.content,
                "last_updated": l0.last_updated
            }, f, ensure_ascii=False, indent=2)
    
    def _load_l1(self) -> Optional[L1Essential]:
        path = Path(self.persist_dir) / self.L1_FILE
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return L1Essential(
                        wing=data.get("wing", "个人"),
                        room=data.get("room", "经验总结"),
                        facts=data.get("facts", []),
                        last_updated=data.get("last_updated", "")
                    )
            except:
                pass
        return None
    
    def _save_l1(self, l1: L1Essential):
        path = Path(self.persist_dir) / self.L1_FILE
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "wing": l1.wing,
                "room": l1.room,
                "facts": l1.facts,
                "last_updated": l1.last_updated
            }, f, ensure_ascii=False, indent=2)
    
    def set_identity(self, identity_text: str):
        """设置L0身份信息"""
        self._l0 = L0Identity(
            content=identity_text[:500],
            last_updated=datetime.now().isoformat()
        )
        self._save_l0(self._l0)
    
    def update_essential(self, wing: str, room: str, new_fact: str):
        """更新L1核心事实"""
        if self._l1 is None or self._l1.wing != wing or self._l1.room != room:
            self._l1 = L1Essential(
                wing=wing,
                room=room,
                facts=[new_fact],
                last_updated=datetime.now().isoformat()
            )
        else:
            if new_fact not in self._l1.facts:
                self._l1.facts.append(new_fact)
                self._l1.facts = self._l1.facts[-5:]
                self._l1.last_updated = datetime.now().isoformat()
        self._save_l1(self._l1)
    
    def get_l0_l1(self) -> str:
        """获取L0+L1组合 - 每次会话必加载 (~170 tokens)"""
        parts = []
        
        if self._l0 and self._l0.content:
            parts.append(f"[身份] {self._l0.content}")
        
        if self._l1 and self._l1.facts:
            facts_text = "; ".join(self._l1.facts[-3:])
            parts.append(f"[核心记忆] {facts_text}")
        
        return "\n".join(parts) if parts else ""
    
    def add_turn(self, user_msg: str, assistant_msg: str):
        if not self.collection:
            return
        
        combined = f"User: {user_msg}\nAssistant: {assistant_msg}"
        key_memories = self.extractor.extract(combined)
        
        wing, room = self.classifier.classify(combined)
        
        if key_memories:
            for mem in key_memories[:3]:
                try:
                    self.collection.add(
                        ids=[str(uuid.uuid4())],
                        documents=[mem.content],
                        metadatas=[{
                            "type": mem.memory_type,
                            "timestamp": mem.timestamp,
                            "kb_id": self.kb_id,
                            "agent_role": self.agent_role,
                            "wing": wing,
                            "room": room
                        }]
                    )
                except Exception as e:
                    print(f"Warning: {e}")
            
            self.update_essential(wing, room, key_memories[0].content[:100])
        else:
            default_mem = KeyMemory(
                memory_type="EXCHANGE",
                content=assistant_msg[:200],
                timestamp=datetime.now().isoformat(),
                relevance=0.5
            )
            try:
                self.collection.add(
                    ids=[str(uuid.uuid4())],
                    documents=[default_mem.content],
                    metadatas=[{
                        "type": default_mem.memory_type,
                        "timestamp": default_mem.timestamp,
                        "kb_id": self.kb_id,
                        "agent_role": self.agent_role,
                        "wing": wing,
                        "room": room
                    }]
                )
            except Exception as e:
                print(f"Warning: {e}")
    
    def get_context_for_query(self, query: str, n_results: int = 1) -> str:
        """获取L2/L3记忆 - 按需加载"""
        if not self.collection:
            return ""
        
        wing, room = self.classifier.classify(query)
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"wing": wing},
                include=["documents", "metadatas", "distances"]
            )
            
            docs = results.get("documents", [[]])[0]
            if not docs:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["documents", "metadatas"]
                )
                docs = results.get("documents", [[]])[0]
            
            if not docs:
                return ""
            
            return docs[0][:300]
            
        except Exception as e:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["documents"]
                )
                docs = results.get("documents", [[]])[0]
                return docs[0][:300] if docs else ""
            except Exception as e:
                print(f"Warning: {e}")
                return ""
    
    def get_context_with_filter(self, query: str, wing: str = None, room: str = None, n_results: int = 3) -> str:
        """按Wing/Room过滤获取记忆 (L2)"""
        if not self.collection:
            return ""
        
        try:
            where_clause = {}
            if wing:
                where_clause["wing"] = wing
            if room:
                where_clause["room"] = room
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas"]
            )
            
            docs = results.get("documents", [[]])[0]
            if not docs:
                return ""
            
            return "\n".join([d[:200] for d in docs])
            
        except Exception as e:
            print(f"Warning: {e}")
            return ""
    
    def count(self) -> int:
        if not self.collection:
            return 0
        try:
            return self.collection.count()
        except:
            return 0
    
    def clear(self):
        if self.collection:
            try:
                self.client.delete_collection(self.collection_name)
            except:
                pass


class ConversationMemory:
    """
    轻量级对话记忆 - MemPalace风格
    只存储关键记忆，不存储完整对话
    """
    
    def __init__(self, kb_id: str, agent_role: str):
        self.kb_id = kb_id
        self.agent_role = agent_role
        self.collection_name = f"key_mem_{kb_id}_{agent_role}"
        self.persist_dir = str(config.DB_DIR / "memories" / self.collection_name)
        
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.client = None
        self.collection = None
        self._init_chroma()
        
        self.extractor = MemoryExtractor()
    
    def _init_chroma(self):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            
            existing = self.client.list_collections()
            if self.collection_name in [c.name for c in existing]:
                self.collection = self.client.get_collection(self.collection_name)
            else:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": f"Key memory for {self.kb_id}/{self.agent_role}"}
                )
        except Exception as e:
            print(f"Warning: Memory init failed: {e}")
    
    def add_turn(self, user_msg: str, assistant_msg: str):
        if not self.collection:
            return
        
        combined = f"User: {user_msg}\nAssistant: {assistant_msg}"
        key_memories = self.extractor.extract(combined)
        
        if not key_memories:
            key_memories = [KeyMemory(
                memory_type="EXCHANGE",
                content=assistant_msg[:200],
                timestamp=datetime.now().isoformat(),
                relevance=0.5
            )]
        
        for mem in key_memories[:3]:
            try:
                self.collection.add(
                    ids=[str(uuid.uuid4())],
                    documents=[mem.content],
                    metadatas=[{
                        "type": mem.memory_type,
                        "timestamp": mem.timestamp,
                        "kb_id": self.kb_id,
                        "agent_role": self.agent_role
                    }]
                )
            except Exception as e:
                print(f"Warning: {e}")
    
    def get_context_for_query(self, query: str) -> str:
        if not self.collection:
            return ""
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=1,
                include=["documents", "distances"]
            )
            
            docs = results.get("documents", [[]])[0]
            if not docs:
                return ""
            
            return docs[0][:300]
            
        except Exception as e:
            print(f"Warning: {e}")
            return ""
    
    def count(self) -> int:
        if not self.collection:
            return 0
        try:
            return self.collection.count()
        except:
            return 0
    
    def clear(self):
        if self.collection:
            try:
                self.client.delete_collection(self.collection_name)
            except:
                pass


class MemoryManager:
    _instances = {}
    
    @classmethod
    def get_memory(cls, kb_id: str, agent_role: str, use_mempalace: bool = True):
        key = f"{kb_id}_{agent_role}"
        if key not in cls._instances:
            if use_mempalace:
                cls._instances[key] = MemPalaceMemory(kb_id, agent_role)
            else:
                cls._instances[key] = ConversationMemory(kb_id, agent_role)
        return cls._instances[key]
    
    @classmethod
    def clear_all(cls):
        cls._instances.clear()