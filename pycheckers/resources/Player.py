class Player:
    """
    A basic object that stores data about a single player,
    i.e. where he has got his pieces and which of them are kings.
    """
    positions = set()
    kings = set()
    pieces = len(positions)
    pieces_with_captures = dict()
