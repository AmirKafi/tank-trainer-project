import json
import logging
from dataclasses import asdict

import redis.asyncio as redis
import asyncio

from config import get_redis_host_and_port
from events import events

logger = logging.getLogger(__name__)
redis = redis.Redis(**get_redis_host_and_port(), db=0)

def publish(channel, event: events.Event()):
    logging.info("publishing: channel=%s, event=%s", channel, event)
    asyncio.run(redis.publish(channel, json.dumps(asdict(event))))