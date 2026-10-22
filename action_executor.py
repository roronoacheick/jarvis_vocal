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


    @staticmethod
    def search_youtube(search_query):
        youtube_search_url = "https://www.youtube.com/results?search_query=" + quote_plus(search_query)
        webbrowser.open(youtube_search_url)

        return f"Recherche Youtube ouverte pour: {search_query}"



    def execute_action(self, tool_name, tool_arguments):
        if tool_name not in self.avaible_actions:
            return f"Action inconnue : {tool_name}"

        action = self.avaible_actions[tool_name]
        return action(**tool_arguments)