# -*- coding: utf-8 -*-
from protorpc import messages, message_types
import endpoints
from protorpc.message_types import VoidMessage


class CheckInOutMessage(messages.Message):
    userEmail = messages.StringField(1, required=True)


ID_RESOURCE = endpoints.ResourceContainer(
    VoidMessage,
    id=messages.IntegerField(1, variant=messages.Variant.INT32))