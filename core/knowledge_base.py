from typing import List, Dict, Optional
from datetime import datetime
import uuid
import json
import os
import config


class KnowledgeBase:
    def __init__(self, id: str, name: str, goal: str):
        self.id = id
        self.name = name
        self.goal = goal
        self.created_at = datetime.now()
        self.documents = []
        self.chunks = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "created_at": self.created_at.isoformat(),
            "documents": self.documents,
            "chunks": self.chunks
        }

    @staticmethod
    def from_dict(data: dict) -> "KnowledgeBase":
        kb = KnowledgeBase(data["id"], data["name"], data["goal"])
        kb.created_at = datetime.fromisoformat(data["created_at"])
        kb.documents = data.get("documents", [])
        kb.chunks = data.get("chunks", 0)
        return kb


class KnowledgeBaseManager:
    def __init__(self):
        self.kbs: Dict[str, KnowledgeBase] = {}
        self.data_file = config.DB_DIR / "knowledge_bases.json"
        self.load()

    def create_kb(self, name: str, goal: str) -> str:
        kb_id = str(uuid.uuid4())
        self.kbs[kb_id] = KnowledgeBase(kb_id, name, goal)
        self.save()
        return kb_id

    def list_kbs(self) -> List[KnowledgeBase]:
        return list(self.kbs.values())

    def get_kb(self, kb_id: str) -> Optional[KnowledgeBase]:
        return self.kbs.get(kb_id)

    def delete_kb(self, kb_id: str):
        if kb_id in self.kbs:
            del self.kbs[kb_id]
            self.save()

    def add_document(self, kb_id: str, filename: str):
        if kb_id in self.kbs:
            if filename not in self.kbs[kb_id].documents:
                self.kbs[kb_id].documents.append(filename)
                self.save()

    def update_chunks(self, kb_id: str, chunks: int):
        if kb_id in self.kbs:
            self.kbs[kb_id].chunks = chunks
            self.save()

    def save(self):
        data = {kb_id: kb.to_dict() for kb_id, kb in self.kbs.items()}
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.kbs = {kb_id: KnowledgeBase.from_dict(kb_data) for kb_id, kb_data in data.items()}