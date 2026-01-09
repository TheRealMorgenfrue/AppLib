import traceback

from applib.module.configuration.tools.search import SEARCH_SEP
from applib.module.logging import LoggingManager


class SearchIndex:
    def __init__(self, d: dict = {}) -> None:
        self._index: dict[str, list[str]] = {}
        self.build(d)

    def _log_ambiguity(self, key: str, candidates: list[str]):
        LoggingManager().warning(
            f"Cannot uniquely identify a path for key `{key}`. "
            + f"Picking the first of possible candidates {candidates}"
        )

    def build(self, d: dict):
        """Build the search index of `d`. Any previous index is overwritten."""
        self._index = {}
        self.update(d, [])

    def update(self, d: dict, path_root: list[str]):
        """Update the search index with `d`, overwriting keys in the
        index if they exists in both `d` and the index"""
        stack = [(d, path_root)]
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
        IndexError
            If no absolute path could be found. Can be caused by an ambigious `search_path`.
        """
        try:
            idx_paths = self._index[key]
        except KeyError:
            idx_paths = []

        if not path and len(idx_paths) == 1:
            # If no path and only one index path matching key, it's uniquely identified.
            return idx_paths[0]

        matches: dict[float, list[str]] = {}
        for idx_path in idx_paths:
            path_len, idx_len = len(path), len(idx_path)
            # A path larger than the index path is irrelevant
            if path_len > idx_len:
                continue
            # The path is already absolute
            elif idx_path == path:
                return idx_path
            elif path_len == 0 and idx_len > 1:
                # Ambigious search path
                self._log_ambiguity(key, idx_paths)
                return idx_paths[0]

            # Check if the path is actually part of the index path
            for p in idx_path.split(SEARCH_SEP):
                if path == p:
                    accuracy = path_len / idx_len
                    try:
                        matches[accuracy].append(idx_path)
                    except KeyError:
                        matches[accuracy] = [idx_path]
                    break

        if matches:
            accuracies = sorted(matches.keys(), reverse=True)
            # Check if multiple paths have equal accuracy
            if len(matches[accuracies[0]]) > 1:
                self._log_ambiguity(key, matches[accuracies[0]])
            return matches[accuracies[0]][0]

        raise IndexError(f"Key '{key}' is not in the index using path '{path}'")

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
            try:
                paths.remove(path)
            except ValueError:
                LoggingManager().error(
                    f"Failed to remove path '{path}' from key '{key}'\n"
                    + traceback.format_exc()
                )
