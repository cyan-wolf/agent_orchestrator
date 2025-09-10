from typing import Sequence
from ai.tracing.schemas import Trace

class Tracer:
    def __init__(self, history: Sequence[Trace] | None = None):
        if history is None:
            self.trace_list: list[Trace] = []
        else:
            self.trace_list = list(history)

    def add(self, trace: Trace):
        self.trace_list.append(trace)

    def get_history(self) -> Sequence[Trace]:
        return self.trace_list.copy()