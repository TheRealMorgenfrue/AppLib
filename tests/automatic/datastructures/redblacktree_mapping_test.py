import pytest

from applib.module.datastructures.redblacktree_mapping import RedBlackTreeMapping


class TestRedblacktreeMapping:
    d1 = {"General": {"loglevel": 1}, "Appearance": {"theme": 2}}

    d2 = {"ProcTest": {"Proc": 1}, "Appearance": {"color": 2}}

    def tree1_init(self):
        return RedBlackTreeMapping([self.d1], "tree1")

    def tree2_init(self):
        return RedBlackTreeMapping([self.d2], "tree2")

    def test_serialize_basic(self):
        """
        Test converting tree to dict.
        Must preserve order of elements from input dict
        """
        assert (
            f"{self.d1}" == f"{self.tree1_init().dump()}"
        ), "Order of elements was not preserved"

    def test_serialize_union(self):
        assert (
            f"{self.d1 | self.d2}"
            == f"{(self.tree1_init() | self.tree2_init()).dump()}"
        ), "Order of elements was not preserved"

    @pytest.mark.skip()
    def test_insert(self):
        pass

    def test_remove(self):
        key = "theme"
        tree = self.tree1_init()
        tree.remove(key)

        with pytest.raises(KeyError):
            assert tree.find(key)

    @pytest.mark.skip()
    def test_union(self):
        pass


if __name__ == "__main__":
    TestRedblacktreeMapping().test_serialize_union()
