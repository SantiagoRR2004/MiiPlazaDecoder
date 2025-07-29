class Outfit:
    """
    Here is the mapping of outfit numbers to their names.

    In this url, we can see the name of all outfits with a picture:
    https://miiwiki.org/wiki/Outfit_(StreetPass_Mii_Plaza)

    They are not in the same order because
    they seem to be ordered by the in-game release date.
    """

    decoder = {
        0: "(None)",
        1: "Mario's Cap",
        2: "Luigi's Cap",
        3: "Toad Hat",
        4: "Bowser Hat",
        5: "Link's Cap",
        6: "Red Pikmin Hat",
        9: "Samus's Helmet",
        10: "Cat Ears",
        11: "Bunny Ears",
        12: "Dog Ears",
        13: "Regal Crown",
        14: "Metroid Hat",
        15: "Kirby Hat",
        16: "Ultimate Helmet",
        19: "Red Ribbon",
        20: "Top Hat",
        21: "Pirate Hat",
        22: "Chef Hat",
        23: "Devil Horns",
        24: "Sunflower",
        25: "Penguin Hat",
        26: "Cheeseburger Hat",
        29: "Piranha Plant",
        30: "Fox Hat",
        32: "Straw Hat",
        33: "Floral Hat",
        34: "Bear Hat",
        35: "Nintendo 3DS",
        38: "Hibiscus",
        39: "Tiny Top Hat",
        40: "Ninja Hood",
        41: "Panda Hat",
        45: "Triforce Hat",
        46: "Magic Hat",
        47: "Yoshi Hat",
        49: "Cake Hat",
        52: "Chomp Hat",
        54: "Epona Hat",
        55: "Daisy's Crown",
        58: "Pink Yoshi Hat",
        59: "Waluigi's Cap",
        61: "Hot Dog Hat",
        62: "NES Hat",
        64: "Blooper Hat",
        65: "Barbara the Bat Wig",
        70: "Dark Lord Helmet",
        71: "Dark Emperor Helmet",
        72: "Prince's Crown",
        73: "Princess's Crown",
        76: "Pixel Mario Hat",
        77: "Super Mushroom Hat",
        78: "1-Up Mushroom Hat",
        79: "Fire Flower",
        80: "Super Star Hat",
        82: "POW Block Hat",
        83: "Goomba Hat",
        85: "Red Shell Hat",
        86: "Spiny Hat",
        88: "Cheep Cheep Hat",
        89: "Wiggler Hat",
        91: "Bowser's Airship Hat",
        92: "Goal Tower Hat",
        94: "Princess Zelda Wig",
        95: "Sheik Mask",
        97: "Rupee Hat",
        101: "Waddle Dee Hat",
        102: "Epic Kirby Hat",
        103: "Prince Fluff Hat",
        104: "Isabelle Hat",
        105: "Tom Nook Hat",
        106: "Dr. Kawashima Hat",
        107: "Devilish Dr. Kawashima Hat",
        108: "Rhythm Monkey Hat",
        109: "Diddy Kong Hat",
        110: "Barrel Hat",
        112: "Wolf O'Donnell Hat",
        113: "Captain Falcon's Helmet",
        116: "Diskun Hat",
        117: "Game Boy Hat",
        118: "Super Famicom Hat",
        120: "Virtual Boy Mask",
        122: "Game Boy Advance Hat",
        123: "GameCube Hat",
        124: "Nintendo DS",
        126: "Spaghetti Hat",
        128: "Sushi Hat",
        129: "Fried Chicken Hat",
        130: "French Fries Hat",
        131: "Baguette Hat",
        133: "Apple Hat",
        135: "Pineapple Hat",
        136: "Caffè Latte Hat",
        137: "Teacup Hat",
        138: "Hockey Mask",
        140: "Cowboy Hat",
        141: "Cow Skull Hat",
        143: "Jack-o'-Lantern Hat",
        144: "Santa Hat",
        145: "Wedding Veil",
        146: "Geisha Wig",
        147: "Frog Hat",
        148: "Elephant Hat",
        149: "Whale Hat",
        150: "Chicken Hat",
        151: "Bird's Nest Hat",
        152: "Lion Hat",
        153: "T. Rex Hat",
        154: "UFO Hat",
        157: "Palm Tree",
        160: "Kingdom Hat",
        161: "Emperor's Crown",
        162: "Flower Bonnet",
        163: "Master Gardener's Crown",
        164: "Smiling Specter Hat",
        165: "Demon King Hat",
        166: "Mii Force Helmet",
        167: "Scout Ship Hat",
        170: "Link Costume",
        171: "Mario Costume",
        172: "Luigi Costume",
        174: "Donkey Kong Suit",
        175: "Tanooki Suit",
        176: "Kitsune Suit",
        180: "Wii U Hat",
        181: "Woolly Yoshi Hat",
        182: "Splatoon Hat",
        183: "Fishing-Boat Hat",
        184: "Guide's Visor",
        185: "Zombie Hat",
        187: "Pirate Costume",
        188: "Chef Costume",
        190: "Football Ball Costume",
        191: "Horror Costume",
        192: "Spartan Armor",
        193: "Cowboy Costume",
        194: "Raceway Hat",
        196: "Stock Market Hat",
        197: "Money Hat",
        198: "Jumbo Beef Hat",
        199: "Epic Banquet Hat",
        201: "Fox Mask",
        203: "Sir Henry Beaksley Hat",
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
