import dataclasses
import json
import types
from copy import deepcopy
from inspect import get_annotations
from typing import Any, Callable, Self

from pika import channel, spec
from pydantic import BaseModel, ValidationError

from pika_wrapper.schema import Queue

from .exceptions import NotFunctionError, ValidateError
from .interface import RabbitMQProtocol, handlerProtocol


class handler:
    def __init__(self, headers: dict = {}) -> None:
        self.headers = headers

    def __call__(self, fn: Callable) -> Self:
        self._fn = fn
        self._fn_types = get_annotations(fn)
        return self

    @property
    def fn(self) -> Callable:
        if not hasattr(self, "_fn"):
            raise NotFunctionError
        return self._fn

    def callback(self, body: bytes):
        dto = self._fn_types.get("body")
        try:
            if dto is None:
                self.fn(body=body)

            elif issubclass(dto, str):
                self.fn(body=body.decode(encoding="utf-8"))

            elif issubclass(dto, dict):
                self.fn(body=json.loads(body))

            elif dataclasses.is_dataclass(dto):
                self.fn(body=dto(**json.loads(body)))

            elif issubclass(dto, BaseModel):
                self.fn(body=dto.model_validate_json(json_data=body))
        except ValidationError as exp:
            raise ValidateError from exp

        except TypeError as exp:
            raise ValidateError from exp

        except json.JSONDecodeError as exp:
            raise ValidateError from exp


class Consumer:
    queue: Queue
    auto_ack: bool = False
    exclusive: bool = False
    consumer_tag: Any | None = None

    def __init__(self, app: RabbitMQProtocol) -> None:
        self.app = app
        self._handlers: list[handlerProtocol] = self._get_route_handlers()

    def _get_route_handlers(self) -> list[handlerProtocol]:
        route_handlers: list[handlerProtocol] = []
        controller_names = set(dir(Consumer))
        self_handlers = [
            getattr(self, name)
            for name in dir(self)
            if name not in controller_names and isinstance(getattr(self, name), handler)
        ]
        for self_handler in self_handlers:
            route_handler = deepcopy(self_handler)

            route_handler._fn = types.MethodType(route_handler._fn, self)
            route_handler.owner = self
            route_handlers.append(route_handler)

        return route_handlers

    def callback(
        self,
        channel: channel.Channel,
        method: spec.Basic.Deliver,
        properties: spec.BasicProperties,
        body: bytes,
    ):
        headers = properties.headers if properties.headers else dict()
        try:
            for handler in self._handlers:
                if all(
                    value == headers.get(key) for key, value in handler.headers.items()
                ):
                    handler.callback(body=body)
                    break
        except ValidateError as exp:
            print(exp)

        except Exception as exp:
            print(exp)

        if not self.auto_ack:
            channel.basic_ack(method.delivery_tag)
