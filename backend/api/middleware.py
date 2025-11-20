from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int, window_seconds: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self.hit_map: defaultdict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        identifier = request.client.host if request.client else "anonymous"
        now = time.time()
        window_start = now - self.window
        queue = self.hit_map[identifier]

        while queue and queue[0] < window_start:
            queue.popleft()

        if len(queue) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
            )

        queue.append(now)
        response: Response = await call_next(request)
        return response
