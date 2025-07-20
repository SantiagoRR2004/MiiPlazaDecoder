class Dream:
    decoder = {
        0: "-",
        1: "Live long",
        2: "Get rich",
        3: "Visit outer space",
        4: "Get married",
        5: "Be a hero",
        6: "Be a prince or princess",
        7: "Be a pro athlete",
        8: "Be a wizard or witch",
        9: "Run a company",
        10: "Be a world champion",
        11: "Be a celebrity",
        12: "Be popular",
        13: "(Other)",
        14: "(Secret)",
        15: "Grow up",
        16: "Fly like a bird",
        17: "Master an art",
        18: "Get fit",
        19: "Gain super powers",
    }

    def __init__(self, number: int) -> None:
        """
        Returns the dream based on the number.

        Args:
            - number (int): The number representing the dream.

        Returns:
            - str: The name of the dream.
        """
        self.dream = self.decoder.get(number, None)
        if self.dream is None:
            raise ValueError(f"Invalid dream number: {number}")

    def getDream(self) -> str:
        """
        Get the dream.

        Args:
            - None

        Returns:
            - str: The name of the dream.
        """
        return self.dream
