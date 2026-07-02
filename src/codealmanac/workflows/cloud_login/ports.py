from typing import Protocol


class BrowserOpener(Protocol):
    def open(self, url: str) -> bool:
        pass
