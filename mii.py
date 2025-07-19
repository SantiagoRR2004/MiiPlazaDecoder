from mappings import PreferredPet


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
        self.setSoftware()
        self.setCountry()
        self.setSubregion()
        self.setNumberCrossedWith()
        self.setStreetPassHits()
        self.setPlazaPopulation()
        self.setPreferredPet()

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

    def setSoftware(self) -> None:
        """
        Decode last software used from bytes 78-86

        For some reason, the bytes are reversed,
        so we reverse them to get the correct TitleID.

        Args:
            - None

        Returns:
            - None
        """
        TitleID = ""
        for c in reversed(self.bytesData[78:86]):
            TitleID += format(c, "02X")

        self.gameID = TitleID

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

    def setNumberCrossedWith(self) -> None:
        """
        Decode the number of times crossed
        with this Mii from bytes 214-216

        This has only been checked up to 35,
        so if it give a value greater than that,
        check that it is accurate.

        Args:
            - None

        Returns:
            - None
        """
        self.nCrossedWith = int.from_bytes(self.bytesData[214:216], byteorder="little")
        if self.nCrossedWith > 35:
            print(
                "Warning: Number of times crossed with this Mii is greater than 35. "
                f"Check if this value is accurate. {self.name} has been crossed {self.nCrossedWith} times."
                "Please report this as an issue to the repository."
            )

    def setStreetPassHits(self) -> None:
        """
        Set the number of StreetPass hits for this Mii
        This is stored in bytes 218-220.

        This has been checked up to 33630.

        Args:
            - None

        Returns:
            - None
        """
        self.streetPassHits = int.from_bytes(
            self.bytesData[218:220], byteorder="little"
        )

    def setPlazaPopulation(self) -> None:
        """
        Set the plaza population from bytes 222-224.

        The maximum value possible is 3000
        and it has been checked up to that value.

        Args:
            - None

        Returns:
            - None
        """
        self.plazaPopulation = int.from_bytes(
            self.bytesData[222:224], byteorder="little"
        )

    def setPreferredPet(self) -> None:
        """
        Set the preferred pet from byte 225.

        Args:
            - None

        Returns:
            - None
        """
        self.preferredPet = PreferredPet(self.bytesData[225]).getPet()

    def getData(self) -> dict:
        """
        Get Mii data as a dictionary

        Args:
            - None

        Returns:
            - dict: Dictionary containing all Mii attributes
        """
        return {
            "Name": self.name,
            "Creator": self.creator,
            "GameID": self.gameID,
            "Country": self.country,
            "Subregion": self.subregion,
            "NumberCrossedWith": self.nCrossedWith,
            "StreetPassHits": self.streetPassHits,
            "PlazaPopulation": self.plazaPopulation,
            "PreferredPet": self.preferredPet,
        }
