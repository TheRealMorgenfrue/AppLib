# TODO: Implement C++ library https:#github.com/Tessil/hat-trie
# using hash function https:#github.com/google/cityhash
# as python bindings https:#pybind11.readthedocs.io/en/stable/


from collections import deque
from typing import Any, Self


class TrieNode:
    def __init__(self, key: str | None):
        self.key = key
        """A character in the whole word"""
        self.data = None  # type: set | None
        """The data associated with the whole word. Only present (not null) if self.end == True"""
        self.parent = None  # type: Self
        self.children = {}  # type: dict[str | None, Self]
        self.end = None  # type: None | str
        """
        Check to see if the node is at the end of a whole word.
        We abuse this variable slightly by also storing the word here if we're at the end.
        """

    def delete(self):
        """Remove this node from the trie."""
        if len(self.children) == 0:
            # Remove reference to this from parent's children.
            self.parent.children.pop(self.key)
        self.end = None
        del self.data
        self.data = None


class Trie:
    def __init__(self):
        """
        A basic Trie of word/data pairs.
        It allows O(k) worst-case additions and O(k + |V_T|) worst-case searches,
        where:
         - k is the word size.
         - |V_T| is the size of the remaining subtree after traversing k trie nodes.
        """
        self.base = TrieNode(None)

    def add(self, word: str, data: Any, override=False):
        """
        Add a word and its associated data.
        Allows mapping multiple data objects to the same word.

        Parameters
        ----------
        word : str
            The word to add.
        data : Any
            The data to associate with `word`.
        override : bool, optional
            If `word` already exists, override existing data in the trie with `data`.
            By default False.
        """
        node = self.base
        for char in word:
            if not char in node.children:
                child = TrieNode(char)
                child.parent = node
                node.children[char] = child
            node = node.children[char]
        else:
            node.end = word
            if not override and isinstance(node.data, set):
                node.data.add(data)
            else:
                node.data = set([data])

    def contains(self, word: str) -> bool:
        """
        Test word membership in the trie.

        Returns
        -------
        bool
            Whether the word is in the trie.
        """
        node = self.base
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                return False
        return node.end is not None

    def find(self, prefix: str, limit: int = 0) -> list[str]:
        """
        Find word/data pairs that contains `prefix`.

        Parameters
        ----------
        prefix : str
            The prefix word to search for.
        limit : int
            Stop search after at most `limit` words. `0` means no limit.
            By default 0.

        Returns
        -------
        list[str]
            List of lists where a[i][0] is a word and a[i][1] is the word's data.
            Ordered by word relevance such that more relevant words have a lower index i.
        """
        node = self.base
        output = []
        for char in prefix:
            if char in node.children:
                node = node.children[char]
            else:
                return output

        stack = deque([node])
        while stack:
            node = stack.popleft()
            #  Base case: If node is at a word, push to output.
            if node.end is not None:
                if limit > 0 and len(output) >= limit:
                    break
                output.append([node.end, node.data])

            # Traverse all children
            for child in node.children.values():
                stack.append(child)
        return output

    def remove(self, word: str, item: Any = None):
        """Removes `item` from the trie.

        Parameters
        ----------
        word : str
            The word to search for.
        item : Any, optional
            Remove `item` from `word`'s data container.
            If None, `word` is completely removed from the trie.
            By default None.
        """
        node = self.base
        for char in word:
            try:
                node = node.children.get(char)  # type: ignore
            except AttributeError:
                return  # word doesn't exist in the trie

        if node and node.end is not None:
            if item is not None:
                if node.data and len(node.data) > 1:
                    try:
                        node.data.remove(item)
                    except KeyError:
                        pass
            else:
                # If we have `item` and deleting would create a node with empty data,
                # delete the node instead.
                node.delete()
