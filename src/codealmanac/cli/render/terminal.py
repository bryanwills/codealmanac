import shlex
import shutil
import sys


def write_line(line: str) -> None:
    sys.stdout.write(f"{line}\n")


def visible_length(value: str) -> int:
    count = 0
    in_escape = False
    for character in value:
        if character == "\x1b":
            in_escape = True
            continue
        if in_escape:
            if character == "m":
                in_escape = False
            continue
        count += 1
    return count


def terminal_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns


def wrap_with_prefixes(
    text: str,
    first_prefix: str,
    next_prefix: str,
    width: int,
) -> tuple[str, ...]:
    words = tuple(word for word in text.split(" ") if len(word) > 0)
    if len(words) == 0:
        return (first_prefix,)
    lines: list[str] = []
    prefix = first_prefix
    line = prefix
    has_word = False
    for word in words:
        candidate = f"{line} {word}" if has_word else f"{prefix}{word}"
        if has_word and visible_length(candidate) > width:
            lines.append(line)
            prefix = next_prefix
            line = f"{prefix}{word}"
            has_word = True
            continue
        line = candidate
        has_word = True
    lines.append(line)
    return tuple(lines)


def card_row(content: str, width: int, border: str, reset: str) -> str:
    padding = max(0, width - visible_length(content))
    return f"{border}│{reset}{content}{' ' * padding}{border}│{reset}"


def card_right_row(content: str, width: int, border: str, reset: str) -> str:
    padding = max(0, width - visible_length(content) - 2)
    return f"{border}│{reset}{' ' * padding}{content}  {border}│{reset}"


def card_center_row(content: str, width: int, border: str, reset: str) -> str:
    visible = visible_length(content)
    left = max(0, (width - visible) // 2)
    right = max(0, width - visible - left)
    return f"{border}│{reset}{' ' * left}{content}{' ' * right}{border}│{reset}"


def shell_command(command: tuple[str, ...]) -> str:
    return shlex.join(command)
