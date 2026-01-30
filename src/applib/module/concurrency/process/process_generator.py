from abc import abstractmethod

from ..process.process_base import ProcessGUI


class ProcessGeneratorBase:

    @abstractmethod
    def program(self) -> str:
        """
        Returns
        -------
        str
            The absolute path of the program to run.
        """
        ...

    @abstractmethod
    def arguments_list(self) -> list[str]:
        """All arguments to executed by the program.

        Returns
        ------
        list[str]
            Each argument is a string in the list, e.g., `--input "path" --output "o"`
        """
        ...

    def process(self) -> type[ProcessGUI]:
        """The Process class in which the arguments are executed by the program.

        Must be a `ProcessGUI` (or a subclass thereof) in order
        to be handled properly by the thread manager.

        Returns
        -------
        type[ProcessBase]
            A reference to the process class.
        """
        return ProcessGUI
