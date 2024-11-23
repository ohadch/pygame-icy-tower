import abc


class Entity(abc.ABC):

    @abc.abstractmethod
    def draw(self):
        pass
