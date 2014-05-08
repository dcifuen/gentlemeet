# -*- coding: utf-8 -*-
from protorpc import messages, message_types
import endpoints
from protorpc.message_types import VoidMessage


class CheckInOutMessage(messages.Message):
    userEmail = messages.StringField(1, required=True)


class EventMessage(messages.Message):
    id = messages.IntegerField(1, variant=messages.Variant.INT32, required=True)
    title = messages.StringField(2)
    summary = messages.StringField(3)
    organizer = messages.StringField(4)
    start_date_time = message_types.DateTimeField(5, required=True)
    end_date_time = message_types.DateTimeField(6, required=True)
    attendees = messages.StringField(7, repeated=True)

    class EventStateEnum(messages.Enum):
        SCHEDULED = 1
        IN_PROGRESS = 2
        FINISHED = 3
        CANCELLED = 4
    state = messages.EnumField(EventStateEnum, 8,
                               default=EventStateEnum.SCHEDULED)


class EventsResponseMessage(messages.Message):
    items = messages.MessageField(EventMessage, 1, repeated=True)

ID_RESOURCE = endpoints.ResourceContainer(
    VoidMessage,
    id=messages.IntegerField(1, variant=messages.Variant.INT32, required=True))