import pytest

from applib.module.datastructures.trie import Trie


@pytest.mark.skip
def test_trie():
    trie = Trie()
    testData = ["Rem", "Ram", "Fubuki", "Unicorn"]

    print("--- Testing Trie ---")

    # Test no duplicate values
    print("Adding values to trie")
    for i, label in enumerate(testData):
        trie.add(label, i)
        print(f"[{i}]: {label}")

    print("\nPerforming membership tests")
    print(f"R | {convertlist(trie.find('R'))}")
    print(f"Re | {convertlist(trie.find('Re'))}")
    print(f"Rem | {convertlist(trie.find('Rem'))}")
    print(f"r | {convertlist(trie.find('r'))}")
    print(f"Fub | {convertlist(trie.find('Fub'))}")
    print(f"corn | {convertlist(trie.find('corn'))}")
    print(f'"" | {convertlist(trie.find(""))}')

    # Test duplicate values
    print("\nAdding duplicate values to trie")
    for i, label in enumerate(testData):
        label = testData[i]
        offset = i + 10
        trie.add(label, offset)
        print(f"[{offset}]: {label}")

    print("\nPerforming duplicate membership tests")
    print(f"R | {convertlist(trie.find('R'))}")
    print(f"Re | {convertlist(trie.find('Re'))}")
    print(f"Rem | {convertlist(trie.find('Rem'))}")
    print(f"r | {convertlist(trie.find('r'))}")
    print(f"Fub | {convertlist(trie.find('Fub'))}")
    print(f"corn | {convertlist(trie.find('corn'))}")
    print(f'"" | {convertlist(trie.find(""))}')

    print("--- Testing of Trie finished ---")


def convertlist(listinput: list) -> str:
    return " ~ ".join([f"{e}" for e in listinput])


if __name__ == "__main__":
    test_trie()
