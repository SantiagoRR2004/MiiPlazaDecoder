from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import xml.etree.ElementTree as ET
from selenium import webdriver
from bs4 import BeautifulSoup
import platformdirs
import requests
import zipfile
import json
import time
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


def getDatabase(filePath: str) -> dict:
    """
    Get the database from the given file path.

    Args:
        - filePath (str): The path to the database file.

    Returns:
        - dict: The database as a dictionary.
    """
    # Ensure it exists
    if not os.path.exists(filePath):
        with open(filePath, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    with open(filePath, "r", encoding="utf-8") as fRead:
        data = json.load(fRead)

    # Sort the data by keys
    data = dict(sorted(data.items()))

    with open(filePath, "w", encoding="utf-8") as fWrite:
        json.dump(data, fWrite, ensure_ascii=False, indent=4)

    return data


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


def getDatomatic() -> dict:
    """
    Get the dictionary of DS games from the datomatic database.

    The datomatic database is used to link the game IDs
    to the ID of the game in English.

    This database is not used directly because the names
    have the region in them.

    There might be more games here than in the dstdb.

    Args:
        - None

    Returns:
        - dict: A dictionary with game IDs as keys and original game IDs as values.
    """
    url = "https://datomatic.no-intro.org/index.php?page=download&op=dat&s=28"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=chrome_options, service=service)

    driver.get(url)

    # Wait for it to load
    time.sleep(4)

    # Find and click the "Prepare" button
    button = driver.find_element(
        By.XPATH, "//input[@type='submit' and @value='Prepare']"
    )
    button.click()

    # Wait for redirection or further action
    time.sleep(5)

    button = driver.find_element(
        By.XPATH, "//input[@type='submit' and @value='Download!!']"
    )
    button.click()

    time.sleep(3)

    # Close the browser
    driver.quit()

    downloadsPath = platformdirs.user_downloads_dir()
    filePath = os.path.join(
        downloadsPath,
        "Nintendo - Nintendo DS (Decrypted) (20250721-143924).zip",
    )

    # Read the only file inside the ZIP
    with zipfile.ZipFile(filePath, "r") as zip_ref:
        file_names = zip_ref.namelist()

        if len(file_names) != 1:
            raise ValueError("Expected exactly one file in the ZIP archive.")

        internal_file_name = file_names[0]

        # Read the file's data (as bytes)
        data = zip_ref.read(internal_file_name)

    # Delete the ZIP file
    os.remove(filePath)

    root = ET.fromstring(data.decode("utf-8"))

    nameChanger = {}

    idMap = {
        child.attrib["id"]: child
        for child in root
        if child.tag == "game" and "id" in child.attrib
    }

    for child in root:
        if child.tag == "game":
            if child.attrib.get("cloneofid"):

                serial = child.find("rom").get("serial")

                if serial:

                    currentID = serial.encode("utf-8").hex().upper()

                    ogID = (
                        idMap[child.attrib["cloneofid"]]
                        .find("rom")
                        .get("serial")
                        .encode("utf-8")
                        .hex()
                        .upper()
                    )

                nameChanger[currentID] = ogID

    return nameChanger


def getDSGames() -> dict:
    """
    Get the dictionary of DS games.

    The hShop seems to have 3DS and DSiWare games,
    but no DS games. Because we trust the hSHop more,
    we only use this when we haven't found the game.

    We keep the database downloaded.

    Args:
        - None

    Returns:
        - dict: A dictionary with game IDs as keys and game names as values.
    """
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    databaseFile = os.path.join(currentDirectory, "dstdb.json")

    if not os.path.exists(databaseFile):
        url = "https://www.gametdb.com/dstdb.txt?LANG=ORIG"
        data = {}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        }  # Pretend to be human
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            textContent = response.text.strip()

            # First line is not a game
            games = textContent.split("\n")[1:]

            for game in games:
                asciiID, title = game.split(" = ")

                # Clean the variables
                asciiID = asciiID.strip()
                title = title.strip()

                # All DS games begin with 00048000 or 0048004
                # so we will need to check it later
                hexID = asciiID.encode("utf-8").hex().upper()

                data[hexID] = title

            # Standardize names
            for key, value in getDatomatic().items():
                if data.get(key):
                    data[key] = data[value]

            # Sort by ID
            data = dict(sorted(data.items()))

            with open(databaseFile, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        else:
            print(f"Failed to fetch file: {response.status_code}")

    return getDatabase(databaseFile)


class Software:
    """
    Class to decode software/game names based on their string ID.

    We use 4 databases:

        - hshop.json
            Stores the games already searched for in the hShop.
            If the game isn't found in the hshop it means the game is
            probably a homebrew game, a system application or a DS game
            Here can be found some system applications:
                - https://www.3dbrew.org/wiki/Title_list
                - https://github.com/gamer-boss/3ds-system-files-cia-updates

        - dstdb.json
            Stores all DS games. Less trusted than hshop so it is
            only used as a last resort.

        - dsLocal.json
            Stores software that couldn't be found on the hShop
            and found on dstdb. We store them so we don't try to
            search hShop again.

        - software.json
            Stores software not found anywhere else.
            They tend to be system applications and homebrew.

    There is one one game I found that is has the wrong name:
        - 00040000000F9800 魔界王子 devils and realist - 代理王の秘宝
    It seems it is a real game, but the creators of
        - Fast PlayCoin - 300 coins NOW
    gave their game the same ID.
    """

    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    databaseFile = os.path.join(currentDirectory, "hshop.json")
    personalDatabaseFile = os.path.join(currentDirectory, "software.json")
    localDSFile = os.path.join(currentDirectory, "dsLocal.json")

    decoder = getDatabase(databaseFile)
    decoder.update(getDatabase(personalDatabaseFile))
    decoder.update(getDatabase(localDSFile))
    decoderDS = getDSGames()

    def __init__(self, gameID: str) -> None:
        """
        Returns the game name based on the string ID.

        Args:
            - gameID (str): The string ID representing the game.

        Returns:
            - str: The name of the game.
        """
        assert len(gameID) == 16
        self.gameName = self.decoder.get(gameID, None)
        if self.gameName is None:

            # Try to find it in the hShop
            self.gameName = titleFromhshop(gameID)

            if self.gameName == "Unknown Game":

                # Try to find in dstbd
                self.gameName = self.decoderDS.get(gameID[-8:], "Unknown Game")
                if self.gameName == "Unknown Game":
                    print(f"Unknown game ID: {gameID}")
                else:
                    updateDatabase(self.localDSFile, self.gameName, gameID)

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
