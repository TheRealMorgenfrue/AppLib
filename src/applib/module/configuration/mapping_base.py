from collections import deque
from collections.abc import Generator
from typing import Any

from applib.module.configuration.tools.template_utils.options import GUIOption, Option

from .tools.search import SEARCH_SEP, SearchMode
from .tools.search.nested_dict_search import NestedDictSearch
from .tools.search.search_index import SearchIndex


class MappingBase:

    def __init__(self, d: dict):
        self._idx = SearchIndex(d)
        self._dict: dict[str, Any] = d

    def __iter__(self):
        # Breath-first search
        queue = deque([self._dict])
        while queue:
            for k, v in queue.popleft().items():
                if isinstance(v, dict):
                    queue.append(v)
                yield k, v

    def __str__(self):
        return f"{self._dict}"

    def options(self) -> Generator[tuple[str, Option | GUIOption, str], Any, None]:
        """Returns the Options of the mapping.

        Yields
        ------
        tuple[str, Option | GUIOption, str]
            A key and its associated Option or GUIOption, and its path in the mapping.
        """
        path = []
        stack = [self._dict]
        visited = set()
        while stack:
            _dict = stack[-1]
            for k, v in _dict.items():
                str_path = f"{f"{SEARCH_SEP}".join([*path, k])}"
                if str_path not in visited:
                    if isinstance(v, dict):
                        path.append(k)
                        stack.append(v)
                        break
                    yield k, v, f"{SEARCH_SEP}".join(path)
            else:
                visited.add(f"{SEARCH_SEP}".join(path))
                stack.pop()
                if path:
                    path.pop()

    def get_path(self, key, base_path="", **kwargs) -> str:
        """Return the path of `key`.

        If `key` does not exist, return `default`.

        The search is fuzzy and may return an incorrect result under certain conditions,
        e.g., duplicate keys with an empty `base_path` parameter.

        Parameters
        ----------
        key : str
            The key whose path to look for.
        default : Any
            The default value, if supplied, is returned instead of raising a
            KeyError if `key` isn't found.

        Returns
        -------
        str
            The path of `key`.

        Raises
        ------
        KeyError
            If `key` isn't found and no `default` value is given.
        """
        try:
            return self._idx.find(key, base_path)
        except KeyError as err:
            try:
                return kwargs["default"]
            except KeyError:
                raise err from None

    def get_value(
        self,
        key: str,
        path: str = "",
        mode=SearchMode.FUZZY,
        **kwargs,
    ) -> Any:
        """Return the value of `key`.

        If `key` does not exist, return `default`.

        Parameters
        ----------
        key : str
            The key to look for.
        path : str, optional
            The path used to guide search in case of duplicate keys.
            May be relative or absolute depending on `search_mode`.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        mode : SearchMode, optional
            How to search the dict. By default SearchMode.FUZZY.
        default : Any
            The default value, if supplied, is returned instead of raising a
            KeyError if `key` isn't found.

        Returns
        -------
        Any
            The value of `key`.

        Raises
        ------
        KeyError
            If `key` isn't found and no `default` value is given.
        """
        return NestedDictSearch.find(self._dict, key, path, self._idx, mode, **kwargs)

    def set_value(
        self,
        key: str,
        value: Any,
        path: str,
        create_missing=False,
    ):
        """Insert a new key/value pair or update an existing.

        Parameters
        ----------
        key : str
            The key to search for.
        value : Any
            The value to insert.
        path : str, optional
            The path used to guide search in case of duplicate keys.
            May be relative or absolute depending on `search_mode`. However, if
            inserting a new key/value pair the path must be absolute.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        create_missing : bool, optional
            Whether to create key/value pairs for keys in `p` which are not found in `d`.
            By default False.
        """
        try:
            abs_path = self._idx.find(key, path)
        except KeyError as e:
            if create_missing:
                NestedDictSearch.insert(self._dict, key, value, path, create_missing)
                self._idx.add(key, path)
            else:
                raise
        NestedDictSearch.update(self._dict, key, value, abs_path, self._idx)

    def remove_value(
        self,
        key: str,
        path: str,
        mode=SearchMode.FUZZY,
    ):
        """Remove a key/value pair.

        Parameters
        ----------
        key : str
            The key to look for.
        path : str, optional
            The path used to guide search in case of duplicate keys.
            May be relative or absolute depending on `search_mode`.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        mode : SearchMode, optional
            How to search the dict. By default SearchMode.FUZZY.
        """
        NestedDictSearch.remove(self._dict, key, path, self._idx, mode)
        if mode == SearchMode.FUZZY:
            path = self._idx.find(key, path)
        self._idx.remove(key, path)
