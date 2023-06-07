from tkinter import *
from tkinter import ttk
import datetime
import time
import random


global MoveInput, MoveCount, MoveList, Side, Root, InputGui, GameArray, BoardCanvas, InputEntry, ContentFrame, GameEnd, CheckmateLabel, \
    BlockingTargetList, MoveInputList, OldBoardStates


BoardScalar = 1.4  # Board scalar
WhiteColor = "#C3C3C2"  # Default white piece color
BlackColor = "#000101"  # Default black piece color
WhiteHighlight = "#6e6e6d"  # Default white highlight
BlackHighlight = "#565656"  # Default black highlight
DarkModeBackground = "#333537"  # Dark background color
DarkModeForeground = "#989998"  # Dark foreground color (text boxes etc.)
TotalMoveCalcs = 0  # Debug, keeps track of final moves

test_fen = "rnbqk2r/ppp1ppbp/3p1np1/8/2P1P3/2N2N2/PP1P1PPP/R1BQKB1R w KQkq"
standard = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq"

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




class Tile:
    """Generic class for all board squares, holds piece and move count for said piece"""
    def __init__(self, piece: str, move: int):
        self.piece = piece
        self.move = move


def graphics_turn(*args):
    global MoveInput, BoardCanvas, InputEntry, MoveList, GameEnd, OldBoardStates
    play_bot_w = True
    play_bot_b = True
    if play_bot_b and not Side and not GameEnd or play_bot_w and Side and not GameEnd:
        print(43, "asked engine for move")
        MoveInput = engine_move(GameArray, Side)
    else:
        print(46, "fetches player's move")
        MoveInput = str(InputGui.get())
    print(39, MoveInput, "pre check")
    check_move_input()
    print(41, MoveInput, "post check")
    if GameEnd and MoveInput != "restart":  # If the game has ended, and you input anything but "restart" nothing will happen
        print("Game Ended")
        return

    elif MoveInput == "restart" or MoveInput == "exit":  # If the game has ended, and you type restart, it will restart
        print("Restarting/Exiting")
        if not GameEnd:
            save_game()  # Saves game if it hasn't already been saved ending a game
        else:
            CheckmateLabel.destroy()
        GameEnd = False
        blank_board()
        board_setup("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq")
        display_game()
        InputEntry.delete(0, END)
        if MoveInput == "exit":
            Root.quit()
        return

    else:  # Standard move main loop (checks input, plays move, erases the board, redraws the board, erases input value)
        print(69, "Standard move:")
        if play_move():
            OldBoardStates.append(fen_from_array(Side))
            print(72, OldBoardStates)
        blank_board()
        display_game()
        InputEntry.delete(0, END)
        return


def board_setup(start_fen: str):
    """Sets up the Game Array, fresh"""
    global MoveCount, MoveList, Side, Material, WhitePieces, BlackPieces, GameArray, CheckMoveLegality, MoveInputList, OldBoardStates, TotalEngineMs, AttackCalls
    Side = True  # True = white's turn
    TotalEngineMs = 0.0
    OldBoardStates = [start_fen]
    AttackCalls = 0
    CheckMoveLegality = False  # Used to modify under_check function to instead check for legal moves to a certain square
    Material = 0  # material advantage (positive is white)
    MoveList = []  # A list of moves played in each game, stored as a list of strings
    MoveInputList = []  # A list of coordinate notation for each prior move
    MoveCount = 0  # Each turn from each player adds 1
    piece_list = "rnbqkbnr"  # the standard layout of the back rank of the chess board
    WhitePieces = [piece for piece in start_fen if piece.isupper() and piece.isalpha()]  # Generates a list of existing pieces on the board that are white
    BlackPieces = [piece for piece in start_fen if piece.islower() and piece.isalpha()]  # Since it's symmetric, it just turns them all lowercase for initialization
    array_from_fen(start_fen)


def array_from_fen(fen: str) -> list[list[Tile]]:
    """Resolves the GameArray from a standard FEN as a string"""
    global GameArray, Side
    Side = True if "w" in fen else False
    piece_row = []
    piece_list = []
    fen = fen.split("/")
    for row in fen:
        piece_row = []
        for piece in row:
            if piece.isnumeric():
                piece = [" " for _ in range(int(piece))]  # Turns numbers in the FEN that represents empty spots into single spaces in a list
            for i in piece:
                piece_row.append(i)
        piece_list.append(piece_row)
    GameArray = [[Tile(piece_list[7 - j][i], 0) for i in range(8)] for j in range(8)]
    return GameArray


def fen_from_array(side: bool) -> str:
    print(116, "fen from array called")
    fen = []
    board_pieces = "BPNKRQbpnkrq"
    blank_squares = 0
    for row in range(8):
        row = 7 - row
        for col in range(8):
            piece = GameArray[row][col].piece
            if piece in board_pieces:
                if blank_squares > 0:
                    fen.append(str(blank_squares))
                    blank_squares = 0
                fen.append(piece)
            elif piece == " ":
                blank_squares += 1
        if blank_squares > 0:
            fen.append(str(blank_squares))
            blank_squares = 0
        fen.append("/")
    if not side:
        fen.append(" b ")
    else:
        fen.append(" w ")

    is_black_king_unmoved = GameArray[7][4].move == 0 and GameArray[7][4].piece == "k"
    is_white_king_unmoved = GameArray[0][4].move == 0 and GameArray[0][4].piece == "K"
    is_white_queen_rook_unmoved = GameArray[0][0].move == 0 and GameArray[0][0].piece == "R"
    is_white_king_rook_unmoved = GameArray[0][7].move == 0 and GameArray[0][7].piece == "R"
    is_black_queen_rook_unmoved = GameArray[7][0].move == 0 and GameArray[7][0].piece == "r"
    is_black_king_rook_unmoved = GameArray[7][7].move == 0 and GameArray[7][7].piece == "r"

    # Add code to add eligible en passant pawn movement recognition

    # Add half move and full move counters (since last pawn move)

    fen.append(" - ")
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
            fen.remove(" - ")
        except ValueError:
            pass

    return ''.join(fen)


def is_threefold(current_fen: str) -> bool:
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
    global Root, InputGui, BoardCanvas, InputEntry, WhiteColor, BlackColor, WhiteHighlight, BlackHighlight, \
        ContentFrame, GameEnd, DarkModeBackground, DarkModeForeground, BoardScalar
    board_setup(start_fen)
    GameEnd = False

    Root = Tk()  # Graphical display initiation/loop
    Root.title("Chess v0.05")  # Assigns title of the window

    ttk.Style().theme_use("clam")  # Changes default them to "clam"
    style = ttk.Style()
    style.configure("TLabel",
                    fill=DarkModeBackground)  # Configures the default Label style to have the appropriate dark mode
    style.configure(".", background=DarkModeBackground, foreground=DarkModeForeground, fieldbackground="#3A3733",
                    highlightbackground="#3A3733")

    ContentFrame = ttk.Frame(Root, padding="12 12 12 7", style="TFrame")  # Creates a content frame to size everything
    ContentFrame.grid(column=0, row=0, sticky="NWES")

    Root.columnconfigure(0, weight=1)
    Root.rowconfigure(0, weight=1)

    InputGui = StringVar()  # Using an object of type StringVar() to receive input from the Entry box
    InputEntry = Entry(ContentFrame, width=7, textvariable=InputGui, background="#3A3730", bd=1,
                       foreground="#C3C3C2")  # Creates input Entry box
    InputEntry.grid(column=2, row=3, sticky="W", pady="5")
    InputEntry.bind("<Return>", graphics_turn)  # Triggers the turn when enter is pressed

    BoardCanvas = Canvas(ContentFrame, width=400 * BoardScalar, height=400 * BoardScalar, background=DarkModeBackground,
                         highlightthickness=0)
    BoardCanvas.grid(column=2, row=2, sticky="NWES")

    display_game()  # Displays the current board state
    InputEntry.focus()  # Causes cursor focus in input entry box
    Root.mainloop()  # The event loop of the Tkinter gui


def blank_board():
    """Creates the blank chess board with no pieces"""
    global BoardCanvas
    BoardCanvas.delete("all")  # Clears old pieces and board
    for j in range(0, 7):  # Creates the grid of light squares
        for i in range(0, 4):
            x1 = i * BoardScalar * 100
            x2 = x1 + BoardScalar * 50
            y1 = j * BoardScalar * 100
            y2 = y1 + BoardScalar * 50
            BoardCanvas.create_rectangle(x1, y1, x2, y2, width=0, fill="#566975", activefill="#8a9da8")
            BoardCanvas.create_rectangle(x1 + BoardScalar * 50, y1 + 50 * BoardScalar, x2 + 50 * BoardScalar,
                                         y2 + 50 * BoardScalar, width=0, fill="#566975", activefill="#8a9da8")

    for j in range(0, 7):  # Creates the grid of dark squares
        for i in range(0, 5):
            x1 = i * BoardScalar * 100 - 50 * BoardScalar
            x2 = x1 + BoardScalar * 50
            y1 = j * BoardScalar * 100
            y2 = y1 + BoardScalar * 50
            BoardCanvas.create_rectangle(x1, y1, x2, y2, width=0, fill="#455561", activefill="#798fa0")
            BoardCanvas.create_rectangle(x1 + 50 * BoardScalar, y1 + 50 * BoardScalar, x2 + 50 * BoardScalar,
                                         y2 + 50 * BoardScalar, width=0, fill="#455561", activefill="#798fa0")


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


def check_move_input() -> str:
    """Verifies a move is a valid input, returns the valid input"""
    global MoveInput
    print(474, f"check move input called for {MoveInput}")
    MoveInput = MoveInput.strip().casefold()
    valid_len = len(MoveInput) == 4 or len(MoveInput) == 5
    special_moves = ("restart", "exit", "flip", "o-o", "o-o-o", "resign")
    if MoveInput in special_moves:
        return MoveInput

    if valid_len and MoveInput[0].isalpha() and MoveInput[2].isalpha() and MoveInput[1].isnumeric() and MoveInput[3].isnumeric():  # Checks if format is proper coordinate notation
        start_col = column_index(MoveInput[0])
        target_col = column_index(MoveInput[2])
        start_row = int(MoveInput[1]) - 1
        target_row = int(MoveInput[3]) - 1
        piece = GameArray[start_row][start_col].piece
        in_bounds = 7 >= start_col >= 0 and 7 >= start_row >= 0 and 7 >= target_col >= 0 and 7 >= target_row >= 0  # Checks that it's within bounds
        correct_turn = Side and piece.isupper() or not Side and piece.islower()
        if in_bounds and correct_turn:
            return MoveInput
        else:
            MoveInput = "invalid"
            print(405, MoveInput, f"in bounds:{in_bounds}, correct_turn:{correct_turn}")
    else:
        MoveInput = "invalid"
        print(408, MoveInput, "Invalid length and not special command")
    return MoveInput


def resign() -> bool:
    global CheckmateLabel, GameEnd
    print(511, "resign called")
    pgn_str = ""
    if Side:
        pgn_str = "Resignation: black wins"
    if not Side:
        pgn_str = "Resignation: white wins"
    MoveList.append(pgn_str)
    save_game()
    display_game()
    CheckmateLabel = ttk.Label(ContentFrame, text=pgn_str, style="TLabel")
    CheckmateLabel.grid(column=2, row=2, sticky="N")
    GameEnd = True
    return True


def play_move() -> bool:
    print(524, f"play move called for move: {MoveInput}")
    if MoveInput == "exit":
        return False
    elif MoveInput == "invalid":
        return False
    elif MoveInput == "resign":
        return resign()
    elif MoveInput == "o-o":
        return castle(False)
    elif MoveInput == "o-o-o":
        return castle(True)

    piece = GameArray[int(MoveInput[1]) - 1][column_index(MoveInput[0])].piece.lower()
    if piece == "q":
        return queen_move()
    elif piece == "r":
        return rook_move()
    elif piece == "b":
        return bishop_move()
    elif piece == "p":
        return pawn_move()
    elif piece == "k":
        if abs(column_index(MoveInput[0]) - column_index(MoveInput[2])) == 2:
            i_2 = column_index(MoveInput[2])
            castle_side = False if i_2 == 6 else True
            return castle(castle_side)
        return king_move()
    elif piece == "n":
        return knight_move()
    return False


def ascii_debug_display(boardstate):
    for i in range(1, 9):
        print("\n", 8 - i, [boardstate[-i][j].piece for j in range(8)])
    print("     0    1    2    3    4    5    6    7  \n")


def display_game():
    """Displays the game board in ascii or graphically"""
    display_side = True  # Used to select which way the board will display (True is white perspective)
    # Handles graphical board update
    ascii_debug_display(GameArray)
    blank_board()
    if display_side:
        for i in range(8):
            for j in range(8):
                color = GameArray[-(i + 1)][j].piece.isupper()
                piece_type = GameArray[-(i + 1)][j].piece.lower()
                if piece_type == "p":
                    draw_pawn(i, j, color)
                elif piece_type == "r":
                    draw_rook(i, j, color)
                elif piece_type == "n":
                    draw_knight(i, j, color)
                elif piece_type == "q":
                    draw_queen(i, j, color)
                elif piece_type == "b":
                    draw_bishop(i, j, color)
                elif piece_type == "k":
                    draw_king(i, j, color)
                elif piece_type == " ":
                    pass
                else:
                    print(593, "display error")
    else:
        for i in range(1, 9):
            for j in range(1, 9):
                if GameArray[-i][-j].piece in "Pp":
                    draw_pawn(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece in "Rr":
                    draw_rook(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece in "Nn":
                    draw_knight(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece in "Qq":
                    draw_queen(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece in "Bb":
                    draw_bishop(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece in "Kk":
                    draw_king(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece == " ":
                    pass
                else:
                    print(612, "display error")


def column_index(column: str) -> int:
    """turns a letter (h through a) into the appropriate array index for the board array"""
    columns = "abcdefgh"
    for i in range(8):
        if columns[i] == column:
            return i
    return -8


def index_column(index: int) -> str:
    """turns a board index into a letter for that column on the chess board"""
    columns = "abcdefgh"
    count = 0
    for column in columns:
        if count == index:
            return column
        count += 1
    return "a"


def under_attack(boardstate: list[list[Tile]], piece_side: bool, row: int, column: int) -> list[list[int, int]]:
    """Determines if a square is under attack by any other pieces, returns True if yes"""
    # Initializes the list to hold the coordinates of attacking squares
    attacking_coords = []

    # Checks the cardinal directions for rooks or queens
    # First, the same column but different rows
    done = False
    for direction in [-1, 1]:
        for i in range(1, 8):
            row_i = row + i * direction
            if not done and 7 >= row_i >= 0 and 7 >= column >= 0:
                opponent = boardstate[row_i][column].piece.isupper() != piece_side
                piece = boardstate[row_i][column].piece
                if piece == " ":
                    continue
                elif piece != " " and not opponent:
                    done = True
                elif opponent and piece in "Rr":
                    attacking_coords.append([row_i, column])
                    attacked = True
                    done = True
                elif opponent and piece in "Qq":
                    attacking_coords.append([row_i, column])
                    attacked = True
                    done = True
                else:
                    done = True
            else:
                continue

    # Secondly, checks within the same row but different columns
    done = False
    for direction in [-1, 1]:
        for i in range(1,
                       8):  # generates col indices in the positive and the negative direction away from the piece and checks them
            col_i = column + i * direction
            if not done and 7 >= col_i >= 0:
                opponent = boardstate[row][col_i].piece.isupper() != piece_side
                piece = boardstate[row][col_i].piece
                if piece == " ":
                    continue
                elif piece != " " and not opponent:
                    done = True
                elif opponent and piece in "Rr":
                    attacking_coords.append([row, column])
                    attacked = True
                    done = True
                elif opponent and piece in "Qq":
                    attacking_coords.append([row, column])
                    attacked = True
                    done = True
                else:
                    done = True
            else:
                continue

    # Checks the diagonals for queens and bishops
    done = False
    for xi in [-1, 1]:
        for yi in [-1, 1]:
            for i in range(1, 8):
                row_i = row + i * yi
                col_i = column + i * xi
                if 7 >= row_i >= 0 and 7 >= col_i >= 0 and not done:
                    opponent = boardstate[row_i][col_i].piece.isupper() != piece_side
                    piece = boardstate[row_i][col_i].piece
                    if piece == " ":
                        continue
                    elif piece != " " and not opponent:
                        done = True
                    elif opponent and piece in "Qq":
                        attacking_coords.append([row_i, col_i])
                        attacked = True
                        done = True
                    elif opponent and piece in "Bb":
                        attacking_coords.append([row_i, col_i])
                        attacked = True
                        done = True
                    else:
                        done = True
                else:
                    pass

    # Checks for knights in either of the 8 possible squares
    done = False
    offset_list = [-2, -1, 1, 2]
    for offset_row in offset_list:
        for offset_col in offset_list:
            t_row = offset_row + row
            t_col = offset_col + column
            if abs(offset_row) == abs(offset_col):
                continue
            elif 7 >= t_row >= 0 and 7 >= t_col >= 0:
                opponent = boardstate[t_row][t_col].piece.isupper() != piece_side
                is_knight = boardstate[t_row][t_col].piece in "Nn"
                if opponent and is_knight:
                    attacking_coords.append([t_row, t_col])
                    attacked = True

    # Checks for pawns, direction is based on the side
    pawn_direct = 1 if piece_side else -1
    for i in [-1, 1]:
        row_i = row + pawn_direct
        col_i = column + i
        if 7 >= row_i >= 0 and 7 >= col_i >= 0:
            pawn_check = boardstate[row_i][col_i].piece in "Pp"
            opponent = boardstate[row_i][col_i].piece.isupper() != piece_side
            if pawn_check and opponent:
                attacking_coords.append([row_i, col_i])
                attacked = True

    # Checks for kings
    for row_offset in [-1, 0, 1]:
        for col_offset in [-1, 0, 1]:
            k_col = col_offset + column
            k_row = row_offset + row
            is_move = k_row != row or k_col != column
            if 7 >= k_col >= 0 and 7 >= k_row >= 0 and is_move:
                is_king = boardstate[k_row][k_col].piece in "Kk"
                is_enemy_king = boardstate[k_row][k_col].piece.isupper() != piece_side
                if is_king and is_enemy_king:  # Enemy king found next to SOI
                    attacked = True
                    attacking_coords.append([k_row, k_col])

    return attacking_coords


def put_king_in_check(boardstate: list[list[Tile]], k_row: int, k_col: int, row_1: int, col_1: int, row_2: int, col_2: int, king_side: bool) -> bool:
    """Checks if said move puts the king into check. For non-king moves"""
    # Stores data to reconstitute
    start_piece = boardstate[row_1][col_1].piece
    end_piece = boardstate[row_2][col_2].piece
    start_move = boardstate[row_1][col_1].move
    end_move = boardstate[row_2][col_2].move

    # Simulates the move
    boardstate = simple_update(boardstate, row_1, col_1, row_2, col_2)

    # Checks for check
    in_check = True if under_attack(boardstate, king_side, k_row, k_col) else False

    # Reconstitutes the move
    boardstate[row_1][col_1].piece = start_piece
    boardstate[row_2][col_2].piece = end_piece
    boardstate[row_1][col_1].move = start_move
    boardstate[row_2][col_2].move = end_move

    return in_check


def find_king(boardstate: list[list[Tile]], side: bool) -> (int, int):
    """Returns a tuple of the king's location"""
    # Determines which king to look for
    king_type = "K" if side else "k"

    # Iterates through the board until it finds the relevant king
    for i in range(8):
        for j in range(8):
            if boardstate[i][j].piece == king_type:
                coords = (i, j)
                return coords


def has_moves(boardstate: list[list[Tile]], row: int, col: int) -> list[str]:
    """Checks if the piece at the coordinates has any legal moves. Returns a list of target coordinates for each legal move it does have, ie ['e3', 'e4'] """
    # Evaluates the piece, the color of the piece, and initializes the list of return moves
    piece_type = boardstate[row][col].piece
    piece_side = boardstate[row][col].piece.isupper()
    legal_move_list = []

    # Finds and records the relevant king
    k_coord = find_king(boardstate, piece_side)
    k_row = k_coord[0]
    k_col = k_coord[1]

    # If the square is empty, it has no legal moves
    if piece_type == " ":
        return []

    # Checks if a king has any legal moves [Checks 3x3 centered on piece, except for the current square]
    if piece_type in "kK":
        for row_offset in [-1, 0, 1]:
            row_2 = row_offset + row
            for col_offset in [-1, 0, 1]:
                col_2 = col_offset + col
                is_move = row_offset != 0 or col_offset != 0
                if 7 >= col_2 >= 0 and 7 >= row_2 >= 0 and is_move:
                    target_piece = boardstate[row_2][col_2].piece
                    legal_enemy = target_piece != " " and target_piece.isupper() != piece_side and not under_attack(boardstate, piece_side, row_2, col_2)
                    is_empty = target_piece == " "

                    # If king has legal move (checks if empty or opponent piece, then if it's in check
                    if is_empty or legal_enemy:
                        is_in_check = put_king_in_check(boardstate, row_2, col_2, row, col, row_2, col_2, piece_side)
                        if not is_in_check:
                            legal_move_list.append(f"{index_column(col_2)}{row_2 + 1}")

        # Handles checking for castling
        i = 0  #
        rook = "R"
        king = "K"
        king_j = 2
        rook_i = 0
        rook_j = 3
        extra_clear = boardstate[i][1].piece == " "

        for long in [True, False]:
            if not Side:
                i = 7
                rook = "r"
                king = "k"
            if not long:
                king_j = 6
                rook_i = 7
                rook_j = 5
                extra_clear = True

            king_legal = boardstate[i][4].piece == king and boardstate[i][4].move == 0
            rook_legal = boardstate[i][rook_i].piece == rook and boardstate[i][rook_i].move == 0
            checks = not under_attack(boardstate, king.isupper(), i, 4) and not under_attack(boardstate, king.isupper(), i, king_j) \
                and not under_attack(boardstate, king.isupper(), i, rook_j)
            clear = boardstate[i][rook_j].piece == " " and boardstate[i][king_j].piece == " " and extra_clear
            # print(1350, king_legal, rook_legal, checks, clear, GameArray[i][4].move == 0, GameArray[i][4].piece == king)

            if king_legal and rook_legal and checks and clear and long:
                legal_move_list.append(f"c{i + 1}")
            if king_legal and rook_legal and checks and clear and not long:
                legal_move_list.append(f"g{i + 1}")

    elif piece_type in "Nn":  # Checks if a knight has any legal moves
        offset_list = [-2, -1, 1, 2]
        for offset_row in offset_list:
            row_2 = offset_row + row
            for offset_col in offset_list:
                col_2 = offset_col + col
                if abs(offset_row) == abs(offset_col):
                    continue
                elif 7 >= col_2 >= 0 and 7 >= row_2 >= 0:
                    is_empty = boardstate[row_2][col_2].piece == " "
                    is_enemy = boardstate[row_2][col_2].piece.isupper() != piece_side and not is_empty
                    if is_enemy or is_empty:
                        if not put_king_in_check(boardstate, k_row, k_col, row, col, row_2, col_2, piece_side):
                            legal_move_list.append(f"{index_column(col_2)}{row_2 + 1}")

    elif piece_type in "Pp":
        done = False
        pawn_direction = 1 if piece_side else -1
        for m in [1, 2]:
            offset_row = row + pawn_direction * m
            if 7 >= offset_row >= 0:
                if boardstate[offset_row][col].piece == " " and not done:  # Check if the pawn can move forward
                    if not put_king_in_check(boardstate, k_row, k_col, row, col, offset_row, col, piece_side):
                        if m == 1 or (m == 2 and boardstate[row][col].move == 0):
                            # print(848, "pawn", piece_side, pawn_direction, end="")
                            legal_move_list.append(f"{index_column(col)}{offset_row + 1}")
                    else:
                        done = True
                else:
                    done = True
        for col_direct in [-1, 1]:  # for diagonal attacks
            offset_col = col + col_direct
            if 7 >= offset_col >= 0 and 7 >= row + pawn_direction >= 0:
                offset_row = row + pawn_direction
                target_square = boardstate[offset_row][offset_col].piece
                if target_square != " " and target_square.isupper() != piece_side:  # Check if the pawn can capture a piece
                    # print(1131)
                    if not put_king_in_check(boardstate, k_row, k_col, row, col, offset_row, offset_col, piece_side):
                        # print(1133)
                        legal_move_list.append(f"{index_column(offset_col)}{offset_row + 1}")

    elif piece_type in "Rr":
        for i in [-1, 1]:  # positive and negative direction
            done = False
            for offset in range(1, 8):
                offset_row = row + offset * i
                if 7 >= offset_row >= 0 and not done:
                    target_square = boardstate[offset_row][col].piece
                    is_enemy = target_square.isupper() != piece_side
                    if target_square == " " or (target_square != " " and is_enemy):
                        if target_square != " ":
                            done = True
                        if not put_king_in_check(boardstate, k_row, k_col, row, col, offset_row, col, piece_side):
                            legal_move_list.append(f"{index_column(col)}{offset_row + 1}")
                    else:
                        done = True
                        continue

            done = False
            for offset in range(1, 8):
                offset_col = col + offset * i
                if 7 >= offset_col >= 0 and not done:
                    target_square = boardstate[row][offset_col].piece
                    is_enemy = target_square.isupper() != piece_side
                    if target_square == " " or (target_square != " " and is_enemy):
                        if target_square != " ":
                            done = True
                        if not put_king_in_check(boardstate, k_row, k_col, row, col, row, offset_col, piece_side):
                            legal_move_list.append(f"{index_column(offset_col)}{row + 1}")
                    else:
                        done = True
                        continue

    elif piece_type in "Bb":
        for i in [-1, 1]:
            for diag_mult in [-1, 1]:
                done = False
                for offset in range(1, 8):  # flip directions
                    bc_row = row + offset * i * diag_mult
                    bc_col = col + offset * i
                    if 7 >= bc_row >= 0 and 7 >= bc_col >= 0 and not done:
                        target_square = boardstate[bc_row][bc_col].piece
                        is_enemy = target_square.isupper() != piece_side
                        if target_square == " " or (target_square != " " and is_enemy):
                            if target_square != " ":
                                done = True
                            if not put_king_in_check(boardstate, k_row, k_col, row, col, bc_row, bc_col, piece_side):
                                legal_move_list.append(f"{index_column(bc_col)}{bc_row + 1}")
                        else:
                            done = True
                            continue

    elif piece_type in "Qq":
        for i in [-1, 1]:
            done = False
            for offset in range(1, 8):
                offset_row = row + offset * i
                if 7 >= offset_row >= 0 and not done:
                    target_square = boardstate[offset_row][col].piece
                    is_enemy = target_square.isupper() != piece_side
                    if target_square == " " or target_square != " " and is_enemy:
                        if target_square != " ":
                            done = True
                        if not put_king_in_check(boardstate, k_row, k_col, row, col, offset_row, col, piece_side):
                            legal_move_list.append(f"{index_column(col)}{offset_row + 1}")
                    else:
                        done = True
                        continue

            done = False
            for offset in range(1, 8):
                offset_col = col + offset * i
                if 7 >= offset_col >= 0 and not done:
                    target_square = boardstate[row][offset_col].piece
                    is_enemy = target_square.isupper() != piece_side
                    if target_square == " " or target_square != " " and is_enemy:
                        if target_square != " ":
                            done = True
                        if not put_king_in_check(boardstate, k_row, k_col, row, col, row, offset_col, piece_side):
                            legal_move_list.append(f"{index_column(offset_col)}{row + 1}")
                    else:
                        done = True
                        continue

            for diag_mult in [-1, 1]:
                done = False
                for offset in range(1, 8):
                    offset_row = row + offset * diag_mult
                    offset_col = col + offset * i
                    if 7 >= offset_row >= 0 and 7 >= offset_col >= 0 and not done:
                        target_square = boardstate[offset_row][offset_col].piece
                        is_enemy = target_square.isupper() != piece_side
                        if target_square == " " or (target_square != " " and is_enemy):
                            if target_square != " ":
                                done = True
                            if not put_king_in_check(boardstate, k_row, k_col, row, col, offset_row, offset_col, piece_side):
                                legal_move_list.append(f"{index_column(offset_col)}{offset_row + 1}")
                        else:
                            done = True
                            continue

    return legal_move_list


def is_checkmate(boardstate: list[list[Tile]], side: bool, checking_piece: str, a_row: int, a_col: int, k_row: int,
                 k_col: int) -> bool:
    skip_block_checks = False
    if boardstate[k_row][k_col].piece not in "Kk":
        # print(1261)
        return False
    if checking_piece.isupper() == boardstate[k_row][k_col].piece.isupper():
        # print(1264)
        return False
    if checking_piece in "Nn":  # if the checking piece is a knight, no need to check for blocking moves
        # print(1267)
        skip_block_checks = True
    if under_attack(boardstate, side, a_row, a_col):  # if the checking piece can be captured, it's not check
        # print(1043, "can capture attacker")
        return False
    for row_offset in [-1, 0, 1]:
        for col_offset in [-1, 0, 1]:
            col = col_offset + k_col
            row = row_offset + k_row
            if row_offset == 0 and col_offset == 0:
                continue
            elif 7 >= col >= 0 and 7 >= row >= 0:
                square_piece_legal = boardstate[row][col].piece != " " and boardstate[row][col].piece.isupper() != \
                                     boardstate[k_row][k_col].piece.isupper() and not under_attack(boardstate, side,
                                                                                                   row, col)
                square_piece_empty = boardstate[row][col].piece == " " and not under_attack(boardstate, side, row, col)
                if square_piece_empty or square_piece_legal:  # if empty space adjacent, and not under check, the king can move out of check
                    return False
    if not skip_block_checks:
        potential_blockers = calculate_squares_between(not side, a_row, a_col, k_row, k_col)
        for i in range(len(potential_blockers)):

            # Translate coordinate notation into board coords
            row_1 = potential_blockers[i][0][0]
            row_2 = potential_blockers[i][1][0]
            col_1 = potential_blockers[i][0][1]
            col_2 = potential_blockers[i][1][1]

            # Store data for undoing test simulation on boardstate
            piece_1 = boardstate[row_2][col_2].piece
            move_1 = boardstate[row_2][col_2].move
            piece_2 = boardstate[row_1][col_1].piece
            move_2 = boardstate[row_1][col_1].move

            # Simulate the board, check if king is left under attack
            boardstate = simple_update(boardstate, row_1, col_1, row_2, col_2)
            attacked = under_attack(boardstate, not side, k_row, k_col)

            # Undo board simulation
            boardstate[row_2][col_2].piece = piece_1
            boardstate[row_2][col_2].move = move_1
            boardstate[row_1][col_1].piece = piece_2
            boardstate[row_1][col_1].move = move_2

            if not attacked:
                return False
        return True
    else:
        return True


def is_stalemate(boardstate: list[list[Tile]]) -> bool:
    # print(1259, "is stalemate called for the current board")
    white_stalemated = True
    black_stalemated = None
    # print(1254)
    for i in range(8):
        # print(1255)
        for j in range(8):
            # print(1272)
            moves = has_moves(boardstate, i, j)
            # print(1274, index_column(j), i, moves, boardstate[i][j].piece)
            if boardstate[i][j].piece.isupper() and boardstate[i][j].piece != " ":
                if len(moves) != 0:
                    # print(1277, f"white side has moves from piece at ({index_column(j)}{i + 1}: {moves})")
                    white_stalemated = False
            if boardstate[i][j].piece.islower() and boardstate[i][j].piece != " ":
                if len(moves) != 0:
                    # print(1281, f"black side has moves from piece at ({index_column(j)}{i + 1}: {moves})")
                    black_stalemated = False
    # print(1330, white_stalemated, black_stalemated)
    return white_stalemated or black_stalemated


def calculate_squares_between(side: bool, a_row: int, a_col: int, k_row: int, k_col: int) -> list[list[list[int]]]:
    """Returns a list of all pieces that could theoretically block the line of attack between the coordinates that are
    passed in. The output is structured like this: the primary list holds the secondary lists. the secondary lists each
    hold two 3rd tier lists, each one of which contains a pair of coords [row, col] the therefor [0][0][0] would get the
    first pair of coordinates, the first coordinate (which is the starting position of a piece that could block check)
    and then grab the row from that coord"""
    # print(1286, "Calculate squares between called")
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
        attacking_coords = under_attack(GameArray, side, pos_move_row, pos_move_col)
        for coord in attacking_coords:
            coord_pair = [coord, [pos_move_row, pos_move_col]]
            move_output.append(coord_pair)

    return move_output  # This is a list of all potential pieces (their coordinates) that could theoretically block the line of attack between the two given coordinate sets, paired with the square they would move to


def piece_move(column_1: int, column_2: int, row_1: int, row_2: int, piece_type) -> bool:
    """Moves piece from coord_1 to coord_2, and checks for legality, and game results. Returns False if illegal"""
    global MoveCount, MoveList, Side, GameArray, Root, ContentFrame, GameEnd, CheckmateLabel, MoveInputList
    print(1323, f"piece move called for the move {index_column(column_1)}{row_1}{index_column(column_2)}{row_2}")
    undo = False
    k_row = None
    k_col = None
    ended = False
    promotion = None
    enemy_k_row = None
    enemy_k_col = None

    backup_piece_1 = GameArray[row_1][
        column_1].piece  # Storing piece data so that the move can be reverted if it results in an illegal position
    backup_move_1 = GameArray[row_1][column_1].move
    backup_piece_2 = GameArray[row_2][column_2].piece
    backup_move_2 = GameArray[row_2][column_2].move

    pgn_str = " "
    pgn_target = GameArray[row_2][column_2].piece.upper()
    pgn_column = index_column(column_2)  # outputs pgn type for each move
    pgn_column_start = index_column(column_1)
    pgn_1 = piece_type.upper()

    if piece_type in "Pp":  # pawn takes notation
        if pgn_target != " " and pgn_target != "P":
            pgn_1 = f"{pgn_column_start}x{pgn_target}"
        elif pgn_target != " " and pgn_target == "P":
            pgn_1 = f"{pgn_column_start}x"
        else:
            pgn_1 = ""

    if piece_type.isupper() == Side:  # Verifying the piece is the appropriate piece for the turn
        if backup_piece_1 in "Pp":  # Checking if the piece is a pawn eligible for promotion
            if Side and row_2 == 7 or not Side and row_2 == 0:
                try:
                    promotion = MoveInput[4].lower()
                except TypeError:
                    promotion = "q"
                except IndexError:
                    promotion = "q"
                if promotion != "q" and promotion != "b" and promotion != "n" and promotion != "r":  # Defaults to a queen
                    promotion = "q"
                if Side:
                    GameArray[row_2][column_2].piece = promotion.upper()
                elif not Side:
                    GameArray[row_2][column_2].piece = promotion.lower()
        if promotion is None:
            GameArray[row_2][column_2].piece = backup_piece_1

        GameArray[row_2][column_2].move = backup_move_1 + 1  # normal movement block
        GameArray[row_1][column_1].piece = " "
        GameArray[row_1][column_1].move = 0
    else:
        print("wrong turn/piece")
        return False

    # check if king (white or black depending on Side) is put in check
    for row_i in range(8):
        for col_i in range(8):
            if GameArray[row_i][col_i].piece in "Kk" and GameArray[row_i][col_i].piece.isupper() == Side:
                k_row = row_i
                k_col = col_i
            if GameArray[row_i][col_i].piece in "Kk" and GameArray[row_i][col_i].piece.isupper() != Side:
                enemy_k_row = row_i
                enemy_k_col = col_i
    # print(Side, k_row, k_col)
    if k_row is None or k_col is None or enemy_k_row is None or enemy_k_col is None:
        undo = True
    else:
        if under_attack(GameArray, Side, k_row, k_col) or undo:
            print("puts in check/illegal move")
            GameArray[row_2][column_2].piece = backup_piece_2
            GameArray[row_2][column_2].move = backup_move_2
            GameArray[row_1][column_1].piece = backup_piece_1
            GameArray[row_1][column_1].move = backup_move_1
            undo = False
            return False

    cols = ["a", "b", "c", "d", "e", "f", "g", "h"]
    moves_since_pawn = 0
    current_fen = fen_from_array(not Side)
    for move in MoveList:  # Counts moves since the last pawn move (for 50 move rule)
        for col in cols:
            if move[0] == col:
                moves_since_pawn = 0
        moves_since_pawn += 1

    for coords in under_attack(GameArray, not Side, enemy_k_row, enemy_k_col):
        print(coords)
        attacker = GameArray[coords[0]][coords[1]].piece
        a_row = coords[0]
        a_col = coords[1]
        if is_checkmate(GameArray, Side, attacker, a_row, a_col, enemy_k_row, enemy_k_col):
            print("Checkmate!")
            if Side:
                color = "white"
            else:
                color = "black"
            pgn_str = f"Checkmate: {color} wins"
            ended = True
    if not ended and moves_since_pawn >= 100:
        pgn_str = "Draw: 50 move rule"
        ended = True
    if not ended and is_stalemate(GameArray):
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
        display_game()
        CheckmateLabel = ttk.Label(ContentFrame, text=pgn_str, style="TLabel")
        CheckmateLabel.grid(column=2, row=2, sticky="N")
        GameEnd = True

    if Side and not ended:
        print("\nBlack to move")
    if not Side and not ended:
        print("\nWhite to move")

    if MoveInput in "o-oO-O" or MoveInput in "o-o-oO-O-O":  # compiles each move into one list of moves
        if piece_type in "Rr":
            if Side:
                MoveList.append(MoveInput.upper())
            else:
                MoveList.append(MoveInput.lower())
            MoveInputList.append(f"{piece_type}{MoveInput}")
            MoveCount += 1
            Side = not Side
            return True
    else:
        print(1447, "standard move")
        Side = not Side
        MoveInputList.append(f"{piece_type}{MoveInput}")
        MoveList.append(f"{pgn_1}{pgn_column}{row_2 + 1}")
        MoveCount += 1
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


def rook_move() -> bool:
    """Logic for legal rook moves"""
    start_column = column_index(MoveInput[0])
    start_row = int(MoveInput[1]) - 1
    target_column = column_index(MoveInput[2])
    target_row = int(MoveInput[3]) - 1
    row_direction = 1
    column_direction = 1
    move_length = abs(target_row - start_row) + abs(target_column - start_column)
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    legal_target = (piece_type.isupper() != target_piece.isupper() or target_piece == " ") and piece_type in "Rr"

    if target_row < start_row:
        row_direction = -1
    if target_row < start_column:
        column_direction = -1

    if start_column == target_column and legal_target:
        for i in range(1, move_length):
            row_i = (i * row_direction) + start_row
            if GameArray[row_i][target_column].piece != " ":
                return False
        return piece_move(start_column, target_column, start_row, target_row, piece_type)

    elif start_row == target_row and legal_target:
        for i in range(1, move_length):
            column_i = i * column_direction
            if GameArray[target_row][column_i].piece != " ":
                return False
        return piece_move(start_column, target_column, start_row, target_row, piece_type)
    else:
        return False


def bishop_move() -> bool:
    """Logic for legal bishop moves"""
    start_column = column_index(MoveInput[0])
    start_row = int(MoveInput[1]) - 1
    target_column = column_index(MoveInput[2])
    target_row = int(MoveInput[3]) - 1
    row_direction = 1  # offset for what direction the piece will move in relative to the array indices
    column_direction = 1
    move_length = abs(start_row - target_row)
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    legal_target = (
                           piece_type.isupper() != target_piece.isupper() or target_piece == " ") and piece_type in "Bb"  # true if legal move

    if target_row < start_row:
        row_direction = -1
    if target_column < start_column:
        column_direction = -1

    if (target_row - start_row) * row_direction == (target_column - start_column) * column_direction and legal_target:
        for i in range(1, move_length):
            row_i = i * row_direction + start_row
            column_i = i * column_direction + start_column
            if GameArray[row_i][column_i].piece != " ":
                return False
        return piece_move(start_column, target_column, start_row, target_row, piece_type)
    else:
        return False


def queen_move() -> bool:
    """Logic for legal queen moves"""
    start_column = column_index(MoveInput[0])
    start_row = int(MoveInput[1]) - 1
    target_column = column_index(MoveInput[2])
    target_row = int(MoveInput[3]) - 1
    move_length = abs(start_row - target_row)
    row_direction = 1
    column_direction = 1
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    legal_target = (
                           piece_type.isupper() != target_piece.isupper() or target_piece == " ") and piece_type in "Qq"  # true if legal move

    if target_row < start_row:
        row_direction = -1
    if target_column < start_column:
        column_direction = -1

    if start_column == target_column and legal_target:  # true if the queen is only moving along the same column
        for i in range(1, move_length):
            row_i = start_row + (row_direction * i)
            if GameArray[row_i][target_column].piece != " ":  # checks that every square along the way is empty
                return False
        return piece_move(start_column, target_column, start_row, target_row, piece_type)  # updates board array

    elif start_row == target_row and legal_target:  # true if the queen is only moving along the same row
        for i in range(1, move_length):
            column_i = start_column + (column_direction * i)
            if GameArray[target_row][column_i].piece != " ":  # checks that every square along the way is empty
                return False
        return piece_move(start_column, target_column, start_row, target_row, piece_type)  # updates board array

    elif start_row != target_row and start_column != target_column:  # case where the target square is on a diagonal
        if (target_row - start_row) * row_direction == (
                target_column - start_column) * column_direction and legal_target:  # checks that it's on a proper diagonal, and if legal target
            for i in range(1, move_length):
                row_i = (i * row_direction) + start_row
                column_i = (i * column_direction) + start_column
                if GameArray[row_i][column_i].piece != " ":  # checks that each square along the path is empty
                    return False
            return piece_move(start_column, target_column, start_row, target_row, piece_type)  # updates the board array

        else:
            return False

    else:
        return False


def knight_move() -> bool:
    """Logic for legal knight moves"""
    print(1597, "knight move called")
    start_column = column_index(MoveInput[0])
    start_row = int(MoveInput[1]) - 1
    target_column = column_index(MoveInput[2])
    target_row = int(MoveInput[3]) - 1
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    legal_target = (
                           target_piece.isupper() != piece_type.isupper() or target_piece == " ") and piece_type in "Nn"  # checks if the target square is empty or an opponent's piece

    if target_row >= start_row:  # determines whether the row direction is up or down
        row_direction = 1
    else:
        row_direction = -1

    if target_column >= start_column:  # determines whether the column direction is left or right
        column_direction = 1
    else:
        column_direction = -1

    horizontal_row_check = start_row + row_direction * 1 == target_row  # these lines check that the target is a legal knight move
    horizontal_column_check = start_column + column_direction * 2 == target_column
    vertical_row_check = start_row + row_direction * 2 == target_row
    vertical_column_check = start_column + column_direction * 1 == target_column

    if vertical_column_check and vertical_row_check and legal_target or horizontal_column_check and horizontal_row_check and legal_target:  # checks that everything is legal and checks out
        return piece_move(start_column, target_column, start_row, target_row, piece_type)
    else:
        return False


def king_move() -> bool:
    """Logic for legal king moves"""
    start_column = column_index(MoveInput[0])
    start_row = int(MoveInput[1]) - 1
    target_column = column_index(MoveInput[2])
    target_row = int(MoveInput[3]) - 1
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    legal_target = piece_type.isupper() != target_piece.isupper() or target_piece == " "
    legal_move = legal_target and piece_type in "Kk"  # checks if it's a legal move basically
    if legal_move:
        return piece_move(start_column, target_column, start_row, target_row, piece_type)
    return False


def pawn_move() -> bool:
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
    start_row = int(MoveInput[1]) - 1
    target_row = int(MoveInput[3]) - 1
    start_column = column_index(MoveInput[0])
    target_column = column_index(MoveInput[2])
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    first_move = GameArray[start_row][start_column].move == 0

    pawn_side = 1  # Used to determine which direction the pawn can move
    if piece_type.islower():
        pawn_side = -1

    empty_target = target_piece == " "
    is_straight = start_column == target_column
    distance = abs(start_row - target_row)
    row_distance = 2 >= distance >= 1
    right_way = pawn_side * abs(start_row - target_row) + start_row == target_row
    is_diag = abs(start_row - target_row) == abs(start_column - target_column) == 1
    is_opponent = piece_type.isupper() != target_piece.isupper() and target_piece != " "

    legal_target_attack = is_diag and right_way and is_opponent  # True if legal for attacking a piece directly diagonal one square left or right
    legal_target_move = is_straight and right_way and empty_target and row_distance and row_distance

    # print(1290, is_diag, right_way, is_opponent, "\n", is_straight, right_way, empty_target, distance, first_move)

    if legal_target_attack or legal_target_move:  # Normal move or attack
        if distance == 1 or distance == 2 and first_move:
            return piece_move(start_column, target_column, start_row, target_row, piece_type)

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
        # print(1306, MoveInputList[-1])
    except IndexError:
        last_move_double = False
        # print(1309, "first pawn move, illegal")

    if last_move_piece and last_move_double:
        if start_row == 4 and Side or start_row == 3 and not Side:  # The only two rows you can do en passant from
            passant_row = True
        for shift in [-1, 1]:
            if last_move_col + shift == start_column:
                passant_col = True
        if passant_col and passant_row:
            piece_move(start_column, target_column, start_row, target_row, piece_type)  # Moves the pawn
            # print(1299, last_move_col, last_move_row_2)
            GameArray[last_move_row_2][last_move_col].piece = " "  # Removes the pawn captured by en passant
            GameArray[last_move_row_2][last_move_col].move = 0
            return True


def castle(long: bool) -> bool:
    """Logic for legal castling"""
    global MoveCount, Side
    i = 0  #
    rook = "R"
    king = "K"
    king_j = 2
    rook_i = 0
    rook_j = 3
    extra_clear = GameArray[i][1].piece == " "

    if not Side:
        i = 7
        rook = "r"
        king = "k"
    if not long:
        king_j = 6
        rook_i = 7
        rook_j = 5
        extra_clear = True

    king_legal = GameArray[i][4].piece == king and GameArray[i][4].move == 0
    rook_legal = GameArray[i][rook_i].piece == rook and GameArray[i][rook_i].move == 0
    checks = not under_attack(GameArray, king.isupper(), i, 4) and not under_attack(GameArray, king.isupper(), i,
                                                                                    king_j) and not under_attack(
        GameArray, king.isupper(), i, rook_j)
    clear = GameArray[i][rook_j].piece == " " and GameArray[i][king_j].piece == " " and extra_clear
    # print(1350, king_legal, rook_legal, checks, clear, GameArray[i][4].move == 0, GameArray[i][4].piece == king)

    if king_legal and rook_legal and checks and clear:
        piece_move(4, king_j, i, i, king)
        Side = not Side
        piece_move(rook_i, rook_j, i, i, rook)
        return True
    else:
        return False


def evaluate_position(boardstate: list[list[Tile]]) -> int:
    """Evaluates a position based on material, negative if black is winning"""
    evaluation = 0

    # if checkmate, count evaluation = 20000 etc
    for i in range(8):
        for j in range(8):
            piece = boardstate[i][j].piece
            if piece in "Kk":
                attackers = under_attack(boardstate, False, i, j)
                for attacking_coords in attackers:
                    king_side = piece.isupper()
                    if is_checkmate(boardstate, king_side, boardstate[attacking_coords[0]][attacking_coords[1]].piece, attacking_coords[0], attacking_coords[1], i, j):
                        return 100000 if king_side else -100000
            count = 0
            if piece.isupper():
                table_y = 7 - i
                table_x = j
            else:
                table_y = i
                table_x = j
            if piece in "Pp":
                count = 100 + pawn_table[table_y][table_x]
            elif piece in "Nn":
                count = 320 + knight_table[table_y][table_x]
            elif piece in "Bb":
                count = 330 + bishop_table[table_y][table_x]
            elif piece in "Rr":
                count = 500 + rook_table[table_y][table_x]
            elif piece in "Qq":
                count = 900 + queen_table[table_y][table_x]
            elif piece in "Kk":
                count = king_table_mid[table_y][table_x]
            else:
                pass
            if piece.isupper():
                evaluation += count
                count = 0
            if piece.islower():
                evaluation -= count
                count = 0
    return evaluation


def simple_update(boardstate: list[list[Tile]], start_row: int, start_col: int, end_row: int, end_col: int) -> list[list[Tile]]:
    boardstate[end_row][end_col].piece = boardstate[start_row][start_col].piece
    boardstate[end_row][end_col].move = boardstate[start_row][start_col].move
    boardstate[start_row][start_col].piece = " "
    boardstate[start_row][start_col].move = 0
    return boardstate


def first_layer(boardstate: list[list[Tile]], side: bool) -> list[list[str]]:
    """Calculates all legal moves from a position for one side"""
    possible_moves_1 = []
    for row in range(8):
        for col in range(8):
            if boardstate[row][col].piece != " " and boardstate[row][col].piece.isupper() == side:
                for coord in has_moves(boardstate, row, col):
                    possible_moves_1.append([f"{index_column(col)}{row + 1}{coord}"])
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
        undo_moves = [(" ", 0, 0, 0, " ", 0, 0, 0) for _ in range(depth)]

        #  Makes all the necessary moves to get the boardstate into the relevant position
        for i in range(depth):
            # print(1725, i)

            # Turns the move string into coords
            row_s = int(move_list[i][1]) - 1
            col_s = int(column_index(move_list[i][0]))
            row_e = int(move_list[i][3]) - 1
            col_e = int(column_index(move_list[i][2]))

            # Grabs the piece and move values at said target
            piece_target = boardstate[row_e][col_e].piece
            piece_start = boardstate[row_s][col_s].piece
            move_target = boardstate[row_e][col_e].move
            move_start = boardstate[row_s][col_s].move

            # Stores information so it can be undone later
            undo_moves[i] = (piece_start, move_start, row_s, col_s, piece_target, move_target, row_e, col_e)

            # Makes the move
            boardstate = simple_update(boardstate, row_s, col_s, row_e, col_e)

        # Finds legal moves and puts them in the possible_moves list, as well as the branch of the move tree that got to it
        for row in range(8):
            for col in range(8):
                if boardstate[row][col].piece != " " and boardstate[row][col].piece.isupper() == side:
                    for coord in has_moves(boardstate, row, col):
                        possible_moves[count] = move_list + [f"{index_column(col)}{row + 1}{coord}"]
                        count += 1
                        # TotalMoveCalcs += 1

        # Undoes all the moves to get the boardstate back to its pristine condition
        for i in range(len(undo_moves)):
            move = undo_moves[-(i + 1)]
            boardstate[move[6]][move[7]].piece = move[4]
            boardstate[move[2]][move[3]].piece = move[0]
            boardstate[move[6]][move[7]].move = move[5]
            boardstate[move[2]][move[3]].move = move[1]

    return possible_moves


def final_layer(boardstate: list[list[Tile]], move_list_list: list[list[str]], side: bool, move_count: int, depth) -> list[list[str, int]]:
    """Calculates all the legal moves at a certain depth"""
    global TotalMoveCalcs

    # Counters
    count_2 = 0

    # Initializes the list that will hold the prior moves (depth 3) and their evaluations (which is based on these calculated moves and a sort)
    minimax = [[" ", " ", " ", 0] for _ in range(32000)]

    # Loops through each of the moves branches it's fed
    for move_list in move_list_list:
        if not move_list:
            continue

        # Counter for eval_list indexing assignment
        count = 0

        # Generates the blank list of tuples which will hold the data necessary to revert the simulated moves
        undo_moves = [(" ", 0, 0, 0, " ", 0, 0, 0) for _ in range(depth)]

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
            piece_target = boardstate[row_e][col_e].piece
            piece_start = boardstate[row_s][col_s].piece
            move_target = boardstate[row_e][col_e].move
            move_start = boardstate[row_s][col_s].move

            # Stores information so it can be undone later
            undo_moves[i] = (piece_start, move_start, row_s, col_s, piece_target, move_target, row_e, col_e)

            # Makes the move
            boardstate = simple_update(boardstate, row_s, col_s, row_e, col_e)

        # Finds legal moves and evaluates them, determining the best evaluation for each depth 3 move, and passing that out as a list, as well as the branch of the move tree that got to it
        # Iterates through each square on the board and checks if it's a relevant piece (the right color)
        for row in range(8):
            for col in range(8):
                if boardstate[row][col].piece != " " and boardstate[row][col].piece.isupper() == side:
                    for coord in has_moves(boardstate, row, col):

                        # Converts coordinate notation into array coordinates
                        row_e = int(coord[1]) - 1
                        col_e = int(column_index(coord[0]))

                        # Grabs the piece values at said target
                        piece_target = boardstate[row_e][col_e].piece
                        piece_start = boardstate[row][col].piece

                        # Makes the suggested move and then evaluates it
                        boardstate = simple_update(boardstate, row, col, row_e, col_e)
                        pos_eval = evaluate_position(boardstate)

                        # Undoes the evaluation move
                        boardstate[row_e][col_e].piece = piece_target
                        boardstate[row][col].piece = piece_start

                        # Adds the move to the most list, with the evaluation after it
                        eval_list[count] = pos_eval
                        count += 1
                        TotalMoveCalcs += 1

        # Sorts the evaluations to find what the best move was for the player at depth 3
        # Populates the list with the move sequence and evaluation that it deserves
        # Weak error: eval_list is an int, move_list is a list of strings, pycharm doesn't like mixing the types (maybe fix, maybe ignore). Will be fixed by switching board representation to int
        eval_list.sort(reverse=side)
        minimax[count_2] = move_list + [eval_list[0]]
        count_2 += 1

        # Undoes all the moves to get the boardstate back to its pristine condition
        for i in range(len(undo_moves)):
            move = undo_moves[-(i + 1)]
            boardstate[move[6]][move[7]].piece = move[4]
            boardstate[move[2]][move[3]].piece = move[0]
            boardstate[move[6]][move[7]].move = move[5]
            boardstate[move[2]][move[3]].move = move[1]

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
                eval_list[count] = move_path_long[-1]
                count += 1

        # Sorts by evaluation
        # Adds the "highest" or "lowest" outcome to the return list plus its move sequence
        eval_list.sort(reverse=side)
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
    depth_3_evals = final_layer(boardstate, possible_moves_3, side, 1000000, 3)

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

    # Counting moves at each layer
    count_m2 = 0
    for move in possible_moves_2:
        if not move:
            continue
        else:
            count_m2 += 1
    print(1835, count_m2)

    count_m3 = 0
    for move in possible_moves_3:
        if not move:
            continue
        else:
            count_m3 += 1
    print(1843, count_m3)

    # Debug information
    print(1943, f"\nTop 5 moves: {depth_1_evals[:4]}\nTop 5 worst moves:{depth_1_evals[-5:]}\nBest moves:{top_moves}\nIn total; {TotalMoveCalcs} moves calculated in {round(TotalEngineMs/1000, 1)}\n{len(possible_moves_1)} first moves")

    # Returns a random legal first move
    return depth_1_evals[random_i][0]


if __name__ == "__main__":
    game_init(test_fen)
    save_game()
