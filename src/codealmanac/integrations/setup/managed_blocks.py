CODEALMANAC_START = "<!-- codealmanac:start -->"
CODEALMANAC_END = "<!-- codealmanac:end -->"


def format_managed_block(guide: str) -> str:
    return f"{CODEALMANAC_START}\n{guide.strip()}\n{CODEALMANAC_END}"


def upsert_managed_block(contents: str, block: str) -> str:
    start = contents.find(CODEALMANAC_START)
    end = contents.find(CODEALMANAC_END)
    if start != -1 and end != -1 and end > start:
        after_end = end + len(CODEALMANAC_END)
        return f"{contents[:start]}{block}{contents[after_end:]}"
    separator = "" if contents == "" else "\n" if contents.endswith("\n") else "\n\n"
    return f"{contents}{separator}{block}\n"


def remove_managed_block(contents: str) -> str:
    start = contents.find(CODEALMANAC_START)
    end = contents.find(CODEALMANAC_END)
    if start == -1 or end == -1 or end < start:
        return contents
    after_end = end + len(CODEALMANAC_END)
    return collapse_blank_lines(f"{contents[:start]}{contents[after_end:]}")


def collapse_blank_lines(contents: str) -> str:
    while "\n\n\n" in contents:
        contents = contents.replace("\n\n\n", "\n\n")
    if contents.strip() != "" and contents.endswith("\n\n"):
        contents = contents.rstrip("\n") + "\n"
    return contents.lstrip("\n")
