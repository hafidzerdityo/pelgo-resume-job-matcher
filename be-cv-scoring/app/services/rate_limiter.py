import time
from fastapi import HTTPException, Request
from redis import Redis
from app.config import settings
from app.logger import get_logger

logger = get_logger("rate_limiter")

class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    async def __call__(self, request: Request):
        # In a real app, you might use API keys or User IDs. 
        # Here we use IP address for simplicity.
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{request.url.path}:{client_ip}"
        
        try:
            current = self.redis.get(key)
            if current is not None and int(current) >= self.times:
                logger.warning("rate_limit_exceeded", client_ip=client_ip, path=request.url.path)
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "too_many_requests",
                        "message": f"Rate limit exceeded. Maximum {self.times} requests per {self.seconds} seconds."
                    }
                )
            
            # Increment the count and set expiry if it's the first request in the window
            pipeline = self.redis.pipeline()
            pipeline.incr(key)
            pipeline.expire(key, self.seconds)
            pipeline.execute()
            
        except HTTPException:
            raise
        except Exception as e:
            # If redis is down, we still want the app to work in dev, 
            # but in prod you might want to fail closed or open depending on security needs.
            logger.error("rate_limiter_redis_error", error=str(e))
            return 
