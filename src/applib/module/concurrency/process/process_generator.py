from abc import ABC, abstractmethod
from typing import Any, Generator

from ..process.process_base import ProcessBase


class ProcessGenerator(ABC):

    @abstractmethod
    def generator(self) -> Generator[ProcessBase, Any, Any]:
        """Generator that creates new processes to be consumed by a thread/process manager.

        Yields
        ------
        Generator[ProcessBase]
            All created processes must inherit the ProcessBase class
        """
        ...

    @abstractmethod
    def canStart(self) -> bool:
        """Whether any processes can be created by the generator.

        Returns
        -------
        bool
            Returns True if the Generator is non-empty.
        """
        ...

    @abstractmethod
    def getTotalProgress(self) -> int:
        """Calculates the total amount of processes that can be created by the generator.

        Returns
        -------
        int
            The total amount of processes that can be created by the generator.
        """
        ...
