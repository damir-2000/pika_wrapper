import ssl
from contextlib import contextmanager
from typing import Generator, List, Optional, Type

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

from .interface import ConsumerProtocol
from .schema import Queue


class RabbitMQ:
    def __init__(
        self,
        user: str = "guest",
        password: str = "guest",
        host: str = "localhost",
        port: int = 5672,
        virtual_host: str = "/",
        broker_id: Optional[str] = None,
        region: Optional[str] = None,
        queue_prefix: str = ""
    ):
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._virtual_host = virtual_host
        self._broker_id = broker_id
        self._region = region
        self._queue_prefix = queue_prefix
        self._consumers: List[Type[ConsumerProtocol]] = []

    @contextmanager
    def create_connection(self) -> Generator[BlockingConnection, None, None]:
        if self._broker_id and self._region:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.set_ciphers("ECDHE+AESGCM:!ECDSA")

            url = f"amqps://{self._user}:{self._password}@{self._broker_id}.mq.{self._region}.amazonaws.com:{self._port}{self._virtual_host}"
            parameters = pika.URLParameters(url)
            parameters.ssl_options = pika.SSLOptions(context=ssl_context)

        elif self._host and self._port:
            credentials = pika.PlainCredentials(
                username=self._user, password=self._password
            )
            parameters = pika.ConnectionParameters(
                host=self._host,
                port=5672,
                credentials=credentials,
                virtual_host=self._virtual_host,
            )

        else:
            raise ValueError
        connection = pika.BlockingConnection(parameters)

        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def create_channel(
        self,
    ) -> Generator[BlockingChannel, None, None]:
        with self.create_connection() as connection:
            channel = connection.channel()
            try:
                yield channel
            finally:
                channel.close()

    def publish(self, body: str, headers: Optional[dict], queue: Queue):
        properties = pika.BasicProperties(headers=headers)

        with self.create_channel() as channel:
            if queue.exchange and queue.routing_key:
                channel.basic_publish(
                    exchange=queue.exchange.exchange,
                    routing_key=queue.routing_key,
                    body=body,
                    properties=properties,
                )

            elif queue:
                channel.basic_publish(
                    exchange="",
                    routing_key=queue.queue,
                    body=body,
                    properties=properties,
                )

    def create_consumer(self, channel: BlockingChannel, consumer: ConsumerProtocol):
        queue = consumer.queue
        exchange = queue.exchange

        channel.queue_declare(
            queue=f"{self._queue_prefix}|{queue.queue}",
            passive=queue.passive,
            durable=queue.durable,
            exclusive=queue.exclusive,
            auto_delete=queue.auto_delete,
        )

        if exchange and queue.routing_key:
            channel.exchange_declare(
                exchange=exchange.exchange,
                exchange_type=exchange.exchange_type,
                passive=exchange.passive,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
            )
            channel.queue_bind(
                queue=queue.queue,
                exchange=exchange.exchange,
                routing_key=queue.routing_key,
            )

        channel.basic_consume(
            queue=queue.queue,
            on_message_callback=consumer.callback,
            auto_ack=consumer.auto_ack,
            exclusive=consumer.exclusive,
            consumer_tag=consumer.consumer_tag,
        )

    def register_consumers(self, consumers: List[Type[ConsumerProtocol]]):
        self._consumers += consumers

    def start_consuming(self):
        with self.create_channel() as channel:
            for consumer in self._consumers:
                self.create_consumer(channel=channel, consumer=consumer(app=self))
            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                print("consuming exit")
