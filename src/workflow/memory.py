from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path
from pydantic import BaseModel
from ..agents.models import FinalOutput

class ConversationMemory(BaseModel):
    """Memory entry for a conversation turn"""
    session_id: str
    timestamp: datetime
    user_input: str
    agent_outputs: Dict[str, Any]
    synthesis_result: Optional[FinalOutput] = None
    refinement_cycles: int = 0
    success: bool = True
    error_details: Optional[str] = None

class MemoryManager:
    """Manages persistent conversation memory"""
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.session_memories: Dict[str, List[ConversationMemory]] = {}
    
    def save_conversation(self, memory: ConversationMemory):
        """Save a conversation turn to memory"""
        session_id = memory.session_id
        
        # Add to session memory
        if session_id not in self.session_memories:
            self.session_memories[session_id] = []
        self.session_memories[session_id].append(memory)
        
        # Persist to file
        session_file = self.memory_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(
                [mem.model_dump() for mem in self.session_memories[session_id]],
                f,
                indent=2,
                default=str
            )
    
    def load_session(self, session_id: str) -> List[ConversationMemory]:
        """Load conversation history for a session"""
        session_file = self.memory_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return []
        
        with open(session_file, 'r') as f:
            data = json.load(f)
            return [ConversationMemory(**item) for item in data]
    
    def get_recent_context(self, session_id: str, limit: int = 5) -> List[ConversationMemory]:
        """Get recent conversation context"""
        if session_id not in self.session_memories:
            self.session_memories[session_id] = self.load_session(session_id)
        
        return self.session_memories[session_id][-limit:]
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.session_memories:
            del self.session_memories[session_id]
        
        session_file = self.memory_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        memories = self.get_recent_context(session_id, limit=100)
        
        if not memories:
            return {"total_turns": 0, "success_rate": 0.0}
        
        total_turns = len(memories)
        successful_turns = sum(1 for mem in memories if mem.success)
        avg_refinement_cycles = sum(mem.refinement_cycles for mem in memories) / total_turns
        
        return {
            "total_turns": total_turns,
            "success_rate": successful_turns / total_turns,
            "avg_refinement_cycles": avg_refinement_cycles,
            "last_activity": memories[-1].timestamp if memories else None
        }
    
    def export_session(self, session_id: str, format: str = "json") -> str:
        """Export session data in specified format"""
        memories = self.get_recent_context(session_id, limit=1000)
        
        if format == "json":
            return json.dumps(
                [mem.model_dump() for mem in memories],
                indent=2,
                default=str
            )
        elif format == "markdown":
            lines = [f"# Session {session_id} Export\n"]
            for mem in memories:
                lines.append(f"## {mem.timestamp}")
                lines.append(f"**User:** {mem.user_input}")
                lines.append(f"**Success:** {mem.success}")
                if mem.synthesis_result:
                    lines.append(f"**Result:** {mem.synthesis_result.solution}")
                lines.append("---\n")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Global memory manager instance
memory_manager = MemoryManager()
