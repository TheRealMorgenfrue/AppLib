from abc import abstractmethod
from typing import Any, Hashable
from ..datastructures.redblacktree_mapping import RedBlackTreeMapping
from ..logging import AppLibLogger


class MappingBase(RedBlackTreeMapping):
    _logger = AppLibLogger().getLogger()

    def __init__(self, iterable=..., name=""):
        super().__init__(iterable, name)

    @abstractmethod
    def _prefixMsg(self) -> str:
        """Prefix log messages with this string. Should include self.name."""
        ...

    def getValue(
        self, key: Hashable, parent: Hashable, immediate: bool = False, default=None
    ) -> Any:
        """
        Return the value for `key`.

        If `key` does not exist, return `default`.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        parent : Optional[Hashable], optional
            The parent of `key`.
            By default None.

        immediate : bool, optional
            If True, `parent` must be the direct predecessor of `key`.
            If False, `parent` must be an ancestor of `key`.
            By default False.

        default : _type_, optional
            Return `default` if key does not exist.
            By default None.
        """
        try:
            return self.find(key, parent, immediate)
        except KeyError:
            return default
        except LookupError as e:
            self._logger.warning(e.args[0])
            self._logger.debug("\n  ".join(e.__notes__))
            return default

    def setValue(
        self, key: Hashable, value: Any, parent: Hashable, immediate: bool = False
    ):
        """
        Update value of `key` with `value`.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        value : Any
            Map value to `key`.

        parent : Optional[Hashable], optional
            The parent of `key`.
            By default None.

        immediate : bool, optional
            If True, `parent` must be the direct predecessor of `key`.
            If False, `parent` must be an ancestor of `key`.
            By default True.
        """
        try:
            self.update(key, value, parent, immediate)
        except KeyError as e:
            self._logger.warning(e.args[0])
        except LookupError as e:
            self._logger.warning(e.args[0])
            self._logger.debug("\n  ".join(e.__notes__))
