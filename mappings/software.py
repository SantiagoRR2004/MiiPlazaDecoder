from bs4 import BeautifulSoup
import requests
import json
import os


def titleFromhshop(gameID: str) -> str:
    """
    Get the game name from hshop based on the game ID.

    It will try to find the english name of the game
    by searching for the product code.

    Args:
        - gameID (str): The ID of the game to search for.

    Returns:
        - str: The name of the game if found, otherwise "Unknown Game".
    """
    url = f"https://hshop.erista.me/search/results?q={gameID}&qt=TitleID"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        name = None
        productCode = None
        region = None
        priority = {"north-america": 1, "europe": 2, "world": 3}

        # Get the first result entry
        entry = soup.find("a", class_="list-entry block-link")

        if entry:
            # Find all meta-content blocks
            meta_contents = entry.find_all("div", class_="meta-content")
            for meta in meta_contents:
                spans = meta.find_all("span")
                if len(spans) >= 2:
                    label = spans[1].text.strip()
                    value = spans[0].text.strip()
                    if label == "Product Code":
                        productCode = value
                    elif label == "Title ID":
                        assert value == gameID, "Something is wrong with hShop"

            # Get game name
            base_info = entry.find("div", class_="base-info")
            if base_info:
                game_name_tag = base_info.find("h3", class_="green bold nospace")
                if game_name_tag:
                    name = game_name_tag.text.strip()

            # Get the region
            h4_tags = base_info.find_all("h4")
            for h4_tag in h4_tags:
                spans = h4_tag.find_all("span", class_="green bold")
                if len(spans) >= 2:
                    region = spans[1].text.strip()

        # Try to find name in English
        if productCode:
            # Remove last character to get all regions
            url = f"https://hshop.erista.me/search/results?q={productCode[:-1]}&qt=ProductCode"

            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Get the all the entries
                entries = soup.find_all("a", class_="list-entry block-link")

                for entry in entries:

                    base_info = entry.find("div", class_="base-info")

                    # Get current region
                    if base_info:
                        foundRegion = None

                        h4_tags = base_info.find_all("h4")
                        for h4_tag in h4_tags:
                            spans = h4_tag.find_all("span", class_="green bold")
                            if len(spans) >= 2:
                                foundRegion = spans[1].text.strip()

                        if priority.get(foundRegion, 0) > priority.get(region, 0):
                            region = foundRegion
                            name = base_info.find(
                                "h3", class_="green bold nospace"
                            ).text.strip()

        if name:
            return name

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
    """
    Class to decode software/game names based on their string ID.

    We use the hshop database to get the game names.

    If the game isn't found in the hshop it means the game is
    probably a homebrew game or a system application.
    Here can be found some system applications:
        - https://www.3dbrew.org/wiki/Title_list
        - https://github.com/gamer-boss/3ds-system-files-cia-updates

    We store those names in software.json.

    There is one one game I found that is has the wrong name:
        - 00040000000F9800 魔界王子 devils and realist - 代理王の秘宝
    It seems it is a real game, but the creators of
        - Fast PlayCoin - 300 coins NOW
    gave their game the same ID.
    """

    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    databaseFile = os.path.join(currentDirectory, "hshop.json")
    personalDatabaseFile = os.path.join(currentDirectory, "software.json")

    # Ensure the database file exists
    if not os.path.exists(databaseFile):
        with open(databaseFile, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    # Order software.json
    with open(personalDatabaseFile, "r", encoding="utf-8") as fRead:
        data = json.load(fRead)
        with open(personalDatabaseFile, "w", encoding="utf-8") as fWrite:
            json.dump(
                dict(sorted(data.items())),
                fWrite,
                ensure_ascii=False,
                indent=4,
            )
        del data

    decoder = json.load(open(databaseFile, encoding="utf-8"))
    decoder.update(json.load(open(personalDatabaseFile, encoding="utf-8")))

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
                self.decoder[gameID] = "Unknown Game"
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
