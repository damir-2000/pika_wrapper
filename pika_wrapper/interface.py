from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable, Generator, List, Optional, Protocol, Self, Type

# from pika import channel, connection, spec

from kombu import Queue, Connection, Message
from kombu.transport import virtual

class handlerProtocol(Protocol):
    headers: dict

    def __init__(self, headers: dict = {}) -> None:
        pass

    def __call__(self, fn: Callable) -> Self:
        pass

    @property
    def fn(self) -> Callable:
        pass

    def callback(self, body: bytes):
        pass


class ConsumerProtocol(Protocol):
    queue: Queue
    auto_ack: bool = False
    exclusive: bool = False
    consumer_tag: Any | None = None

    def __init__(self, app: RabbitMQProtocol) -> None:
        pass

    def _get_route_handlers(self) -> list[handlerProtocol]:
        pass

    def callback(
        self,
        body: bytes, 
        message: Message
    ):
        pass


class RabbitMQProtocol(Protocol):
    def __init__(
        self,
        user: str = "guest",
        password: str = "guest",
        host: str = "localhost",
        port: int = 5672,
        virtual_host: str = "/",
        broker_id: Optional[str] = None,
        region: Optional[str] = None,
    ):
        pass

    @contextmanager
    def create_connection(self) -> Generator[Connection, None, None]:
        pass


    def publish(self, body: str, headers: Optional[dict], queue: Queue):
        pass

    def create_consumer(self, channel: virtual.Channel, consumer: ConsumerProtocol):
        pass

    def register_consumers(self, consumers: List[Type[ConsumerProtocol]]):
        pass

    def start_consuming(self):
        pass
