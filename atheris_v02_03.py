import datetime as dt
import time as t
import random as r
from copy import deepcopy

global Side, GameArray, BlockingTargetList

play_bot_w = True  # Toggle if white plays as black or white or both, or neither
play_bot_b = True

TotalMoveCalcs, TotalEngineMs = 0, 0  # Debug
OldBoardStates, MoveList, MoveInputList, MoveCount, GameEnd = (
    [],
    [],
    [],
    0,
    False,
)  # FEN for each move, list of inputs, half moves, game end

pawn_table = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 30, 30, 10, 5, 5],
    [0, 0, 0, 60, 60, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -30, -30, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
knight_table = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]
bishop_table = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]
rook_table = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, -20, 0, 5, 5, 0, -20, 0],
]
queen_table = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]
king_table_mid = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]
king_table_end = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10, 0, 0, -10, -20, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -30, 0, 0, 0, 0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50],
]


class Tile:
    """Generic class for all board squares, holds piece and move count for said piece"""
    def __init__(self, piece: int, move: bool, color: bool):
        self.piece = piece
        self.move = move
        self.color = color


def chess_turn(boardstate: list[list[Tile]], side: bool) -> tuple[list[list[Tile]], bool]:
    """Takes in the board and the side, gets move data, executes it, returns updated board array"""
    global OldBoardStates
    if play_bot_b and not side or play_bot_w and side:
        print(118, f"asked engine for a move; Side: {side}")
        move_input = engine_move(boardstate, side)
    else:
        print(121, f"player move; Side: {side}")
        move_input = str(input(f"Enter player move fpr {'white' if side else 'black'}:"))
    move_input = check_move_input(boardstate, move_input, side)
    print(41, move_input, "post check")

    if play_move(boardstate, move_input, side):
        side = not side
        OldBoardStates.append(fen_from_array(boardstate, side))

    return boardstate, side


def piece_to_int(piece: str) -> int:
    """Converts a PGN style piece representation into int (0-6)"""
    # TODO: figure out a way to do this without if/elif block
    if piece == " ":
        return 0
    elif piece in "Pp":
        return 1
    elif piece in "Nn":
        return 2
    elif piece in "Bb":
        return 3
    elif piece in "Rr":
        return 4
    elif piece in "Qq":
        return 5
    elif piece in "Kk":
        return 6
    else:
        return 0


def display_int(piece_int: int, piece_color) -> str:
    """Takes in an integer piece representation and color data and returns PGN piece representation"""
    return " pnbrqk"[piece_int] if not piece_color else " PNBRQK"[piece_int]


def array_from_fen(fen: str) -> tuple[list[list[Tile]], bool]:
    """Resolves a board array from a FEN string"""
    side = "w" in fen  # Reads side data from FEN
    piece_list = []
    for row in fen.split("/"):
        piece_row = []
        for piece in row:
            if piece.isnumeric():
                piece = [" " for _ in range(int(piece))]
            for i in piece:
                piece_row.append([piece_to_int(i), i.isupper()])
        piece_list.append(piece_row)
    return [[Tile(piece_list[7 - j][i][0], False, piece_list[7 - j][i][1]) for i in range(8)] for j in range(8)], side


def fen_from_array(boardstate: list[list[Tile]], side: bool) -> str:
    """Generates a FEN from the board array and side to play"""
    fen = []
    blank_squares = 0
    for row in range(8):
        row = 7 - row  # Flips for proper ordering
        for col in range(8):
            tile = boardstate[row][col]
            if 6 >= tile.piece >= 1:
                if blank_squares > 0:
                    fen.append(str(blank_squares))
                    blank_squares = 0
                fen.append(display_int(tile.piece, tile.color))
            elif tile.piece == 0:
                blank_squares += 1
        if blank_squares > 0:
            fen.append(str(blank_squares))
            blank_squares = 0
        fen.append("/")
    if not side:
        fen.append(" b ")
    else:
        fen.append(" w ")

    # TODO: Add code to add eligible en passant pawn movement recognition, and half move and full move counters (since last pawn move), and proper castling display

    return "".join(fen)


def is_threefold(current_fen: str) -> bool:
    """Check if a certain position has been reached three times"""
    repetitions = 0
    for i in range(len(OldBoardStates)):
        if OldBoardStates[i] == current_fen:
            repetitions += 1
    return repetitions >= 2


def check_move_input(boardstate: list[list[Tile]], move_input: str, side: bool) -> str:
    """Verifies a move is a valid input, returns the valid input"""
    move_input = move_input.strip().lower()
    if move_input in ("resign", "draw"):  # TODO: Expand special moves
        return move_input

    valid_len = len(move_input) == 4 or len(move_input) == 5
    if (
        valid_len
        and move_input[0].isalpha()
        and move_input[2].isalpha()
        and move_input[1].isnumeric()
        and move_input[3].isnumeric()
    ):  # Checks if format is proper coordinate notation
        # Converting coordinate notation into board indices in a tuple
        coords = (
            column_index(move_input[0]),
            int(move_input[1]) - 1,
            column_index(move_input[2]),
            int(move_input[3]) - 1,
        )
        piece_color = boardstate[coords[1]][coords[0]].color
        in_bounds = (
            7 >= coords[0] >= 0 and 7 >= coords[1] >= 0 and 7 >= coords[2] >= 0 and 7 >= coords[3] >= 0
        )  # Bounds check
        if in_bounds and piece_color == side:
            return move_input
        else:
            print(
                585,
                move_input,
                f"in bounds:{in_bounds}, correct_turn:{piece_color == side}",
            )
    else:
        print(586, move_input, "Invalid length and not special command")
    return "invalid"


def resign(boardstate: list[list[Tile]], side: bool) -> None:
    """Handles the resignation game state"""
    global MoveList
    pgn_str = "Resignation: Black wins" if side else "Resignation: White wins"
    MoveList.append("Resignation: Black wins" if side else "Resignation: White wins")
    save_game()
    print(MoveList[-1])


def play_move(boardstate: list[list[Tile]], move_input: str, side: bool) -> bool:
    """Checks if the start coords have the legal move to the second coords, then plays the move if yes"""
    # Checks for special move inputs
    if move_input == "invalid":
        return False
    elif move_input == "resign":
        resign(boardstate, side)
        return True

    # Check if the move is within the fetch_moves list for that start coordinate. TODO: En Passant for fetch_moves()
    row_1, row_2, col_1, col_2 = (
        int(move_input[1]) - 1,
        int(move_input[3]) - 1,
        column_index(move_input[0]),
        column_index(move_input[2]),
    )
    legal_moves = fetch_moves(boardstate, row_1, col_1)
    target = move_input[2:4]
    return piece_move(boardstate, move_input, side) if target in legal_moves else False


def ascii_debug_display(boardstate: list[list[Tile]], side: bool) -> None:
    """Prints the board state to console with indices displayed"""
    print(f"Side to play:{side}")
    for i in range(1, 9):
        print(
            "\n",
            8 - i,
            [display_int(boardstate[-i][j].piece, boardstate[-i][j].color) for j in range(8)],
        )
    print("     0    1    2    3    4    5    6    7  \n")


def column_index(column: str) -> int:
    """Turns a column letter into an array index integer"""
    columns = "abcdefgh"
    for i in range(8):
        if columns[i] == column:
            return i
    return -8


def cardinal_checks(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[tuple[int, int]]:
    """Returns a list of pieces in the cardinal directions who could be attacking the piece at col, row"""
    output = []
    for dx, dy in (
        (0, 1),
        (1, 0),
        (0, -1),
        (-1, 0),
    ):
        for i in range(1, 8):
            row_i, col_i = row + dx * i, col + dy * i
            if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:  # Bounds check
                break
            tile = boardstate[row_i][col_i]
            if tile.piece == 0:
                continue
            opponent = tile.color != piece_side
            if not opponent:
                break
            elif tile.piece not in [4, 5] and opponent:
                break
            else:
                output.append((row_i, col_i))
                break
    return output


def diagonal_checks(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[tuple[int, int]]:
    """Returns a list of the indexes of any pieces on the diagonals which are attacking the piece at col, row"""
    output = []
    for dx, dy in ((1, 1), (-1, -1), (-1, 1), (1, -1)):
        for i in range(1, 8):
            row_i, col_i = row + i * dx, col + i * dy
            if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:  # Bounds check
                break
            tile = boardstate[row_i][col_i]
            if tile.piece == 0:
                continue
            opponent = tile.color != piece_side
            if not opponent:
                break
            elif tile.piece not in [3, 5] and opponent:
                break
            else:
                output.append((row_i, col_i))
                break

    return output


def knight_checks(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[tuple[int, int]]:
    """Returns a list of the indices of any knights attacking the piece at row, col"""
    output = []
    for dx, dy in (
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
    ):  # Each of the possible offsets for a knight
        row_i, col_i = row + dx, col + dy
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:  # Bounds check
            continue
        tile = boardstate[row_i][col_i]
        if tile.piece != 2:  # Is knight?
            continue
        if tile.color != piece_side:
            output.append((row_i, col_i))
    return output


def pawn_checks(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[tuple[int, int]]:
    """Returns a list of the indices of any pawns attacking the piece at row, col"""
    output = []
    pawn_direct = -1 if piece_side else 1  # Direction of movement
    for i in (-1, 1):
        row_i, col_i = row + pawn_direct, col + i
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:  # Bounds check
            continue
        tile = boardstate[row_i][col_i]
        if tile.piece != 1:
            continue
        if tile.color != piece_side:
            output.append((row_i, col_i))
    return output


def king_checks(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[tuple[int, int]]:
    """Returns a list of the indices of any king attacking the piece at row, col"""
    output = []
    for dx, dy in (
        (1, 1),
        (1, 0),
        (1, -1),
        (0, 1),
        (0, -1),
        (-1, 1),
        (-1, 0),
        (-1, -1),
    ):  # Iterates through each of the 8 adjacent locations
        row_i, col_i = row + dx, col + dy
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:  # Bounds check
            continue
        tile = boardstate[row_i][col_i]
        if tile.piece != 6:  # If not king continue
            continue
        if tile.color != piece_side:
            output.append((row_i, col_i))
    return output


def under_attack(boardstate: list[list[Tile]], piece_side: bool, row: int, col: int) -> list[tuple[int, int]]:
    """Determines if a square is under attack by any other pieces, returns a list of tuples containing the board indices of each attacker"""
    return (
        cardinal_checks(boardstate, row, col, piece_side)
        + diagonal_checks(boardstate, row, col, piece_side)
        + knight_checks(boardstate, row, col, piece_side)
        + pawn_checks(boardstate, row, col, piece_side)
        + king_checks(boardstate, row, col, piece_side)
    )


def put_king_in_check(
    boardstate: list[list[Tile]],
    k_row: int,
    k_col: int,
    row_1: int,
    col_1: int,
    row_2: int,
    col_2: int,
    king_side: bool,
) -> bool:
    """Checks if said move puts the king into check. For non-king moves"""
    tile_1, tile_2 = (
        boardstate[row_1][col_1],
        boardstate[row_2][col_2],
    )  # Stores data, simulates, checks king attacks, undoes simulation
    stored_data = (
        tile_1.piece,
        tile_2.piece,
        tile_1.move,
        tile_2.move,
        tile_1.color,
        tile_2.color,
    )
    boardstate = simple_update(boardstate, row_1, col_1, row_2, col_2)
    in_check = True if under_attack(boardstate, king_side, k_row, k_col) else False
    (
        tile_1.piece,
        tile_2.piece,
        tile_1.move,
        tile_2.move,
        tile_1.color,
        tile_2.color,
    ) = stored_data
    return in_check


def find_king(boardstate: list[list[Tile]], side: bool) -> tuple[int, int]:
    """Returns a tuple of the king's coordinates (the king of the passed in side)"""

    # Iterates through the board until it finds the relevant king
    for i in range(8):
        for j in range(8):
            if boardstate[i][j].piece == 6 and boardstate[i][j].color == side:
                return i, j


def legal_king_moves(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[str]:
    """Checks for legal king moves (not including castling"""
    output = []
    for dx, dy in (
        (1, 1),
        (1, 0),
        (1, -1),
        (0, 1),
        (0, -1),
        (-1, 1),
        (-1, 0),
        (-1, -1),
    ):
        row_i, col_i = row + dx, col + dy
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
            continue
        tile = boardstate[row_i][col_i]
        legal_square = tile.piece == 0 or tile.color != piece_side  # Empty or capturable
        if legal_square and not put_king_in_check(boardstate, row_i, col_i, row, col, row_i, col_i, piece_side):
            output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
    return output


def legal_castling(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[str]:
    """Checks for castling, returns list of coordinates for each one ('g1', 'c1', 'g8', 'c8' for castling)"""
    output = []
    i, rook, king, king_j, rook_i, rook_j, kr_side = 0, 4, 6, 2, 0, 3, True
    extra_clear = boardstate[i][1].piece == 0
    for long in [True, False]:
        if not piece_side:
            i, kr_side = 7, False
        if not long:
            king_j, rook_i, rook_j, extra_clear = 6, 7, 5, True
        king_legal = boardstate[i][4].piece == king and boardstate[i][4].move == 0
        rook_legal = boardstate[i][rook_i].piece == rook and boardstate[i][rook_i].move == 0
        checks = (
            not under_attack(boardstate, kr_side, i, 4)
            and not under_attack(boardstate, kr_side, i, king_j)
            and not under_attack(boardstate, kr_side, i, rook_j)
        )
        clear = boardstate[i][rook_j].piece == 0 and boardstate[i][king_j].piece == 0 and extra_clear

        if king_legal and rook_legal and checks and clear and long:
            output.append(f"c{i + 1}")
        if king_legal and rook_legal and checks and clear and not long:
            output.append(f"g{i + 1}")
    return output


def legal_knight_moves(
    boardstate: list[list[Tile]],
    row: int,
    col: int,
    k_row: int,
    k_col: int,
    piece_side: bool,
) -> list[str]:
    """Returns a list of the coordinates of all legal moves for a knight at row, col"""
    # Initializes output list
    output = []

    # Iterates through each of the 8 possible locations for a knight
    for dx, dy in (
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
    ):
        row_i = row + dx
        col_i = col + dy

        # If out of bounds, continue
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
            continue

        # Recalls the Tile object at square to reduce calls to the boardstate list
        tile = boardstate[row_i][col_i]

        # If it's an opponent or an empty square, and it doesn't put the king in check
        if (tile.piece == 0 or tile.color != piece_side) and not put_king_in_check(
            boardstate, k_row, k_col, row, col, row_i, col_i, piece_side
        ):
            output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")

    return output


def legal_pawn_moves(
    boardstate: list[list[Tile]],
    row: int,
    col: int,
    k_row: int,
    k_col: int,
    piece_side: bool,
) -> list[str]:
    """Returns a list of coordinates the pawn can move to/capture"""
    output = []
    pawn_direct = 1 if piece_side else -1  # Pawn forwards/backwards
    for distance in [1, 2]:  # Moves
        row_i = row + distance * pawn_direct
        if not 0 <= row_i <= 7:  # Bounds check
            break
        tile = boardstate[row_i][col]
        if tile.piece != 0 or (distance == 2 and not (row == 1 or row == 6)):  # Not empty, or too far
            break
        if not put_king_in_check(boardstate, k_row, k_col, row, col, row_i, col, piece_side):
            output.append(f"{'abcdefgh'[col]}{row_i + 1}")

    for i in (-1, 1):  # Captures
        row_i, col_i = row + pawn_direct, col + i
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:  # Bounds check
            continue
        tile = boardstate[row_i][col_i]
        if tile.piece == 0:  # Empty square
            continue
        if tile.color != piece_side:
            output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")

    en_passant = legal_en_passant(boardstate, row, col, k_row, k_col, piece_side)
    if not en_passant:
        return output
    else:
        output.append(en_passant)

    return output


def legal_en_passant(
    boardstate: list[list[Tile]],
    row: int,
    col: int,
    k_row: int,
    k_col: int,
    piece_side: bool,
) -> any:
    """returns the legal en passant capture if one is possible"""
    if len(MoveInputList) < 1:
        return
    last_move = MoveInputList[-1]
    if piece_side and row != 4 or not piece_side and row != 3:
        return
    if "o" in last_move or last_move[0] != "1":
        return
    if int(last_move[4]) not in (3, 4):
        return
    if abs(int(last_move[2]) - int(last_move[4])) != 2:
        return
    if piece_side and last_move[2] != "6" or not piece_side and last_move[2] != "1":
        return
    col_2 = column_index(last_move[1])
    if abs(col_2 - col) != 1:
        return
    direct = 1 if piece_side else -1
    row_2 = row + direct
    if put_king_in_check(boardstate, k_row, k_col, row, col, row_2, col_2, piece_side):
        return

    return f"{'abcdefgh'[col]}{row + 1}{col_2}{row_2}"


def legal_diag_moves(
    boardstate: list[list[Tile]],
    row: int,
    col: int,
    k_row: int,
    k_col: int,
    piece_side: bool,
) -> list[str]:
    """Returns a list of the indexes of any squares on the diagonals which are legal moves"""
    output = []
    for dx, dy in (
        (1, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
    ):  # Runs through each of the four direction in order
        for i in range(1, 8):
            row_i, col_i = row + i * dx, col + i * dy
            if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:  # Bounds check
                break
            tile = boardstate[row_i][col_i]
            opponent = tile.color != piece_side
            if tile.piece != 0 and not opponent:  # If own piece
                break
            # If moving in this direction puts the king in check, break TODO: determine if this results in any potentially illegal moves rather than using continue
            if put_king_in_check(boardstate, k_row, k_col, row, col, row_i, col_i, piece_side):
                break
            if tile.piece == 0:  # Empty square
                output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
                continue
            if opponent:  # Opponent piece
                output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
                break

    return output


def legal_cardinal_moves(
    boardstate: list[list[Tile]],
    row: int,
    col: int,
    k_row: int,
    k_col: int,
    piece_side: bool,
) -> list[str]:
    """Returns a list of coords in the cardinal directions that the piece at row, col could legally move to"""
    output = []
    for dx, dy in (
        (0, 1),
        (1, 0),
        (0, -1),
        (-1, 0),
    ):  # Loops through each of the 4 cardinal directions
        for i in range(1, 8):
            row_i, col_i = row + dx * i, col + dy * i
            if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:  # If out of bounds, break
                break
            tile = boardstate[row_i][col_i]
            opponent = tile.color != piece_side
            if tile.piece != 0 and not opponent:  # If it's not empty, and same side, break
                break
            # If moving in this direction puts the king in check, break TODO: determine if this results in any potentially illegal moves rather than using continue
            if put_king_in_check(boardstate, k_row, k_col, row, col, row_i, col_i, piece_side):
                break
            if tile.piece == 0:  # If it's an empty square, add to list and continue
                output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
                continue
            if opponent:  # If it's not empty, but is capturable, add to output and then break
                output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
                break

    return output


def legal_queen_moves(
    boardstate: list[list[Tile]],
    row: int,
    col: int,
    k_row: int,
    k_col: int,
    piece_side: bool,
) -> list[str]:
    """Combines diagonal and cardinal move checks"""
    return legal_cardinal_moves(boardstate, row, col, k_row, k_col, piece_side) + legal_diag_moves(
        boardstate, row, col, k_row, k_col, piece_side
    )


def king_and_castle_moves(
    boardstate: list[list[Tile]],
    row: int,
    col: int,
    k_row: int,
    k_col: int,
    piece_side: bool,
) -> list[str]:
    """Combines diagonal and cardinal move checks"""
    return legal_king_moves(boardstate, row, col, piece_side) + legal_castling(boardstate, row, col, piece_side)


# Call dictionary for has_moves
check_moves = {
    1: legal_pawn_moves,
    2: legal_knight_moves,
    3: legal_diag_moves,
    4: legal_cardinal_moves,
    5: legal_queen_moves,
    6: king_and_castle_moves,
}


def fetch_moves(boardstate: list[list[Tile]], row: int, col: int) -> list[str]:
    """Checks if the piece at the coordinates has any legal moves. Returns a list of target coordinates for each legal move it does have, ie ['e3', 'e4']"""
    tile = boardstate[row][col]
    piece_type, piece_side = tile.piece, tile.color

    try:  # Tries to find the king, returns an empty list of moves if no king can be found
        k_row, k_col = find_king(boardstate, piece_side)
    except (IndexError, ValueError, TypeError):
        return []

    return (
        check_moves[piece_type](boardstate, row, col, k_row, k_col, piece_side) if piece_type else []
    )  # Calls the appropriate functions for moves. TODO: en passant


def is_checkmate(
    boardstate: list[list[Tile]],
    side: bool,
    a_row: int,
    a_col: int,
    k_row: int,
    k_col: int,
) -> bool:
    skip_block_checks = False
    tile_1, tile_2 = boardstate[k_row][k_col], boardstate[a_row][a_col]

    if (
        tile_1.piece != 6 or tile_2.color == tile_1.color or fetch_moves(boardstate, k_row, k_col)
    ):  # Verifies it's a king, actually under check, and can't move
        return False

    for capture in under_attack(boardstate, side, a_row, a_col):
        if boardstate[capture[0]][capture[1]].piece == 6:
            if not under_attack(boardstate, not side, a_row, a_col):
                return False
        else:
            return False

    if tile_2.piece == 2:  # If it's a knight, no blocks
        return True

    potential_blockers = calculate_squares_between(boardstate, not side, a_row, a_col, k_row, k_col)
    for i in range(len(potential_blockers)):  # Simulates all possible check blocking moves and evaluates the results
        block_sub = potential_blockers[i]
        row_1, col_1, col_2, row_2 = (
            block_sub[0][0],
            block_sub[0][1],
            block_sub[1][1],
            block_sub[1][0],
        )
        if not 0 <= row_1 <= 7 or not 0 <= col_1 <= 7 or not 0 <= row_2 <= 7 or not 0 <= col_2 <= 7:
            continue
        tile_1, tile_2 = boardstate[row_1][col_1], boardstate[row_2][col_2]
        stored_data = (
            tile_1.piece,
            tile_1.move,
            tile_1.color,
            tile_2.piece,
            tile_2.move,
            tile_2.color,
        )
        attacked = under_attack(simple_update(boardstate, row_1, col_1, row_2, col_2), side, k_row, k_col)
        (
            tile_1.piece,
            tile_1.move,
            tile_1.color,
            tile_2.piece,
            tile_2.move,
            tile_2.color,
        ) = stored_data
        if not attacked:
            return False
    return True


def is_stalemate(boardstate: list[list[Tile]]) -> bool:
    """Determines if a position is stalemate"""
    white_stalemated = True
    black_stalemated = True

    for i in range(8):
        for j in range(8):
            tile = boardstate[i][j]
            if not tile.piece:
                continue
            moves = fetch_moves(boardstate, i, j)
            if tile.color:
                if len(moves) != 0:
                    white_stalemated = False
            if not tile.color:
                if len(moves) != 0:
                    black_stalemated = False
    return white_stalemated or black_stalemated


def calculate_squares_between(
    boardstate: list[list[Tile]],
    side: bool,
    a_row: int,
    a_col: int,
    k_row: int,
    k_col: int,
) -> list[list[list[int, int]]]:
    """Returns a list of all pieces that could block the line of attack between the coordinates that are passed in"""
    row_diff, col_diff = a_row - k_row, a_col - k_col
    row_direct, col_direct, distance = 0, 0, 0
    output = []
    if not col_diff or not row_diff:
        distance = abs(row_diff) + abs(col_diff)
    if abs(col_diff) == abs(row_diff):
        distance = abs(row_diff)

    if col_diff > 0:  # A must be in the positive col from K
        col_direct = 1
    elif col_diff < 0:
        col_direct = -1
    if row_diff > 0:
        row_direct = 1
    elif row_diff < 0:
        row_direct = -1
    for pos_move in range(1, distance):
        pos_move_row = a_row + pos_move * row_direct  # these are the squares in line with the check
        pos_move_col = a_col + pos_move * col_direct
        attacking_coords = under_attack(boardstate, not side, pos_move_row, pos_move_col)
        for coord in attacking_coords:
            coord_pair = [coord, [pos_move_row, pos_move_col]]
            output.append(coord_pair)

    return output  # This is a list of all potential pieces (their coordinates) that could theoretically block the line of attack between the two given coordinate sets, paired with the square they would move to


def pgn_append(move: str, piece_1: int, piece_2: int, color_2: bool, special: str):
    """Takes in a move, the piece making the move, and the piece and color of the target, and appends it to the move list of PGNs"""
    global MoveList
    pgn_target, pgn_column, pgn_column_start, pgn_1 = (
        display_int(piece_2, color_2),
        "abcdefgh"[column_index(move[3])],
        "abcdefgh"[column_index(move[1])],
        display_int(piece_1, True),
    )
    if piece_1 == 1:
        if pgn_target not in " P":
            pgn_1 = f"{pgn_column_start}x{pgn_target}"
        elif pgn_target == "P":
            pgn_1 = f"{pgn_column_start}x"
        else:
            pgn_1 = ""

    MoveList.append(f"{pgn_1}{pgn_column}{int(move[3])}")
    MoveList.append(special)


def piece_move(boardstate: list[list[Tile]], move_input: str, side: bool) -> tuple[list[list[Tile]], bool]:
    """Executes a move and checks for game ends"""
    global MoveCount, GameEnd, MoveInputList, GameArray
    print(1323, f"piece move called for the move {move_input}")
    ended, pgn_str = False, ""  # Initializing variables, getting piece data
    col_1, row_1, col_2, row_2 = (
        column_index(move_input[0]),
        int(move_input[1]) - 1,
        column_index(move_input[2]),
        int(move_input[3]) - 1,
    )
    tile_1, tile_2 = boardstate[row_1][col_1], boardstate[row_2][col_2]
    piece_1, move_1, color_1, piece_2, move_2, color_2 = (
        tile_1.piece,
        tile_1.move,
        tile_1.color,
        tile_2.piece,
        tile_2.move,
        tile_2.color,
    )

    if color_1 != side:  # Turn check
        print("Wrong turn")
        return boardstate, False

    if piece_1 == 1 and (side and row_2 == 7 or not side and row_2 == 0):  # Promotion check
        try:
            promotion = move_input[4].lower()
        except (TypeError, IndexError):
            promotion = "q"
        tile_2.piece = piece_to_int(promotion if promotion in "qbnr" else "q")  # Default queen promotion
    else:
        tile_2.piece = piece_1
    tile_1.piece, tile_1.move, tile_1.color, tile_2.move, tile_2.color = (
        0,
        True,
        False,
        True,
        color_1,
    )  # Standard movement

    k_row, k_col = find_king(boardstate, side)  # Finds kings and calculates the FEN
    enemy_k_row, enemy_k_col = find_king(boardstate, not side)
    for coords in under_attack(
        boardstate, not side, enemy_k_row, enemy_k_col
    ):  # If the opposing king is attacked, check for checkmate
        attacker = boardstate[coords[0]][coords[1]].piece
        a_row, a_col = coords[0], coords[1]
        if is_checkmate(boardstate, side, a_row, a_col, enemy_k_row, enemy_k_col):
            print(876, "checkmate")
            color = "white" if side else "black"
            pgn_str = f"Checkmate: {color} wins"
            ended = True
    if not ended and is_stalemate(boardstate):  # Check for stalemate
        print(881, "stalemate")
        pgn_str = "Stalemate: draw"
        ended = True
    if not ended and is_threefold(fen_from_array(boardstate, not side)):  # Check for threefold repetition
        print(885, "threefold repetition")
        pgn_str = "Threefold Repetition: draw"
        ended = True
    if ended:
        save_game()
        print(pgn_str)
        GameEnd = True

    if piece_1 == 4 and move_input in (
        "e1g1",
        "e1c1",
        "e8g8",
        "e8c8",
    ):  # Slightly different behavior for castling
        if side and move_input == "e1g1":
            MoveList.append("O-O")
        if not side and move_input == "e8g8":
            MoveList.append("o-o")
        if side and move_input == "e1c1":
            MoveList.append("O-O-O")
        if not side and move_input == "e8c8":
            MoveList.append("o-o-o")

    side = not side
    MoveInputList.append(f"{piece_1}{move_input}")
    pgn_append(move_input, piece_1, piece_2, color_2, pgn_str)
    MoveCount += 1
    return boardstate, True


def save_game():
    pgn_str = ""
    if MoveCount > 0:
        now = dt.datetime.now()  # Gets the current timestamp
        for move in MoveList:
            pgn_str += str(move)
            pgn_str += " "
        previous_games = open("pgn_log.txt", "a")
        pgn_str = str(now) + ": " + pgn_str + f"Move count:{MoveCount} \n\n"
        previous_games.write(pgn_str)
        previous_games.close()


def evaluate_position(boardstate: list[list[Tile]]) -> int:
    """Evaluates a position based on material, negative if black is winning"""
    evaluation = 0
    for i in range(8):
        for j in range(8):
            count = 0
            tile = boardstate[i][j]
            if not tile.piece:
                continue
            if tile.piece == 6:  # Check for checkmate
                attackers = under_attack(boardstate, False, i, j)
                for attacking_coords in attackers:
                    king_side = tile.color
                    if is_checkmate(
                        boardstate,
                        king_side,
                        attacking_coords[0],
                        attacking_coords[1],
                        i,
                        j,
                    ):
                        return 100000 if king_side else -100000

            table_y, table_x = (7 - i, j) if tile.color else (i, j)  # Mirror tables for b/w

            # Evaluate the piece based on its material value, and its piece square table (position)
            if tile.piece == 1:
                count = 100 + pawn_table[table_y][table_x]
            elif tile.piece == 2:
                count = 320 + knight_table[table_y][table_x]
            elif tile.piece == 3:
                count = 330 + bishop_table[table_y][table_x]
            elif tile.piece == 4:
                count = 500 + rook_table[table_y][table_x]
            elif tile.piece == 5:
                count = 900 + queen_table[table_y][table_x]
            elif tile.piece == 6:
                count = king_table_mid[table_y][table_x]
            else:
                continue

            if tile.color:
                evaluation += count
            else:
                evaluation -= count
    return evaluation


def simple_update(boardstate: list[list[Tile]], row_1: int, col_1: int, row_2: int, col_2: int) -> list[list[Tile]]:
    """Moves from a piece from square 1 to square 2, returns boardstate"""
    tile_1, tile_2 = boardstate[row_1][col_1], boardstate[row_2][col_2]
    tile_2.piece, tile_2.move, tile_2.color = tile_1.piece, True, tile_1.color
    tile_1.piece, tile_1.move, tile_1.color = 0, True, False
    return boardstate


def first_layer(boardstate: list[list[Tile]], side: bool) -> list[list[str]]:
    """Calculates all legal moves from a position for one side"""
    possible_moves_1 = []
    for row in range(8):
        for col in range(8):
            tile = boardstate[row][col]
            if tile.piece != 0 and tile.color == side:
                for coord in fetch_moves(boardstate, row, col):
                    possible_moves_1.append([f"{'abcdefgh'[col]}{row + 1}{coord}"])
    return possible_moves_1


def intermediate_layer(
    boardstate: list[list[Tile]],
    move_list_list: list[list[str]],
    side: bool,
    move_count: int,
    depth: int,
) -> list[list[str]]:
    """Calculates all the legal moves at a certain depth"""
    possible_moves = [[] for _ in range(move_count)]
    count = 0

    for indiv_move in move_list_list:  # Loops through each move branch
        if not indiv_move:
            continue
        undo_moves = [(0, False, False, 0, 0, 0, False, False, 0, 0) for _ in range(depth)]
        null_check = False

        for i in range(depth):  # Simulates move path and stores the prior board
            if indiv_move[i] != "a1a1":
                row_1 = int(indiv_move[i][1]) - 1
                col_1 = column_index(indiv_move[i][0])
                row_2 = int(indiv_move[i][3]) - 1
                col_2 = column_index(indiv_move[i][2])
                tile_1 = boardstate[row_1][col_1]
                tile_2 = boardstate[row_2][col_2]
                if indiv_move[i] in ("e1g1", "e1c1", "e8g8", "e8c8") and tile_1.piece == 6:  # If it's a castling move
                    col_a = 7 if col_2 == 6 else 0
                    row_a = 0 if row_1 == 0 else 7
                    col_b = 5 if col_2 == 6 else 3
                    undo_moves.insert(0, (4, False, tile_1.color, row_a, col_a, 0, True, False, row_a, col_b))
                    boardstate = simple_update(boardstate, row_a, col_a, row_a, col_b)
                undo_moves[i] = (
                    tile_1.piece,
                    tile_1.move,
                    tile_1.color,
                    row_1,
                    col_1,
                    tile_2.piece,
                    tile_2.move,
                    tile_2.color,
                    row_2,
                    col_2,
                )
                boardstate = simple_update(boardstate, row_1, col_1, row_2, col_2)

        for row in range(8):  # Fetches legal moves of each relevant piece
            for col in range(8):
                tile = boardstate[row][col]
                if tile.piece != 0 and tile.color == side:
                    for coord in fetch_moves(boardstate, row, col):
                        possible_moves[count] = indiv_move + [f"{'abcdefgh'[col]}{row + 1}{coord}"]
                        null_check = True
                        count += 1
        if not null_check:
            possible_moves[count] = indiv_move + ["a1a1"]

        for i in range(len(undo_moves)):  # Undoes move path
            move = undo_moves[-(i + 1)]
            if move[3] == move[8] and move[4] == move[9]:
                continue
            tile_1 = boardstate[move[3]][move[4]]
            tile_2 = boardstate[move[8]][move[9]]
            tile_2.piece = move[5]
            tile_1.piece = move[0]
            tile_2.move = move[6]
            tile_1.move = move[1]
            tile_2.color = move[7]
            tile_1.color = move[2]
    return possible_moves


def move_eval(boardstate: list[list[Tile]], row_1: int, col_1: int, row_2: int, col_2: int) -> int:
    """Takes in a board position and a move from row_1,col_1 to row_2,col_2 and returns its eval"""
    tile_1 = boardstate[row_1][col_1]
    tile_2 = boardstate[row_2][col_2]
    piece_2 = tile_2.piece
    move_2 = tile_2.move
    color_2 = tile_2.color
    piece_1 = tile_1.piece
    move_1 = tile_1.move
    color_1 = tile_1.color
    pos_eval = evaluate_position(simple_update(boardstate, row_1, col_1, row_2, col_2))
    tile_2.piece = piece_2
    tile_2.move = move_2
    tile_2.color = color_2
    tile_1.piece = piece_1
    tile_1.move = move_1
    tile_1.color = color_1
    return pos_eval


def final_layer(
    boardstate: list[list[Tile]],
    move_list_list: list[list[str]],
    side: bool,
    move_count: int,
    depth,
) -> list[list[str, int]]:
    """Calculates all the legal moves at a certain depth"""
    global TotalMoveCalcs
    count_2, minimax = 0, [[" ", " ", " ", 0] for _ in range(128000)]  # Output list
    fake_null = -10000 if side else 10000
    for move_list in move_list_list:  # Loops through each move branch
        if not move_list:
            continue
        count = 0
        eval_list = [fake_null for _ in range(16000)]
        undo_moves = [(0, False, False, 0, 0, 0, False, False, 0, 0) for _ in range(depth)]

        for i in range(depth):  # Simulates move path and stores the prior board
            if move_list[i] != "a1a1":
                row_1 = int(move_list[i][1]) - 1
                col_1 = column_index(move_list[i][0])
                row_2 = int(move_list[i][3]) - 1
                col_2 = column_index(move_list[i][2])
                tile_1 = boardstate[row_1][col_1]
                tile_2 = boardstate[row_2][col_2]
                if move_list[i] in ("e1g1", "e1c1", "e8g8", "e8c8") and tile_1.piece == 6:  # If it's a castling move
                    col_a = 7 if col_2 == 6 else 0
                    row_a = 0 if row_1 == 0 else 7
                    col_b = 5 if col_2 == 6 else 3
                    undo_moves.insert(0, (4, False, tile_1.color, row_a, col_a, 0, True, False, row_a, col_b))
                    boardstate = simple_update(boardstate, row_a, col_a, row_a, col_b)
                undo_moves[i] = (
                    tile_1.piece,
                    tile_1.move,
                    tile_1.color,
                    row_1,
                    col_1,
                    tile_2.piece,
                    tile_2.move,
                    tile_2.color,
                    row_2,
                    col_2,
                )
                boardstate = simple_update(boardstate, row_1, col_1, row_2, col_2)

        for row in range(8):
            for col in range(8):
                tile_3 = boardstate[row][col]
                if tile_3.piece != 0 and tile_3.color == side:
                    for coord in fetch_moves(boardstate, row, col):  # simulates & evaluates all moves
                        row_2 = int(coord[1]) - 1
                        col_2 = column_index(coord[0])
                        eval_list[count] = move_eval(boardstate, row, col, row_2, col_2)
                        count += 1
                        TotalMoveCalcs += 1

        eval_list.sort(reverse=side)  # Sort for least worst move, adds to list
        # noinspection PyTypeChecker
        minimax[count_2] = move_list + [eval_list[0]]
        count_2 += 1

        for i in range(depth):  # Undoes move path
            move = undo_moves[-(i + 1)]
            if move[3] == move[8] and move[4] == move[9]:
                continue
            tile_1 = boardstate[move[3]][move[4]]
            tile_2 = boardstate[move[8]][move[9]]
            tile_2.piece = move[5]
            tile_1.piece = move[0]
            tile_2.move = move[6]
            tile_1.move = move[1]
            tile_2.color = move[7]
            tile_1.color = move[2]
    return minimax


def minimax_layer_2(
    depth_3_evals: list[list[str, int]],
    depth_2_moves: list[list[str]],
    boardstate: list[list[Tile]],
    side: bool,
) -> list[list[str, int]]:
    """Takes in a list of depth 2 moves, and a list of depth 3 moves and their evals, and calculates the meaningful evaluation for depth 2 moves, then returns that"""
    count_2, fake_null = (0, -10000) if side else (0, 10000)
    minimax = [[] for _ in range(len(depth_2_moves))]
    for move_list in depth_2_moves:  # Iterates through each depth 2 move
        if not move_list:
            continue

        count = 0
        eval_list = [fake_null for _ in range(128)]

        for move_path_long in depth_3_evals:  # Finds correct move branch, appends evals
            if not move_path_long:
                continue
            if move_list[0:2] == move_path_long[0:2]:
                # noinspection PyTypeChecker
                eval_list[count] = move_path_long[-1]
                count += 1

        eval_list.sort(reverse=side)  # Sorts for least worst move
        # noinspection PyTypeChecker
        minimax[count_2] = move_list + [eval_list[0]]
        count_2 += 1
    return minimax


def minimax_layer_1(
    depth_2_evals: list[list[str, int]],
    depth_1_moves: list[list[str]],
    boardstate: list[list[Tile]],
    side: bool,
) -> list[list[str, int]]:
    """Takes in a list of depth 1 moves, and a list of depth 2 moves and their evals, and calculates the meaningful evaluation for depth 1 moves, then returns that. Returns trimmed list"""
    minimax = [[] for _ in range(len(depth_1_moves))]  # Output
    count_2 = 0
    fake_null = -10000 if side else 10000

    for move_list in depth_1_moves:  # Iterates through each depth 1 move
        null_check = False
        if not move_list:
            continue
        count, eval_list = 0, []
        for move_path_long in depth_2_evals:  # Sorts by path
            if not move_path_long:
                continue
            if move_list[0] == move_path_long[0]:
                eval_list.append(move_path_long[-1])
                count += 1
                null_check = True
        if not null_check:  # Re-evaluates the position to look for checkmate etc
            # (1649, move_list[0])
            row_1 = int(move_list[0][1]) - 1
            col_1 = column_index(move_list[0][0])
            row_2 = int(move_list[0][3]) - 1
            col_2 = column_index(move_list[0][2])
            tile_1 = boardstate[row_1][col_1]
            tile_2 = boardstate[row_2][col_2]
            undo = (
                tile_1.piece,
                tile_1.move,
                tile_1.color,
                row_1,
                col_1,
                tile_2.piece,
                tile_2.move,
                tile_2.color,
                row_2,
                col_2,
            )
            boardstate = simple_update(boardstate, row_1, col_1, row_2, col_2)
            eval_list.append(-evaluate_position(boardstate))
            (
                tile_1.piece,
                tile_1.move,
                tile_1.color,
                row_1,
                col_1,
                tile_2.piece,
                tile_2.move,
                tile_2.color,
                row_2,
                col_2,
            ) = undo

        eval_list.sort(reverse=side)  # Sorts for least worst move
        # print(len(eval_list))
        minimax[count_2] = move_list + [eval_list[0]]
        count_2 += 1

    return minimax


def engine_move(boardstate_real: list[list[Tile]], side: bool) -> str:
    global TotalMoveCalcs
    TotalMoveCalcs = 0
    start = t.process_time()
    boardstate = deepcopy(boardstate_real)

    # Move tree growth
    possible_moves_1 = first_layer(boardstate, side)
    print(1734, possible_moves_1)
    possible_moves_2 = intermediate_layer(boardstate, possible_moves_1, not side, len(possible_moves_1) * 75, 1)
    possible_moves_3 = intermediate_layer(boardstate, possible_moves_2, side, len(possible_moves_2) * 50, 2)
    depth_3_evals = final_layer(boardstate, possible_moves_3, not side, len(possible_moves_3) * 50, 3)

    sort_start = t.process_time()

    # Eval backpropagation and sort
    depth_2_evals = minimax_layer_2(depth_3_evals, possible_moves_2, boardstate, side)
    depth_1_evals = minimax_layer_1(depth_2_evals, possible_moves_1, boardstate, not side)
    depth_1_evals.sort(key=lambda eval_int: eval_int[-1], reverse=side)

    best_eval = depth_1_evals[0][1]  # Randomizes among equally evaluated moves
    top_moves = [move for move in depth_1_evals if move[-1] == best_eval]
    random_i = r.randint(0, len(top_moves) - 1)

    process_time = t.process_time() - start
    sort_time = t.process_time() - sort_start

    count_m2 = 0  # Debug move counts
    for move in possible_moves_2:
        if not move:
            continue
        else:
            count_m2 += 1

    count_m3 = 0
    for move in possible_moves_3:
        if not move:
            continue
        else:
            count_m3 += 1

    print(
        1528,
        f"\nDepth 1 moves: {len(possible_moves_1)}\nDepth 2 moves: {count_m2}\nDepth 3 moves: {count_m3}\nDepth 4 moves: {TotalMoveCalcs}\n"
        f"Engine process time: {round(process_time * 1000)} ms\nPer move time: {round(((process_time - sort_time)* 1000000)/TotalMoveCalcs)} μs\nSort time: {round(sort_time * 1000)} ms\nMove evals: {depth_1_evals}\nTop 5 moves: {depth_1_evals[:4]}\nTop 5 worst moves:{depth_1_evals[-5:]}\n"
        f"Best move(s):{top_moves}",
    )
    return depth_1_evals[random_i][0]


if __name__ == "__main__":
    test_fen = "rnbqk2r/ppp1ppbp/3p1np1/8/2PPP3/2N2N2/PP3PPP/R1BQKB1R b KQkq"
    test_fen_mate = "8/k7/6R1/8/8/8/8/4K2R w K -"
    standard = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq"
    board, turn = array_from_fen(standard)
    ascii_debug_display(board, turn)
    while True:
        if play_bot_b and play_bot_w:
            input("Enter to continue")
        board, turn = chess_turn(board, turn)
        ascii_debug_display(board, turn)
        if GameEnd:
            break
    save_game()
