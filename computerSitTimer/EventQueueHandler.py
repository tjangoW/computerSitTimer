from enum import Enum
from queue import Queue
import random
from typing import Dict, Any, List, Optional, Final


class _Event:
    worker: List[int]
    name: Final[Enum]

    def __init__(self, event: Enum, worker: List[int]):
        self.name = event
        self.worker = worker

    def __repr__(self):
        return f"Event: {self.name}, worker(s): {', '.join([str(i) for i in self.worker])}"


class EventQueueHandler:
    """
    This is a class to handle calls to events.
    So now have a business logic at the core, and have 2 or more children (UI elements).
    When 1 child has been triggered, it needs to be propagated to the other children as well.
    Also for the case where core has event that should be handled by the children.
    """
    _events_queue: List[_Event]
    _children: Dict[int, Any]

    def __init__(self):
        self._children = {}
        self._events_queue = []

    def addEvent(self, reporter_id: int, event: Enum) -> None:
        worker_ids = list(self._children.keys())
        if reporter_id != 0:
            worker_ids.remove(reporter_id)
        if not worker_ids:
            return
        self._events_queue.append(_Event(event, worker_ids))

    def getWorkForChild(self, child_id: int) -> List[Enum]:
        out_event_names = []
        for event in self._events_queue:
            if child_id in event.worker:
                out_event_names.append(event.name)
                event.worker.remove(child_id)
        self._pruneEmptyEvents()
        return out_event_names

    def _pruneEmptyEvents(self) -> None:
        empty_event_idx = []
        for i, e in enumerate(self._events_queue):
            if not e.worker:
                empty_event_idx.append(i)
        empty_event_idx.reverse()
        for i in empty_event_idx:
            self._events_queue.pop(i)

    def _addChild(self, obj: Any, given_id: Optional[int] = None, skip_check=False) -> int:
        if given_id is None or given_id == 0 and not skip_check:
            while True:
                given_id = random.randint(1, 100)
                if given_id not in self._children:
                    break
        self._children[given_id] = obj
        return given_id

    def addChild(self, obj: Any, given_id: Optional[int] = None, skip_check=True) -> 'ChildReporterHelper':
        child_id = self._addChild(obj, given_id, skip_check)
        return self.ChildReporterHelper(self, child_id)

    class ChildReporterHelper:
        def __init__(self, parent: 'EventQueueHandler', child_id: int):
            self._parent = parent
            self._id = child_id

        def report(self, event: Enum) -> None:
            self._parent.addEvent(self._id, event)

        def getMyEvents(self) -> List[Enum]:
            return self._parent.getWorkForChild(self._id)


if __name__ == "__main__":
    e = EventQueueHandler()
    c1 = 1
    c2 = "ads"
    c3 = [123123, 123123]
    e1 = e.addChild(c1, 0)
    e2 = e.addChild(c2)
    e3 = e.addChild(c3, 333)

    e1.report("hello 1")
    print(e2.getMyEvents())

    print("-" * 7)

    e2.report("2 responded")
    print(e._events_queue)
    e.addEvent(0, "from mother")

    e3.getMyEvents()
    assert (len(e._events_queue) == 2)
