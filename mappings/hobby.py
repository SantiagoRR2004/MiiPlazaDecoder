class Hobby:
    decoder = {
        0: "-",
        1: "Drawing",
        2: "Playing sports",
        3: "Reading",
        4: "Taking photos",
        5: "Keeping pets",
        6: "Dancing",
        7: "Listening to music",
        8: "Watching films",
        9: "Using the internet",
        10: "Video games",
        11: "Cooking",
        12: "Travelling",
        13: "The outdoors",
        14 : "Fishing",
        15: "Going for drives",
        16: "Shopping",
        17: "(Other)",
        18: "(Secret)",
        19: "Eating",
        20: "Sleeping",
        21: "Chatting",
        22: "Fashion",
        23: "Studying",
        24: "Helping others",
        25: "Parties",
        26: "Making money",
        27: "Cleaning",
    }

    def __init__(self, number: int) -> None:
        """
        Returns the hobby based on the number.

        Args:
            - number (int): The number representing the hobby.

        Returns:
            - str: The name of the hobby.
        """
        self.hobby = self.decoder.get(number, None)
        if self.hobby is None:
            raise ValueError(f"Invalid hobby number: {number}")

    def getHobby(self) -> str:
        """
        Get the hobby.

        Args:
            - None

        Returns:
            - str: The name of the hobby.
        """
        return self.hobby
