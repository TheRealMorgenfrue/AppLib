def decodeInput(input: str | bytes, encoding: str = "utf-8") -> str:
    if isinstance(input, str):
        return input
    return input.decode(encoding=encoding, errors="ignore")
