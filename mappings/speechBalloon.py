class SpeechBalloon:
    """
    Here is the mapping of speech balloon numbers to their names.

    In this url, we can see the name of all speech balloons with a picture:
    https://miiwiki.org/wiki/Speech_Balloon
    """

    decoder = {
        0: "Normal",
        1: "Thought",
        52: "Find Mii",
        53: "Puzzle Swap",
        57: "Bunny",
        58: "Mii Force",
        59: "Flower Town",
        60: "Warrior's Way",
        61: "Streetpass Mansion",
        62: "Ultimate Angler",
        63: "Battleground Z",
        64: "Slot Car Rivals",
        65: "Market Crashers",
        66: "Feed Mii",
        67: "Ninja Launcher",
        68: "Mii Trek",
    }

    def __init__(self, number: int) -> None:
        """
        Returns the speech balloon based on the number.

        Args:
            - number (int): The number representing the speech balloon.

        Returns:
            - str: The name of the speech balloon.
        """
        self.speechBalloon = self.decoder.get(number, "Unknown Speech Balloon")

        if self.speechBalloon == "Unknown Speech Balloon":
            print(f"Warning: Unknown speech balloon number {number}")

    def getSpeechBalloon(self) -> str:
        """
        Get the speech balloon.
        Args:
            - None

        Returns:
            - str: The name of the speech balloon.
        """
        return self.speechBalloon
