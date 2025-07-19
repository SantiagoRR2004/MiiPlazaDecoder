class Outfit:
    decoder = {
        0: "(None)",
        1: "Mario's Cap",
        2: "Luigi's Cap",
        5: "Link's Cap",
        6: "Red Pikmin Hat",
        10: "Cat Ears",
        11: "Bunny Ears",
        13: "Regal Crown",
        14: "Metroid Hat",
        15: "Kirby Hat",
        21: "Pirate Hat",
        23: "Devil Horns",
        24: "Sunflower",
        25: "Penguin Hat",
        32: "Straw Hat",
        34: "Bear Hat",
        41: "Panda Hat",
        49: "Cake Hat",
        62: "NES Hat",
        65: "Barbara the Bat Wig",
        73: "Princess's Crown",
        76: "Pixel Mario Hat",
        78: "1-Up Mushroom Hat",
        80: "Super Star Hat",
        88: "Cheep Cheep Hat",
        105: "Tom Nook Hat",
        113: "Captain Falcon's Helmet",
        116: "Diskun Hat",
        123: "GameCube Hat",
        128: "Sushi Hat",
        133: "Apple Hat",
        137: "Teacup Hat",
        144: "Santa Hat",
        146: "Geisha Wig",
        152: "Lion Hat",
        170: "Link Costume",
        191: "Horror Costume",
        193: "Cowboy Costume",
        197: "Money Hat",
        199: "Epic Banquet Hat",
    }

    def __init__(self, number: int) -> None:
        """
        Returns the outfit based on the number.

        Args:
            - number (int): The number representing the outfit.

        Returns:
            - str: The name of the outfit.
        """
        self.outfit = self.decoder.get(number, "Unknown Outfit")

    def getOutfit(self) -> str:
        """
        Get the outfit.

        Args:
            - None

        Returns:
            - str: The name of the outfit.
        """
        return self.outfit
