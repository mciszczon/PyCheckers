class Board:
    """
    Stores the basic board setup, i.e. the dimensions.
    """
    columns = rows = 8

    def __init__(self):
        self.columns = 8
        self.rows = 8

    def get_rows(self):
        """
        Returns an iterable list of rows.
        :return list:
        """
        return range(self.rows)

    def get_columns(self):
        """
        Returns an iterable list of columns.
        :return list:
        """
        return range(self.columns)

    @staticmethod
    def check_if_allowed(row, column):
        if (row % 2 == 0 and column % 2 != 0) or (row % 2 != 0 and column % 2 == 0):
            return True
        else:
            return False
