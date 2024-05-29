import dataclasses
import json
from inspect import get_annotations
from typing import Any, Callable, List, Optional

from pydantic import BaseModel

from .interface import RabbitMQProtocol
from .schema import Queue


def args_type_validate_decorator(args_name: List[str]):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            kwargs_annotation = get_annotations(func)
            all(isinstance(o, t) for o, t in zip(args, kwargs_annotation.values()))
            if not (
                all(key in kwargs_annotation.keys() for key in args_name)
                and (
                    all(
                        isinstance(kwargs.get(key), kwargs_annotation.get(key))
                        for key in args_name
                    )
                    or all(
                        isinstance(o, t)
                        for o, t in zip(args, kwargs_annotation.values())
                    )
                )
            ):
                raise TypeError

            return func(*args, **kwargs)

        return wrapper

    return decorator


class Producer:
    queue: Queue

    def __init__(self, app: RabbitMQProtocol) -> None:
        self.app = app

    def publish(self, body: Any, headers: Optional[dict] = None):
        if isinstance(body, dict):
            body = json.dumps(body)

        elif dataclasses.is_dataclass(body):
            body = json.dumps(dataclasses.asdict(body))

        elif isinstance(body, BaseModel):
            body = body.model_dump_json()

        elif not isinstance(body, str):
            raise TypeError

        self.app.publish(body=body, headers=headers, queue=self.queue)
