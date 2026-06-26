import asyncio
import threading
from collections import defaultdict
from typing import Optional, Callable, Awaitable

from ..utils.logger import bot_logger


class QueueService:
    def __init__(self):
        self._queues = defaultdict(list)
        self._locks = defaultdict(asyncio.Lock)
        self._guild_locks = defaultdict(threading.RLock)
        self._processing = defaultdict(bool)
        self._max_concurrent = defaultdict(int)
        self._active_codes = defaultdict(set)
        self._logger = bot_logger

    async def enqueue(self, guild_id: str, code_hash: str, priority: int = 0):
        async with self._locks[guild_id]:
            if code_hash in self._active_codes[guild_id]:
                return False
            
            self._queues[guild_id].append({"code_hash": code_hash, "priority": priority})
            self._queues[guild_id].sort(key=lambda x: x["priority"])
            return True

    async def dequeue(self, guild_id: str) -> Optional[str]:
        async with self._locks[guild_id]:
            if not self._queues[guild_id]:
                return None
            
            if self._processing[guild_id]:
                return None
            
            item = self._queues[guild_id].pop(0)
            code_hash = item["code_hash"]
            self._active_codes[guild_id].add(code_hash)
            return code_hash

    async def mark_processing(self, guild_id: str, code_hash: str):
        async with self._locks[guild_id]:
            self._processing[guild_id] = True
            self._active_codes[guild_id].add(code_hash)

    async def mark_complete(self, guild_id: str, code_hash: str):
        async with self._locks[guild_id]:
            self._processing[guild_id] = False
            self._active_codes[guild_id].discard(code_hash)

    def is_processing(self, guild_id: str, code_hash: str) -> bool:
        return code_hash in self._active_codes.get(guild_id, set())

    def get_queue_size(self, guild_id: str) -> int:
        return len(self._queues.get(guild_id, []))

    def get_total_queue_size(self) -> int:
        return sum(len(q) for q in self._queues.values())

    async def clear_guild(self, guild_id: str):
        async with self._locks[guild_id]:
            self._queues[guild_id] = []
            self._processing[guild_id] = False
            self._active_codes[guild_id].clear()

    def get_all_pending(self, guild_id: str) -> list:
        return [item["code_hash"] for item in self._queues.get(guild_id, [])]


queue_service = QueueService()
