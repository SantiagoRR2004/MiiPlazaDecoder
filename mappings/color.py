class Color:
    decoder = {
        0: "Red",
        1: "Orange",
        2: "Yellow",
        3: "Green",
        4: "Light Green",
        5: "Blue",
        6: "Light Blue",
        7: "Pink",
        8: "Purple",
        9: "Brown",
        10: "White",
        11: "Black",
    }

    def __init__(self, byteData: int) -> None:
        """
        Decode the color from the middle bits
        00XXXX00 of one byte.

        Args:
            - byteData (int): The byte containing the color data.

        Returns:
            - None
        """
        colorBits = (byteData >> 2) & 0x0F
        self.color = self.decoder.get(colorBits, None)
        if self.color is None:
            raise ValueError(f"Invalid color bits: {byteData}")

    def getColor(self) -> str:
        """
        Get the decoded color.

        Args:
            - None

        Returns:
            - str: The decoded color.
        """
        return self.color
