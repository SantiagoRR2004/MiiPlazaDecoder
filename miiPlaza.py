import pandas as pd
import mii


class MiiPlaza:
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
        self.setMiis()

    def setMiis(self) -> None:
        """
        Set all Mii attributes by decoding the bytes data
        They are stored beginning on the 14154 byte.

        Args:
            - None

        Returns:
            - None
        """
        miis = []
        pos = 14154

        while self.bytesData[pos] != 0:
            miiData = self.bytesData[pos : pos + mii.Mii.MII_SIZE]
            miis.append(mii.Mii(miiData))
            pos += mii.Mii.MII_SIZE

        self.miis = miis

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

        combinedDf = classifier.merge(unknownBits, on=["Name", "Creator"], how="left")
        combinedDf = combinedDf.drop(columns=["Name", "Creator"])

        groupedDf = combinedDf.groupby(classifierName)
        bitColumns = [col for col in combinedDf.columns if col != classifierName]

        possibleBits = []

        for i in range(len(bitColumns) - nBits + 1):
            group = bitColumns[i : i + nBits]

            # Check that the group is ascending and only 1 distance between bits
            if max(group) - min(group) == nBits - 1:
                groupBits = groupedDf[group]

                # Check that all groups have only one unique value
                if (groupBits.nunique() == 1).all().all():

                    # Now we check that all groups have different values
                    if (groupBits.nunique().nunique() == len(groupedDf)).all():
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
