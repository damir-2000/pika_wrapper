from kombu import Exchange, Queue

from pika_wrapper import RabbitMQ, consumer
from pydantic import BaseModel
import time

app = RabbitMQ()
exchange = Exchange("test", "direct")
queue = Queue(name="test", exchange=exchange, routing_key="test_route", durable=True)
queue2 = Queue(name="test2", exchange=exchange, routing_key="test_route2", durable=True)

class TestDTO(BaseModel):
    name: str



class TestConsumer(consumer.Consumer):
    queue = queue

    @consumer.handler(headers=dict(action="action"))
    def test(self, body: TestDTO):
        print(body)
        time.sleep(10)
    
class TestConsumer2(consumer.Consumer):
    queue = queue2

    @consumer.handler(headers=dict(action="action"))
    def test(self, body: TestDTO):
        print(body)


app.register_consumers([TestConsumer, TestConsumer2])
app.start_consuming()