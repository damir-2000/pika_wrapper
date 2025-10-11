import socket
from contextlib import contextmanager
from typing import Generator, List, Optional, Type
from time import sleep

from kombu import Connection, Consumer, Queue, Producer
from kombu.transport import virtual

from .interface import ConsumerProtocol


class RabbitMQ:
    def __init__(
        self,
        user: str = "guest",
        password: str = "guest",
        host: str = "localhost",
        port: int = 5672,
        virtual_host: str = "/",
        queue_prefix: str = ""
    ):
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._virtual_host = virtual_host
        self._queue_prefix = queue_prefix
        self._consumers: List[Type[ConsumerProtocol]] = []

    @contextmanager
    def create_connection(self) -> Generator[Connection, None, None]:
        url = f"amqp://{self._user}:{self._password}@{self._host}:{self._port}{self._virtual_host}"
        
        connection = Connection(url)
        try:
            yield connection
        finally:
            connection.close()


    def publish(self, body: str, headers: Optional[dict], queue: Queue):

        with self.create_connection() as conn:
            with conn.channel() as channel:
                producer = Producer(
                    channel=channel,
                    routing_key=queue.routing_key,
                    exchange=queue.exchange
                )
                producer.publish(
                    body=body,  retry=True, headers=headers
                )
        

    def create_consumers(self, channel: virtual.Channel) -> list[Consumer]:
        consumers = []
        for consumer in self._consumers:
            consumer.queue.name = f"{self._queue_prefix}|{consumer.queue.name}"
            kombu_consumer = Consumer(channel=channel, queues=consumer.queue)
            kombu_consumer.register_callback(consumer(app=self).callback)
            consumers.append(kombu_consumer)
        return consumers

    def register_consumers(self, consumers: List[Type[ConsumerProtocol]]):
        self._consumers += consumers

    def start_consuming(self):
        while True:
            try:
                with self.create_connection() as conn:
                    def consume():
                        try:
                            conn.drain_events(timeout=1)
                        except socket.timeout:
                            pass

                    with conn.channel() as channel:
                        
                        consumers = self.create_consumers(channel=channel)
                        
                        while True:
                            for consumer in consumers:
                                with consumer:
                                    consume = conn.ensure(conn, consume)
                                    consume()
            
            except Exception as exc:
                print("error", exc)
                sleep(15)