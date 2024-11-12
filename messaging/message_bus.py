import logging
from typing import List, Union, Dict, Type, Callable

from events import commands,events
from services.UnitOfWork import AbstractUnitOfWork, UnitOfWork
from services.handlres import book_handler, member_handler
from services.handlres import reservation_handler
from services.handlres.otp_handler import publish_otp_event, send_otp_handler

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]



EVENT_HANDLERS = {
    events.OTPSendEvent:[publish_otp_event]
}# type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.CreateBookCommand :book_handler.add_book_handler,
    commands.UpdateBookCommand :book_handler.update_book_handler,
    commands.AddToMemberBalanceCommand:member_handler.add_to_balance_handler,
    commands.ReserveBookCommand:reservation_handler.reserve_handler,
    commands.SetMemberVIPCommand:member_handler.set_to_vip_handler,
    commands.CreateMemberCommand:member_handler.add_member_handler
}# type: Dict[Type[commands.Command], Callable]

class MessageBus:
    def __init__(
        self,
        uow: UnitOfWork,
        event_handlers: Dict[Type[events.Event], List[Callable]],
        command_handlers: Dict[Type[commands.Command], Callable],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message):
        self.queue = [message]
        print(self.queue)
        while self.queue:
            message = self.queue.pop(0)
            logger.debug(type(message))
            if isinstance(message, events.Event):
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")

    def handle_event(self, event: events.Event):
        for handler in self.event_handlers[type(event)]:
            try:
                logger.debug("handling event %s with handler %s", event, handler)
                handler(event)
                self.queue.extend(self.uow.collect_new_events())
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue

    def handle_command(self, command: commands.Command):
        logger.debug("handling command %s", command)
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise