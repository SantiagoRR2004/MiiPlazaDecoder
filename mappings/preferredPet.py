class PreferredPet:
    decoder = {0: "-", 1: "Dogs", 2: "Cats"}

    def __init__(self, number: int) -> None:
        """
        Returns the preferred pet based on the number.

        Args:
            - number (int): The number representing the preferred pet.

        Returns:
            - str: The name of the preferred pet.
        """
        self.pet = self.decoder.get(number, None)
        if self.pet is None:
            raise ValueError(f"Invalid pet number: {number}")

    def getPet(self) -> str:
        """
        Get the preferred pet.

        Args:
            - None

        Returns:
            - str: The name of the preferred pet.
        """
        return self.pet
