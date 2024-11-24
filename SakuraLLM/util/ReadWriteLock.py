import asyncio

class ReadWriteLock:
    def __init__(self):
        self._readers = 0
        self._writer = False
        self._lock = asyncio.Lock()
        self._read_ready = asyncio.Condition(self._lock)

    async def acquire_read(self):
        async with self._lock:
            while self._writer:
                await self._read_ready.wait()
            self._readers += 1

    async def release_read(self):
        async with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    async def acquire_write(self):
        async with self._lock:
            while self._writer or self._readers > 0:
                await self._read_ready.wait()
            self._writer = True

    async def release_write(self):
        async with self._lock:
            self._writer = False
            self._read_ready.notify_all()
