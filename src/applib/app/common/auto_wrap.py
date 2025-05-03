from re import sub
from typing import Tuple

from qfluentwidgets import TextWrap


class AutoTextWrap(TextWrap):
    @classmethod
    def text_format(cls, text: str, newline_repl: str = "/n") -> str:
        """
        Strip whitespace and newlines in strings.

        Has support for defining newlines which should be kept using ``newline_repl`.

        Parameters
        ----------
        text : str
            Text to process.

        newline_repl : str, optional
            Character which represents a newline character.
            Use in text to force a linebreak, as the newline character `\\n`
            is removed during processing.
            By default "/n".

        Returns
        -------
        str
            The string processed for whitespace characters and newlines.
        """
        clean_str = sub(pattern=r"\s+", repl=" ", string=text).strip()
        return sub(pattern=newline_repl, repl="<br>", string=clean_str)

    @classmethod
    def _wrap_line(
        cls, text: str, width: int, wrap_with: str, once: bool = True
    ) -> Tuple[str, bool]:
        line_buffer = ""
        wrapped_lines = []
        current_width = 0

        for token in cls.tokenizer(text):
            token_width = cls.get_text_width(token)
            if token == " " and current_width == 0:
                continue
            if current_width + token_width <= width:
                line_buffer += token
                current_width += token_width
                if current_width == width:
                    wrapped_lines.append(line_buffer.rstrip())
                    line_buffer = ""
                    current_width = 0
            else:
                if current_width != 0:
                    wrapped_lines.append(line_buffer.rstrip())
                chunks = cls.split_long_token(token, width)
                for chunk in chunks[:-1]:
                    wrapped_lines.append(chunk.rstrip())
                line_buffer = chunks[-1]
                current_width = cls.get_text_width(chunks[-1])

        if current_width != 0:
            wrapped_lines.append(line_buffer.rstrip())
        if once:
            return wrap_with.join([wrapped_lines[0], " ".join(wrapped_lines[1:])]), True
        return wrap_with.join(wrapped_lines), True

    @classmethod
    def wrap(
        cls, text: str, width: int, wrap_with: str = "\n", once: bool = False
    ) -> str:
        """
        Wrap according to string length.

        Parameters
        ----------
        text: str
            The text to be wrapped.

        width: int
            The maximum length of a single line.
            The length of Chinese characters is 2.

        wrap_with : str
            The string to indicate a linebreak.

        once: bool
            Whether to wrap only once.

        Returns
        -------
        wrap_text: str
            Text after auto word wrap process.
        """
        width = int(width)
        if wrap_with == "\n":
            lines = text.splitlines()
        else:
            lines = text.split(wrap_with)

        wrapped_lines = []
        for line in lines:
            line = cls.process_text_whitespace(line)
            if cls.get_text_width(line) > width:
                wrapped_line, is_wrapped = cls._wrap_line(line, width, wrap_with, once)
                wrapped_lines.append(wrapped_line)
                if once:
                    wrapped_lines.append(text[len(wrapped_line) :].rstrip())
                    return "".join(wrapped_lines)
            else:
                wrapped_lines.append(line)
        return wrap_with.join(wrapped_lines)
