from typing import Optional
from datetime import date


class BackupBirthday:
    decoder = {
        b"\x10\x21": None,
        b"\xae\x63": date(day=1, month=1, year=1968),
        b"\xdc\xaf": date(day=26, month=2, year=1968),
        b"\x89\xa1": date(day=27, month=2, year=1968),
        b"\x32\xaa": date(day=28, month=2, year=1968),
        b"\x67\xa4": date(day=29, month=2, year=1968),
        b"\x68\xda": date(day=1, month=3, year=1968),
        b"\xc3\x5c": date(day=30, month=4, year=1968),
        b"\x33\x30": date(day=1, month=5, year=1968),
        b"\xcc\x22": date(day=2, month=5, year=1968),
        b"\x99\x2c": date(day=3, month=5, year=1968),
        b"\x22\x27": date(day=4, month=5, year=1968),
        b"\x77\x29": date(day=5, month=5, year=1968),
        b"\x88\x3b": date(day=6, month=5, year=1968),
        b"\xdd\x35": date(day=7, month=5, year=1968),
        b"\x06\x27": date(day=8, month=5, year=1968),
        b"\x53\x29": date(day=9, month=5, year=1968),
        b"\xac\x3b": date(day=10, month=5, year=1968),
        b"\xf9\x35": date(day=11, month=5, year=1968),
        b"\x42\x3e": date(day=12, month=5, year=1968),
        b"\x17\x30": date(day=13, month=5, year=1968),
        b"\xe8\x22": date(day=14, month=5, year=1968),
        b"\xbd\x2c": date(day=15, month=5, year=1968),
        b"\xa6\x0c": date(day=16, month=5, year=1968),
        b"\xf3\x02": date(day=17, month=5, year=1968),
        b"\x0c\x10": date(day=18, month=5, year=1968),
        b"\x59\x1e": date(day=19, month=5, year=1968),
        b"\xe2\x15": date(day=20, month=5, year=1968),
        b"\xb7\x1b": date(day=21, month=5, year=1968),
        b"\xd8\x4c": date(day=22, month=5, year=1968),
        b"\x2d\xac": date(day=23, month=5, year=1968),
        b"\x66\xfb": date(day=24, month=5, year=1968),
        b"\xf2\x4d": date(day=25, month=5, year=1968),
        b"\x9d\x1a": date(day=26, month=5, year=1968),
        b"\x68\xfa": date(day=27, month=5, year=1968),
        b"\x43\xb4": date(day=28, month=5, year=1968),
        b"\x15\xae": date(day=29, month=5, year=1968),
        b"\x7a\xf9": date(day=30, month=5, year=1968),
        b"\x8f\x19": date(day=31, month=5, year=1968),
        b"\x1e\xc5": date(day=1, month=6, year=1968),
        b"\x83\x95": date(day=2, month=6, year=1968),
        b"\x55\xa2": date(day=25, month=7, year=1968),
        b"\x6f\xa8": date(day=1, month=8, year=1968),
        b"\x81\xad": date(day=7, month=8, year=1968),
        b"\x5a\xbf": date(day=8, month=8, year=1968),
        b"\x50\x88": date(day=18, month=8, year=1968),
        b"\x6a\xe1": date(day=7, month=9, year=1968),
        b"\x27\x0d": date(day=15, month=10, year=1968),
        b"\x93\x78": date(day=20, month=11, year=1968),
        b"\xf2\xfb": date(day=1, month=12, year=1968),
        b"\x38\xfe": date(day=11, month=12, year=1968),
        b"\xbc\xd5": date(day=31, month=12, year=1968),
    }

    def __init__(self, bytesData: bytes) -> None:
        """
        The birthday from the owner of the plaza is also encoded
        in 2 other bytes, but the pattern hasn't been found.

        Args:
            - bytesData (bytes): 2 bytes containing the birthday data

        Returns:
            - None
        """
        self.birthday = self.decoder.get(bytesData, None)

        if self.birthday is None and bytesData != b"\x10\x21":
            print(f"Warning: Unknown backup birthday bytes {bytesData.hex()}")

    def getBirthday(self) -> Optional[date]:
        """
        Get the decoded birthday.

        Args:
            - None

        Returns:
            - Optional[date]: The decoded birthday or None if not set.
        """
        return self.birthday

    @staticmethod
    def generateFile() -> None:
        """
        Generate a text file with the confirmed birthdays for easier reference.

        Args:
            - None

        Returns:
            - None
        """
        with open("confirmedBirthdays.txt", "w", encoding="utf-8") as f:

            for bytesData, birthday in BackupBirthday.decoder.items():

                b1, b2 = bytesData[0], bytesData[1]
                dateLabel = (
                    "Not set"
                    if birthday is None
                    else f"{birthday.day} {birthday.strftime("%B")}"
                )
                f.write(f"{b1:08b} {b2:08b}\t{b1:02X} {b2:02X}\t{dateLabel}\n")


if __name__ == "__main__":
    BackupBirthday.generateFile()
