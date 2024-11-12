import asyncio
import json
import logging

import redis

from events import events
from services.handlres import otp_handler

logger = logging.getLogger(__name__)

redis_client = redis.Redis(host="localhost", port=6379, db=0)

def main():
    logger.info("Redis pubsub starting")
    pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("otp_request")

    # Run listen() in a separate thread to avoid blocking
    for msg in pubsub.listen():
        handle_otp_request(msg)

def handle_otp_request(msg):
    print(f"handling {msg}")
    data = json.loads(msg["data"])
    print(data['phone_number'])
    event = events.OTPSendEvent(data['phone_number'])
    otp_handler.send_otp_handler(event)

if __name__ == "__main__":
    main()
