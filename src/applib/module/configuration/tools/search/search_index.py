from applib.module.configuration.tools.search import SEARCH_SEP


class SearchIndex:
    def __init__(self, d: dict = {}) -> None:
        self._index: dict[str, list[str]] = {}
        self.build(d)

    def build(self, d: dict):
        """Build the search index of `d`. Any previous index is overwritten."""
        self._index = {}
        stack = [(d, [])]
        while stack:
            d_, p = stack.pop()
            for k, v in d_.items():
                if isinstance(v, dict):
                    stack.append((v, [*p, k]))
                self.add(k, f"{SEARCH_SEP}".join(p))

    def find(self, key: str, path: str) -> str:
        """Find the absolute path of `key` in the search index.

        Parameters
        ----------
        key : str
            The key to find the absolute path for.
        search_path : str
            The path used to guide the index search in case of duplicate keys.
            May be relative or absolute.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.

        Returns
        -------
        str
            The absolute path of `key`.

        Raises
        ------
        KeyError
            If no absolute path could be found. Can be caused by an ambigious `search_path`.
        """
        try:
            paths = self._index[key]
        except KeyError:
            paths = []

        for key_path in paths:
            substring_idx = key_path.find(path)
            if substring_idx != -1:
                if (
                    len(key_path) != substring_idx
                    and key_path[substring_idx + 1] == SEARCH_SEP
                ) or key_path == path:
                    return key_path
        raise IndexError(f"Key '{key}' is not in the index")

    def add(self, key: str, path: str):
        """Add a new key/path pair or add a new path to an existing key.

        Parameters
        ----------
        key : str
            The key to add a new absolute path to.
        path : str
            The path used to build the index with.
            Must be absolute.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        """
        try:
            self._index[key].append(path)
        except KeyError:
            self._index[key] = [path]

    def remove(self, key: str, path: str):
        """Remove a path from the key.
        If the last path of a key is removed, the key is removed too.

        Parameters
        ----------
        key : str
            The key to remove a path from.
        path : str
            The path to remove from the index.
            Must be absolute.
            Paths are separated by forward slash, e.g. `Path/to/some/place`.
        """
        paths = self._index[key]  # KeyError

        if len(paths) == 1:
            self._index.pop(key)
        else:
            paths.remove(path)
