import random as rn


class FullBingoFace:
    """
    This class holds the data connected with a single bingo card from the verification lists.
    Each element in the paths list contains a bingo line associated with a verification number.
    """

    def __init__(self, verify, rows):
        self.verify = verify
        self.paths = []
        self.paths.append(rows)

    def add_path(self, row: list[str | int]) -> None:
        """
        This method adds a bingo path to the paths list

        :param row: list of bingo spots comprising a bingo line
        :type row: list[str | int]
        :return: None
        :rtype: None
        """
        self.paths.append(row)

    def line(self, index) -> list[str] | None:
        """
        This method returns the bingo line located in the index position of the paths list,
        or returns None if the index is not in the paths list.

        :param index: position of the desired bingo line
        :type index: int
        :return: bingo line
        :rtype: list[str] or None
        """
        if 0 <= index < len(self.paths):
            return self.paths[index]
        else:
            return None

    def number_of_paths(self) -> int:
        """
        This method returns the number of bingo lines in the paths list

        :return: number of bingo lines in the paths list or -1 if paths equals None
        :rtype: int
        """
        if self.paths is not None:
            return len(self.paths)
        else:
            return -1

    def shuffle_paths(self) -> None:
        """
        This method shuffles the bingo lines in the paths list a random number of times.

        :return: None
        :rtype: None
        """
        shuffles = rn.randint(4, 25)
        for x in range(shuffles):
            rn.shuffle(self.paths)

    def verification(self) -> int | str:
        """
        This method returns the bingo card verification number.

        :return: bingo card verification number
        :rtype: int or str
        """
        return self.verify
