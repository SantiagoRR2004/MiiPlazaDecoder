from typing import Optional
from datetime import date


class Birthday:

    def __init__(self, bytesData: bytes) -> None:
        """
        Decode the birthday from 2 bytes.

        The whole first byte and only the last
        two bits of the second byte are used.

        The way the birthday is encoded is very strange,
        it also seems that it is ready to have no day or month,
        while only no day and month is possible.

        The last 4 bits of the first byte are used for the month.
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
        that the first 4 bits of the first byte are even for the first
        7 months, and odd for the last 5 months.

        The day of the month isn't more simple. Using the first 4
        bits of the first byte,the first of the month is 2 or 3
        (depending on the month), and it goes by adding 2.
        When it reaches the max (14-15), it resets to 0 or 1 and
        add 1 to the last two bits of the second byte.

        This means the last two bits of the second byte are which set of
        8 days of the month it is:
            0 -> days 1-7
            1 -> days 8-15
            2 -> days 16-23
            3 -> days 24-31

        Args:
            - bytesData (bytes): 2 bytes containing the birthday data

        Returns:
            - None
        """
        dayBits = (bytesData[0] >> 4) & 0x0F
        monthBits = bytesData[0] & 0x0F

        if dayBits % 2 == 0:
            # Even, first set of months
            month = monthBits // 2
        else:
            # Odd, second set of months
            month = (monthBits // 2) + 8

        day = dayBits // 2 + (8 * (bytesData[1] & 0x03))

        self.birthday: Optional[date] = None

        if not (day == 0 and month == 0):
            # Leap year close to 1970 (Unix 0 time)
            self.birthday = date(month=month, day=day, year=1968)

    def getBirthday(self) -> Optional[date]:
        """
        Get the decoded birthday.

        Args:
            - None

        Returns:
            - Optional[date]: The decoded birthday or None if not set.
        """
        return self.birthday
