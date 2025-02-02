from abc import ABC
from typing import Sequence

import blxr_rlp as rlp
from blxr_rlp.sedes import List

from astracommon.messages.abstract_message import AbstractMessage


class AbstractEthMessage(AbstractMessage, ABC, Sequence):
    msg_type = None
    fields = []

    # Cache of serializer instance per class
    _serializer = None

    def __init__(self, msg_bytes, *args, **kwargs):
        self._msg_bytes = None
        self._memory_view = None

        if msg_bytes is None:
            self._set_fields_from_args(args, kwargs)
            self._is_deserialized = True
        else:
            self._set_raw_bytes(msg_bytes)
            self._is_deserialized = False

    def __iter__(self):
        for field, _ in self.fields:
            yield self.get_field_value(field)

    def __len__(self):
        return len(self.fields)

    def __getitem__(self, item):
        return self.get_field_value(self.fields[item][0])

    @classmethod
    def initialize_class(cls, cls_type, buf, unpacked_args):
        """
        Initialize message class with arguments. Returns cls_type instance.
        """

        return cls_type(buf)

    @classmethod
    def serialize(cls, obj):
        """
        Special handling for direct RLP encoding this class as an attribute of another message class.

        Undoes the 1 length field list serializer simplification (len(serializers) == 1).
        """
        serializer = cls.get_serializer()
        if not isinstance(serializer, List):
            serializer = List([serializer])
        return serializer.serialize(obj)

    @classmethod
    def deserialize(cls, serial):
        """
        Special handling for direct RLP encoding this class as an attribute of another message class.

        Undoes the 1 length field list serializer simplification (len(serializers) == 1).
        """
        serializer = cls.get_serializer()
        if not isinstance(serializer, List):
            serializer = List([serializer])
        return serializer.deserialize(serial)

    def serialize_message(self):
        encoded_payload = self._serialize_rlp_payload()
        self._set_raw_bytes(encoded_payload)

    def deserialize_message(self):
        assert self._msg_bytes is not None
        self._deserialize_rlp_payload(self._msg_bytes)
        self._is_deserialized = True

    def rawbytes(self) -> memoryview:
        if self._msg_bytes is None:
            self.serialize_message()

        assert self._msg_bytes is not None

        return self._msg_bytes

    def get_field_value(self, field_name):
        if not self._is_deserialized:
            self.deserialize_message()

        return getattr(self, field_name, None)

    def _serialize_rlp_payload(self):
        field_values = [getattr(self, field) for field, _ in self.fields]

        # get single value if message has just one field
        if len(field_values) == 1:
            field_values = field_values[0]

        payload = self.get_serializer().serialize(field_values)
        encoded_payload = rlp.encode(payload)

        return encoded_payload

    def _deserialize_rlp_payload(self, encoded_payload):
        if isinstance(encoded_payload, memoryview):
            encoded_payload = encoded_payload.tobytes()
        payload = rlp.decode(encoded_payload, strict=False)

        serializers = self.get_serializer()

        if serializers:
            values = serializers.deserialize(payload)

            # if message has just one field that serializers.deserialize(payload) returns a single value
            if len(self.fields) == 1:
                setattr(self, self.fields[0][0], values)
            else:
                for (field, _), value in zip(self.fields, values):
                    setattr(self, field, value)

    @classmethod
    def get_serializer(cls):
        if cls._serializer is not None:
            return cls._serializer

        serializers = [serializer for _, serializer in cls.fields]
        serializer = serializers[0] if len(serializers) == 1 else List(serializers)

        cls._serializer = serializer

        return serializer

    def _set_raw_bytes(self, msg_bytes):
        if msg_bytes is None:
            raise ValueError("Bytes expected")

        self._msg_bytes = msg_bytes
        self._memory_view = memoryview(msg_bytes)

    def _set_fields_from_args(self, args, kwargs):
        # check keyword arguments are known
        field_set = set(field for field, _ in self.fields)

        # set positional arguments
        for (field, _), arg in zip(self.fields, args):
            setattr(self, field, arg)
            field_set.remove(field)

        # set keyword arguments, if not already set
        for (field, value) in kwargs.items():
            if field in field_set:
                setattr(self, field, value)
                field_set.remove(field)

        if len(field_set) != 0:
            raise TypeError("Not all fields initialized")

    def __eq__(self, other):
        """
        Expensive equality comparison. Use only for tests.
        """
        if not isinstance(other, AbstractEthMessage):
            return False
        else:
            return self.rawbytes() == other.rawbytes()
