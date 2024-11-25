import asyncio
from collections import deque


class SlidingWindowRateCalculator:
    def __init__(self, window_size: float):
        self.window_size = window_size
        self.timestamps = deque()
        self.counts = deque()
        self.total_count = 0

    def reset(self):
        self.timestamps.clear()
        self.counts.clear()
        self.total_count = 0

    def add_count(self, count: float):
        current_time = asyncio.get_event_loop().time()
        self.timestamps.append(current_time)
        self.counts.append(count)
        self.total_count += count

        # Remove old entries outside the window
        while self.timestamps and (current_time - self.timestamps[0] > self.window_size):
            self.total_count -= self.counts.popleft()
            self.timestamps.popleft()

    def get_rate(self) -> str:
        if not self.timestamps:
            return '?'
        elapsed_time = self.timestamps[-1] - self.timestamps[0]
        if elapsed_time == 0:
            return '?'
        rate = self.total_count / elapsed_time
        return f'{rate:.2f}'
