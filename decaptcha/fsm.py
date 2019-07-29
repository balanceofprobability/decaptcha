from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def next(self):
        pass


class StateMachine(ABC):
    def __init__(self, initialstate: State):
        self.state = initialstate

    @abstractmethod
    def run(self) -> None:
        pass
