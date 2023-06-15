
def board_y(index: int) -> int:
    return index // 8 % 8


def board_x(index: int) -> int:
    return index % 8

def pos_to_notation_square(pos):
    num_to_char = {
        0:"a",
        1:"b",
        2:"c",
        3:"d",
        4:"e",
        5:"f",
        6:"g",
        7:"h",
    }
    return NotationSquare(num_to_char[board_x(pos)] + str(board_y(pos))).square


class NotationSquare:  # A square in traditional chess notation, e.g. `d4`
    def __init__(self, square: str) -> None:
        self.square = square
        self.file = square[0]
        self.rank = square[1]

    def to_pos(self) -> int:
        char_to_num = {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5,
            "f": 6,
            "g": 7,
            "h": 8,
        }
        return 63 - (int(self.rank) * 8) + char_to_num[self.file]

    def is_valid_notation(self) -> bool:
        return self.file in ["a", "b", "c", "d", "e", "f", "g", "h"] and self.rank in [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
        ]

def fen_to_board(fen: str):
    fen_list = fen.split(' ')
    board, turn, castling_rights, en_passant_target_pos, tempi, moves = fen_list
    board = list(board.replace('/', ''))
    for i, char in enumerate(board):
        if char.isnumeric():
            board[i] = '.' * int(char)
    board = list(''.join(board))

    # turn and castling_rights are of the same format
    if en_passant_target_pos == '-':
        en_passant_target_pos = 64
    else:
        en_passant_target_pos = NotationSquare(en_passant_target_pos).to_pos()

    tempi = int(tempi)
    moves = int(moves)

    return board, str(turn), list(castling_rights), en_passant_target_pos, tempi, moves
