# -*- coding: utf-8 -*-
from protorpc import messages

class String(messages.Message):
    value = messages.StringField(1)


class StringList(messages.Message):
    items = messages.MessageField(String, 1, repeated=True)


class CheckInOutMessage(messages.Message):

    user_email = messages.StringField(1, required=True)

    class CheckInOutChoices(messages.Enum):
        IN = 1
        OUT = 2
    type = messages.EnumField(CheckInOutChoices, 2, required=True,
                              default=CheckInOutChoices.IN)
    event_id = messages.IntegerField(3, required=True)
