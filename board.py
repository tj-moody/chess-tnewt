from __future__ import annotations

from textwrap import wrap

from conversions import *
from offsets import *

STARTING_BOARD = list("rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR")
STARTING_CASTLING_RIGHTS = list("KQkq")

class Move:
    def __init__(self, starting_position: int, ending_position: int) -> None:
        # both positions are 0-63 inclusive
        self.starting_pos = starting_position
        self.ending_pos = ending_position

    def get_xy_offset(self) -> dict[str, int]:
        return {
            "x": (self.ending_pos % 8) - (self.starting_pos % 8),
            "y": (self.ending_pos // 8 % 8) - (self.starting_pos // 8 % 8),
        }


def of_same_color(piece1: str, piece2: str) -> bool:
    return (piece1.isupper() == piece2.isupper()) and (piece1 != ".") and (piece2 != ".")


class Board:
    def __init__(
        self,
        board: list[str] = STARTING_BOARD,
        turn: str = "w",
        castling_rights: list[str] = STARTING_CASTLING_RIGHTS,
        en_passant_square: int = 64,  # possible target square for en passant,
        tempi: int = 0,
        moves: int = 0,
        state: str = "p",
    ) -> None:
        self.board = board
        self.castling_rights = castling_rights
        self.turn = turn
        self.en_passant_target_pos = en_passant_square
        self.tempi = tempi
        self.moves = moves
        self.state = state
        # 'p' -> playing,
        # 'd' -> drawn,
        # 'w' -> white victory,
        # 'b' -> black victory

    def reset(self):
        self.board = STARTING_BOARD
        self.castling_rights = STARTING_CASTLING_RIGHTS
        self.turn = "w"

    def copy(self):
        return Board(
            self.board, self.turn, self.castling_rights, self.en_passant_target_pos, self.tempi, self.moves, self.state
        )

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
        self.turn = "b" if self.turn == "w" else "w"

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

    def _piece_matches_turn(self, piece: str):
        return (piece.isupper() and self.turn == "w") or (piece.islower() and self.turn == "b" and piece != ".")

    def _king_threatmap(self, starting_pos):
        threatmap = []
        for offset in king_offsets["move"]:
            if not offset_is_in_board(starting_pos, offset):
                continue
            target_piece = self.board[get_ending_pos(starting_pos, offset)]
            if self._piece_matches_turn(target_piece):
                continue
            threatmap.append(get_ending_pos(starting_pos, offset))

        can_castle_sides = {"k": True, "q": True}
        for side, offsets in king_offsets["castle"].items():
            for offset in offsets["between"]:
                target_piece = self.board[get_ending_pos(starting_pos, offset)]
                if target_piece != ".":
                    can_castle_sides[side] = False
        for side, can_castle in can_castle_sides.items():
            if can_castle:
                threatmap.append(get_ending_pos(starting_pos, king_offsets["castle"][side]["target"]))

        return threatmap

    def _branch_threatmap(self, starting_pos, branches):
        threatmap = []
        for branch in branches:
            for offset in branch:
                if not offset_is_in_board(starting_pos, offset):
                    break
                target_piece = self.board[get_ending_pos(starting_pos, offset)]
                if self._piece_matches_turn(target_piece):
                    break
                threatmap.append(get_ending_pos(starting_pos, offset))
                if target_piece != ".":
                    break

        return threatmap

    def _knight_threatmap(self, starting_pos):
        threatmap = []
        for offset in knight_offsets:
            if not offset_is_in_board(starting_pos, offset):
                continue
            target_piece = self.board[get_ending_pos(starting_pos, offset)]
            if not self._piece_matches_turn(target_piece):
                threatmap.append(get_ending_pos(starting_pos, offset))

        return threatmap

    def _pawn_threatmap(self, starting_pos):
        threatmap = []
        offsets = pawn_offsets(self.turn)
        single_offset = offsets["single"]
        if not offset_is_in_board(starting_pos, single_offset):
            return []

        single_target_pos = get_ending_pos(starting_pos, single_offset)
        print(self.board[single_target_pos])
        if self.board[single_target_pos] == ".":
            threatmap.append(single_target_pos)
            double_offset = offsets["double"]
            if not offset_is_in_board(starting_pos, double_offset):
                return []
            double_target_pos = get_ending_pos(starting_pos, double_offset)
            if (self.turn == "w" and board_y(starting_pos) == 6) or (self.turn == "b" and board_y(starting_pos) == 1):
                if self.board[double_target_pos] == ".":
                    threatmap.append(double_target_pos)

        for offset in offsets["captures"]:
            capture_target_pos = get_ending_pos(starting_pos, offset)
            target_piece = self.board[capture_target_pos]
            if not self._piece_matches_turn(target_piece) and target_piece != ".":
                threatmap.append(capture_target_pos)

        for offset in offsets["enpassant"]:
            en_passant_target_pos = get_ending_pos(starting_pos, offset)
            if self.en_passant_target_pos == en_passant_target_pos:
                threatmap.append(en_passant_target_pos)
        # TODO: Promotion

        return threatmap

    def threatmap(self, starting_pos) -> list:
        moving_piece = self.board[starting_pos]
        if moving_piece == ".":
            return []

        if not self._piece_matches_turn(moving_piece):
            return []

        match moving_piece.lower():
            case "k":
                return self._king_threatmap(starting_pos)
            case "q":
                return self._branch_threatmap(starting_pos, rook_offsets + bishop_offsets)
            case "r":
                return self._branch_threatmap(starting_pos, rook_offsets)
            case "b":
                return self._branch_threatmap(starting_pos, bishop_offsets)
            case "n":
                return self._knight_threatmap(starting_pos)
            case "p":
                return self._pawn_threatmap(starting_pos)
            case _:
                return []

    def pos_in_check(self, board: Board, pos):
        for piece_pos, piece in enumerate(board.board):
            if piece.lower() != "." and self._piece_matches_turn(piece):
                if pos in self.threatmap(piece_pos):
                    return True
        return False

    def move_causes_check(self, move: Move):  # Assumes move is pseudo legal
        board = self.copy()
        board.move_piece(move)

        king_pos = 64
        for i, piece in enumerate(board.board):
            # color checking inverted as turn is swapped after calling move_piece()
            if (piece == "K" and board.turn == "b") or (piece == "k" and board.turn == "w"):
                king_pos = i
        if king_pos == 64:
            return True

        return self.pos_in_check(board, king_pos)

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

        current_move = Move(NotationSquare(starting_position).to_pos(), NotationSquare(ending_position).to_pos())
        threatmap = self.threatmap(current_move.starting_pos)
        if current_move.ending_pos in threatmap:
            self.move_piece(current_move)
        else:
            print("ILLEGAL MOVE")
            return self.get_player_move()

    def to_fen(self):
        board_lines = wrap("".join(self.board))
        fen_board = ""
        for line in board_lines:
            count = 0
            for piece in list(line):
                if piece != ".":
                    fen_board += str(piece)
                    if count != 0:
                        fen_board += str(count)
                    count = 0
                else:
                    count += 1

        turn = self.turn
        castling_rights = "".join(self.castling_rights)
        if self.en_passant_target_pos == 64:
            en_passant_target_square = "-"
        else:
            en_passant_target_square = pos_to_notation_square(self.en_passant_target_pos)
        tempi = str(self.tempi)
        moves = str(self.moves)

        return " ".join(
            [
                fen_board,
                turn,
                castling_rights,
                en_passant_target_square,
                tempi,
                moves,
            ]
        )

    def _offer_draw(self):  # for 50 move rule
        # draw = input("Draw? ").lower()
        # if draw[0] == 'y':
        #     self.state = 'd'
        self.state = "d"

    def _promote(self, promotion_pos):  # for now underpromotions unimplemented
        piece = 'Q' if self.turn == 'w' else 'q'
        self.board[promotion_pos] = piece

    def move_piece(self, move: Move):
        # set last pawn double move to allow en passant
        moving_piece = self.board[move.starting_pos]
        target_piece = self.board[move.ending_pos]
        self.en_passant_target_pos = 8
        offset = move.ending_pos - move.starting_pos
        if moving_piece.lower() == "p":
            # set `en_passant_target_pos`
            self.tempi = 0
            if offset == -16 or offset == 16:
                if self.turn == "w":
                    self.en_passant_target_pos = move.ending_pos - 8
                else:
                    self.en_passant_target_pos = move.ending_pos + 8
            # promotion
            target_y = board_y(move.ending_pos)
            if target_y == 0 or target_y == 7:
                self._promote(move.starting_pos)
        elif self.board[move.ending_pos] != ".":
            self.tempi = 0
        else:
            self.tempi = 0

        if self.turn == "b":
            self.moves += 1

        if self.tempi >= 100:
            self._offer_draw()

        if moving_piece.lower() == "k":
            if self.turn == "w":
                self.castling_rights.remove("K")
                self.castling_rights.remove("Q")
            else:
                self.castling_rights.remove("k")
                self.castling_rights.remove("q")

        def rook_revoke_castling_rights(rook_pos):
            match rook_pos:
                case 0:
                    self.castling_rights.remove("q")
                case 7:
                    self.castling_rights.remove("k")
                case 56:
                    self.castling_rights.remove("Q")
                case 63:
                    self.castling_rights.remove("K")

        if moving_piece.lower() == 'r':
            rook_revoke_castling_rights(move.starting_pos)
        if target_piece.lower() == 'r':
            rook_revoke_castling_rights(move.ending_pos)

        self.board[move.ending_pos] = moving_piece
        self.board[move.starting_pos] = "."
        self.change_turn()
