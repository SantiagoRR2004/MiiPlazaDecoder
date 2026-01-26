from mappings import Expression, Outfit, SpeechBalloon
from typing import Optional
from grapher import Grapher
from datetime import date
import pandas as pd
import mii


class MiiPlaza:
    """
    There is more information in the Mii Plaza savefile
    that has not been decoded yet.

    Here is a good reference:
    https://www.reddit.com/r/3dshacks/comments/4c5rcp/streetpass_mii_plaza_puzzle_swap_unlock_all/
    https://github.com/marcrobledo/savegame-editors/blob/master/streetpass-mii-plaza/streetpass-mii-plaza.js
    """

    MII_PLAZA_SIZE = 393216

    def __init__(self, bytesData: bytes) -> None:
        """
        Initialize MiiPlaza object with bytes data

        Args:
            - bytesData (bytes): The raw bytes data of the Mii

        Returns:
            - None
        """
        assert len(bytesData) == self.MII_PLAZA_SIZE, "Invalid Mii Plaza size"
        self.bytesData = bytesData
        self.setAll()

    def setAll(self) -> None:
        """
        Set all attributes of the Mii Plaza object by decoding the bytes data

        Args:
            - None

        Returns:
            - None
        """
        self.setBirthday()
        self.setMiis()
        self.setStreetPassTags()
        self.setOutfit()
        self.setGreeting()
        self.setNumberOfTickets()
        self.setFantasticRatings()
        self.setGreetingExpression()
        self.setBalloon()

    def setBirthday(self) -> None:
        """
        Decode the birthday from byte 28 and the last
        two bits of byte 29.

        The way the birthday is encoded is very strange,
        it also seems that it is ready to have no day or month,
        while only no day and month is possible.

        The last 4 bits of byte 28 are used for the month.
        It doesn't use the even values and goes by adding 2.
        Because it starts at 2, we can only have 7 months
        before having to reset to 0:
            2 -> January
            4 -> February
            6 -> March
            8 -> April
            10 -> May
            12 -> June
            14 -> July
            0 -> August
            2 -> September
            4 -> October
            6 -> November
            8 -> December

        The way to differentiate between when it is reset is
        that the first 4 bits of byte 28 are even for the first
        7 months, and odd for the last 5 months.

        The day of the month isn't more simple. Using the first 4
        bits of byte 28,the first of the month is 2 or 3
        (depending on the month), and it goes by adding 2.
        When it reaches the max (14-15), it resets to 0 or 1 and
        add 1 to the last two bits of byte 29.

        This means the last two bits of byte 29 are which set of
        8 days of the month it is:
            0 -> days 1-7
            1 -> days 8-15
            2 -> days 16-23
            3 -> days 24-31

        Args:
            - None

        Returns:
            - None
        """
        dayBits = (self.bytesData[28] >> 4) & 0x0F
        monthBits = self.bytesData[28] & 0x0F

        if dayBits % 2 == 0:
            # Even, first set of months
            month = monthBits // 2
        else:
            # Odd, second set of months
            month = (monthBits // 2) + 8

        day = dayBits // 2 + (8 * (self.bytesData[29] & 0x03))

        self.birthday: Optional[date] = None

        if not (day == 0 and month == 0):
            # Leap year close to 1970 (Unix 0 time)
            self.birthday = date(month=month, day=day, year=1968)

    def setMiis(self) -> None:
        """
        Set all Mii attributes by decoding the bytes data
        from bytes 14154-278153.

        At most 1000 Miis (264 bytes each) are stored. If there are more,
        they are replaced in the same order except
        the VIPs, which are not replaced.

        TODO Something to note is that the last 26 bytes of the
        last Mii, seem not to be about the Mii itself.
        The number of streetpass tags overlap with these bytes,
        which means that these bytes should not be accounted for
        decoding the Mii. However, the MAC OUI is stored there,
        and with the final Mii is a valid address.

        Args:
            - None

        Returns:
            - None
        """
        miis = []
        pos = 14154

        while self.bytesData[pos] != 0 and len(miis) < 1000:
            miiData = self.bytesData[pos : pos + mii.Mii.MII_SIZE]
            miis.append(mii.Mii(miiData))
            pos += mii.Mii.MII_SIZE

        self.miis: list[mii.Mii] = miis

    def setStreetPassTags(self) -> None:
        """
        Decode the streetPass tags from bytes 278128-278131

        Args:
            - None

        Returns:
            - None
        """
        self.streetPassTags = int.from_bytes(
            self.bytesData[278128:278132], byteorder="little"
        )

    def setOutfit(self) -> None:
        """
        Set the outfit from byte 278134.

        Args:
            - None

        Returns:
            - None
        """
        self.outfit = Outfit(self.bytesData[278134]).getOutfit()

        if self.outfit == "Unknown Outfit":
            print("Current main Mii Plaza outfit is unknown.")

    def setGreeting(self) -> None:
        """
        Decode the greeting from bytes 278144-278175

        Args:
            - None

        Returns:
            - None
        """
        greeting = ""
        currentPosition = 278144

        while (
            self.bytesData[currentPosition : currentPosition + 2] != b"\x00\x00"
            and currentPosition < 278176
        ):
            byte = self.bytesData[currentPosition : currentPosition + 2]
            greeting += byte.decode("utf-16le")
            currentPosition += 2

        self.greeting = greeting

    def setNumberOfTickets(self) -> None:
        """
        Decode the number of tickets from bytes 373606-373607

        Args:
            - None

        Returns:
            - None
        """
        self.nTickets = int.from_bytes(
            self.bytesData[373606:373608], byteorder="little"
        )

    def setFantasticRatings(self) -> None:
        """
        Decode the fantastic ratings from bytes 373974-373975

        Args:
            - None

        Returns:
            - None
        """
        self.fantasticRatings = int.from_bytes(
            self.bytesData[373974:373976], byteorder="little"
        )

    def setGreetingExpression(self) -> None:
        """
        Decode the greeting expression from byte 374008

        Args:
            - None

        Returns:
            - None
        """
        self.greetingExpression = Expression(self.bytesData[374008]).getExpression()

    def setBalloon(self) -> None:
        """
        Decode the balloon from byte 376849

        Args:
            - None

        Returns:
            - None
        """
        self.balloon = SpeechBalloon(self.bytesData[376849]).getSpeechBalloon()

    def getMiiData(self) -> pd.DataFrame:
        """
        Get Mii data as a pandas DataFrame

        Args:
            - None

        Returns:
            - pd.DataFrame: DataFrame containing Mii names and creators
        """
        data = [mii.getData() for mii in self.miis]
        return pd.DataFrame(data)

    def getMiiUnknownBytes(self) -> pd.DataFrame:
        """
        Get Mii unknown bytes as a pandas DataFrame

        Args:
            - None

        Returns:
            - pd.DataFrame: DataFrame containing Mii names and unknown bytes
        """
        data = [mii.getUnkownBytes() for mii in self.miis]
        return pd.DataFrame(data)

    def getMiiUnknownBits(self) -> pd.DataFrame:
        """
        Get Mii unknown bits as a pandas DataFrame

        Args:
            - None

        Returns:
            - pd.DataFrame: DataFrame containing Mii names and unknown bits
        """
        data = [mii.getUnknownBits() for mii in self.miis]
        return pd.DataFrame(data)

    def showGeneralData(self) -> None:
        """
        Show general Mii Plaza data

        Args:
            - None

        Returns:
            - None
        """
        print(
            self.birthday.strftime("Birthday Date: %B %-d")
            if self.birthday
            else "Birthday Date: Not set"
        )
        print(f"Number of StreetPass Tags: {self.streetPassTags}")
        print(f"Outfit: {self.outfit}")
        print(f"Greeting: {self.greeting}")
        print(f"Number of Tickets: {self.nTickets}")
        print(f"Fantastic Ratings: {self.fantasticRatings}")
        print(f"Greeting Expression: {self.greetingExpression}")
        print(f"Speech Balloon: {self.balloon}")

    def findPossibleBits(self, classifier: pd.DataFrame, nBits: int) -> list:
        """
        This is to help find where possible characteristics are
        stored in the Mii data.

        The classifier should have a column named 'Name',
        another column named 'Creator',
        and the final one to have the value of the characteristic.

        We will find all the nBits bits that are together that
        have different values for each of the values of the characteristic.

        Args:
            - classifier (pd.DataFrame): DataFrame containing classifier data
            - nBits (int): Number of bits to find

        Returns:
            - list: List of possible bits
        """
        unknownBits = self.getMiiUnknownBits()
        classifierName = [
            col for col in classifier.columns if col not in ("Name", "Creator")
        ][0]

        # Normalize "Creator" in both dataframes
        classifier["Creator"] = classifier["Creator"].fillna("")
        unknownBits["Creator"] = unknownBits["Creator"].fillna("")

        combinedDf = classifier.merge(unknownBits, on=["Name", "Creator"], how="inner")
        combinedDf = combinedDf.drop(columns=["Name", "Creator"])

        groupedDf = combinedDf.groupby(classifierName)
        bitColumns = [col for col in combinedDf.columns if col != classifierName]

        possibleBits = []

        for i in range(len(bitColumns) - nBits + 1):
            group = bitColumns[i : i + nBits]

            # Check that the group is ascending and only 1 distance between bits
            if max(group) - min(group) == nBits - 1:

                valid = True

                for cl, group_df in groupedDf:
                    groupBits = group_df[group]

                    # Check that all Miis in cl have the same value
                    # We find the opposite
                    if (groupBits.nunique() != 1).any():
                        valid = False
                        break

                if valid:

                    # Now we check that all groups have different values
                    patterns = (
                        groupedDf[group].first().apply(lambda row: tuple(row), axis=1)
                    )
                    if patterns.is_unique:
                        possibleBits.append(group)

        return possibleBits

    def hexdump(self, width=16) -> str:
        """
        Get a hex dump of the Mii Plaza data

        Args:
            - None

        Returns:
            - str: Hex dump of the Mii Plaza data
        """
        toret = ""
        for offset in range(0, len(self.bytesData), width):
            chunk = self.bytesData[offset : offset + width]
            hex_bytes = " ".join(f"{b:02X}" for b in chunk)

            # Only show printable ASCII and non-zero bytes
            ascii_bytes = ""
            for b in chunk:
                if 32 <= b < 127:
                    ascii_bytes += chr(b)
                elif b != 0:
                    ascii_bytes += str(b)

            # Padding for shorter lines
            hex_bytes = hex_bytes.ljust(width * 3)

            line = f"{hex_bytes}\t{ascii_bytes}"
            toret += line + "\n"

        return toret

    def graphPieChart(self, column: str) -> None:
        miiDf = self.getMiiData()

        Grapher().graphPieChartTkinter(miiDf[column])

    def graphPieChart2(self, column: str) -> None:
        miiDf = self.getMiiData()

        Grapher().graphPieChartMatplotlib(miiDf[column])
