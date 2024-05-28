from dataclasses import dataclass

from pika.exchange_type import ExchangeType


@dataclass
class Exchange:
    exchange: str
    exchange_type: ExchangeType | str
    passive: bool = False
    durable: bool = False
    auto_delete: bool = False
    internal: bool = False


@dataclass
class Queue:
    queue: str
    exchange: Exchange
    routing_key: str
    passive: bool = False
    durable: bool = False
    exclusive: bool = False
    auto_delete: bool = False
