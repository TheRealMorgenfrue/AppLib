# TODO: Implement C++ library https:#github.com/Tessil/hat-trie
# using hash function https:#github.com/google/cityhash
# as python bindings https:#pybind11.readthedocs.io/en/stable/


from collections import deque
from typing import Any, Self


class TrieNode:
    def __init__(self, key: str | None):
        # the "key" value will be the character in sequence
        self.key = key
        # the "data" value is the data associated with the whole word. Thus only present (not None) if self.end == True
        self.data = None  # type: set | None
        # we keep a reference to parent
        self.parent = None  # type: Self | None
        # we have a dict of children
        self.children = {}  # type: dict[str, Self]
        # check to see if the node is at the end
        self.end = False

    def getWord(self):
        output = []
        node = self
        while node.parent is not None:
            output.append(node.key)
            node = node.parent
        return "".join(reversed(output))


class Trie:
    def __init__(self):
        """
        A basic Trie of word/data pairs.

        It allows O(k) worst-case additions and O(dk) worst-case searches,
        where k is the word size and d is size of the alphabet.
        """
        self.base = TrieNode(None)

    def add(self, word: str, data: Any, override=False):
        """
        Add a word and its associated data.
        Allows mapping multiple data objects to the same word.

        Parameters
        ----------
        word : str
            The word to add. If it already exists, `data` is appended to its internal list (unless `override` is True).
        data : Any
            Data associated with `word`.
        override : bool, optional
            If `word` already exists, override its data with `data`.
            By default False.
        """
        node = self.base
        for point in word:
            if not point in node.children:
                node.children[point] = TrieNode(point)
                node.children[point].parent = node
            node = node.children[point]
        else:
            node.end = True
            if not override and isinstance(node.data, set):
                node.data.add(data)
            else:
                node.data = set([data])

    def contains(self, word: str) -> bool:
        """
        Test word membership in the trie

        Returns
        -------
        bool
            Whether the word is in the trie.
        """
        node = self.base
        for point in word:
            if point in node.children:
                node = node.children[point]
            else:
                return False
        return node.end

    def find(self, prefix: str) -> list[str]:
        """
        Find word/data pairs that contains `prefix`

        Returns
        -------
        list[str]
            List of lists where a[i][0] is a word and a[i][1] is the word's data.
            Ordered by word relevance such that more relevant words have a lower index i.
        """
        node = self.base
        output = []
        for point in prefix:
            # make sure prefix actually has words
            if point in node.children:
                node = node.children[point]
            else:
                # there's none. just return it.
                return output

        queue = deque([node])
        while queue:
            node = queue.popleft()
            # base case, if node is at a word, append to output
            if node.end:
                output.append([node.getWord(), node.data])

            for child in node.children:
                queue.append(node.children[child])
        return reversed(output)
