import inspect
import logging
from typing import Callable

from adapters import redis_publisher, table_mapping
from messaging import message_bus, rabbitMQ_broker
from messaging.rabbitMQ_broker import RabbitMQBroker
from services.UnitOfWork import UnitOfWork, AbstractUnitOfWork

logger = logging.getLogger(__name__)

def bootstrap(
    start_orm: bool = True,
    uow: AbstractUnitOfWork = UnitOfWork(),
    publish: Callable = RabbitMQBroker().publish_message,
) -> message_bus.MessageBus:

    if start_orm:
        table_mapping.start_mappers()

    dependencies = {"uow": uow, "publish": publish}
    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies)
            for handler in event_handlers
        ]
        for event_type, event_handlers in message_bus.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in message_bus.COMMAND_HANDLERS.items()
    }

    return message_bus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}
    return lambda message: handler(message, **deps)
