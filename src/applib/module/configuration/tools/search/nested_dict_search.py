from typing import Any

from . import SEARCH_SEP, SearchMode
from .search_index import SearchIndex


class NestedDictSearch:
    @classmethod
    def split(cls, path: str) -> list[str]:
        return path.split(SEARCH_SEP) if path else []

    @classmethod
    def _search_strict(cls, d: dict, key: str, path: list[str]) -> dict:
        stack = [d]
        i, n = 0, max(len(path) - 1, 0)
        d_ = {}
        while stack:
            d_ = stack.pop()

            try:
                v = d_[path[i]]  # KeyError
            except IndexError:
                break  # Key is top-level

            if i == n:
                return v
            elif isinstance(v, dict):  # We're still searching
                stack.append(v)
            elif i > n:  # We're out of bounds
                raise KeyError(
                    f"Couldn't find key '{key}' with parents {path[0:max(n-2, 0)]} in the dict"
                )
            i += 1
        return d_

    @classmethod
    def _search_fuzzy(
        cls, d: dict, key: str, search_path: str, idx: SearchIndex
    ) -> dict:
        abs_path = idx.find(key, search_path)
        return cls._search_strict(d, key, cls.split(abs_path))

    @classmethod
    def _search(
        cls, d: dict, key: str, search_path: str, idx: SearchIndex, mode: SearchMode
    ) -> dict:
        if mode == SearchMode.FUZZY:
            return cls._search_fuzzy(d, key, search_path, idx)
        elif mode == SearchMode.STRICT:
            return cls._search_strict(d, key, cls.split(search_path))
        else:
            raise ValueError(
                f"Invalid value for SearchMode. Got '{mode}', expected one of {SearchMode._member_names_}"
            )

    @classmethod
    def _generate(cls, d: dict, k: str, p: list[str]) -> dict:
        """Traverse `d` and generate key/value pairs for any missing keys in `p`.
        Generated keys are taken from `p` and values are empty mappings.

        Parameters
        ----------
        d : dict
            The dict to traverse.
        k : str
            The key to search for.
        p : list[str], optional
            The parents of `k`, ordered by index such that a lower index is an
            ancestor further away from `k` in the dict.

        Returns
        -------
        dict
            The dict containing `k`

        Example
        -------
        The input
        ```
        d = {"A": {"B"}}
        k = "D"
        p = ["A", "B", "C"]
        ```
        Returns
        ```
        d = {"A": {"B": {"C": {}}}}
        ```
        """
        p.append(k)
        stack = [d]
        i, n = 0, len(p) - 1
        while stack:
            d = stack.pop()

            # We've reached the dict where key will be inserted
            if i == n:
                break

            try:
                v = d[p[i]]
            except KeyError:
                d[p[i]] = v = type(d)()  # Create new mapping

            if isinstance(v, dict):
                stack.append(v)
            elif i != n:
                d[p[i]] = type(d)()  # Create new mapping
            i += 1
        return d

    @classmethod
    def find(
        cls,
        d: dict,
        key: str,
        search_path: str,
        idx: SearchIndex,
        mode=SearchMode.FUZZY,
        **kwargs,
    ) -> Any:
        """Return the value of `key`.

        If `key` does not exist, return `default`.
        Works on dicts of arbitrary depth.

        Parameters
        ----------
        d : dict
            The dict to traverse.
        key : str
            The key to search for.
        search_path : str, optional
            The path used to guide search in case of duplicate keys.
            May be relative or absolute depending on `search_mode`.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        idx : SearchIndex
            The search index of `d`.
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
        try:
            d = cls._search(d, key, search_path, idx, mode)
        except IndexError as e:
            try:
                return kwargs["default"]
            except KeyError:
                raise KeyError from e
        return d[key]

    @classmethod
    def insert(
        cls,
        d: dict,
        key: str,
        value: Any,
        path: str,
        create_missing=False,
    ):
        """Insert a new key/value pair.

        Works on dicts of arbitrary depth.

        Parameters
        ----------
        d : dict
            The dict to traverse.
        key : str
            The key to search for.
        value : Any
            The value to insert.
        path : str, optional
            The path used to guide search in case of duplicate keys.
            It must be absolute.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        create_missing : bool, optional
            Whether to create key/value pairs for keys in `p` which are not found in `d`.
            By default False.
        """
        p = cls.split(path)
        if create_missing:
            d_ = cls._generate(d, key, p)
        else:
            d_ = cls._search_strict(d, key, p)
        d_[key] = value

    @classmethod
    def update(
        cls,
        d: dict,
        key: str,
        value: Any,
        path: str,
        idx: SearchIndex,
        mode=SearchMode.FUZZY,
    ):
        """Update an existing key/value pair.

        Works on dicts of arbitrary depth.

        Parameters
        ----------
        d : dict
            The dict to traverse.
        key : str
            The key to search for.
        value : Any
            The value to insert.
        path : str, optional
            The path used to guide search in case of duplicate keys.
            May be relative or absolute depending on `search_mode`.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        idx : SearchIndex, optional
            The search index of `d`.
        mode : SearchMode, optional
            How to search the dict. By default SearchMode.FUZZY.
        """
        d_ = cls._search(d, key, path, idx, mode)
        d_[key] = value

    @classmethod
    def remove(
        cls,
        d: dict,
        key: str,
        search_path: str,
        idx: SearchIndex,
        mode=SearchMode.FUZZY,
    ):
        """Remove a key/value pair.

        Works on dicts of arbitrary depth.

        Parameters
        ----------
        d : dict
            The dict to traverse.
        key : str
            The key to search for.
        search_path : str, optional
            The path used to guide search in case of duplicate keys.
            May be relative or absolute depending on `search_mode`.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        idx : SearchIndex
            The search index of `d`.
        mode : SearchMode, optional
            How to search the dict. By default SearchMode.FUZZY.
        """
        try:
            d_ = cls._search(d, key, search_path, idx, mode)
            d_.pop(key)
        except IndexError as e:
            raise KeyError from e
