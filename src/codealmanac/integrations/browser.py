import webbrowser


class WebBrowserOpener:
    def open(self, url: str) -> bool:
        return webbrowser.open(url)
