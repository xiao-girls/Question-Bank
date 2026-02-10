import os
import json
import shutil
from typing import List, Dict, Optional
from pathlib import Path
from pydantic import BaseModel


class KnowledgeBase(BaseModel):
    id: str
    name: str
    description: str
    files: List[str]
    created_at: str


class KnowledgeManager:
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_file = self.base_dir / "knowledge_bases.json"
        self._load_knowledge_bases()

    def _load_knowledge_bases(self):
        if self.knowledge_file.exists():
            with open(self.knowledge_file, "r", encoding="utf-8") as f:
                self.knowledge_bases = json.load(f)
        else:
            self.knowledge_bases = {}

    def _save_knowledge_bases(self):
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_bases, f, ensure_ascii=False, indent=2)

    def create_knowledge_base(self, name: str, description: str) -> str:
        kb_id = f"kb_{len(self.knowledge_bases) + 1}"
        kb_dir = self.base_dir / kb_id
        kb_dir.mkdir(exist_ok=True)

        kb = KnowledgeBase(
            id=kb_id,
            name=name,
            description=description,
            files=[],
            created_at=""
        )
        self.knowledge_bases[kb_id] = kb.model_dump()
        self._save_knowledge_bases()
        return kb_id

    def upload_file(self, kb_id: str, filename: str, content: str) -> bool:
        if kb_id not in self.knowledge_bases:
            return False

        kb_dir = self.base_dir / kb_id
        file_path = kb_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        if filename not in self.knowledge_bases[kb_id]["files"]:
            self.knowledge_bases[kb_id]["files"].append(filename)
            self._save_knowledge_bases()

        return True

    def get_knowledge_base(self, kb_id: str) -> Optional[Dict]:
        return self.knowledge_bases.get(kb_id)

    def list_knowledge_bases(self) -> List[Dict]:
        return list(self.knowledge_bases.values())

    def get_knowledge_content(self, kb_id: str) -> str:
        if kb_id not in self.knowledge_bases:
            return ""

        kb_dir = self.base_dir / kb_id
        content = ""

        for filename in self.knowledge_bases[kb_id]["files"]:
            file_path = kb_dir / filename
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content += f"\n\n=== {filename} ===\n"
                    content += f.read()

        return content

    def delete_knowledge_base(self, kb_id: str) -> bool:
        if kb_id not in self.knowledge_bases:
            return False

        kb_dir = self.base_dir / kb_id
        if kb_dir.exists():
            shutil.rmtree(kb_dir)

        del self.knowledge_bases[kb_id]
        self._save_knowledge_bases()
        return True

    def update_knowledge_base(self, kb_id: str, name: str, description: str) -> bool:
        if kb_id not in self.knowledge_bases:
            return False

        self.knowledge_bases[kb_id]["name"] = name
        self.knowledge_bases[kb_id]["description"] = description
        self._save_knowledge_bases()
        return True

    def delete_file(self, kb_id: str, filename: str) -> bool:
        if kb_id not in self.knowledge_bases:
            return False

        if filename not in self.knowledge_bases[kb_id]["files"]:
            return False

        # 删除文件
        kb_dir = self.base_dir / kb_id
        file_path = kb_dir / filename
        if file_path.exists():
            file_path.unlink()

        # 从知识库中移除文件记录
        self.knowledge_bases[kb_id]["files"].remove(filename)
        self._save_knowledge_bases()
        return True
