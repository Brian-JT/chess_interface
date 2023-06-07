from tkinter import *
from tkinter import ttk
import datetime
import time
import random


global Side, Root, InputGui, GameArray, BoardCanvas, InputEntry, ContentFrame, BlockingTargetList, CheckmateLabel


# Toggle if white plays as black or white or both, or neither
play_bot_w = False
play_bot_b = True
BoardScalar = 1.4  # Board scalar
WhiteColor = "#C3C3C2"  # Default white piece color
BlackColor = "#000101"  # Default black piece color
WhiteHighlight = "#6e6e6d"  # Default white highlight
BlackHighlight = "#565656"  # Default black highlight
DarkModeBackground = "#333537"  # Dark background color
DarkModeForeground = "#989998"  # Dark foreground color (text boxes etc.)
TotalMoveCalcs = 0  # Debug, keeps track of final moves
TotalEngineMs = 0  # Debug, keeps track of total Ms of engine time
OldBoardStates = []  # Keeps track of previous board states to track threefold repetitions
MoveList = []  # A list of moves played in each game, stored as a list of strings
MoveInputList = []  # A list of coordinate notation for each prior move's input
MoveCount = 0  # Each turn from each player adds 1, so it's a halfmove
GameEnd = False  # Used to stop the moves from being played after reaching a game end position

pawn_table = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 30, 30, 10, 5, 5],
    [0, 0, 0, 60, 60, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]
knight_table = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]
bishop_table = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]
rook_table = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, -20, 0, 5, 5, 0, -20, 0]
]
queen_table = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]
king_table_mid = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]
king_table_end = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10, 0, 0, -10, -20, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -30, 0, 0, 0, 0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50]
]


# Each square in the board representation is stored as a Tile
# Piece: 0-6 in ascending piece value (empty, pawn, knight, bishop, rook, queen, king)
# Move: True means the piece has moved, false means it hasn't
# Color: True means it's a white piece, False means black piece
class Tile:
    """Generic class for all board squares, holds piece and move count for said piece"""
    def __init__(self, piece: int, move: bool, color: bool):
        self.piece = piece
        self.move = move
        self.color = color


def graphics_turn(*args):
    global OldBoardStates

    if play_bot_b and not Side and not GameEnd or play_bot_w and Side and not GameEnd:
        print(118, f"asked engine for a move; Side: {Side}")
        move_input = engine_move(GameArray, Side)
    else:
        print(121, f"player move; Side: {Side}")
        move_input = str(InputGui.get())

    # Calls the function to check move input formatting
    print(39, move_input, "pre check")
    move_input = check_move_input(GameArray, move_input)
    print(41, move_input, "post check")

    # Standard move main loop (checks input, plays move, erases the board, redraws the board, erases input value)
    if play_move(GameArray, move_input):
        OldBoardStates.append(fen_from_array(GameArray, Side))

    # Redraws the game board
    blank_board()
    display_game(GameArray, Side)

    # Wipes the entry box
    InputEntry.delete(0, END)
    return


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


def array_from_fen(fen: str) -> list[list[Tile]]:
    """Resolves a board array from a FEN string"""
    global Side

    # Looks for the side data in a FEN, specifically if there's a w which means it must be White to play
    Side = "w" in fen

    # Splits the FEN up at the slashes and decompresses numerals to blank spaces.
    piece_list = []
    for row in fen.split("/"):
        piece_row = []
        for piece in row:

            # Decompresses numerals
            if piece.isnumeric():
                piece = [" " for _ in range(int(piece))]

            # Converts to a list of integer piece representations and color data
            for i in piece:
                piece_row.append([piece_to_int(i), i.isupper()])
        piece_list.append(piece_row)

    # Returns a 8x8 array of Tile objects, has to mirror it because FEN is mirrored from the indexing the array uses by default
    # Moved is always False to start, obviously
    return [[Tile(piece_list[7 - j][i][0], False, piece_list[7 - j][i][1]) for i in range(8)] for j in range(8)]


def fen_from_array(boardstate: list[list[Tile]], side: bool) -> str:
    """Generates a FEN from the board array and side to play"""
    fen = []
    blank_squares = 0
    for row in range(8):
        # Flips it for proper FEN row order
        row = 7 - row
        for col in range(8):
            piece = boardstate[row][col].piece
            color = boardstate[row][col].color
            if 6 >= piece >= 1:
                if blank_squares > 0:
                    fen.append(str(blank_squares))
                    blank_squares = 0
                fen.append(display_int(piece, color))

            # Counts up blank squares, to compress them into FEN numbering
            elif piece == 0:
                blank_squares += 1
        if blank_squares > 0:
            fen.append(str(blank_squares))
            blank_squares = 0
        fen.append("/")
    if not side:
        fen.append(" b ")
    else:
        fen.append(" w ")

    # Check that the pieces involved in castling are still valid
    is_black_king_unmoved = not boardstate[7][4].move and boardstate[7][4].piece == 6 and not boardstate[7][4].color
    is_white_king_unmoved = not boardstate[0][4].move and boardstate[0][4].piece == 6 and boardstate[0][4].color
    is_white_queen_rook_unmoved = not boardstate[0][0].move and boardstate[0][0].piece == 4 and boardstate[0][0].color
    is_white_king_rook_unmoved = not boardstate[0][7].move and boardstate[0][7].piece == 4 and boardstate[0][7].color
    is_black_queen_rook_unmoved = not boardstate[7][0].move and boardstate[7][0].piece == 4 and not boardstate[7][0].color
    is_black_king_rook_unmoved = not boardstate[7][7].move and boardstate[7][7].piece == 4 and not boardstate[7][7].color

    # TODO: Add code to add eligible en passant pawn movement recognition

    # TODO: Add half move and full move counters (since last pawn move)

    # Attaches data to FEN for castling rights. TODO: fix this
    fen.append(" - - ")
    is_one_check = False
    if is_white_king_unmoved and is_white_king_rook_unmoved:
        is_one_check = True
        fen.append("K")
    if is_white_king_unmoved and is_white_queen_rook_unmoved:
        is_one_check = True
        fen.append("Q")
    if is_black_king_unmoved and is_black_king_rook_unmoved:
        is_one_check = True
        fen.append("k")
    if is_black_king_unmoved and is_black_queen_rook_unmoved:
        is_one_check = True
        fen.append("q")

    if is_one_check:
        try:
            fen.remove(" - - ")
        except ValueError:
            pass

    return ''.join(fen)


def is_threefold(current_fen: str) -> bool:
    """Check if a certain position has been reached three times"""
    repetitions = 0
    for i in range(len(OldBoardStates)):
        if OldBoardStates[i] == current_fen:
            repetitions += 1
    if repetitions >= 2:
        return True
    else:
        return False


def game_init(start_fen: str):
    """Initiates the Tkinter event loop (and thus the entire game)"""
    global Root, InputGui, BoardCanvas, InputEntry, ContentFrame, GameArray
    GameArray = array_from_fen(start_fen)

    # Graphical display initiation/loop
    Root = Tk()

    # Assigns title of the window
    Root.title("Atheris v.02")

    # Setting up the theme and style
    # Changes default them to "clam"
    # Setting up the dark mode styling
    ttk.Style().theme_use("clam")
    style = ttk.Style()
    style.configure("TLabel", fill=DarkModeBackground)
    style.configure(".", background=DarkModeBackground, foreground=DarkModeForeground, fieldbackground="#3A3733", highlightbackground="#3A3733")

    # Creates a content frame to size and place everything
    ContentFrame = ttk.Frame(Root, padding="12 12 12 7", style="TFrame")
    ContentFrame.grid(column=0, row=0, sticky="NWES")

    Root.columnconfigure(0, weight=1)
    Root.rowconfigure(0, weight=1)

    # Using an object of type StringVar() to receive input from the Entry box
    InputGui = StringVar()

    # Creates input Entry box
    InputEntry = Entry(ContentFrame, width=7, textvariable=InputGui, background="#3A3730", bd=1, foreground="#C3C3C2")
    InputEntry.grid(column=2, row=3, sticky="W", pady="5")

    # Triggers the turn when enter is pressed
    InputEntry.bind("<Return>", graphics_turn)

    # Creating the board canvas and placing it
    BoardCanvas = Canvas(ContentFrame, width=400 * BoardScalar, height=400 * BoardScalar, background=DarkModeBackground, highlightthickness=0)
    BoardCanvas.grid(column=2, row=2, sticky="NWES")

    # Displays the current board state
    # Pulls focus automatically to the move entry widget
    # The event loop of the Tkinter gui
    display_game(GameArray, Side)
    InputEntry.focus()
    Root.mainloop()


def blank_board():
    """Creates the blank chess board with no pieces"""
    global BoardCanvas

    # Clears old pieces and board
    BoardCanvas.delete("all")

    # Creates the grid of light squares
    for j in range(0, 7):
        for i in range(0, 4):
            x1 = i * BoardScalar * 100
            x2 = x1 + BoardScalar * 50
            y1 = j * BoardScalar * 100
            y2 = y1 + BoardScalar * 50
            BoardCanvas.create_rectangle(x1, y1, x2, y2, width=0, fill="#566975", activefill="#8a9da8")
            BoardCanvas.create_rectangle(x1 + BoardScalar * 50, y1 + 50 * BoardScalar, x2 + 50 * BoardScalar, y2 + 50 * BoardScalar, width=0, fill="#566975", activefill="#8a9da8")

    # Creates the grid of dark squares
    for j in range(0, 7):
        for i in range(0, 5):
            x1 = i * BoardScalar * 100 - 50 * BoardScalar
            x2 = x1 + BoardScalar * 50
            y1 = j * BoardScalar * 100
            y2 = y1 + BoardScalar * 50
            BoardCanvas.create_rectangle(x1, y1, x2, y2, width=0, fill="#455561", activefill="#798fa0")
            BoardCanvas.create_rectangle(x1 + 50 * BoardScalar, y1 + 50 * BoardScalar, x2 + 50 * BoardScalar, y2 + 50 * BoardScalar, width=0, fill="#455561", activefill="#798fa0")


def draw_pawn(row: int, column: int, color: bool):
    """Draws a pawn at the coordinates passed in, on the board canvas"""
    global BoardCanvas
    row *= 50 * BoardScalar
    column *= 50 * BoardScalar
    a = 21 * BoardScalar + column
    b = 21 * BoardScalar + row

    c = 29 * BoardScalar + column
    d = 45 * BoardScalar + row

    if color:
        piece_color = WhiteColor
        highlight_color = WhiteHighlight
    else:
        piece_color = BlackColor
        highlight_color = BlackHighlight

    BoardCanvas.create_rectangle(a, b, c, d, fill=piece_color, activefill=highlight_color, outline=highlight_color)


def draw_bishop(row: int, column: int, color: bool):
    """Draws a bishop on the square passed in, on the board canvas"""
    global BoardCanvas
    row *= 50 * BoardScalar
    column *= 50 * BoardScalar
    a = 16 * BoardScalar + column
    b = 15 * BoardScalar + row

    c = 36 * BoardScalar + column
    d = 45 * BoardScalar + row

    if color:
        piece_color = WhiteColor
        highlight_color = WhiteHighlight
    else:
        piece_color = BlackColor
        highlight_color = BlackHighlight

    BoardCanvas.create_rectangle(a, b, c, d, fill=piece_color, activefill=highlight_color, outline=highlight_color)


def draw_rook(row: int, column: int, color: bool):
    """Draws a rook square passed in, on the board canvas"""
    global BoardCanvas
    row *= 50 * BoardScalar
    column *= 50 * BoardScalar
    a = 15 * BoardScalar + column
    b = 20 * BoardScalar + row

    c = 35 * BoardScalar + column
    d = 35 * BoardScalar + row

    e = 11 * BoardScalar + column
    f = 10 * BoardScalar + row

    g = 38 * BoardScalar + column
    h = 20 * BoardScalar + row

    i = 11 * BoardScalar + column
    j = 35 * BoardScalar + row

    k = 38 * BoardScalar + column
    l_ = 45 * BoardScalar + row

    if color:
        piece_color = WhiteColor
        highlight_color = WhiteHighlight
    else:
        piece_color = BlackColor
        highlight_color = BlackHighlight

    BoardCanvas.create_rectangle(a, b, c, d, fill=piece_color, activefill=highlight_color, outline=highlight_color)
    BoardCanvas.create_rectangle(e, f, g, h, fill=piece_color, activefill=highlight_color, outline=highlight_color)
    BoardCanvas.create_rectangle(i, j, k, l_, fill=piece_color, activefill=highlight_color, outline=highlight_color)


def draw_king(row: int, column: int, color: bool):
    """Draws a king on the square passed in, on the board canvas"""
    global BoardCanvas
    row *= 50 * BoardScalar
    column *= 50 * BoardScalar
    a = 15 * BoardScalar + column
    b = 15 * BoardScalar + row

    c = 38 * BoardScalar + column
    d = 45 * BoardScalar + row

    e = 25.5 * BoardScalar + column
    f = 15 * BoardScalar + row

    g = 25.5 * BoardScalar + column
    h = 8 * BoardScalar + row

    i = 28.5 * BoardScalar + column
    j = 15 * BoardScalar + row

    k = 30.5 * BoardScalar + column
    l_ = 8 * BoardScalar + row

    m = 22.5 * BoardScalar + column
    n = 15 * BoardScalar + row

    o = 20.5 * BoardScalar + column
    p = 8 * BoardScalar + row

    if color:
        piece_color = WhiteColor
        highlight_color = WhiteHighlight
    else:
        piece_color = BlackColor
        highlight_color = BlackHighlight

    BoardCanvas.create_line(e, f, g, h, width=3, fill=piece_color, activefill=highlight_color)
    BoardCanvas.create_line(i, j, k, l_, width=3, fill=piece_color, activefill=highlight_color)
    BoardCanvas.create_line(m, n, o, p, width=3, fill=piece_color, activefill=highlight_color)

    BoardCanvas.create_rectangle(a, b, c, d, fill=piece_color, activefill=highlight_color, outline=highlight_color)


def draw_queen(row: int, column: int, color: bool):
    """Draws a queen on the square passed in, on the board canvas"""
    global BoardCanvas
    row *= 50 * BoardScalar
    column *= 50 * BoardScalar
    a = 15 * BoardScalar + column
    b = 15 * BoardScalar + row

    c = 35 * BoardScalar + column
    d = 27.5 * BoardScalar + row

    e = 20 * BoardScalar + column
    f = 27.5 * BoardScalar + row

    g = 30 * BoardScalar + column
    h = 32.5 * BoardScalar + row

    i = 15 * BoardScalar + column
    j = 32.5 * BoardScalar + row

    k = 35 * BoardScalar + column
    l_ = 45 * BoardScalar + row

    m = 25.5 * BoardScalar + column
    n = 15 * BoardScalar + row

    o = 25.5 * BoardScalar + column
    p = 8 * BoardScalar + row

    q = 28.5 * BoardScalar + column
    r = 15 * BoardScalar + row

    s = 30.5 * BoardScalar + column
    t = 8 * BoardScalar + row

    u = 22.5 * BoardScalar + column
    v = 15 * BoardScalar + row

    w = 20.5 * BoardScalar + column
    x = 8 * BoardScalar + row

    if color:
        piece_color = WhiteColor
        highlight_color = WhiteHighlight
    else:
        piece_color = BlackColor
        highlight_color = BlackHighlight
    BoardCanvas.create_line(m, n, o, p, width=3, fill=piece_color, activefill=highlight_color)  # the lines of the crown
    BoardCanvas.create_line(q, r, s, t, width=3, fill=piece_color, activefill=highlight_color)
    BoardCanvas.create_line(u, v, w, x, width=3, fill=piece_color, activefill=highlight_color)

    BoardCanvas.create_rectangle(a, b, c, d, fill=piece_color, activefill=highlight_color,
                                 outline=highlight_color)  # the body
    BoardCanvas.create_rectangle(e, f, g, h, fill=piece_color, activefill=highlight_color, outline=highlight_color)
    BoardCanvas.create_rectangle(i, j, k, l_, fill=piece_color, activefill=highlight_color, outline=highlight_color)


def draw_knight(row: int, column: int, color: bool):
    """Draws a knight on the square passed in, on the board canvas"""
    global BoardCanvas
    row *= 50 * BoardScalar
    column *= 50 * BoardScalar
    a = 12 * BoardScalar + column
    b = 35 * BoardScalar + row

    c = 41 * BoardScalar + column
    d = 45 * BoardScalar + row

    e = 20 * BoardScalar + column
    f = 10 * BoardScalar + row

    g = 33 * BoardScalar + column
    h = 35 * BoardScalar + row

    i = 20 * BoardScalar + column
    j = 15 * BoardScalar + row

    k = 15 * BoardScalar + column
    l_ = 25 * BoardScalar + row

    if color:
        piece_color = WhiteColor
        highlight_color = WhiteHighlight
    else:
        piece_color = BlackColor
        highlight_color = BlackHighlight

    BoardCanvas.create_rectangle(a, b, c, d, fill=piece_color, activefill=highlight_color, outline=highlight_color)
    BoardCanvas.create_rectangle(e, f, g, h, fill=piece_color, activefill=highlight_color, outline=highlight_color)
    BoardCanvas.create_rectangle(i, j, k, l_, fill=piece_color, activefill=highlight_color, outline=highlight_color)


def check_move_input(boardstate: list[list[Tile]], move_input: str) -> str:
    """Verifies a move is a valid input, returns the valid input"""
    # Remove capitalization and whitespace
    move_input = move_input.strip().lower()

    # Check for special moves
    special_moves = ("resign", "draw")
    if move_input in special_moves:
        return move_input

    # Check length and formatting
    valid_len = len(move_input) == 4 or len(move_input) == 5
    if valid_len and move_input[0].isalpha() and move_input[2].isalpha() and move_input[1].isnumeric() and move_input[3].isnumeric():  # Checks if format is proper coordinate notation
        # Converting coordinate notation into board indices in a tuple
        coords = (column_index(move_input[0]), int(move_input[1]) - 1, column_index(move_input[2]), int(move_input[3]) - 1)

        # Checks that it's the proper turn for the piece to be moved
        piece_color = boardstate[coords[1]][coords[0]].color

        # Checks that it's within bounds
        in_bounds = 7 >= coords[0] >= 0 and 7 >= coords[1] >= 0 and 7 >= coords[2] >= 0 and 7 >= coords[3] >= 0
        if in_bounds and piece_color == Side:
            return move_input
        else:
            print(585, move_input, f"in bounds:{in_bounds}, correct_turn:{piece_color == Side}")
    else:
        print(586, move_input, "Invalid length and not special command")
    return "invalid"


def resign(boardstate: list[list[Tile]]) -> bool:
    """Handles the resignation game state"""
    global CheckmateLabel, GameEnd, MoveList

    # Adds the outcome to the PGN
    if Side:
        pgn_str = "Resignation: Black wins"
    else:
        pgn_str = "Resignation: White wins"
    MoveList.append(pgn_str)

    # Saves, updates display, sets GameEnd to True, and displays special resignation text on screen
    save_game()
    display_game(boardstate, Side)
    CheckmateLabel = ttk.Label(ContentFrame, text=pgn_str, style="TLabel")
    CheckmateLabel.grid(column=2, row=2, sticky="N")
    GameEnd = True
    return GameEnd


def play_move(boardstate: list[list[Tile]], move_input: str) -> bool:
    """Attempts to play the appropriate move(s) for a certain move_input in coordinate notation"""
    print(612, f"play move called for move: {move_input}")
    if move_input == "invalid":
        return False
    elif move_input == "resign":
        return resign(boardstate)
    elif move_input in ("e1g1", "e8g8"):
        return castle(boardstate, move_input, False)
    elif move_input in ("e1c1", "e8c8"):
        return castle(boardstate, move_input, True)

    # Chooses which piece movement function to call depending on the piece
    piece = boardstate[int(move_input[1]) - 1][column_index(move_input[0])].piece
    if piece == 1:
        return pawn_move(boardstate, move_input)
    elif piece == 2:
        return knight_move(boardstate, move_input)
    elif piece == 3:
        return bishop_move(boardstate, move_input)
    elif piece == 4:
        return rook_move(boardstate, move_input)
    elif piece == 5:
        return queen_move(boardstate, move_input)
    elif piece == 6:
        return king_move(boardstate, move_input)
    return False


def ascii_debug_display(boardstate):
    """Prints the board state to console with indices displayed"""
    for i in range(1, 9):
        print("\n", 8 - i, [display_int(boardstate[-i][j].piece, boardstate[-i][j].color) for j in range(8)])
    print("     0    1    2    3    4    5    6    7  \n")


def display_game(boardstate: list[list[Tile]], display_side: bool):
    """Updates GUI display to reflect boardstate. if display_side True, shows from White's perspective."""
    display_side = True
    # Updates ascii display
    ascii_debug_display(boardstate)

    # Blanks the board
    blank_board()

    # Builds board from White perspective
    if display_side:
        for i in range(8):
            for j in range(8):
                color = boardstate[-(i + 1)][j].color
                piece_type = boardstate[-(i + 1)][j].piece
                if piece_type == 0:
                    continue
                if piece_type == 1:
                    draw_pawn(i, j, color)
                elif piece_type == 2:
                    draw_knight(i, j, color)
                elif piece_type == 3:
                    draw_bishop(i, j, color)
                elif piece_type == 4:
                    draw_rook(i, j, color)
                elif piece_type == 5:
                    draw_queen(i, j, color)
                elif piece_type == 6:
                    draw_king(i, j, color)
                else:
                    print(566, "display error, invalid piece")

    # Builds board from Black perspective
    else:
        for i in range(8):
            for j in range(8):
                color = boardstate[i][-(j + 1)].color
                piece_type = boardstate[i][-(j + 1)].piece
                if piece_type == 0:
                    continue
                if piece_type == 1:
                    draw_pawn(i, j, color)
                elif piece_type == 2:
                    draw_knight(i, j, color)
                elif piece_type == 3:
                    draw_bishop(i, j, color)
                elif piece_type == 4:
                    draw_rook(i, j, color)
                elif piece_type == 5:
                    draw_queen(i, j, color)
                elif piece_type == 6:
                    draw_king(i, j, color)
                else:
                    print(589, "display error, invalid piece")


def column_index(column: str) -> int:
    """Turns a column letter into an array index integer"""
    columns = "abcdefgh"
    for i in range(8):
        if columns[i] == column:
            return i
    return -8


def cardinal_checks(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[tuple[int, int]]:
    """Returns a list of pieces in the cardinal directions who could be attacking the piece at col, row"""
    # Initialize output list
    output = []

    # Loops through each of the 4 cardinal directions
    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0),):
        for i in range(1, 8):
            # Assigns row and col indices for the square being checked
            row_i = row + dx * i
            col_i = col + dy * i

            # If out of bounds or line of sight blocked, break
            if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
                break

            # Recalls the Tile object at square to reduce calls to the boardstate list
            tile = boardstate[row_i][col_i]

            # If the square is empty, continue
            if tile.piece == 0:
                continue

            # Determine if the piece is an opponent
            opponent = tile.color != piece_side

            # If it's a piece on your side, that blocks line of sight
            # If it's an enemy piece, but it isn't a queen or a rook, it blocks line of sight and can't attack (kings are separate)
            # If it's anything else, it blocks line of sight, and must be a queen or rook, so its coordinates are added to the output
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
    # Initialize output list
    output = []

    # Runs through each of the four direction in order
    for dx, dy in ((1, 1), (-1, -1), (-1, 1), (1, -1)):
        for i in range(1, 8):
            # Assigns row and col indices for the square being checked
            row_i = row + i * dx
            col_i = col + i * dy

            # If out of bounds or line of sight blocked, continue
            if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
                break

            # Recalls the Tile object at square to reduce calls to the boardstate list
            tile = boardstate[row_i][col_i]

            # If it's empty, continue
            if tile.piece == 0:
                continue

            # Assuming it's not empty, determine if it's an opponent
            opponent = tile.color != piece_side

            # If it's a piece on your side, that blocks line of sight
            # If it's an enemy piece, but it isn't a queen or a bishop, it blocks line of sight and can't attack (kings and pawns are separate)
            # If it's anything else, it blocks line of sight, and must be a queen or bishop, so its coordinates are added to the output
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
    # Initializes output list
    output = []

    # Iterates through each of the 8 possible locations for a knight
    for dx, dy in ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)):
        row_i = row + dx
        col_i = col + dy

        # If out of bounds, continue
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
            continue

        # Recalls the Tile object at square to reduce calls to the boardstate list
        tile = boardstate[row_i][col_i]

        # Check if the square has a knight, and if not, continue
        if tile.piece != 2:
            continue

        # If it's an opponent's knight, add to output list
        if tile.color != piece_side:
            output.append((row_i, col_i))
    return output


def pawn_checks(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[tuple[int, int]]:
    """Returns a list of the indices of any pawns attacking the piece at row, col"""
    # Initializing output list
    output = []

    # The direction the pawn can attack from due to only moving forwards
    pawn_direct = -1 if piece_side else 1

    # Checks to the left and right
    for i in (-1, 1):
        row_i = row + pawn_direct
        col_i = col + i

        # If out of bounds, continue
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
            continue

        # Assigns the Tile object at the square to reduce reads from the main boardstate
        tile = boardstate[row_i][col_i]

        if tile.piece != 1:
            continue

        # If it's an opponent's pawn, add to output list
        if tile.color != piece_side:
            output.append((row_i, col_i))

    return output


def king_checks(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[tuple[int, int]]:
    """Returns a list of the indices of any king attacking the piece at row, col"""
    # Initializes output list
    output = []

    # Iterates through each of the 8 adjacent locations
    for dx, dy in ((1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)):
        row_i = row + dx
        col_i = col + dy

        # Checks if the square is in bounds
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
            continue

        # Assigns the Tile object at the square to reduce reads from the main boardstate
        tile = boardstate[row_i][col_i]

        if tile.piece != 6:
            continue

        # If it's an opponent's king, add to output list
        if tile.color != piece_side:
            output.append((row_i, col_i))

    return output


def under_attack(boardstate: list[list[Tile]], piece_side: bool, row: int, col: int) -> list[tuple[int, int]]:
    """Determines if a square is under attack by any other pieces, returns a list of tuples containing the board indices of each attacker"""
    # If row or column values aren't valid, returns empty list
    if row is None or col is None:
        return []

    attacking_coords = []

    # Check cardinal directions
    attacking_coords.extend(cardinal_checks(boardstate, row, col, piece_side))

    # Checks the diagonals for queens and bishops
    attacking_coords.extend(diagonal_checks(boardstate, row, col, piece_side))

    # Checks for knights in either of the 8 possible squares
    attacking_coords.extend(knight_checks(boardstate, row, col, piece_side))

    # Checks for pawns, direction is based on the side
    attacking_coords.extend(pawn_checks(boardstate, row, col, piece_side))

    # Checks for kings
    attacking_coords.extend(king_checks(boardstate, row, col, piece_side))

    return attacking_coords


def put_king_in_check(boardstate: list[list[Tile]], k_row: int, k_col: int, row_1: int, col_1: int, row_2: int, col_2: int, king_side: bool) -> bool:
    """Checks if said move puts the king into check. For non-king moves"""
    # Stores data to reconstitute
    start_piece = boardstate[row_1][col_1].piece
    end_piece = boardstate[row_2][col_2].piece
    start_move = boardstate[row_1][col_1].move
    end_move = boardstate[row_2][col_2].move
    start_color = boardstate[row_1][col_1].color
    end_color = boardstate[row_2][col_2].color

    # Simulates the move
    boardstate = simple_update(boardstate, row_1, col_1, row_2, col_2)

    # Checks for check
    in_check = True if under_attack(boardstate, king_side, k_row, k_col) else False

    # Reconstitutes the board from prior to the simulation
    boardstate[row_1][col_1].piece = start_piece
    boardstate[row_2][col_2].piece = end_piece
    boardstate[row_1][col_1].move = start_move
    boardstate[row_2][col_2].move = end_move
    boardstate[row_1][col_1].color = start_color
    boardstate[row_2][col_2].color = end_color

    return in_check


def find_king(boardstate: list[list[Tile]], side: bool) -> tuple[int, int]:
    """Returns a tuple of the king's coordinates (the king of the passed in side)"""

    # Iterates through the board until it finds the relevant king
    for i in range(8):
        for j in range(8):
            if boardstate[i][j].piece == 6 and boardstate[i][j].color == side:
                return i, j


def legal_king_moves(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[str]:
    # Initializes output list
    output = []

    # Iterates through each of the 8 adjacent locations
    for dx, dy in ((1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)):
        row_i = row + dx
        col_i = col + dy

        # Checks if the square is in bounds
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
            continue

        # Assigns the Tile object at the square to reduce reads from the main boardstate
        tile = boardstate[row_i][col_i]

        # Checks if the square can be moved to, without checking for checks (empty, or opponent's piece)
        legal_square = tile.piece == 0 or tile.color != piece_side

        # Then check if that move puts the king in check
        if legal_square and not put_king_in_check(boardstate, row_i, col_i, row, col, row_i, col_i, piece_side):
            output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")

    return output


def legal_castling(boardstate: list[list[Tile]], row: int, col: int, piece_side: bool) -> list[str]:
    """Checks for castling, returns list of coordinates for each one ('g1', 'c1', 'g8', 'c8' for castling)"""
    output = []

    i = 0  #
    rook = 4
    king = 6
    king_j = 2
    rook_i = 0
    rook_j = 3
    kr_side = True
    extra_clear = boardstate[i][1].piece == 0

    for long in [True, False]:
        if not Side:
            i = 7
            kr_side = False
        if not long:
            king_j = 6
            rook_i = 7
            rook_j = 5
            extra_clear = True

        king_legal = boardstate[i][4].piece == king and boardstate[i][4].move == 0
        rook_legal = boardstate[i][rook_i].piece == rook and boardstate[i][rook_i].move == 0
        checks = not under_attack(boardstate, kr_side, i, 4) and not under_attack(boardstate, kr_side, i, king_j) and not under_attack(boardstate, kr_side, i, rook_j)
        clear = boardstate[i][rook_j].piece == 0 and boardstate[i][king_j].piece == 0 and extra_clear

        if king_legal and rook_legal and checks and clear and long:
            output.append(f"c{i + 1}")
        if king_legal and rook_legal and checks and clear and not long:
            output.append(f"g{i + 1}")

    return output


def legal_knight_moves(boardstate: list[list[Tile]], row: int, col: int, k_row: int, k_col: int, piece_side: bool) -> list[str]:
    """Returns a list of the coordinates of all legal moves for a knight at row, col"""
    # Initializes output list
    output = []

    # Iterates through each of the 8 possible locations for a knight
    for dx, dy in ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)):
        row_i = row + dx
        col_i = col + dy

        # If out of bounds, continue
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
            continue

        # Recalls the Tile object at square to reduce calls to the boardstate list
        tile = boardstate[row_i][col_i]

        # If it's an opponent or an empty square, and it doesn't put the king in check
        if (tile.piece == 0 or tile.color != piece_side) and not put_king_in_check(boardstate, k_row, k_col, row, col, row_i, col_i, piece_side):
            output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")

    return output


def legal_pawn_moves(boardstate: list[list[Tile]], row: int, col: int, k_row: int, k_col: int, piece_side: bool) -> list[str]:
    """Returns a list of coordinates the pawn can move to/capture"""
    # Initializing output list
    output = []

    # The direction the pawn can move due to only moving forwards
    pawn_direct = 1 if piece_side else -1

    # Moving forwards
    for distance in [1, 2]:
        row_i = row + distance * pawn_direct

        # If out of bounds, continue
        if not 0 <= row_i <= 7:
            break

        # Assigns the Tile object at the square to reduce reads from the main boardstate
        tile = boardstate[row_i][col]

        # If the piece isn't empty, or it's a distance of two but not the pawn's first move, break
        if tile.piece != 0 or distance == 2 and boardstate[row][col].move:
            break

        if not put_king_in_check(boardstate, k_row, k_col, row, col, row_i, col, piece_side):
            output.append(f"{'abcdefgh'[col]}{row_i + 1}")

    # Diagonal captures
    for i in (-1, 1):
        row_i = row + pawn_direct
        col_i = col + i

        # If out of bounds, continue
        if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
            continue

        # Assigns the Tile object at the square to reduce reads from the main boardstate
        tile = boardstate[row_i][col_i]

        # If the target square is empty, it can't be captured as a move
        if tile.piece == 0:
            continue

        # If it's an opponent's pawn, add to output list
        if tile.color != piece_side:
            output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")

    return output


def legal_diag_moves(boardstate: list[list[Tile]], row: int, col: int, k_row: int, k_col: int, piece_side: bool) -> list[str]:
    """Returns a list of the indexes of any squares on the diagonals which are legal moves"""
    # Initialize output list
    output = []

    # Runs through each of the four direction in order
    for dx, dy in ((1, 1), (-1, -1), (-1, 1), (1, -1)):
        for i in range(1, 8):
            # Assigns row and col indices for the square being checked
            row_i = row + i * dx
            col_i = col + i * dy

            # If out of bounds, break
            if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
                break

            # Recalls the Tile object at square to reduce calls to the boardstate list
            tile = boardstate[row_i][col_i]

            # Determine if it's an opponent
            opponent = tile.color != piece_side

            # If it's not empty, and same side, break
            if tile.piece != 0 and not opponent:
                break

            # If moving in this direction puts the king in check, break TODO: determine if this results in any potentially illegal moves rather than using continue
            if put_king_in_check(boardstate, k_row, k_col, row, col, row_i, col_i, piece_side):
                break

            # If it's an empty square, add to list and continue
            if tile.piece == 0:
                output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
                continue

            # If it's not empty, but is capturable, add to output and then break
            if opponent:
                output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
                break

    return output


def legal_cardinal_moves(boardstate: list[list[Tile]], row: int, col: int, k_row: int, k_col: int, piece_side: bool) -> list[str]:
    """Returns a list of coords in the cardinal directions that the piece at row, col could legally move to"""
    # Initialize output list
    output = []

    # Loops through each of the 4 cardinal directions
    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0),):
        for i in range(1, 8):
            # Assigns row and col indices for the square being checked
            row_i = row + dx * i
            col_i = col + dy * i

            # If out of bounds, break
            if not 0 <= row_i <= 7 or not 0 <= col_i <= 7:
                break

            # Recalls the Tile object at square to reduce calls to the boardstate list
            tile = boardstate[row_i][col_i]

            # Determine if it's an opponent
            opponent = tile.color != piece_side

            # If it's not empty, and same side, break
            if tile.piece != 0 and not opponent:
                break

            # If moving in this direction puts the king in check, break TODO: determine if this results in any potentially illegal moves rather than using continue
            if put_king_in_check(boardstate, k_row, k_col, row, col, row_i, col_i, piece_side):
                break

            # If it's an empty square, add to list and continue
            if tile.piece == 0:
                output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
                continue

            # If it's not empty, but is capturable, add to output and then break
            if opponent:
                output.append(f"{'abcdefgh'[col_i]}{row_i + 1}")
                break

    return output


def legal_queen_moves(boardstate: list[list[Tile]], row: int, col: int, k_row: int, k_col: int, piece_side: bool) -> list[str]:
    """Combines diagonal and cardinal move checks"""
    return legal_cardinal_moves(boardstate, row, col, k_row, k_col, piece_side) + legal_diag_moves(boardstate, row, col, k_row, k_col, piece_side)


def king_and_castle_moves(boardstate: list[list[Tile]], row: int, col: int, k_row: int, k_col: int, piece_side: bool) -> list[str]:
    """Combines diagonal and cardinal move checks"""
    return legal_king_moves(boardstate, row, col, piece_side) + legal_castling(boardstate, row, col, piece_side)


# Call dictionary for has_moves
check_moves = {
        1: legal_pawn_moves,
        2: legal_knight_moves,
        3: legal_diag_moves,
        4: legal_cardinal_moves,
        5: legal_queen_moves,
        6: king_and_castle_moves
    }


def fetch_moves(boardstate: list[list[Tile]], row: int, col: int) -> list[str]:
    """Checks if the piece at the coordinates has any legal moves. Returns a list of target coordinates for each legal move it does have, ie ['e3', 'e4'] """
    # Evaluates the piece, the color of the piece, and initializes the list of return moves
    tile = boardstate[row][col]
    piece_type, piece_side = tile.piece, tile.color

    # Tries to find the king, returns an empty list of moves if no king can be found
    try:
        k_row, k_col = find_king(boardstate, piece_side)
    except (IndexError, ValueError, TypeError):
        return []

    # Calls the appropriate functions for movement checks. TODO: en passant
    return check_moves[piece_type](boardstate, row, col, k_row, k_col, piece_side) if piece_type else []


def is_checkmate(boardstate: list[list[Tile]], side: bool, a_row: int, a_col: int, k_row: int, k_col: int) -> bool:
    skip_block_checks = False
    king_tile = boardstate[k_row][k_col]
    check_tile = boardstate[a_row][a_col]

    # Verifies that the piece in question is a king
    if king_tile.piece != 6:
        return False

    # Verifies that it's an opponent
    if check_tile.color == king_tile.color:
        return False

    # Determines if the checking piece is knight, as it won't need to check for blocking moves
    if check_tile.piece == 2:
        skip_block_checks = True

    # If the attacking piece is itself under attack, it may not be checkmate
    possible_counter_takers = under_attack(boardstate, side, a_row, a_col)
    for capture in possible_counter_takers:
        if boardstate[capture[0]][capture[1]].piece == 6:
            if not under_attack(boardstate, not side, a_row, a_col):
                return False
            else:
                continue
        else:
            return False

    # Checks for legal king moves
    if fetch_moves(boardstate, k_row, k_col):
        return False

    # If the piece isn't a knight, runs code to determine if a piece can block the check
    if not skip_block_checks:

        # Calculate all the moves that could theoretically block the line of sight
        potential_blockers = calculate_squares_between(not side, a_row, a_col, k_row, k_col)
        for i in range(len(potential_blockers)):

            # Translate coordinate notation into board indices
            row_1 = potential_blockers[i][0][0]
            col_1 = potential_blockers[i][0][1]
            col_2 = potential_blockers[i][1][1]
            row_2 = potential_blockers[i][1][0]

            if not 0 <= row_1 <= 7 or not 0 <= col_1 <= 7 or not 0 <= row_2 <= 7 or not 0 <= col_2 <= 7:
                continue

            # Store data for undoing test simulation on boardstate
            piece_1 = boardstate[row_1][col_1].piece
            move_1 = boardstate[row_1][col_1].move
            color_1 = boardstate[row_1][col_1].color
            piece_2 = boardstate[row_2][col_2].piece
            move_2 = boardstate[row_2][col_2].move
            color_2 = boardstate[row_2][col_2].color

            # Simulate the board, check if king is left under attack
            boardstate = simple_update(boardstate, row_1, col_1, row_2, col_2)
            attacked = under_attack(boardstate, side, k_row, k_col)

            # Undo board simulation
            boardstate[row_1][col_1].piece = piece_1
            boardstate[row_1][col_1].move = move_1
            boardstate[row_1][col_1].color = color_1
            boardstate[row_2][col_2].piece = piece_2
            boardstate[row_2][col_2].move = move_2
            boardstate[row_2][col_2].color = color_2

            if attacked is None:
                return False

    return True


def is_stalemate(boardstate: list[list[Tile]]) -> bool:
    """Determines if a position is stalemate"""
    # Default True, if a move is found, set to not be a stalemate
    white_stalemated = True
    black_stalemated = None

    # Iterates through each square on the board
    for i in range(8):
        for j in range(8):
            tile = boardstate[i][j]

            # If the piece isn't empty, checks if it has legal moves
            if tile.piece != 0:
                moves = fetch_moves(boardstate, i, j)
            else:
                continue

            if tile.color:
                if len(moves) != 0:
                    white_stalemated = False
            if not tile.color:
                if len(moves) != 0:
                    black_stalemated = False

    return white_stalemated or black_stalemated


def calculate_squares_between(side: bool, a_row: int, a_col: int, k_row: int, k_col: int) -> list[list[list[int]]]:
    """Returns a list of all pieces that could theoretically block the line of attack between the coordinates that are
    passed in. The output is structured like this: the primary list holds the secondary lists. the secondary lists each
    hold two 3rd tier lists, each one of which contains a pair of coords [row, col] the therefor [0][0][0] would get the
    first pair of coordinates, the first coordinate (which is the starting position of a piece that could block check)
    and then grab the row from that coord. Pass in the side of the piece you are checking as the *target*"""
    row_diff = a_row - k_row
    col_diff = a_col - k_col
    move_output = []
    row_direct = 0
    col_direct = 0
    distance = 0
    if col_diff == 0 or row_diff == 0:
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
        attacking_coords = under_attack(GameArray, not side, pos_move_row, pos_move_col)
        for coord in attacking_coords:
            coord_pair = [coord, [pos_move_row, pos_move_col]]
            move_output.append(coord_pair)

    return move_output  # This is a list of all potential pieces (their coordinates) that could theoretically block the line of attack between the two given coordinate sets, paired with the square they would move to


def piece_move(boardstate: list[list[Tile]], move_input: str, col_1: int, col_2: int, row_1: int, row_2: int) -> bool:
    """Moves piece from coord_1 to coord_2, and checks for legality, and game results. Returns False if illegal"""
    global MoveCount, MoveList, Side, Root, ContentFrame, GameEnd, CheckmateLabel, MoveInputList, GameArray
    print(1323, f"piece move called for the move {'abcdefgh'[col_1]}{row_1 + 1}{'abcdefgh'[col_2]}{row_2 + 1}")

    # Initializing variables
    undo = False
    k_row = None
    k_col = None
    ended = False
    promotion = None
    enemy_k_row = None
    enemy_k_col = None

    # Storing piece data so that the move can be reverted if it results in an illegal position
    tile_1 = boardstate[row_1][col_1]
    tile_2 = boardstate[row_2][col_2]
    piece_1 = tile_1.piece
    move_1 = tile_1.move
    color_1 = tile_1.color
    piece_2 = tile_2.piece
    move_2 = tile_2.move
    color_2 = tile_2.color

    # Fetching data for PGN output
    pgn_str = " "
    pgn_target = display_int(tile_2.piece, tile_2.color)
    pgn_column = 'abcdefgh'[col_2]  # outputs pgn type for each move
    pgn_column_start = 'abcdefgh'[col_1]
    pgn_1 = display_int(tile_1.piece, True)

    # Special PGN notation for pawn takes moves
    if piece_1 == 1:
        if pgn_target != " " and pgn_target != "P":
            pgn_1 = f"{pgn_column_start}x{pgn_target}"
        elif pgn_target != " " and pgn_target == "P":
            pgn_1 = f"{pgn_column_start}x"
        else:
            pgn_1 = ""

    if color_1 == Side:  # Verifying the piece is the appropriate piece for the turn
        if piece_1 == 1:  # Checking if the piece is a pawn eligible for promotion
            if Side and row_2 == 7 or not Side and row_2 == 0:
                try:
                    promotion = move_input[4].lower()
                except TypeError:
                    promotion = "q"
                except IndexError:
                    promotion = "q"
                if promotion != "q" and promotion != "b" and promotion != "n" and promotion != "r":  # Defaults to a queen
                    promotion = "q"
                tile_2.piece = piece_to_int(promotion)
                tile_2.color = color_1
        if promotion is None:
            tile_2.piece = piece_1
            tile_2.color = color_1

        # Normal movement block
        tile_2.move = True
        tile_1.piece = 0
        tile_1.color = False
        tile_1.move = False
    else:
        print("wrong turn/piece")
        return False
    print(1201)
    # Finds the kings
    for row_i in range(8):
        for col_i in range(8):
            if boardstate[row_i][col_i].piece == 6 and boardstate[row_i][col_i].color == Side:
                k_row = row_i
                k_col = col_i
            if boardstate[row_i][col_i].piece == 6 and boardstate[row_i][col_i].color != Side:
                enemy_k_row = row_i
                enemy_k_col = col_i
    print(1211, k_row, k_col, enemy_k_row, enemy_k_col)
    # If it can't find both kings, it undoes the move
    # If it can, it checks if the move leaves it under attack, in which case it undoes the move
    if k_row is None or k_col is None or enemy_k_row is None or enemy_k_col is None:
        print(1215, "couldn't find both kings")
        undo = True
    else:
        if under_attack(boardstate, Side, k_row, k_col) or undo:
            print("puts in check/illegal move", undo)
            tile_1.piece = piece_1
            tile_1.move = move_1
            tile_1.color = color_1
            tile_2.piece = piece_2
            tile_2.move = move_2
            tile_2.color = color_2
            undo = False
            return False

    cols = "abcdefgh"
    moves_since_pawn = 0
    current_fen = fen_from_array(boardstate, not Side)
    for move in MoveList:  # Counts moves since the last pawn move (for 50 move rule)
        for col in cols:
            if move[0] == col:
                moves_since_pawn = 0
        moves_since_pawn += 1

    for coords in under_attack(boardstate, not Side, enemy_k_row, enemy_k_col):
        print(1238, coords)
        attacker = boardstate[coords[0]][coords[1]].piece
        a_row = coords[0]
        a_col = coords[1]
        if is_checkmate(boardstate, Side, a_row, a_col, enemy_k_row, enemy_k_col):
            print("Checkmate!")
            color = "white" if Side else "black"
            pgn_str = f"Checkmate: {color} wins"
            ended = True
    if not ended and moves_since_pawn >= 100:
        pgn_str = "Draw: 50 move rule"
        ended = True
    if not ended and is_stalemate(boardstate):
        print(1416, "stalemate")
        pgn_str = "Stalemate: draw"
        ended = True
    if not ended and is_threefold(current_fen):
        pgn_str = "Threefold Repetition: draw"
        ended = True
    if ended:
        print(1423, "ended")
        MoveList.append(f"{pgn_1}{pgn_column}{row_2 + 1}")
        MoveList.append(pgn_str)
        save_game()
        display_game(boardstate, Side)
        CheckmateLabel = ttk.Label(ContentFrame, text=pgn_str, style="TLabel")
        CheckmateLabel.grid(column=2, row=2, sticky="N")
        GameEnd = True

    if Side and not ended:
        print("\nBlack to move")
    if not Side and not ended:
        print("\nWhite to move")

    if move_input in "o-oO-O" or move_input in "o-o-oO-O-O":  # compiles each move into one list of moves
        if piece_1 == 4:
            if Side:
                MoveList.append(move_input.upper())
            else:
                MoveList.append(move_input.lower())
            MoveInputList.append(f"{piece_1}{move_input}")
            MoveCount += 1
            Side = not Side
            GameArray = boardstate
            return True
    else:
        print(1447, "standard move")
        Side = not Side
        MoveInputList.append(f"{piece_1}{move_input}")
        MoveList.append(f"{pgn_1}{pgn_column}{row_2 + 1}")
        MoveCount += 1
        GameArray = boardstate
        return True


def save_game():
    print(1467, "game saved")
    pgn_str = ""
    if MoveCount > 0:
        now = datetime.datetime.now()  # Gets the current timestamp
        for move in MoveList:
            pgn_str += str(move)
            pgn_str += " "
        previous_games = open("pgn_log.txt", "a")
        pgn_str = str(now) + ": " + pgn_str + f"Move count:{MoveCount} \n\n"
        previous_games.write(pgn_str)
        previous_games.close()


def rook_move(boardstate: list[list[Tile]], move_input: str) -> bool:
    """Logic for legal rook moves"""
    col_1 = column_index(move_input[0])
    row_1 = int(move_input[1]) - 1
    col_2 = column_index(move_input[2])
    row_2 = int(move_input[3]) - 1

    piece_1 = boardstate[row_1][col_1].piece
    color_1 = boardstate[row_1][col_1].color
    piece_2 = boardstate[row_2][col_2].piece
    color_2 = boardstate[row_2][col_2].color

    row_direction = 1
    column_direction = 1

    move_length = abs(row_2 - row_1) + abs(col_2 - col_1)
    legal_target = (color_1 != color_2 or piece_2 == 0) and piece_1 == 4

    if row_2 < row_1:
        row_direction = -1
    if row_2 < col_1:
        column_direction = -1

    if col_1 == col_2 and legal_target:
        for i in range(1, move_length):
            row_i = (i * row_direction) + row_1
            if boardstate[row_i][col_2].piece != 0:
                return False
        return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)

    elif row_1 == row_2 and legal_target:
        for i in range(1, move_length):
            column_i = i * column_direction
            if boardstate[row_2][column_i].piece != 0:
                return False
        return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)
    else:
        return False


def bishop_move(boardstate: list[list[Tile]], move_input: str) -> bool:
    """Logic for legal bishop moves"""
    row_direction = 1
    column_direction = 1

    col_1 = column_index(move_input[0])
    row_1 = int(move_input[1]) - 1
    col_2 = column_index(move_input[2])
    row_2 = int(move_input[3]) - 1

    tile_1 = boardstate[row_1][col_1]
    tile_2 = boardstate[row_2][col_2]

    move_length = abs(row_1 - row_2)
    legal_target = (tile_1.color != tile_2.color or tile_2.piece == 0) and tile_1.piece == 3  # true if legal move

    if row_2 < row_1:
        row_direction = -1
    if col_2 < col_1:
        column_direction = -1

    if (row_2 - row_1) * row_direction == (col_2 - col_1) * column_direction and legal_target:
        for i in range(1, move_length):
            row_i = i * row_direction + row_1
            column_i = i * column_direction + col_1
            if boardstate[row_i][column_i].piece != 0:
                return False
        return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)
    else:
        return False


def queen_move(boardstate: list[list[Tile]], move_input: str) -> bool:
    """Logic for legal queen moves"""
    col_1 = column_index(move_input[0])
    row_1 = int(move_input[1]) - 1
    col_2 = column_index(move_input[2])
    row_2 = int(move_input[3]) - 1
    move_length = abs(row_1 - row_2)
    row_direction = 1
    column_direction = 1
    tile_1 = boardstate[row_1][col_1]
    tile_2 = boardstate[row_2][col_2]
    legal_target = (tile_1.color != tile_2.color or tile_2.piece == 0) and tile_1.piece == 5  # true if legal move

    if row_2 < row_1:
        row_direction = -1
    if col_2 < col_1:
        column_direction = -1

    if col_1 == col_2 and legal_target:  # true if the queen is only moving along the same column
        for i in range(1, move_length):
            row_i = row_1 + (row_direction * i)
            if boardstate[row_i][col_2].piece != 0:  # checks that every square along the way is empty
                return False
        return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)  # updates board array

    elif row_1 == row_2 and legal_target:  # true if the queen is only moving along the same row
        for i in range(1, move_length):
            column_i = col_1 + (column_direction * i)
            if boardstate[row_2][column_i].piece != 0:  # checks that every square along the way is empty
                return False
        return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)  # updates board array

    elif row_1 != row_2 and col_1 != col_2:  # case where the target square is on a diagonal
        if (row_2 - row_1) * row_direction == (
                col_2 - col_1) * column_direction and legal_target:  # checks that it's on a proper diagonal, and if legal target
            for i in range(1, move_length):
                row_i = (i * row_direction) + row_1
                column_i = (i * column_direction) + col_1
                if boardstate[row_i][column_i].piece != 0:  # checks that each square along the path is empty
                    return False
            return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)  # updates the board array

        else:
            return False

    else:
        return False


def knight_move(boardstate: list[list[Tile]], move_input: str) -> bool:
    """Logic for legal knight moves"""
    col_1 = column_index(move_input[0])
    row_1 = int(move_input[1]) - 1
    col_2 = column_index(move_input[2])
    row_2 = int(move_input[3]) - 1
    tile_1 = boardstate[row_1][col_1]
    tile_2 = boardstate[row_2][col_2]
    legal_target = (tile_1.color != tile_2.color or tile_2.piece == 0) and tile_1.piece == 2  # checks if the target square is empty or an opponent's piece

    if row_2 >= row_1:  # determines whether the row direction is up or down
        row_direction = 1
    else:
        row_direction = -1

    if col_2 >= col_1:  # determines whether the column direction is left or right
        column_direction = 1
    else:
        column_direction = -1

    horizontal_row_check = row_1 + row_direction * 1 == row_2  # these lines check that the target is a legal knight move
    horizontal_column_check = col_1 + column_direction * 2 == col_2
    vertical_row_check = row_1 + row_direction * 2 == row_2
    vertical_column_check = col_1 + column_direction * 1 == col_2

    if vertical_column_check and vertical_row_check and legal_target or horizontal_column_check and horizontal_row_check and legal_target:  # checks that everything is legal and checks out
        return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)
    else:
        return False


def king_move(boardstate: list[list[Tile]], move_input: str) -> bool:
    """Logic for legal king moves"""
    col_1 = column_index(move_input[0])
    row_1 = int(move_input[1]) - 1
    col_2 = column_index(move_input[2])
    row_2 = int(move_input[3]) - 1

    tile_1 = boardstate[row_1][col_1]
    tile_2 = boardstate[row_2][col_2]

    legal_target = tile_2.piece == 0 or (tile_1.color != tile_2.color)

    print(1460, tile_1.piece, legal_target, move_input)

    if legal_target and tile_1.piece == 6:
        return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)
    return False


def pawn_move(boardstate: list[list[Tile]], move_input: str) -> bool:
    """Logic for legal pawn moves"""
    global GameArray
    last_move_col = 0
    last_move_piece = 0
    last_move_row_1 = 0
    last_move_row_2 = 0
    passant_row = False
    passant_col = False
    legal_target_move = False
    legal_target_attack = False
    row_1 = int(move_input[1]) - 1
    row_2 = int(move_input[3]) - 1
    col_1 = column_index(move_input[0])
    col_2 = column_index(move_input[2])
    tile_1 = boardstate[row_1][col_1]
    tile_2 = boardstate[row_2][col_2]

    pawn_direction = 1 if tile_1.color else -1  # Used to determine which direction the pawn can move
    print(1484, pawn_direction)

    empty_target = tile_2.piece == 0
    is_straight = col_1 == col_2
    distance = abs(row_1 - row_2)
    row_distance = 2 >= distance >= 1
    right_way = pawn_direction * abs(row_1 - row_2) + row_1 == row_2
    is_diag = abs(row_1 - row_2) == abs(col_1 - col_2) and abs(row_1 - row_2) == 1
    is_opponent = tile_1.color != tile_2.color and tile_2.piece != 0

    legal_target_attack = is_diag and right_way and is_opponent  # True if legal for attacking a piece directly diagonal one square left or right
    legal_target_move = is_straight and right_way and empty_target and row_distance

    # print(1290, is_diag, right_way, is_opponent, "\n", is_straight, right_way, empty_target, distance, first_move)

    if legal_target_attack or legal_target_move:  # Normal move or attack
        if distance == 1 or (distance == 2 and not tile_1.move):
            return piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)

    # En Passant logic:
    try:
        last_move_row_1 = int(MoveInputList[-1][1]) - 1
        last_move_row_2 = int(MoveInputList[-1][3]) - 1
        last_move_double = abs(last_move_row_1 - last_move_row_2) == 2
        last_move_piece = MoveInputList[-1][0] in "Pp"
        last_move_col = column_index(MoveInputList[-1][0])
        # print(1303, MoveInputList[-1])
    except ValueError:
        last_move_double = False
    except IndexError:
        last_move_double = False

    if last_move_piece and last_move_double:
        passant_row = row_1 == 4 and Side or row_1 == 3 and not Side
        passant_col = last_move_col == col_1
        if passant_col and passant_row:
            piece_move(boardstate, move_input, col_1, col_2, row_1, row_2)  # Moves the pawn
            # print(1299, last_move_col, last_move_row_2)
            GameArray[last_move_row_2][last_move_col].piece = 0  # Removes the pawn captured by en passant
            GameArray[last_move_row_2][last_move_col].move = False
            GameArray[last_move_row_2][last_move_col].color = False
            return True


def castle(boardstate: list[list[Tile]], move_input: str, long: bool) -> bool:
    """Logic for legal castling"""
    global MoveCount, Side
    i = 0  #
    rook = 4
    king = 6
    king_j = 2
    rook_i = 0
    rook_j = 3
    extra_clear = GameArray[i][1].piece == 0

    if not Side:
        i = 7
    if not long:
        king_j = 6
        rook_i = 7
        rook_j = 5
        extra_clear = True

    king_legal = boardstate[i][4].piece == king and boardstate[i][4].move == 0
    rook_legal = boardstate[i][rook_i].piece == rook and boardstate[i][rook_i].move == 0
    checks = not under_attack(boardstate, Side, i, 4) and not under_attack(boardstate, Side, i, king_j) and not under_attack(boardstate, Side, i, rook_j)
    clear = boardstate[i][rook_j].piece == 0 and boardstate[i][king_j].piece == 0 and extra_clear
    # print(1350, king_legal, rook_legal, checks, clear, GameArray[i][4].move == 0, GameArray[i][4].piece == king)

    if king_legal and rook_legal and checks and clear:
        piece_move(boardstate, move_input, 4, king_j, i, i)
        Side = not Side
        piece_move(boardstate, f"{'abcdefgh'[i]}{rook_i + 1}{'abcdefgh'[i]}{rook_j + 1}", rook_i, rook_j, i, i)
        return True
    else:
        return False


def evaluate_position(boardstate: list[list[Tile]]) -> int:
    """Evaluates a position based on material, negative if black is winning"""
    evaluation = 0

    # if checkmate, count evaluation = 100000 etc
    for i in range(8):
        for j in range(8):
            tile = boardstate[i][j]
            if tile.piece == 0:
                continue
            if tile.piece == 6:
                attackers = under_attack(boardstate, False, i, j)
                for attacking_coords in attackers:
                    king_side = tile.color
                    if is_checkmate(boardstate, king_side, attacking_coords[0], attacking_coords[1], i, j):
                        return 100000 if king_side else -100000
            count = 0
            if tile.color:
                table_y = 7 - i
                table_x = j
            else:
                table_y = i
                table_x = j
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
                pass
            if tile.color:
                evaluation += count
                count = 0
            else:
                evaluation -= count
                count = 0
    return evaluation


def simple_update(boardstate: list[list[Tile]], row_1: int, col_1: int, row_2: int, col_2: int) -> list[list[Tile]]:
    tile_1 = boardstate[row_1][col_1]
    tile_2 = boardstate[row_2][col_2]
    tile_2.piece = tile_1.piece
    tile_2.move = tile_1.move
    tile_2.color = tile_1.color
    tile_1.piece = 0
    tile_1.move = True
    tile_1.color = False
    return boardstate


def first_layer(boardstate: list[list[Tile]], side: bool) -> list[list[str]]:
    """Calculates all legal moves from a position for one side"""
    possible_moves_1 = []
    for row in range(8):
        for col in range(8):
            if boardstate[row][col].piece != 0 and boardstate[row][col].color == side:
                for coord in fetch_moves(boardstate, row, col):
                    possible_moves_1.append([f"{'abcdefgh'[col]}{row + 1}{coord}"])
    return possible_moves_1


def intermediate_layer(boardstate: list[list[Tile]], move_list_list: list[list[str]], side: bool, move_count: int, depth: int) -> list[list[str]]:
    """Calculates all the legal moves at a certain depth"""
    # Memory allocation for the possible moves string
    possible_moves = [[] for _ in range(move_count)]
    count = 0

    # Loops through each of the moves branches it's fed
    for move_list in move_list_list:
        if not move_list:
            continue
        undo_moves = [(0, False, False, 0, 0, 0, False, False, 0, 0) for _ in range(depth)]

        #  Makes all the necessary moves to get the boardstate into the relevant position
        for i in range(depth):
            # print(1725, i)

            # Turns the move string into coords
            row_s = int(move_list[i][1]) - 1
            col_s = int(column_index(move_list[i][0]))
            row_e = int(move_list[i][3]) - 1
            col_e = int(column_index(move_list[i][2]))

            # Grabs the piece and move values at said target
            tile_1 = boardstate[row_s][col_s]
            tile_2 = boardstate[row_e][col_e]
            piece_target = tile_2.piece
            piece_start = tile_1.piece
            move_target = tile_2.move
            move_start = tile_1.move
            color_target = tile_2.color
            color_start = tile_1.color

            # Stores information so it can be undone later
            undo_moves[i] = (piece_start, move_start, color_start, row_s, col_s, piece_target, move_target, color_target, row_e, col_e)

            # Makes the move
            boardstate = simple_update(boardstate, row_s, col_s, row_e, col_e)

        # Finds legal moves and puts them in the possible_moves list, as well as the branch of the move tree that got to it
        for row in range(8):
            for col in range(8):
                if boardstate[row][col].piece != 0 and boardstate[row][col].color == side:
                    for coord in fetch_moves(boardstate, row, col):
                        possible_moves[count] = move_list + [f"{'abcdefgh'[col]}{row + 1}{coord}"]
                        count += 1
                        # TotalMoveCalcs += 1

        # Undoes all the moves to get the boardstate back to its pristine condition
        for i in range(len(undo_moves)):
            move = undo_moves[-(i + 1)]
            tile_1 = boardstate[move[3]][move[4]]
            tile_2 = boardstate[move[8]][move[9]]
            tile_2.piece = move[5]
            tile_1.piece = move[0]
            tile_2.move = move[6]
            tile_1.move = move[1]
            tile_2.color = move[7]
            tile_1.color = move[2]

    return possible_moves


def final_layer(boardstate: list[list[Tile]], move_list_list: list[list[str]], side: bool, move_count: int, depth) -> list[list[str, int]]:
    """Calculates all the legal moves at a certain depth"""
    global TotalMoveCalcs

    # Counters
    count_2 = 0

    # Initializes the list that will hold the prior moves (depth 3) and their evaluations (which is based on these calculated moves and a sort)
    minimax = [[" ", " ", " ", 0] for _ in range(128000)]

    # Loops through each of the moves branches it's fed
    for move_list in move_list_list:
        if not move_list:
            continue

        # Counter for eval_list indexing assignment
        count = 0

        # Generates the blank list of tuples which will hold the data necessary to revert the simulated moves
        undo_moves = [(0, False, False, 0, 0, 0, False, False, 0, 0) for _ in range(depth)]

        # Initialized the list of move evaluations for this particular move_list
        fake_null = -10000 if side else 10000
        eval_list = [fake_null for _ in range(128)]

        #  Makes all the necessary moves to get the boardstate into the relevant position
        for i in range(depth):
            # print(1725, i)

            # Turns the move string into coords
            row_s = int(move_list[i][1]) - 1
            col_s = int(column_index(move_list[i][0]))
            row_e = int(move_list[i][3]) - 1
            col_e = int(column_index(move_list[i][2]))

            # Grabs the piece and move values at said target
            tile_1 = boardstate[row_s][col_s]
            tile_2 = boardstate[row_e][col_e]
            piece_target = tile_2.piece
            piece_start = tile_1.piece
            move_target = tile_2.move
            move_start = tile_1.move
            color_target = tile_2.color
            color_start = tile_1.color

            # Stores information so it can be undone later
            undo_moves[i] = (piece_start, move_start, color_start, row_s, col_s, piece_target, move_target, color_target, row_e, col_e)

            # Makes the move
            boardstate = simple_update(boardstate, row_s, col_s, row_e, col_e)

        # Finds legal moves and evaluates them, determining the best evaluation for each depth 3 move, and passing that out as a list, as well as the branch of the move tree that got to it
        # Iterates through each square on the board and checks if it's a relevant piece (the right color)
        for row in range(8):
            for col in range(8):
                if boardstate[row][col].piece != 0 and boardstate[row][col].color == side:
                    for coord in fetch_moves(boardstate, row, col):

                        # Converts coordinate notation into array coordinates
                        row_e = int(coord[1]) - 1
                        col_e = int(column_index(coord[0]))

                        # Grabs the piece and move values at said target
                        tile_1 = boardstate[row][col]
                        tile_2 = boardstate[row_e][col_e]
                        piece_target = tile_2.piece
                        piece_start = tile_1.piece
                        move_target = tile_2.move
                        move_start = tile_1.move
                        color_target = tile_2.color
                        color_start = tile_1.color

                        # Makes the suggested move and then evaluates it
                        boardstate = simple_update(boardstate, row, col, row_e, col_e)
                        pos_eval = evaluate_position(boardstate)

                        # Undoes the evaluation move
                        tile_2.piece = piece_target
                        tile_1.piece = piece_start
                        tile_2.move = move_target
                        tile_1.move = move_start
                        tile_2.color = color_target
                        tile_1.color = color_start

                        # Adds the move to the most list, with the evaluation after it
                        eval_list[count] = pos_eval
                        count += 1
                        TotalMoveCalcs += 1

        # Sorts the evaluations to find what the best move was for the player at depth 3
        # Populates the list with the move sequence and evaluation that it deserves
        # Weak error: eval_list is an int, move_list is a list of strings, pycharm doesn't like mixing the types (maybe fix, maybe ignore). Will be fixed by switching board representation to int
        eval_list.sort(reverse=side)
        # noinspection PyTypeChecker
        minimax[count_2] = move_list + [eval_list[0]]
        count_2 += 1

        # Undoes all the moves to get the boardstate back to its pristine condition
        for i in range(len(undo_moves)):
            move = undo_moves[-(i + 1)]
            tile_1 = boardstate[move[3]][move[4]]
            tile_2 = boardstate[move[8]][move[9]]
            tile_2.piece = move[5]
            tile_1.piece = move[0]
            tile_2.move = move[6]
            tile_1.move = move[1]
            tile_2.color = move[7]
            tile_1.color = move[2]

    return minimax


def minimax_layer_2(depth_3_evals: list[list[str, int]], depth_2_moves: list[list[str]], boardstate: list[list[Tile]], side: bool) -> list[list[str, int]]:
    """Takes in a list of depth 2 moves, and a list of depth 3 moves and their evals, and calculates the meaningful evaluation for depth 2 moves, then returns that"""
    # Allocates the memory for the return list [count_2 for assignment]
    minimax = [[] for _ in range(len(depth_2_moves))]
    count_2 = 0

    # Iterates through each depth 2 move
    for move_list in depth_2_moves:
        if not move_list:
            continue
        count = 0
        fake_null = -10000 if side else 10000
        eval_list = [fake_null for _ in range(128)]

        # Checks if the first two moves in each move path among the depth 3 moves equals the two moves in the particular depth 2 move
        for move_path_long in depth_3_evals:
            if not move_path_long:
                continue
            if move_list[0] == move_path_long[0] and move_list[1] == move_path_long[1]:
                # noinspection PyTypeChecker
                eval_list[count] = move_path_long[-1]
                count += 1

        # Sorts by evaluation
        # Adds the "highest" or "lowest" outcome to the return list plus its move sequence
        eval_list.sort(reverse=side)
        # noinspection PyTypeChecker
        minimax[count_2] = move_list + [eval_list[0]]
        count_2 += 1

    return minimax


def minimax_layer_1(depth_2_evals: list[list[str, int]], depth_1_moves: list[list[str]], boardstate: list[list[Tile]], side: bool) -> list[list[str, int]]:
    """Takes in a list of depth 1 moves, and a list of depth 2 moves and their evals, and calculates the meaningful evaluation for depth 1 moves, then returns that. Returns trimmed list"""
    # Allocates the memory for the return list [count_2 for assignment]
    minimax = [[] for _ in range(len(depth_1_moves))]
    count_2 = 0

    # Iterates through each depth 2 move
    for move_list in depth_1_moves:
        if not move_list:
            continue
        count = 0
        fake_null = -10000 if side else 10000
        eval_list = []

        # Checks if the first two moves in each move path among the depth 3 moves equals the two moves in the particular depth 2 move
        for move_path_long in depth_2_evals:
            if not move_path_long:
                continue
            if move_list[0] == move_path_long[0]:
                eval_list.append(move_path_long[-1])
                count += 1

        # Sorts by evaluation
        # Adds the "highest" or "lowest" outcome to the return list plus its move sequence
        eval_list.sort(reverse=side)
        try:
            minimax[count_2] = move_list + [eval_list[0]]
            count_2 += 1
        except IndexError:
            print("index error, potential game end calculated")
            return []

    return minimax


def engine_move(boardstate: list[list[Tile]], side: bool) -> str:
    global TotalEngineMs, TotalMoveCalcs

    # Tracks the time to calculate one entire move
    start = time.process_time()

    # First layer
    possible_moves_1 = first_layer(boardstate, side)

    # Second layer
    side = not side
    possible_moves_2 = intermediate_layer(boardstate, possible_moves_1, side, 6400, 1)

    # Third layer
    side = not side
    possible_moves_3 = intermediate_layer(boardstate, possible_moves_2, side, 128000, 2)

    # Fourth layer
    side = not side
    depth_3_evals = final_layer(boardstate, possible_moves_3, side, 3200000, 3)

    # Working backwards, calculating depth 2 move evals
    side = not side
    depth_2_evals = minimax_layer_2(depth_3_evals, possible_moves_2, boardstate, side)

    # Working backwards, calculating depth 2 move evals
    side = not side
    depth_1_evals = minimax_layer_1(depth_2_evals, possible_moves_1, boardstate, side)

    # Sorts the moves by eval
    side = not side
    depth_1_evals.sort(key=lambda eval_int: eval_int[-1], reverse=side)

    # Randomizes among equally evaluated moves
    best_eval = depth_1_evals[0][1]
    top_moves = [move for move in depth_1_evals if move[-1] == best_eval]
    random_i = random.randint(0, len(top_moves) - 1)

    # Tallies process time
    end = time.process_time()
    TotalEngineMs += (end-start) * 1000

    # Debug information
    # Counting moves at each layer
    count_m2 = 0
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
        2131,
        f"\nDepth 1 moves: {len(possible_moves_1)}\n"
        f"Depth 2 moves: {count_m2}\n"
        f"Depth 3 moves: {count_m3}\n"
        f"Depth 4 moves: {TotalMoveCalcs}\n"
        f"Engine process time: {round(TotalEngineMs/1000, 2)}\n"
        f"Move evals: {depth_1_evals}\n"
        f"Top 5 moves: {depth_1_evals[:4]}\n"
        f"Top 5 worst moves:{depth_1_evals[-5:]}\n"
        f"Best move(s):{top_moves}"
        )

    TotalMoveCalcs = 0
    TotalEngineMs = 0

    # Returns a random legal first move
    return depth_1_evals[random_i][0]


if __name__ == "__main__":
    test_fen = "rnbqk2r/ppp1ppbp/3p1np1/8/2PPP3/2N2N2/PP3PPP/R1BQKB1R b KQkq"
    standard = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq"
    game_init(standard)
    save_game()
