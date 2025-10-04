from grapher import Grapher
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
        self.setMiis()
        self.setStreetPassTags()
        self.setNumberOfTickets()
        self.setFantasticRatings()

    def setMiis(self) -> None:
        """
        Set all Mii attributes by decoding the bytes data
        from bytes 14154-278153.

        At most 1000 Miis (264 bytes each) are stored. If there are more,
        they are replaced in the same order except
        the VIPs, which are not replaced.

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
            ascii_bytes = "".join((chr(b) if 32 <= b < 127 else ".") for b in chunk)

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
