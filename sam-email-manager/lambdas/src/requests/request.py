from src.models.event import Event


class Request:
    @classmethod
    def from_event(cls, event: Event):
        """
        Factory method to create a Request instance from an Event.
        Args:
            event (Event): The Event instance.
        Returns:
            Request: An instance of the Request class.
        """
        try:
            return cls(**event.data)
        except TypeError as e:
            raise TypeError(f"Invalid event data for {cls.__name__}: {e}")