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
