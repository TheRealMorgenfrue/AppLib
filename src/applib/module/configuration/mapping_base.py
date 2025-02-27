from abc import abstractmethod
from typing import Any, Hashable, Iterable, Literal, Union, override

from ..datastructures.pure.meldableheap import MeldableHeap
from ..datastructures.redblacktree_mapping import RedBlackTreeMapping, _rbtm_item
from ..logging import AppLibLogger


class MappingBase(RedBlackTreeMapping):
    _logger = AppLibLogger().get_logger()

    def __init__(self, iterable=[], name=""):
        self._settings_cache = None
        super().__init__(iterable, name)

    @abstractmethod
    def _prefix_msg(self) -> str:
        """Prefix log messages with this string. Should include self.name."""
        ...

    @abstractmethod
    def _is_setting(self, item: _rbtm_item) -> bool: ...

    @override
    def update(self, key, value, parents=[]):
        super().update(key, value, parents)
        self._settings_cache = None

    def get_settings(self) -> list[_rbtm_item]:
        """
        Get settings with corresponding options as specified in the template documentation.

        Returns
        -------
        list[dict[Hashable, Any]]
            A position-prioritised list of settings.
        """
        if self._settings_cache is None:
            heap = MeldableHeap(
                [
                    RedBlackTreeMapping.HeapNode(*item)
                    for item in self
                    if self._is_setting(item)
                ]
            )
            d_settings = []
            while heap:
                h_node = heap.remove()  # type: RedBlackTreeMapping.HeapNode
                key, value, pos, ps = h_node.get()
                dump = {key: {}}
                if self._check_value(value):
                    v = (
                        value.x
                    )  # type: list[tuple[RedBlackTreeMapping.TreeNode, Iterable[Hashable]]]
                    for tn, tn_ps in v:
                        c_k, c_v, c_i, c_ps = tn.get(tn.index(tn_ps))
                        dump[key][c_k] = c_v
                else:
                    dump[key] = value
                d_settings.append((key, dump, pos, ps))
            self._settings_cache = d_settings
        return self._settings_cache

    def get_value(
        self,
        key: Hashable,
        parents: Union[Hashable, list[Hashable]] = [],
        default=None,
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
        errors: Literal["ignore", "raise"] = "ignore",
    ) -> Any:
        """
        Return the value for `key`.

        If `key` does not exist, return `default`.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        parents : Hashable | list[Hashable], optional
            The parents of `key`.
            By default [].

        default : Any, optional
            Return `default` if key does not exist.
            By default None.

        search_mode : Literal["strict", "smart", "immediate", "any"], optional
            How to search for `key`.
            - "strict"
                &ensp; Requires `parents` to match exactly.
                I.e. ["a", "b"] == ["a", "b"]
            - "smart"
                &ensp; Tries to find the key using different heuristics.
                Note that it can result in the wrong key under certain conditions.
            - "immediate"
                &ensp; Requires `parents` to be a Hashable that matches the closest parent.
                I.e. "b" == ["a", "b"]
            - "any"
                &ensp; Requires `parents` to be a Hashable that matches any parent.
                I.e. "a" == ["a", "b"]

            By default "smart".

        errors : Literal["ignore", "raise"]
            Action to take if `key` does not exist.
                "ignore"
                    Ignores errors and returns `default`.
                "raise"
                    Raises any error that may occur.

            By default "ignore".
        """
        try:
            return self.find(key, parents, search_mode)
        except KeyError as e:
            if errors == "raise":
                raise e from None
        except LookupError as e:
            if errors == "raise":
                raise e from None
            self._logger.error(
                f"{e.args[0]}. Returning default '{default}'\n  {"\n  ".join(e.__notes__)}"
            )
        return default

    def set_value(
        self,
        key: Hashable,
        value: Any,
        parents: Union[Hashable, list[Hashable]] = [],
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
        errors: Literal["ignore", "raise"] = "ignore",
    ):
        """
        Update value of `key` with `value`.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        value : Any
            Map value to `key`.

        parents : Hashable | list[Hashable], optional
            The parents of `key`.
            By default [].

        search_mode : Literal["strict", "smart", "immediate", "any"], optional
            How to search for `key`.
            - "strict"
                &ensp; Requires `parents` to match exactly.
                I.e. ["a", "b"] == ["a", "b"]
            - "smart"
                &ensp; Tries to find the key using different heuristics.
                Note that it can result in the wrong key under certain conditions.
            - "immediate"
                &ensp; Requires `parents` to be a Hashable that matches the closest parent.
                I.e. "b" == ["a", "b"]
            - "any"
                &ensp; Requires `parents` to be a Hashable that matches any parent.
                I.e. "a" == ["a", "b"]

            By default "smart".

        errors : Literal["ignore", "raise"]
            Action to take if `key` does not exist.
                "ignore"
                    Ignores errors and returns `default`.
                "raise"
                    Raises any error that may occur.

            By default "ignore".
        """
        try:
            self.update(key, value, parents)
        except KeyError as e:
            if errors == "raise":
                raise e from None
            self._logger.warning(e.args[0])
        except LookupError as e:
            if errors == "raise":
                raise e from None
            self._logger.warning(f"{e.args[0]}\n  {"\n  ".join(e.__notes__)}")
