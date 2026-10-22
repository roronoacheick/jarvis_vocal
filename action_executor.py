import webbrowser
from urllib.parse import quote_plus


class ActionExecutor:
    def __init__(self):
        self.avaible_actions ={
            "open_website": self.open_website,
            "search_youtube": self.search_youtube,
        }


    @staticmethod
    def open_website(url):
        if not url.starswith("https://"):
            return f"Action refusée : l'URL doit commencer par https:// (reçu : {url})"

        webbrowser.open(url)
        return f"Site ouvert : {url}"