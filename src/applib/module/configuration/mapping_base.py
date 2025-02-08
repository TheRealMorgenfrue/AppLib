from abc import abstractmethod
from typing import Any, Hashable, Iterable, Literal, Union

from ..datastructures.redblacktree_mapping import RedBlackTreeMapping
from ..logging import AppLibLogger


class MappingBase(RedBlackTreeMapping):
    _logger = AppLibLogger().getLogger()

    def __init__(self, iterable=[], name=""):
        super().__init__(iterable, name)

    @abstractmethod
    def _prefix_msg(self) -> str:
        """Prefix log messages with this string. Should include self.name."""
        ...

    def get_value(
        self,
        key: Hashable,
        parents: Union[Hashable, Iterable[Hashable]] = [],
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

        parents : Hashable | Iterable[Hashable], optional
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
        parents: Union[Hashable, Iterable[Hashable]] = [],
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

        parents : Hashable | Iterable[Hashable], optional
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
            self.update(key, value, parents, search_mode)
        except KeyError as e:
            if errors == "raise":
                raise e from None
            self._logger.warning(e.args[0])
        except LookupError as e:
            if errors == "raise":
                raise e from None
            self._logger.warning(f"{e.args[0]}\n  {"\n  ".join(e.__notes__)}")
