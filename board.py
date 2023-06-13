from offsets import *

startingFen = list("rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR")
startingCastlingRights = list("KQkq")


class Move:
    def __init__(self, starting_position: int, ending_position: int) -> None:
        # both positions are 0-63 inclusive
        self.starting_position = starting_position
        self.ending_position = ending_position

    def get_xy_offset(self) -> dict[str, int]:
        return {
            "x": (self.ending_position % 8) - (self.starting_position % 8),
            "y": (self.ending_position // 8 % 8) - (self.starting_position // 8 % 8),
        }


def of_same_color(piece1: str, piece2: str) -> bool:
    return (piece1.isupper() == piece2.isupper()) and (piece1 != ".") and (piece2 != ".")


def board_y(index: int) -> int:
    return index // 8 % 8


def board_x(index: int) -> int:
    return index % 8


class NotationSquare:  # A square in traditional chess notation, e.g. `d4`
    def __init__(self, square: str) -> None:
        self.square = square
        self.file = square[0]
        self.rank = square[1]

    def to_coordinate(self) -> int:
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


class Board:
    def __init__(self, fen: list[str], castling_rights: list[str], turn: int, pawn_double_rank: int = 8) -> None:
        self.fen = fen
        self.castling_rights = castling_rights
        self.turn = turn
        self.pawn_double_rank = pawn_double_rank

    def reset(self):
        self.fen = startingFen
        self.castling_rights = startingCastlingRights
        self.turn = 1  # 1 = white, -1 = black

    def calc_material_diff(self) -> int:
        white_material = 0
        black_material = 0
        pieceValuesDict = {
            "k": 0,
            "q": 9,
            "b": 3,
            "n": 3,
            "r": 5,
            "p": 1,
            ".": 0,
        }
        for i in range(len(self.fen)):
            if self.fen[i].isupper():
                white_material += pieceValuesDict[self.fen[i].lower()]
            else:
                black_material += pieceValuesDict[self.fen[i].lower()]
        return white_material - black_material

    def calc_taken_pieces_string(self) -> str:
        taken_pieces_tally = {
            "k": 1,
            "q": 1,
            "b": 2,
            "n": 2,
            "r": 2,
            "p": 8,
            "K": 1,
            "Q": 1,
            "B": 2,
            "N": 2,
            "R": 2,
            "P": 8,
            ".": 0,
        }
        for i in range(len(self.fen)):
            taken_pieces_tally[self.fen[i]] -= 1
        taken_pieces_string = ""
        pieceTypes = [
            "k",
            "q",
            "b",
            "n",
            "r",
            "p",
        ]
        for piece_type in pieceTypes:
            taken_pieces_string += piece_type.upper() * taken_pieces_tally[piece_type.upper()]
        taken_pieces_string += " "
        for piece_type in pieceTypes:
            taken_pieces_string += piece_type * taken_pieces_tally[piece_type]
        return taken_pieces_string

    def print(self):  # print the current board
        pieceCharDict = {  # placeholders for now
            "k": "k",
            "q": "q",
            "b": "b",
            "n": "n",
            "r": "r",
            "p": "p",
            ".": ".",
            "K": "K",
            "Q": "Q",
            "B": "B",
            "N": "N",
            "R": "R",
            "P": "P",
        }
        for i in range(8):
            for j in range(8):
                print(f" {pieceCharDict[self.fen[8*i + j]]}", end="")
            print("\n", end="")
        material_diff = self.calc_material_diff()
        if material_diff > 0:
            print(f"   +{material_diff} ", end="")
        elif material_diff < 0:
            print(f"   {material_diff} ", end="")
        print(self.calc_taken_pieces_string())

    def get_pseudo_legal_moves(self, starting_pos) -> list:
        moving_piece = self.fen[starting_pos]
        if moving_piece == ".":
            return []

        def piece_matches_turn(piece, turn):
            return (piece.isupper() and turn == 1) or (piece.islower() and turn == -1)

        # if current_fen[starting_position]:
        if not piece_matches_turn(moving_piece, self.turn):
            return []

        pseudo_legal_target_positions = []

        match moving_piece.lower():
            case "k":
                for offset in king_xy_offsets:
                    if not offset_is_in_board(starting_pos, offset):
                        continue
                    target_piece = self.fen[get_ending_pos(starting_pos, offset)]
                    if of_same_color(moving_piece, target_piece):
                        continue
                    pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))

                return pseudo_legal_target_positions
            case "q":
                for branch in bishop_xy_offsets + rook_xy_offsets:
                    for offset in branch:
                        if not offset_is_in_board(starting_pos, offset):
                            break
                        target_piece = self.fen[get_ending_pos(starting_pos, offset)]
                        if of_same_color(moving_piece, target_piece):
                            break
                        pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))
                        if target_piece != ".":
                            break

                return pseudo_legal_target_positions
            case "b":
                for branch in bishop_xy_offsets:
                    for offset in branch:
                        if not offset_is_in_board(starting_pos, offset):
                            break
                        target_piece = self.fen[get_ending_pos(starting_pos, offset)]
                        if of_same_color(moving_piece, target_piece):
                            break
                        pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))
                        if target_piece != ".":
                            break

                return pseudo_legal_target_positions
            case "n":
                for offset in knight_xy_offsets:
                    target_piece = self.fen[get_ending_pos(starting_pos, offset)]
                    if offset_is_in_board(starting_pos, offset) and not of_same_color(moving_piece, target_piece):
                        pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))

                return pseudo_legal_target_positions
            case "r":
                for branch in rook_xy_offsets:
                    for offset in branch:
                        if not offset_is_in_board(starting_pos, offset):
                            break
                        target_piece = self.fen[get_ending_pos(starting_pos, offset)]
                        if of_same_color(moving_piece, target_piece):
                            break
                        pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))
                        if target_piece != ".":
                            break

                return pseudo_legal_target_positions
            case "p":
                offsets = get_pawn_offsets(moving_piece.isupper())
                single_target_pos = get_ending_pos(starting_pos, offsets["single"])
                if self.fen[single_target_pos] == ".":
                    pseudo_legal_target_positions.append(single_target_pos)
                    double_target_pos = get_ending_pos(starting_pos, offsets["double"])
                    if self.fen[double_target_pos] == ".":
                        pseudo_legal_target_positions.append(double_target_pos)

                for offset in offsets["captures"]:
                    capture_target_pos = get_ending_pos(starting_pos, offset)
                    target_piece = self.fen[capture_target_pos]
                    if not of_same_color(target_piece, moving_piece) and target_piece != '.':
                        pseudo_legal_target_positions.append(capture_target_pos)

                for offset in offsets["enpassant"]:
                    enpassant_target_pos = get_ending_pos(starting_pos, offset)
                    if self.pawn_double_rank == board_x(enpassant_target_pos):
                        if moving_piece.isupper() and board_y(starting_pos) == 3:
                            pseudo_legal_target_positions.append(enpassant_target_pos)
                        elif board_y(starting_pos) == 4:
                            pseudo_legal_target_positions.append(enpassant_target_pos)

                return pseudo_legal_target_positions
            case _:
                return []

    def get_player_move(self) -> None:
        # TODO: for some reason responding with invalid, valid, valid calls the ending square a second time, returns the second not the first

        starting_position = input("Starting Square: ")
        if not NotationSquare(starting_position).is_valid_notation():
            print("INVALID INPUT")
            return self.get_player_move()
        ending_position = input("Ending Square: ")
        if not NotationSquare(starting_position[0] + starting_position[1]).is_valid_notation():
            print("INVALID INPUT")
            return self.get_player_move()

        current_move = Move(
            NotationSquare(starting_position).to_coordinate(), NotationSquare(ending_position).to_coordinate()
        )
        if current_move.ending_position in self.get_pseudo_legal_moves(current_move.starting_position):
            self.move_piece(current_move)
        else:
            print("ILLEGAL MOVE")
            return self.get_player_move()

    def move_piece(self, current_move):  # affects only fen last move
        # set last pawn double move to allow en passant
        self.pawn_double_rank = 8
        if self.fen[current_move.starting_position].lower() == 'p':
            offset = current_move.ending_position - current_move.starting_position
            if offset == -16 or offset == 16:
                self.pawn_double_rank = board_x(current_move.ending_position)

        self.fen[current_move.ending_position] = self.fen[current_move.starting_position]
        self.fen[current_move.starting_position] = "."
        self.turn *= -1
