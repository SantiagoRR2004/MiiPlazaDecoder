class Mii:
    MII_SIZE = 264

    def __init__(self, bytesData: bytes) -> None:
        """
        Initialize Mii object with bytes data

        Args:
            - bytesData (bytes): The raw bytes data of the Mii

        Returns:
            - None
        """
        assert len(bytesData) == self.MII_SIZE, "Invalid Mii size"
        self.bytesData = bytesData
        self.setAll()

    def setAll(self) -> None:
        """
        Set all attributes of the Mii object by decoding the bytes data

        Args:
            - None

        Returns:
            - None
        """
        self.setName()
        self.setCreator()
        self.setCountry()
        self.setSubregion()

    def setName(self) -> None:
        """
        Decode Mii name from bytes 0-19

        There tends to be noise after two null bytes,
        so we stop once we find the first occurrence.

        Args:
            - None

        Returns:
            - None
        """
        nameEnd = self.bytesData[:20].find(b"\x00\x00")

        if nameEnd != -1:
            nameEnd = nameEnd if nameEnd % 2 == 0 else nameEnd + 1
        else:
            nameEnd = 20

        self.name = self.bytesData[:nameEnd].decode("utf-16le").strip("\x00")

    def setCreator(self) -> None:
        """
        Decode creator name from bytes 46-65

        There tends to be noise after two null bytes,
        so we stop once we find the first occurrence.

        Args:
            - None

        Returns:
            - None
        """
        creatorEnd = self.bytesData[46:66].find(b"\x00\x00")

        if creatorEnd != -1:
            creatorEnd = creatorEnd if creatorEnd % 2 == 0 else creatorEnd + 1
        else:
            creatorEnd = 0

        self.creator = (
            self.bytesData[46 : 46 + creatorEnd].decode("utf-16le").strip("\x00")
        )

    def setCountry(self) -> None:
        """
        Decode country from bytes 86-149

        Args:
            - None

        Returns:
            - None
        """
        self.country = self.bytesData[86:150].decode("utf-16le").strip("\x00")

    def setSubregion(self) -> None:
        """
        Decode subregion from bytes 150-213

        Args:
            - None

        Returns:
            - None
        """
        self.subregion = self.bytesData[150:214].decode("utf-16le").strip("\x00")

    def getData(self) -> dict:
        """
        Get Mii data as a dictionary

        Args:
            - None

        Returns:
            - dict: Dictionary containing all Mii attributes
        """
        return {
            "name": self.name,
            "creator": self.creator,
            "country": self.country,
            "subregion": self.subregion,
        }
