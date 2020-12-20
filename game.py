from checkers import game

class Game(game.Game):
    def __init__(self):
        self._set_winner = None
        super().__init__()

    def get_board_winner(self):
        return self._set_winner

    def is_board_over(self):
        return self._set_winner is not None

    def set_winner(self, winner):
        self._set_winner = winner
