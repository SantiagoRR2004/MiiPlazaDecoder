class Expression:
    """
    These names are not official, they were assigned
    based on what was considered appropriate.
    """

    decoder = {
        0: "Smiling",
        1: "Happy",
        2: "Neutral",
        3: "Surprised",
        4: "Sad",
        5: "Dozing",
    }

    def __init__(self, number: int) -> None:
        """
        Returns the expression based on the number.

        Args:
            - number (int): The number representing the expression.

        Returns:
            - str: The name of the expression.
        """
        self.expression = self.decoder.get(number, None)

        if self.expression is None:
            raise ValueError(f"Invalid expression number: {number}")

    def getExpression(self) -> str:
        """
        Get the expression.

        Args:
            - None

        Returns:
            - str: The name of the expression.
        """
        return self.expression
