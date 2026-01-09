import pytest

from applib.module.configuration.tools.search import SEARCH_SEP
from applib.module.configuration.tools.search.nested_dict_search import NestedDictSearch
from applib.module.configuration.tools.search.search_index import SearchIndex


class TestNestedDictSearch:

    def get_test_dict(self) -> dict:
        return {"L1": {"L2": {"I1": 1}, "I2": 2, "L2_1": {"I2": {"I1": 46}}}, "I3": 3}

    def get_search_index(self) -> SearchIndex:
        return SearchIndex(self.get_test_dict())

    def test_find_I1_1(self):
        """Find value 3 layers down"""
        d = self.get_test_dict()
        k = "I1"
        p = f"L1{SEARCH_SEP}L2"
        v = NestedDictSearch.find(d, k, p, self.get_search_index())
        assert v == 1

    def test_find_I1_2(self):
        """Find value 3 layers down with two branches on second layer"""
        d = self.get_test_dict()
        k = "I1"
        p = f"L1{SEARCH_SEP}L2_1{SEARCH_SEP}I2"
        v = NestedDictSearch.find(d, k, p, self.get_search_index())
        assert v == 46

    def test_find_I2(self):
        """Find value two layers down with a branch on second layer"""
        d = self.get_test_dict()
        k = "I2"
        p = "L1"
        v = NestedDictSearch.find(d, k, p, self.get_search_index())
        assert v == 2

    def test_find_I3(self):
        """Find last value in layer 1"""
        d = self.get_test_dict()
        k = "I3"
        p = ""
        v = NestedDictSearch.find(d, k, p, self.get_search_index())
        assert v == 3

    def test_find_L1(self):
        """Find first value in layer 1"""
        d = self.get_test_dict()
        k = "L1"
        p = ""
        v = NestedDictSearch.find(d, k, p, self.get_search_index())
        assert d[k] == v

    def test_find_L2(self):
        """Find value on layer 2 containing other key/value pairs"""
        d = self.get_test_dict()
        k = "L2"
        p = "L1"
        v = NestedDictSearch.find(d, k, p, self.get_search_index())
        assert d[p][k] == v

    def test_find_L2_1(self):
        """Find value on layer 2 containing other key/value pairs with a branch on the second layer"""
        d = self.get_test_dict()
        k = "L2_1"
        p = "L1"
        v = NestedDictSearch.find(d, k, p, self.get_search_index())
        assert d[p][k] == v

    def test_find_nonexisting(self):
        """Find key that doesn't exist"""
        d = self.get_test_dict()
        k = "K1"
        p = "L1"
        with pytest.raises(KeyError):
            NestedDictSearch.find(d, k, p, self.get_search_index())

    def test_find_default(self):
        """Find key that doesn't exist but return a default value"""
        d = self.get_test_dict()
        k = "K1"
        default = 10
        p = ""
        v = NestedDictSearch.find(d, k, p, self.get_search_index(), default=default)
        assert default == v

    def test_insert(self):
        """Insert a key/value pair into first existing layer"""
        d = self.get_test_dict()
        k = "U1"
        v = 98
        p = ""
        NestedDictSearch.insert(d, k, v, p)
        idx = self.get_search_index()
        idx.add(k, p)
        o = NestedDictSearch.find(d, k, p, idx)
        assert o == v

    def test_insert_L1(self):
        """Insert a key/value pair into second existing layer"""
        d = self.get_test_dict()
        k = "U1"
        v = 98
        p = "L1"
        NestedDictSearch.insert(d, k, v, p)
        idx = self.get_search_index()
        idx.add(k, p)
        o = NestedDictSearch.find(d, k, p, idx)
        assert o == v

    def test_insert_L2(self):
        """Insert a key/value pair into third existing layer"""
        d = self.get_test_dict()
        k = "U1"
        v = 98
        p = f"L1{SEARCH_SEP}L2"
        NestedDictSearch.insert(d, k, v, p)
        idx = self.get_search_index()
        idx.add(k, p)
        o = NestedDictSearch.find(d, k, p, idx)
        assert o == v

    def test_insert_I2_nested(self):
        """Insert a key/value pair into fourth existing layer, where the same key exists on layer 2"""
        d = self.get_test_dict()
        k = "U1"
        v = 98
        p = f"L1{SEARCH_SEP}L2_1{SEARCH_SEP}I2"
        NestedDictSearch.insert(d, k, v, p)
        idx = self.get_search_index()
        idx.add(k, p)
        o = NestedDictSearch.find(d, k, p, idx)
        assert o == v

    def test_insert_generate(self):
        """Insert a key/value pair into fourth layer, creating three layers along the way"""
        d = self.get_test_dict()
        k = "U1"
        v = 98
        p = f"L1{SEARCH_SEP}L4{SEARCH_SEP}L5{SEARCH_SEP}L6"
        NestedDictSearch.insert(d, k, v, p, create_missing=True)
        idx = self.get_search_index()
        idx.add(k, p)
        o = NestedDictSearch.find(d, k, p, idx)
        assert o == v

    def test_update(self):
        """Update the value of a key"""
        d = self.get_test_dict()
        k = "I1"
        v = 98
        p = f"L1{SEARCH_SEP}L2"
        idx = self.get_search_index()
        NestedDictSearch.update(d, k, v, p, idx)
        o = NestedDictSearch.find(d, k, p, idx)
        assert o == v

    def test_remove_nonexisting(self):
        """Remove a key that doesn't exist"""
        d = self.get_test_dict()
        k = "U1"
        p = ""
        idx = self.get_search_index()
        with pytest.raises(KeyError):
            NestedDictSearch.remove(d, k, p, idx)

    def test_remove_I3(self):
        """Remove last value in layer 1"""
        d = self.get_test_dict()
        k = "I3"
        p = ""
        idx = self.get_search_index()
        NestedDictSearch.remove(d, k, p, idx)
        idx.remove(k, p)
        with pytest.raises(KeyError):
            NestedDictSearch.find(d, k, p, idx)

    def test_remove_L1(self):
        """Remove a value containing other key/value pairs"""
        d = self.get_test_dict()
        k = "L1"
        p = ""
        idx = self.get_search_index()
        NestedDictSearch.remove(d, k, p, idx)
        idx.remove(k, p)
        with pytest.raises(KeyError):
            NestedDictSearch.find(d, k, p, idx)

    def test_remove_I1(self):
        """Remove a value on layer 3"""
        d = self.get_test_dict()
        k = "I1"
        p = f"L1{SEARCH_SEP}L2"
        idx = self.get_search_index()
        NestedDictSearch.remove(d, k, p, idx)
        idx.remove(k, p)
        with pytest.raises(KeyError):
            NestedDictSearch.find(d, k, p, idx)

    def test_remove_I2_nested(self):
        """Remove a key from fourth existing layer, where the same key exists on layer 3"""
        d = self.get_test_dict()
        k = "I2"
        p = f"L1{SEARCH_SEP}L2_1"
        idx = self.get_search_index()
        NestedDictSearch.remove(d, k, p, idx)
        idx.remove(k, p)
        with pytest.raises(KeyError):
            NestedDictSearch.find(d, k, p, idx)


if __name__ == "__main__":
    TestNestedDictSearch().test_insert_L1()
