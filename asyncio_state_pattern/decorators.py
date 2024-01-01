from .constants import entry_action_attr, exit_action_attr, event_action_attr


def on_entry(method):
    setattr(method, entry_action_attr, True)
    return method


def on_exit(method):
    setattr(method, exit_action_attr, True)
    return method


def on_event(event: str):
    def decorator(method):
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)

        setattr(wrapper, event_action_attr, event)
        return wrapper

    return decorator
