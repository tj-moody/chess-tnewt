from board import Board, Move
from conversions import fen_to_board

#  0  1  2  3  4  5  6  7
#  8  9 10 11 12 13 14 15
# 16 17 18 19 20 21 22 23
# 24 25 26 27 28 29 30 31
# 32 33 34 35 36 37 38 39
# 40 41 42 43 44 45 46 47
# 48 49 50 51 52 53 54 55
# 56 57 58 59 60 61 62 63

#  r  n  b  q  k  b  b  r
#  p  p  p  p  2  3  4  5
#  .  .  .  .  .  .  .  .
#  .  .  .  .  .  .  .  .
#  .  .  .  .  .  .  .  .
#  .  .  .  .  .  .  .  .
#  p  p  p  p  p  p  p  p
#  R  N  B  Q  K  B  N  R
startingFen = list("rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR")
startingCastlingRights = list("KQkq")

board = Board()
# moves = [
#     Move(51, 35),
#     Move(11, 27),
#     Move(62, 45),
#     Move(1, 18),
# ]
# board.print()
# for move in moves:
#     if move.ending_position in board.get_pseudo_legal_moves(move.starting_position):
#         board.move_piece(move)
#         board.print()

print(board.to_fen())
board, turn, castling_rights, en_passant_target_pos, tempi, moves = fen_to_board('rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2')
Board(board, turn, castling_rights, en_passant_target_pos, tempi, moves).print()
