from offsets import (
    get_ending_pos,
    offset_is_in_board,
    knight_offsets,
    king_offsets,
    bishop_offsets,
    rook_offsets,
    pawn_offsets,
)
from conversions import NotationSquare, board_x, board_y, pos_to_notation_square
from textwrap import wrap

startingBoard = list("rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR")
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


class Board:
    def __init__(
        self,
        board: list[str] = startingBoard,
        turn: str = 'w',
        castling_rights: list[str] = startingCastlingRights,
        en_passant_square: int = 64,  # possible target square for en passant,
        tempi: int = 0,
        moves: int = 0,
    ) -> None:
        self.board = board
        self.castling_rights = castling_rights
        self.turn = turn
        self.en_passant_target_pos = en_passant_square
        self.tempi = tempi
        self.moves = moves

    def reset(self):
        self.board = startingBoard
        self.castling_rights = startingCastlingRights
        self.turn = 'w'

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
        for i in range(len(self.board)):
            if self.board[i].isupper():
                white_material += pieceValuesDict[self.board[i].lower()]
            else:
                black_material += pieceValuesDict[self.board[i].lower()]
        return white_material - black_material

    def change_turn(self):
        self.turn = 'b' if self.turn == 'w' else 'w'

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
        for i in range(len(self.board)):
            taken_pieces_tally[self.board[i]] -= 1
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
                print(f" {pieceCharDict[self.board[8*i + j]]}", end="")
            print("\n", end="")
        material_diff = self.calc_material_diff()
        if material_diff > 0:
            print(f"   +{material_diff} ", end="")
        elif material_diff < 0:
            print(f"   {material_diff} ", end="")
        print(self.calc_taken_pieces_string())

    def get_pseudo_legal_moves(self, starting_pos) -> list:
        moving_piece = self.board[starting_pos]
        if moving_piece == ".":
            return []

        def piece_matches_turn(piece: str, turn: str):
            return (piece.isupper() and turn == 'w') or (piece.islower() and turn == 'b')

        if not piece_matches_turn(moving_piece, self.turn):
            return []

        pseudo_legal_target_positions = []

        match moving_piece.lower():
            case "k":
                for offset in king_offsets:
                    if not offset_is_in_board(starting_pos, offset):
                        continue
                    target_piece = self.board[get_ending_pos(starting_pos, offset)]
                    if of_same_color(moving_piece, target_piece):
                        continue
                    pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))

                # TODO: Castling

                return pseudo_legal_target_positions
            case "q":
                for branch in bishop_offsets + rook_offsets:
                    for offset in branch:
                        if not offset_is_in_board(starting_pos, offset):
                            break
                        target_piece = self.board[get_ending_pos(starting_pos, offset)]
                        if of_same_color(moving_piece, target_piece):
                            break
                        pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))
                        if target_piece != ".":
                            break

                return pseudo_legal_target_positions
            case "b":
                for branch in bishop_offsets:
                    for offset in branch:
                        if not offset_is_in_board(starting_pos, offset):
                            break
                        target_piece = self.board[get_ending_pos(starting_pos, offset)]
                        if of_same_color(moving_piece, target_piece):
                            break
                        pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))
                        if target_piece != ".":
                            break

                return pseudo_legal_target_positions
            case "n":
                for offset in knight_offsets:
                    if not offset_is_in_board(starting_pos, offset):
                        continue
                    target_piece = self.board[get_ending_pos(starting_pos, offset)]
                    if not of_same_color(moving_piece, target_piece):
                        pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))

                return pseudo_legal_target_positions
            case "r":
                for branch in rook_offsets:
                    for offset in branch:
                        if not offset_is_in_board(starting_pos, offset):
                            break
                        target_piece = self.board[get_ending_pos(starting_pos, offset)]
                        if of_same_color(moving_piece, target_piece):
                            break
                        pseudo_legal_target_positions.append(get_ending_pos(starting_pos, offset))
                        if target_piece != ".":
                            break

                return pseudo_legal_target_positions
            case "p":
                offsets = pawn_offsets(self.turn)
                single_offset = offsets["single"]
                if not offset_is_in_board(starting_pos, single_offset):
                    return []
                single_target_pos = get_ending_pos(starting_pos, single_offset)
                print(self.board[single_target_pos])
                if self.board[single_target_pos] == ".":
                    pseudo_legal_target_positions.append(single_target_pos)
                    double_offset = offsets["double"]
                    if not offset_is_in_board(starting_pos, double_offset):
                        return []
                    double_target_pos = get_ending_pos(starting_pos, double_offset)
                    if (self.turn == 'w' and board_y(starting_pos) == 6) or (
                        self.turn == 'b' and board_y(starting_pos) == 1
                    ):
                        if self.board[double_target_pos] == ".":
                            pseudo_legal_target_positions.append(double_target_pos)

                for offset in offsets["captures"]:
                    capture_target_pos = get_ending_pos(starting_pos, offset)
                    target_piece = self.board[capture_target_pos]
                    if not of_same_color(target_piece, moving_piece) and target_piece != ".":
                        pseudo_legal_target_positions.append(capture_target_pos)

                for offset in offsets["enpassant"]:
                    en_passant_target_pos = get_ending_pos(starting_pos, offset)
                    if self.en_passant_target_pos == en_passant_target_pos:
                        pseudo_legal_target_positions.append(en_passant_target_pos)
                # TODO: Promotion

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
            NotationSquare(starting_position).to_pos(),
            NotationSquare(ending_position).to_pos()
        )
        if current_move.ending_position in self.get_pseudo_legal_moves(current_move.starting_position):
            self.move_piece(current_move)
        else:
            print("ILLEGAL MOVE")
            return self.get_player_move()

    def to_fen(self):
        board_lines = wrap(''.join(self.board))
        fen_board = ""
        for line in board_lines:
            count = 0
            for piece in list(line):
                if piece != '.':
                    fen_board += str(piece)
                    if count != 0:
                        fen_board += str(count)
                    count = 0
                else:
                    count += 1

        turn = self.turn
        castling_rights = ''.join(self.castling_rights)
        if self.en_passant_target_pos == 64:
            en_passant_target_square = '-'
        else:
            en_passant_target_square = pos_to_notation_square(self.en_passant_target_pos)
        tempi = str(self.tempi)
        moves = str(self.moves)

        return " ".join([fen_board, turn, castling_rights, en_passant_target_square, tempi, moves])

    def move_piece(self, current_move: Move):
        # set last pawn double move to allow en passant
        self.en_passant_target_pos = 8
        if self.board[current_move.starting_position].lower() == "p":
            self.tempi = 0
            offset = current_move.ending_position - current_move.starting_position
            if offset == -16 or offset == 16:
                if self.turn == 'w':
                    self.en_passant_target_pos = current_move.ending_position - 8
                else:
                    self.en_passant_target_pos = current_move.ending_position + 8
        elif self.board[current_move.ending_position] != '.':
            self.tempi = 0
        else:
            self.tempi = 0

        if self.turn == 'b':
            self.moves += 1

        self.board[current_move.ending_position] = self.board[current_move.starting_position]
        self.board[current_move.starting_position] = "."
        self.change_turn()
