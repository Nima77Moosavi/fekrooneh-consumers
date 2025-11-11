import asyncio
import json
import os
import redis.asyncio as redis
from redis.exceptions import ResponseError   # ✅ import exceptions from top-level

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
STREAM = "leaderboard_events"
GROUP = "leaderboard-consumers"
CONSUMER_NAME = "consumer-1"


async def main():
    r = redis.from_url(REDIS_URL, decode_responses=True)

    # Create consumer group if not exists
    try:
        await r.xgroup_create(STREAM, GROUP, id="$", mkstream=True)
    except ResponseError as e:   # ✅ use imported ResponseError
        if "BUSYGROUP" not in str(e):
            raise

    print("Consumer started. Listening for events...")

    while True:
        # Block until new events arrive (5s timeout)
        resp = await r.xreadgroup(GROUP, CONSUMER_NAME, {STREAM: ">"}, count=1, block=5000)
        if not resp:
            continue

        for _, messages in resp:
            for msg_id, fields in messages:
                event = fields  # already dict-like
                print("Got event:", event)

                # Example: update leaderboard sorted set
                if event["event"] in ("user_created", "checkin"):
                    user_key = f"user:{event['user_id']}"
                    xp = int(event["xp"])
                    await r.zincrby("leaderboard:global", xp, user_key)

                # Acknowledge message
                await r.xack(STREAM, GROUP, msg_id)

if __name__ == "__main__":
    asyncio.run(main())
