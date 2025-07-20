from bs4 import BeautifulSoup
import requests
import json
import os


def titleFromhshop(gameID: str) -> str:
    url = f"https://hshop.erista.me/search/results?q={gameID}&qt=TitleID"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        base_info = soup.find("div", class_="base-info")
        if base_info:
            game_name_tag = base_info.find("h3", class_="green bold nospace")
            if game_name_tag:
                return game_name_tag.text.strip()
    return "Unknown Game"


def updateDatabase(filePath: str, gameName: str, gameID: str) -> None:
    """
    Update the hshop database with a new game name.

    Args:
        - filePath (str): Path to the hshop.json file.
        - gameName (str): The name of the game to add.
        - gameID (str): The ID of the game to add.

    Returns:
        - None
    """
    with open(filePath, "r", encoding="utf-8") as f:
        data = json.load(f)

    data[gameID] = gameName

    # Order the keys alphabetically
    data = dict(sorted(data.items()))

    with open(filePath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class Software:
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    databaseFile = os.path.join(currentDirectory, "hshop.json")

    # Ensure the database file exists
    if not os.path.exists(databaseFile):
        with open(databaseFile, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    decoder = json.load(open(databaseFile))

    def __init__(self, gameID: str) -> None:
        """
        Returns the game name based on the string ID.

        Args:
            - gameID (str): The string ID representing the game.

        Returns:
            - str: The name of the game.
        """
        self.gameName = self.decoder.get(gameID, None)
        if self.gameName is None:
            self.gameName = titleFromhshop(gameID)
            if self.gameName == "Unknown Game":
                print(f"Invalid game ID: {gameID}")
            else:
                updateDatabase(self.databaseFile, self.gameName, gameID)
                self.decoder[gameID] = self.gameName

    def getGameName(self) -> str:
        """
        Get the game name.

        Args:
            - None

        Returns:
            - str: The name of the game.
        """
        return self.gameName
