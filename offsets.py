def get_xy_ending_pos(starting_pos: int, xy_offset: dict) -> dict:
    xy_pos = {
        "x": starting_pos % 8,
        "y": (starting_pos // 8) % 8,
    }
    return {
        "x": xy_pos["x"] + xy_offset["x"],
        "y": xy_pos["y"] + xy_offset["y"],
    }


def get_ending_pos(starting_pos: int, xy_offset: dict) -> int:
    xy_ending_pos = get_xy_ending_pos(starting_pos, xy_offset)
    return xy_ending_pos["x"] + (8 * xy_ending_pos["y"])


def offset_is_in_board(starting_pos: int, xy_offset: dict) -> bool:
    xy_pos = {
        "x": starting_pos % 8,
        "y": (starting_pos // 8) % 8,
    }
    x = xy_pos["x"] + xy_offset["x"]
    y = xy_pos["y"] + xy_offset["y"]
    return not (x > 7 or x < 0 or y > 7 or x < 0)


knight_offsets = [
    {"x": 1, "y": 2},
    {"x": 2, "y": 1},
    {"x": 2, "y": -1},
    {"x": 1, "y": -2},
    {"x": -1, "y": -2},
    {"x": -2, "y": -1},
    {"x": -2, "y": 1},
    {"x": -1, "y": 2},
]
king_offsets = [
    {"x": 1, "y": 1},
    {"x": 1, "y": 0},
    {"x": 1, "y": -1},
    {"x": 0, "y": -1},
    {"x": -1, "y": -1},
    {"x": -1, "y": 0},
    {"x": -1, "y": 1},
    {"x": 0, "y": 1},
]
bishop_offsets = [
    [
        {"x": 1, "y": 1},
        {"x": 2, "y": 2},
        {"x": 3, "y": 3},
        {"x": 4, "y": 4},
        {"x": 5, "y": 5},
        {"x": 6, "y": 6},
        {"x": 7, "y": 7},
    ],
    [
        {"x": 1, "y": -1},
        {"x": 2, "y": -2},
        {"x": 3, "y": -3},
        {"x": 4, "y": -4},
        {"x": 5, "y": -5},
        {"x": 6, "y": -6},
        {"x": 7, "y": -7},
    ],
    [
        {"x": -1, "y": -1},
        {"x": -2, "y": -2},
        {"x": -3, "y": -3},
        {"x": -4, "y": -4},
        {"x": -5, "y": -5},
        {"x": -6, "y": -6},
        {"x": -7, "y": -7},
    ],
    [
        {"x": -1, "y": 1},
        {"x": -2, "y": 2},
        {"x": -3, "y": 3},
        {"x": -4, "y": 4},
        {"x": -5, "y": 5},
        {"x": -6, "y": 6},
        {"x": -7, "y": 7},
    ],
]
rook_offsets = [
    [
        {"x": 1, "y": 0},
        {"x": 2, "y": 0},
        {"x": 3, "y": 0},
        {"x": 4, "y": 0},
        {"x": 5, "y": 0},
        {"x": 6, "y": 0},
        {"x": 7, "y": 0},
    ],
    [
        {"x": -1, "y": 0},
        {"x": -2, "y": 0},
        {"x": -3, "y": 0},
        {"x": -4, "y": 0},
        {"x": -5, "y": 0},
        {"x": -6, "y": 0},
        {"x": -7, "y": 0},
    ],
    [
        {"x": 0, "y": 1},
        {"x": 0, "y": 2},
        {"x": 0, "y": 3},
        {"x": 0, "y": 4},
        {"x": 0, "y": 5},
        {"x": 0, "y": 6},
        {"x": 0, "y": 7},
    ],
    [
        {"x": 0, "y": -1},
        {"x": 0, "y": -2},
        {"x": 0, "y": -3},
        {"x": 0, "y": -4},
        {"x": 0, "y": -5},
        {"x": 0, "y": -6},
        {"x": 0, "y": -7},
    ],
]


# key is piece.isupper()
def pawn_offsets(turn: str):
    if turn == 'w':
        return {
            "single": {"x": 0, "y": -1},
            "double": {"x": 0, "y": -2},
            "captures": [
                {"x": -1, "y": -1},
                {"x": 1, "y": -1},
            ],
            "enpassant": [
                {"x": -1, "y": -2},
                {"x": 1, "y": -2},
            ],
        }
    else:
        return {
            "single": {"x": 0, "y": 1},
            "double": {"x": 0, "y": 2},
            "captures": [
                {"x": -1, "y": 1},
                {"x": 1, "y": 1},
            ],
            "enpassant": [
                {"x": -1, "y": 2},
                {"x": 1, "y": 2},
            ],
        }
