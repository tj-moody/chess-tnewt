startingFen = list('rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR')
startingCastlingRights = list('KQkq')

knight_offsets = [-17, -15, -10, -6, 6, 10, 15, 17]
king_offsets = [-9, -8, -7, -1, -1, 7, 8, 9]

class Move:
    def __init__(self, starting_position: int, ending_position: int) -> None:
        # both positions are 0-63 inclusive
        self.starting_position = starting_position
        self.ending_position = ending_position

class Square:  # A square in traditional chess notation, e.g. `d4`
    def __init__(self, square: str) -> None:
        self.square = square
        self.file = square[0]
        self.rank = square[1]

    def to_coordinate(self) -> int:
        char_to_num = {
            'a':1,
            'b':2,
            'c':3,
            'd':4,
            'e':5,
            'f':6,
            'g':7,
            'h':8,
        }
        return 63 - (int(self.rank) * 8 ) + char_to_num[self.file]

class Board:
    move = Move(0, 0)
    def __init__(self, fen: list[str], castling_rights: list[str], turn: int) -> None:
        self.fen = fen
        self.castling_rights = castling_rights
        self.turn = turn

    def reset(self):
        self.fen = startingFen
        self.castling_rights = startingCastlingRights
        self.turn = 1  # 1 = white, -1 = black

    def calc_material_diff(self,) -> int:
        white_material = 0
        black_material = 0
        pieceValuesDict = {
            'k':0,
            'q':9,
            'b':3,
            'n':3,
            'r':5,
            'p':1,
            '.':0,
        }
        for i in range(len(self.fen)):
            if self.fen[i].isupper():
                white_material += pieceValuesDict[self.fen[i].lower()]
            else:
                black_material += pieceValuesDict[self.fen[i].lower()]
        return white_material - black_material

    def calc_taken_pieces_string(self) -> str:
        taken_pieces_tally = {
            'k':0,
            'q':0,
            'b':0,
            'n':0,
            'r':0,
            'p':0,
            'K':0,
            'Q':0,
            'B':0,
            'N':0,
            'R':0,
            'P':0,
            '.':0,
        }
        for i in range(len(self.fen)):
            taken_pieces_tally[self.fen[i]] -= 1
        taken_pieces_tally['k'] += 1
        taken_pieces_tally['q'] += 1
        taken_pieces_tally['b'] += 2
        taken_pieces_tally['n'] += 2
        taken_pieces_tally['r'] += 2
        taken_pieces_tally['p'] += 8
        taken_pieces_tally['K'] += 1
        taken_pieces_tally['Q'] += 1
        taken_pieces_tally['B'] += 2
        taken_pieces_tally['N'] += 2
        taken_pieces_tally['R'] += 2
        taken_pieces_tally['P'] += 8
        taken_pieces_string = ''
        pieceTypes = ['k','q','b','n','r','p',]
        for piece_type in pieceTypes:
            taken_pieces_string += piece_type.upper() * taken_pieces_tally[piece_type.upper()]
        taken_pieces_string += ' '
        for piece_type in pieceTypes:
            taken_pieces_string += piece_type * taken_pieces_tally[piece_type]
        return taken_pieces_string

    def print(self): # print the current board
        pieceCharDict = {
            'k':'k',
            'q':'q',
            'b':'b',
            'n':'n',
            'r':'r',
            'p':'p',
            '.':'.',
            'K':'K',
            'Q':'Q',
            'B':'B',
            'N':'N',
            'R':'R',
            'P':'P',
        }
        for i in range(8):
            for j in range(8):
                print(f" {pieceCharDict[self.fen[8*i + j]]}", end='')
            print("\n", end='')
        material_diff = self.calc_material_diff()
        if material_diff > 0:
            print(f"   +{material_diff} ", end = '')
        elif material_diff < 0:
            print(f"   {material_diff} ", end = '')
        print(self.calc_taken_pieces_string())

    def get_player_move(self) -> None:
        # TODO: for some reason responding with invalid, valid, valid calls the ending square a second time, returns the second not the first
        def is_valid_notation(notation) -> bool:
            return notation[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] and notation[1] in ['1', '2', '3', '4', '5', '6', '7', '8'] and len(notation) == 2

        def panic_and_loop() -> None:
            print("INVALID INPUT")
            return self.get_player_move()

        starting_position = input('Starting Square: ')
        if not is_valid_notation(starting_position):
            panic_and_loop()
        ending_position = input('Ending Square: ')
        if not is_valid_notation(ending_position):
            panic_and_loop()

        self.move = Move(Square(starting_position).to_coordinate(), Square(ending_position).to_coordinate())

    def move_piece(self):
        self.fen[self.move.ending_position] = self.fen[self.move.starting_position]

    def check_legality(self) -> bool:
        moving_piece = self.fen[self.move.starting_position]
        target_piece = self.fen[self.move.ending_position]
        offset = self.move.ending_position - self.move.starting_position

        def piece_matches_turn(piece, turn):
            return (piece.isupper() and turn == 1) or (piece.islower() and turn == -1)
        # if current_fen[starting_position]:
        if not piece_matches_turn(moving_piece, self.turn):
            return False
        if moving_piece.isupper() == target_piece.isupper():
            return False
        match moving_piece.lower():
            case 'k':
                return True
            case 'q':
                return True
            case 'b':
                return True
            case 'n':
                if not offset in knight_offsets:
                    return False
            case 'r':
                return True
            case 'p':
                return True

        return True
