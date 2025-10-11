from kombu import Exchange, Queue

from pika_wrapper import RabbitMQ, producer
from pydantic import BaseModel


app = RabbitMQ()
exchange = Exchange("test", "direct")
queue = Queue(name="test", exchange=exchange, routing_key="test_route", durable=True)
queue2 = Queue(name="test2", exchange=exchange, routing_key="test_route2", durable=True)

class TestDTO(BaseModel):
    name: str


class TestProducer(producer.Producer):
    queue = queue
           
    @producer.args_type_validate_decorator(args_name=["body"])
    def test(
        self, body: TestDTO
    ):
        headers = dict(
            action="action",
        )
        self.publish(body=body, headers=headers)
        
class TestProducer2(producer.Producer):
    queue = queue2
           
    @producer.args_type_validate_decorator(args_name=["body"])
    def test(
        self, body: TestDTO
    ):
        headers = dict(
            action="action",
        )
        self.publish(body=body, headers=headers)

TestProducer(app=app).test(body=TestDTO(name="damir"))
TestProducer2(app=app).test(body=TestDTO(name="damir2"))