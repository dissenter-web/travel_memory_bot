import random

from app.models import Memory
from app.repository import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository

    def choose_next(self) -> Memory:
        memories = self.repository.load_memories()
        if not memories:
            raise RuntimeError("No valid photos found")

        sent_keys = self.repository.get_sent_keys()
        unsent_memories = [memory for memory in memories if memory.key not in sent_keys]

        if not unsent_memories:
            raise RuntimeError("All memories have already been sent")

        return random.choice(unsent_memories)

    def choose_random(self) -> Memory:
        memories = self.repository.load_memories()
        if not memories:
            raise RuntimeError("No valid photos found")

        return random.choice(memories)

    def confirm_sent(self, memory: Memory) -> None:
        self.repository.mark_as_sent(memory.key)
