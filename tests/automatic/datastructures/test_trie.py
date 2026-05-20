from typing import Any

from applib.module.datastructures.trie import Trie
from applib.module.logging import LoggingManager


def test_trie():
    trie = Trie()
    testData = ["Rem", "Ram", "Fubuki", "Unicorn"]
    logger = LoggingManager()

    logger.info("--- Testing Trie ---")

    # Test no duplicate values
    logger.info("Adding values to trie")
    for i, label in enumerate(testData):
        trie.add(label, i)
        logger.info(f"[{i}]: {label}")

    assert validate_output(trie.find("R"), [("Rem", {0}), ("Ram", {1})])
    assert validate_output(trie.find("Re"), [("Rem", {0})])
    assert validate_output(trie.find("Rem"), [("Rem", {0})])
    assert len(trie.find("r")) == 0
    assert validate_output(trie.find("Fub"), [("Fubuki", {2})])
    assert len(trie.find("corn")) == 0
    assert validate_output(
        trie.find(""), [("Rem", {0}), ("Ram", {1}), ("Fubuki", {2}), ("Unicorn", {3})]
    )

    # Test duplicate values
    logger.info("\nAdding duplicate values to trie")
    for i, label in enumerate(testData):
        label = testData[i]
        offset = i + 10
        trie.add(label, offset)
        logger.info(f"[{offset}]: {label}")

    assert validate_output(trie.find("R"), [("Rem", {0, 10}), ("Ram", {1, 11})])
    assert validate_output(trie.find("Re"), [("Rem", {0, 10})])
    assert validate_output(trie.find("Rem"), [("Rem", {0, 10})])
    assert len(trie.find("r")) == 0
    assert validate_output(trie.find("Fub"), [("Fubuki", {2, 12})])
    assert len(trie.find("corn")) == 0
    assert validate_output(
        trie.find(""),
        [("Rem", {0, 10}), ("Ram", {1, 11}), ("Fubuki", {2, 12}), ("Unicorn", {3, 13})],
    )


def validate_output(
    output: list[tuple[str, set[Any] | None]],
    expected_output: list[tuple[str, set[Any]]],
) -> bool:
    state = True and len(output) == len(expected_output)

    for item in output:
        state = state and item in expected_output
        if not state:
            break
    return state


if __name__ == "__main__":
    test_trie()
