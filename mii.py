from mappings import Software, Outfit, PreferredPet, Dream, Hobby, Birthday
from datetime import datetime, timedelta, timezone


class Mii:
    """
    Class representing a Mii object.

    Not all the bytes have been decoded yet,
    but here are some that might be missing:

        - The type of dialogue box
        There are 54 values so 6 bits are needed.

        - The information from Mii Maker:
        A mii is 62 bytes as in this url:
        https://www.3dbrew.org/wiki/Mii
        Because we can't fit in here all that data,
        there must be an identifier that links to the CFL_DB.dat

        - The text of the personal message.

        - The gesture of the personal message.
        There are 6 values so 3 bits are needed.

        - Whether the mii has been VIP'd or not.
        I couldn't find this one.

        - Maybe some of the game records.
    """

    MII_SIZE = 264

    unknownBytes = (
        list(range(0, 8))
        + list(range(27, 53))
        + list(range(73, 77))
        + list(range(82, 85))
        + [223, 224]
        + [228]
        + list(range(235, 261))
    )

    unknownBits = [b * 8 + i for b in unknownBytes for i in range(8)]
    unknownBits.remove((238) * 8)  # Premium status

    # The bytes that are always empty
    emptyBytes = (
        [3, 4]
        + [46]
        + [73, 74]
        + [82, 83, 84]
        + [223, 224]
        + [228]
        + [241, 242, 243, 244]
    )
    assert set(emptyBytes).issubset(
        set(unknownBytes)
    ), "Not all emptyBytes are in unknownBytes"

    emptyBits = [
        223,
        231,
        260,
        261,
        262,
        263,
        276,
        283,
        294,
        295,
        311,
        326,
        327,
        342,
        343,
        391,
        402,
        423,
        1881,
        1882,
        1883,
        1884,
        1885,
        1886,
        1887,
        1889,
        1890,
        1891,
        1892,
        1893,
        1894,
        1895,
        1903,
        1906,
        1907,
        1908,
        1909,
        1910,
        1911,
        1927,
        1972,
        1974,
        1975,
        1984,
        1985,
        1986,
        1987,
        1990,
        1991,
        2061,
    ]
    assert set(emptyBits).issubset(
        set(unknownBits)
    ), "Not all emptyBits are in unknownBits"
    # Assert no overlap between bits in empty bytes and emptyBits
    assert {byteIndex * 8 + i for byteIndex in emptyBytes for i in range(8)}.isdisjoint(
        emptyBits
    ), "Some bits in emptyBits fall inside emptyBytes"

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
        self.checkAssumptions()

    def setAll(self) -> None:
        """
        Set all attributes of the Mii object by decoding the bytes data

        Args:
            - None

        Returns:
            - None
        """
        self.setBirthday()
        self.setName()
        self.setCreator()
        self.setDateLastCrossedWith()
        self.setSoftware()
        self.setCountry()
        self.setSubregion()
        self.setNumberCrossedWith()
        self.setStreetPassHits()
        self.setPlazaPopulation()
        self.setOutfit()
        self.setPreferredPet()
        self.setDream()
        self.setHobby()
        self.setPremium()
        self.setMACOUI()

    def setBirthday(self) -> None:
        """
        Decode the birthday from byte 5 and the last
        two bits of byte 6.

        Args:
            - None

        Returns:
            - None
        """
        self.birthday = Birthday(self.bytesData[5:7]).getBirthday()

    def setName(self) -> None:
        """
        Decode Mii name from bytes 7-26

        The name is stored in UTF-16LE format
        and it ends with an empty character
        (two null bytes).

        Args:
            - None

        Returns:
            - None
        """
        name = ""
        currentPosition = 7

        while (
            self.bytesData[currentPosition : currentPosition + 2] != b"\x00\x00"
            and currentPosition < 27
        ):
            byte = self.bytesData[currentPosition : currentPosition + 2]
            name += byte.decode("utf-16le")
            currentPosition += 2

        self.name = name

    def setCreator(self) -> None:
        """
        Decode creator name from bytes 53-72

        The creator name is stored in UTF-16LE format
        and it ends with an empty character
        (two null bytes).

        Args:
            - None

        Returns:
            - None
        """
        creator = ""
        currentPosition = 53

        while (
            self.bytesData[currentPosition : currentPosition + 2] != b"\x00\x00"
            and currentPosition < 73
        ):
            byte = self.bytesData[currentPosition : currentPosition + 2]
            creator += byte.decode("utf-16le")
            currentPosition += 2

        self.creator = creator

    def setDateLastCrossedWith(self) -> None:
        """
        Decode the date of last crossed with from bytes 77-81

        It is stored as a timestamp in milliseconds, with the
        bytes reversed and the date adjusted by -1 day and +30 years.

        Args:
            - None

        Returns:
            - None
        """
        timestampMs = int.from_bytes(
            self.bytesData[77:82][::-1], byteorder="big", signed=False
        )

        rawDatetime = datetime.fromtimestamp(timestampMs / 1000, tz=timezone.utc)

        adjustedDatetime = rawDatetime - timedelta(days=1)
        adjustedDatetime = adjustedDatetime.replace(year=adjustedDatetime.year + 30)

        self.dateLastCrossedWith = adjustedDatetime

    def setSoftware(self) -> None:
        """
        Decode last software used from bytes 85-93

        For some reason, the bytes are reversed,
        so we reverse them to get the correct TitleID.

        Args:
            - None

        Returns:
            - None
        """
        TitleID = ""
        for c in reversed(self.bytesData[85:93]):
            TitleID += format(c, "02X")

        self.gameID = TitleID
        self.gameName = Software(self.gameID).getGameName()

    def setCountry(self) -> None:
        """
        Decode country from bytes 93-156

        Args:
            - None

        Returns:
            - None
        """
        self.country = self.bytesData[93:157].decode("utf-16le").strip("\x00")

    def setSubregion(self) -> None:
        """
        Decode subregion from bytes 157-220

        Args:
            - None

        Returns:
            - None
        """
        self.subregion = self.bytesData[157:221].decode("utf-16le").strip("\x00")

    def setNumberCrossedWith(self) -> None:
        """
        Decode the number of times crossed
        with this Mii from bytes 221-223

        This has only been checked up to 55,
        so if it give a value greater than that,
        check that it is accurate.

        Args:
            - None

        Returns:
            - None
        """
        self.nCrossedWith = int.from_bytes(self.bytesData[221:223], byteorder="little")
        if self.nCrossedWith > 55:
            print(
                "Warning: Number of times crossed with this Mii is greater than 55. "
                f"Check if this value is accurate. {self.name} has been crossed {self.nCrossedWith} times. "
                "Please report this as an issue to the repository."
            )

    def setStreetPassHits(self) -> None:
        """
        Set the number of StreetPass hits for this Mii
        This is stored in bytes 225-227.

        This has been checked up to 33630.

        Args:
            - None

        Returns:
            - None
        """
        self.streetPassHits = int.from_bytes(
            self.bytesData[225:227], byteorder="little"
        )

    def setPlazaPopulation(self) -> None:
        """
        Set the plaza population from bytes 229-231.

        The maximum value possible is 3000
        and it has been checked up to that value.

        Args:
            - None

        Returns:
            - None
        """
        self.plazaPopulation = int.from_bytes(
            self.bytesData[229:231], byteorder="little"
        )

    def setOutfit(self) -> None:
        """
        Set the outfit from byte 231.

        Args:
            - None

        Returns:
            - None
        """
        self.outfit = Outfit(self.bytesData[231]).getOutfit()

        if self.outfit == "Unknown Outfit":
            print(
                f"Name: {self.name}",
                f"Creator: {self.creator}",
            )

    def setPreferredPet(self) -> None:
        """
        Set the preferred pet from byte 232.

        Args:
            - None

        Returns:
            - None
        """
        self.preferredPet = PreferredPet(self.bytesData[232]).getPet()

    def setDream(self) -> None:
        """
        Set the dream from byte 233.

        Args:
            - None

        Returns:
            - None
        """
        self.dream = Dream(self.bytesData[233]).getDream()

    def setHobby(self) -> None:
        """
        Set the hobby from byte 234.

        Args:
            - None

        Returns:
            - None
        """
        self.hobby = Hobby(self.bytesData[234]).getHobby()

    def setPremium(self) -> None:
        """
        Set the premium status from first
        bit of byte 238.

        If the bit is set, the Mii has paid
        for the DLC.

        Args:
            - None

        Returns:
            - None
        """
        self.premium = bool((self.bytesData[238] >> 0) & 1)

    def setMACOUI(self) -> None:
        """
        Set the MAC OUI from bytes 261-263.

        The OUI is the first 3 bytes of the MAC address.
        It is used to identify the manufacturer of the device.
        In this case, they are all Nintendo devices.

        Args:
            - None

        Returns:
            - None
        """
        self.macOUI = ":".join(f"{b:02X}" for b in self.bytesData[261:264])

    def checkAssumptions(self) -> None:
        """
        Check assumptions about the Mii data.

        Args:
            - None

        Returns:
            - None
        """
        self.checkEmptyBytes()
        self.checkEmptyBits()

    def checkEmptyBytes(self) -> None:
        """
        Check if all the empty bytes are indeed empty.

        If they are not, please report it as an issue.
        It means that there could be data stored in those bytes.

        Args:
            - None

        Returns:
            - None
        """
        for byte in self.emptyBytes:
            assert (
                self.bytesData[byte] == 0
            ), f"Byte {byte} is not empty in Mii {self.name}"

    def checkEmptyBits(self) -> None:
        """
        Check if all the empty bits are indeed empty.

        If they are not, please report it as an issue.
        It means that there could be data stored in those bits.

        Args:
            - None

        Returns:
            - None
        """
        for bit in self.emptyBits:
            byteIndex = bit // 8
            bitIndex = bit % 8
            assert (
                self.bytesData[byteIndex] >> bitIndex
            ) & 1 == 0, f"Bit {bit} is not empty in Mii {self.name}"

    def getData(self) -> dict:
        """
        Get Mii data as a dictionary

        Args:
            - None

        Returns:
            - dict: Dictionary containing all Mii attributes
        """
        return {
            "Birthday": self.birthday,
            "Name": self.name,
            "Creator": self.creator,
            "DateLastCrossedWith": self.dateLastCrossedWith,
            "GameID": self.gameID,
            "GameName": self.gameName,
            "Country": self.country,
            "Subregion": self.subregion,
            "NumberCrossedWith": self.nCrossedWith,
            "StreetPassHits": self.streetPassHits,
            "PlazaPopulation": self.plazaPopulation,
            "PreferredPet": self.preferredPet,
            "Outfit": self.outfit,
            "Dream": self.dream,
            "Hobby": self.hobby,
            "Premium": self.premium,
            "MAC_OUI": self.macOUI,
        }

    def getUnkownBytes(self) -> list:
        """
        Get the unknown bytes of the Mii

        Args:
            - None

        Returns:
            - list: List of unknown bytes
        """
        toret = {"Name": self.name, "Creator": self.creator}
        toret.update({i: self.bytesData[i] for i in self.unknownBytes})
        return toret

    def getUnknownBits(self) -> dict:
        """
        Get the unknown bits of the Mii

        Args:
            - None

        Returns:
            - dict: Dictionary of unknown bits
        """
        toret = {"Name": self.name, "Creator": self.creator}
        for i in self.unknownBits:
            toret[i] = (self.bytesData[i // 8] >> (i % 8)) & 1
        return toret
