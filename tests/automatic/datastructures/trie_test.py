from applib.module.datastructures.pure.trie import Trie


def test_trie():
    trie = Trie()
    testData = ["Rem", "Ram", "Fubuki", "Unicorn"]

    print(f"--- Testing Trie ---")

    # Test no duplicate values
    print(f"Adding values to trie")
    for i, label in enumerate(testData):
        trie.add(label, i)
        print(f"[{i}]: {label}")

    print(f"\nPerforming membership tests")
    print(f"R | {convertlist(trie.find("R"))}")
    print(f"Re | {convertlist(trie.find("Re"))}")
    print(f"Rem | {convertlist(trie.find("Rem"))}")
    print(f"r | {convertlist(trie.find("r"))}")
    print(f"Fub | {convertlist(trie.find("Fub"))}")
    print(f"corn | {convertlist(trie.find("corn"))}")
    print(f'"" | {convertlist(trie.find(""))}')

    # Test duplicate values
    print(f"\nAdding duplicate values to trie")
    for i, label in enumerate(testData):
        label = testData[i]
        offset = i + 10
        trie.add(label, offset)
        print(f"[{offset}]: {label}")

    print(f"\nPerforming duplicate membership tests")
    print(f"R | {convertlist(trie.find("R"))}")
    print(f"Re | {convertlist(trie.find("Re"))}")
    print(f"Rem | {convertlist(trie.find("Rem"))}")
    print(f"r | {convertlist(trie.find("r"))}")
    print(f"Fub | {convertlist(trie.find("Fub"))}")
    print(f"corn | {convertlist(trie.find("corn"))}")
    print(f'"" | {convertlist(trie.find(""))}')

    print(f"--- Testing of Trie finished ---")


def convertlist(l: list) -> str:
    return " ~ ".join([f"{e}" for e in l])


if __name__ == "__main__":
    test_trie()
