# versión simple (in-memory). luego reemplazable por Redis

subscribers = []


def publish(event: dict):
    for fn in subscribers:
        fn(event)


def subscribe(handler):
    subscribers.append(handler)