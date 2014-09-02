# -*- coding: utf-8 -*-
from protorpc import messages, message_types
import endpoints
from protorpc.message_types import VoidMessage

import constants


def event_db_to_rcp(resource_event):
    """ Converts datastore ResourceEvent entity to RPC EventMessage object """
    return EventMessage(
        id=resource_event.key.string_id(),
        title=resource_event.title,
        summary=resource_event.summary,
        organizer=resource_event.organizer,
        start_date_time=resource_event.start_date_time,
        end_date_time=resource_event.end_date_time,
        remaining_time=resource_event.remaining_time,
        actual_attendees=resource_event.actual_attendees,
        yes_attendees=resource_event.yes_attendees,
        no_attendees=resource_event.no_attendees,
        maybe_attendees=resource_event.maybe_attendees,
        no_response_attendees=resource_event.no_response_attendees,
        state=EnumHelpers.EventStateFromString(resource_event.state),
        description=resource_event.description
    )


class EnumHelpers:
    @classmethod
    def EventStateFromString(cls, str):
        return {
            constants.STATE_SCHEDULED: EventMessage.EventStateEnum.SCHEDULED,
            constants.STATE_IN_PROGRESS: EventMessage.EventStateEnum.IN_PROGRESS,
            constants.STATE_FINISHED: EventMessage.EventStateEnum.FINISHED,
            constants.STATE_CANCELLED: EventMessage.EventStateEnum.CANCELLED,
        }.get(str, EventMessage.EventStateEnum.UNDEFINED)


class CheckInOutMessage(messages.Message):
    userEmail = messages.StringField(1, required=True)


class EventMessage(messages.Message):
    class EventStateEnum(messages.Enum):
        SCHEDULED = 1
        IN_PROGRESS = 2
        FINISHED = 3
        CANCELLED = 4
        UNDEFINED = 255

    id = messages.StringField(1, required=True)
    title = messages.StringField(2)
    summary = messages.StringField(3)
    organizer = messages.StringField(4)
    start_date_time = message_types.DateTimeField(5, required=True)
    end_date_time = message_types.DateTimeField(6, required=True)
    remaining_time = messages.IntegerField(7)
    actual_attendees = messages.StringField(8, repeated=True)
    yes_attendees = messages.StringField(9, repeated=True)
    no_attendees = messages.StringField(10, repeated=True)
    maybe_attendees = messages.StringField(11, repeated=True)
    no_response_attendees = messages.StringField(12, repeated=True)
    state = messages.EnumField(EventStateEnum, 13,
                               default=EventStateEnum.SCHEDULED)
    description = messages.StringField(14)


class EventsResponseMessage(messages.Message):
    items = messages.MessageField(EventMessage, 1, repeated=True)


ID_RESOURCE = endpoints.ResourceContainer(
    VoidMessage,
    id=messages.StringField(1,  required=True),
    userEmail=messages.StringField(2, required=False)

)