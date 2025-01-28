from abc import abstractmethod
from typing import Any, Hashable, Iterable, override

from ..datastructures.pure.meldableheap import MeldableHeap
from ..datastructures.redblacktree_mapping import RedBlackTreeMapping
from ..logging import AppLibLogger


class MappingBase(RedBlackTreeMapping):
    _logger = AppLibLogger().getLogger()

    def __init__(self, iterable=..., name=""):
        super().__init__(iterable, name)
        self._modified = False
        self._heap = None
        self._settings = None

    @abstractmethod
    def _prefix_msg(self) -> str:
        """Prefix log messages with this string. Should include self.name."""
        ...

    @override
    def _add(self, key, value, position, parents=...):
        self._modified = True
        return super()._add(key, value, position, parents)

    @override
    def remove(self, key, parent=None, immediate=True):
        self._modified = True
        return super().remove(key, parent, immediate)

    @override
    def update(self, key, value, parent=None, immediate=True):
        self._modified = True
        return super().update(key, value, parent, immediate)

    def get_settings(self) -> list[tuple[Hashable, Any, Iterable[Hashable]]]:
        """
        Get settings with corresponding options as specified in the template documentation.

        Example
        -------
        >>> {
        >>>  "appTheme": {
        >>>    "ui_type": UITypes.COMBOBOX,
        >>>    "ui_title": "Set application theme",
        >>>    "default": "System",
        >>>    "values": AppArgs.template_themes,
        >>>    "validators": [
        >>>       validateTheme
        >>>    ]
        >>>  }
        >>> }

        Returns
        -------
        list[tuple[Hashable, Any, Iterable[Hashable]]]
            A position-prioritised list of settings.
            [0] : key
            [1] :
        """
        if self._modified or not self._settings:
            self._heap = MeldableHeap(
                [
                    RedBlackTreeMapping.HeapNode(k, v, pos, ps)
                    for k, v, pos, ps in self
                    if not self._check_value(v)
                ]
            )
            self._settings = []
            current_ps = None
            option = []
            for node in self._heap:
                k, v, pos, ps = node.get()
                str_ps = f"{ps}"
                if current_ps[0] != str_ps:
                    self._settings.append((k, dict(option), current_ps[1]))
                    current_ps = (str_ps, ps)
                    option.clear()
                option.append((k, v))
        return self._settings

    def get_value(
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

    def set_value(
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
