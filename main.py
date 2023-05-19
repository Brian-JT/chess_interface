from tkinter import *
from tkinter import ttk
import datetime
import copy

global MoveInput, MoveCount, MoveList, Side, Material, WhitePieces, BlackPieces, Root, InputGui, GameArray, \
    BoardCanvas, InputEntry, WhiteColor, BlackColor, WhiteHighlight, BlackHighlight, ContentFrame, GameEnd, \
    CheckmateLabel, DarkModeBackground, DarkModeForeground, CheckMoveLegality, AttackingCoords, BlockingTargetList, \
    MoveInputList, BoardScalar, OldBoardStates, StartFen


class Tile:
    """Generic class for all board squares, holds piece and move count for said piece"""
    def __init__(self, piece: str, move: int):
        self.piece = piece
        self.move = move

    def __str__(self):
        if self.piece != " ":
            return f"{self.piece} has moved {self.move} time(s)"
        else:
            return " "

    def __repr__(self):
        return f"Tile('{self.piece}', {self.move})"

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        piece = self.piece == other.piece
        move = self.move == other.move
        return piece and move


def graphics_turn(*args):
    global MoveInput, BoardCanvas, InputEntry, MoveList, GameEnd, OldBoardStates
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
        board_setup(StartFen)
        display_game()
        InputEntry.delete(0, END)
        if MoveInput == "exit":
            Root.quit()
        return

    else:  # Standard move main loop (checks input, plays move, erases the board, redraws the board, erases input value)
        print("Standard move:")
        if play_move():
            OldBoardStates.append(fen_from_array(Side))
            print(66, OldBoardStates)
        blank_board()
        display_game()
        InputEntry.delete(0, END)
        return


def board_setup(start_fen: str):
    """Sets up the Game Array, fresh"""
    global MoveCount, MoveList, Side, Material, WhitePieces, BlackPieces, GameArray, CheckMoveLegality, MoveInputList, OldBoardStates
    Side = True  # True = white's turn
    OldBoardStates = [start_fen]
    CheckMoveLegality = False  # Used to modify under_check function to instead check for legal moves to a certain square
    Material = 0  # material advantage (positive is white)
    MoveList = []  # A list of moves played in each game, stored as a list of strings
    MoveInputList = []  # A list of coordinate notation for each prior move
    MoveCount = 0  # Each turn from each player adds 1
    piece_list = ["r", "n", "b", "q", "k", "b", "n", "r"]  # the standard layout of the back rank of the chess board
    WhitePieces = [piece for piece in start_fen if piece.isupper() and piece.isalpha()]  # Generates a list of existing pieces on the board that are white
    BlackPieces = [piece for piece in start_fen if piece.islower() and piece.isalpha()]  # Since it's symmetric, it just turns them all lowercase for initialization
    array_from_fen(start_fen)


def array_from_fen(fen: str):
    """Resolves the GameArray from a standard FEN as a string"""
    global GameArray
    piece_row = []
    piece_list = []
    inverse = [7, 6, 5, 4, 3, 2, 1, 0]
    fen = fen.split("/")
    for row in fen:
        piece_row = []
        for piece in row:
            if piece.isnumeric():
                piece = [" " for _ in range(int(piece))]  # Turns numbers in the FEN that represents empty spots into single spaces in a list
            for i in piece:
                piece_row.append(i)
        piece_list.append(piece_row)
    GameArray = [[Tile(piece_list[j][i], 0) for i in range(8)] for j in inverse]


def fen_from_array(side: bool) -> str:
    fen = []
    inverse = [7, 6, 5, 4, 3, 2, 1, 0]
    board_pieces = ["b", "n", "k", "r", "q", "p"]
    blank_squares = 0
    for row in inverse:
        for col in range(8):
            piece = GameArray[row][col].piece
            if piece.lower() in board_pieces:
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
        print(172, i, OldBoardStates[i], current_fen)
        if OldBoardStates[i] == current_fen:
            repetitions += 1
    print(repetitions)
    if repetitions >= 2:
        return True
    else:
        return False


def game_init(start_fen: str):
    """Initiates the Tkinter event loop (and thus the entire game)"""
    global Root, InputGui, BoardCanvas, InputEntry, WhiteColor, BlackColor, WhiteHighlight, BlackHighlight, \
        ContentFrame, GameEnd, DarkModeBackground, DarkModeForeground, BoardScalar, StartFen
    board_setup(start_fen)
    StartFen = start_fen
    GameEnd = False

    BoardScalar = 1.4  # Board scalar
    WhiteColor = "#C3C3C2"  # Default white piece color
    BlackColor = "#000101"  # Default black piece color
    WhiteHighlight = "#6e6e6d"  # Default highlights
    BlackHighlight = "#565656"
    DarkModeBackground = "#333537"
    DarkModeForeground = "#989998"

    Root = Tk()  # Graphical display initiation/loop
    Root.title("Chess v0.05")  # Assigns title of the window

    ttk.Style().theme_use("clam")  # Changes default them to "clam"
    style = ttk.Style()
    style.configure("TLabel", fill=DarkModeBackground)  # Configures the default Label style to have the appropriate dark mode
    style.configure(".", background=DarkModeBackground, foreground=DarkModeForeground, fieldbackground="#3A3733", highlightbackground="#3A3733")

    ContentFrame = ttk.Frame(Root, padding="12 12 12 7", style="TFrame")  # Creates a content frame to size everything
    ContentFrame.grid(column=0, row=0, sticky="NWES")

    Root.columnconfigure(0, weight=1)
    Root.rowconfigure(0, weight=1)

    InputGui = StringVar()  # Using an object of type StringVar() to receive input from the Entry box
    InputEntry = Entry(ContentFrame, width=7, textvariable=InputGui, background="#3A3730", bd=1, foreground="#C3C3C2")  # Creates input Entry box
    InputEntry.grid(column=2, row=3, sticky="W", pady="5")
    InputEntry.bind("<Return>", graphics_turn)  # Triggers the turn when enter is pressed

    BoardCanvas = Canvas(ContentFrame, width=400 * BoardScalar, height=400 * BoardScalar, background=DarkModeBackground, highlightthickness=0)
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
            BoardCanvas.create_rectangle(x1 + BoardScalar * 50, y1 + 50 * BoardScalar, x2 + 50 * BoardScalar, y2 + 50 * BoardScalar, width=0, fill="#566975", activefill="#8a9da8")

    for j in range(0, 7):  # Creates the grid of dark squares
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
    a = 22 * BoardScalar + column
    b = 21 * BoardScalar + row

    c = 30 * BoardScalar + column
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

    BoardCanvas.create_rectangle(a, b, c, d, fill=piece_color, activefill=highlight_color, outline=highlight_color)  # the body
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
    """Verifies a move is a valid input, returns the piece string of the piece to be moved, or the special moves"""
    global MoveInput
    MoveInput = MoveInput.strip().casefold()
    if MoveInput == "restart" or MoveInput == "exit" or MoveInput == "flip" or MoveInput == "o-o" or MoveInput == "o-o-o" or MoveInput == "resign":  # Checks if input is a special case
        return MoveInput

    valid_len = len(MoveInput) == 4 or len(MoveInput) == 5
    if len(MoveInput) == 5:
        try:
            MoveInput[4]
        except IndexError:
            MoveInput += "q"
            print(391, MoveInput, "idk how this would run")

    if valid_len and MoveInput[0].isalpha() and MoveInput[2].isalpha() and MoveInput[1].isnumeric() and MoveInput[3].isnumeric():  # Checks if format is proper coordinate notation
        start_col = column_index(MoveInput[0])
        target_col = column_index(MoveInput[2])
        start_row = int(MoveInput[1]) - 1
        target_row = int(MoveInput[3]) - 1
        piece = GameArray[start_row][start_col].piece
        in_bounds = 7 >= start_col >= 0 and 7 >= start_row >= 0 and 7 >= target_col >= 0 and 7 >= target_row >= 0  # Checks that it's within bounds
        correct_turn = Side and piece.isupper() or not Side and piece.islower()
        if in_bounds and correct_turn:
            return piece
        else:
            MoveInput = "invalid"
            print(405, MoveInput, f"in bounds:{in_bounds}, correct_turn:{correct_turn}")
    else:
        MoveInput = "invalid"
        print(408, MoveInput, "Invalid length and not special command")
    return MoveInput


def resign():
    global CheckmateLabel, GameEnd
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


def play_move() -> bool:
    piece = check_move_input().lower()
    if piece == "exit":
        return False
    elif piece == "invalid":
        return False
    elif piece == "resign":
        return resign()
    elif piece == "o-o":
        return castle(False)
    elif piece == "o-o-o":
        return castle(True)
    elif piece == "q":
        return queen_move()
    elif piece == "r":
        return rook_move()
    elif piece == "b":
        return bishop_move()
    elif piece == "p":
        return pawn_move()
    elif piece == "k":
        return king_move()
    elif piece == "n":
        return knight_move()
    return False


def display_game():
    """Displays the game board in ascii or graphically"""
    material_update()
    material_side = ""
    display_side = True  # Used to select which way the board will display (True is white perspective)

    if Material > 0:
        print(f"Material:{material_side}{Material}\n")
    for i in range(1, 9):
        print("\n", 8 - i, [GameArray[-i][j].piece for j in range(8)])
    print("     0    1    2    3    4    5    6    7  \n")
    if Material < 0:
        print(f"Material:{material_side}{Material}\n")

    # Handles graphical board update
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
                    print(462, "display error")
    else:
        for i in range(1, 9):
            for j in range(1, 9):
                if GameArray[-i][-j].piece.lower() == "p":
                    draw_pawn(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece.lower() == "r":
                    draw_rook(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece.lower() == "n":
                    draw_knight(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece.lower() == "q":
                    draw_queen(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece.lower() == "b":
                    draw_bishop(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece.lower() == "k":
                    draw_king(i - 1, j - 1, GameArray[-i][-j].piece.isupper())
                elif GameArray[-i][-j].piece.lower() == " ":
                    pass
                else:
                    print("display error, functions.390")


def material_update():
    global Material
    Material = 0
    for row in range(8):
        for column in range(8):
            piece = GameArray[row][column].piece
            if piece == "p":
                Material -= 1
            elif piece == "P":
                Material += 1
            elif piece == "B" or piece == "N":
                Material += 3
            elif piece == "b" or piece == "n":
                Material -= 3
            elif piece == "r":
                Material -= 5
            elif piece == "R":
                Material += 5
            elif piece == "q":
                Material -= 9
            elif piece == "Q":
                Material += 9


def column_index(column: str) -> int:
    """turns a letter (h through a) into the appropriate array index for the board array"""
    columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
    for i in range(8):
        if columns[i] == column:
            return i
    return -8


def index_column(index: int) -> str:
    """turns a board index into a letter for that column on the chess board"""
    columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
    count = -1
    for column in columns:
        count += 1
        if count == index:
            return column
    return "a"


def under_attack(piece_side: bool, row: int, column: int) -> bool:
    """Determines if a square is under attack by any other pieces, returns True if yes"""
    global CheckMoveLegality, AttackingCoords
    reverse_row = [*range(0, row)]
    reverse_row.reverse()
    reverse_col = [*range(0, column)]
    reverse_col.reverse()
    AttackingCoords = []
    attacked = False
    # check for queens, rooks, and kings on rows and columns
    done = False
    for row_i in range(row + 1, 8):  # generates row indices in the positive direction away from the piece and checks them
        if not done:
            try:
                opponent = GameArray[row_i][column].piece.isupper() != piece_side
                piece = GameArray[row_i][column].piece.lower()
            except IndexError:
                opponent = False
                piece = False
            if piece == " ":
                continue
            elif piece != " " and not opponent:
                done = True
            elif opponent and piece == "p" or piece == "n" and opponent or piece == "b" and opponent:
                done = True
            elif opponent and piece == "r":
                AttackingCoords.append([row_i, column])
                attacked = True
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column])
                attacked = True
                done = True
            elif opponent and piece == "k" and row_i == row + 1:
                AttackingCoords.append([row_i, column])
                attacked = True
                done = True
            else:
                done = True
        else:
            pass

    done = False
    for row_i in reverse_row:  # generates row indices in the negative direction away from the piece and checks them
        if not done:
            try:
                opponent = GameArray[row_i][column].piece.isupper() != piece_side
                piece = GameArray[row_i][column].piece.lower()
            except IndexError:
                opponent = False
                piece = False
            if piece == " ":
                continue
            elif piece != " " and not opponent:
                done = True
            elif opponent and piece == "p" or piece == "n" and opponent or piece == "b" and opponent:
                done = True
            elif opponent and piece == "r":
                AttackingCoords.append([row_i, column])
                attacked = True
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column])
                attacked = True
                done = True
            elif opponent and piece == "k" and row_i == row - 1:
                AttackingCoords.append([row_i, column])
                attacked = True
                done = True
            else:
                done = True
        else:
            pass

    done = False
    for column_i in range(column + 1, 8):  # generates column indices in the positive direction away from the piece
        if not done:
            try:
                opponent = GameArray[row][column_i].piece.isupper() != piece_side
                piece = GameArray[row][column_i].piece.lower()
            except IndexError:
                opponent = False
                piece = False
            if piece == " ":
                continue
            elif piece != " " and not opponent:
                done = True
            elif opponent and piece == "p" or piece == "n" and opponent or piece == "b" and opponent:
                done = True
            elif opponent and piece == "r":
                AttackingCoords.append([row, column_i])
                attacked = True
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row, column_i])
                attacked = True
                done = True
            elif opponent and piece == "k" and column_i == column + 1:
                AttackingCoords.append([row, column_i])
                attacked = True
                done = True
            else:
                done = True
        else:
            pass

    done = False
    for column_i in reverse_col:  # generates column indices in the negative direction away from the piece
        if not done:
            try:
                opponent = GameArray[row][column_i].piece.isupper() != piece_side
                piece = GameArray[row][column_i].piece.lower()
            except IndexError:
                opponent = False
                piece = False
            if piece == " ":
                continue
            elif piece != " " and not opponent:
                done = True
            elif opponent and piece == "p" or piece == "n" and opponent or piece == "b" and opponent:
                done = True
            elif opponent and piece == "r":
                AttackingCoords.append([row, column_i])
                attacked = True
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row, column_i])
                attacked = True
                done = True
            elif opponent and piece == "k" and column_i == column - 1:
                AttackingCoords.append([row, column_i])
                attacked = True
                done = True
            else:
                done = True
        else:
            pass

    done = False
    # checks each diagonal direction
    for row_i in range(row + 1, 8):  # + +
        difference = row_i - row
        column_i = column + difference
        if column_i > 7 or column_i < 0:
            done = True
        if row_i < 0 or row_i > 7:
            done = True
        if not done:
            try:
                opponent = GameArray[row_i][column_i].piece.isupper() != piece_side
                piece = GameArray[row_i][column_i].piece.lower()
            except IndexError:
                opponent = False
                piece = False
            if piece == " ":
                continue
            elif piece != " " and not opponent:
                done = True
            elif opponent and piece == "r" or opponent and piece == "n" or opponent and piece == "k" or opponent and piece == "p":
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column_i])
                attacked = True
                done = True
            elif opponent and piece == "b":
                AttackingCoords.append([row_i, column_i])
                attacked = True
                done = True
            else:
                done = True
        else:
            pass

    done = False
    for row_i in range(row + 1, 8):  # + -
        difference = row_i - row
        column_i = column - difference
        if column_i > 7 or column_i < 0:
            done = True
        if row_i < 0 or row_i > 7:
            done = True
        if not done:
            try:
                opponent = GameArray[row_i][column_i].piece.isupper() != piece_side
                piece = GameArray[row_i][column_i].piece.lower()
            except IndexError:
                opponent = False
                piece = False
            if piece == " ":
                continue
            elif piece != " " and not opponent:
                done = True
            elif opponent and piece == "r" or opponent and piece == "n" or opponent and piece == "k" or opponent and piece == "p":
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column_i])
                attacked = True
                done = True
            elif opponent and piece == "b":
                AttackingCoords.append([row_i, column_i])
                attacked = True
                done = True
            else:
                done = True
        else:
            pass

    done = False
    for row_i in reverse_row:  # - -
        difference = row - row_i
        column_i = column - difference
        if column_i > 7 or column_i < 0:
            done = True
        if row_i < 0 or row_i > 7:
            done = True
        if not done:
            try:
                opponent = GameArray[row_i][column_i].piece.isupper() != piece_side
                piece = GameArray[row_i][column_i].piece.lower()
            except IndexError:
                opponent = False
                piece = False
            if piece == " ":
                continue
            elif piece != " " and not opponent:
                done = True
            elif opponent and piece == "r" or opponent and piece == "n" or opponent and piece == "k" or opponent and piece == "p":
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column_i])
                attacked = True
                done = True
            elif opponent and piece == "b":
                AttackingCoords.append([row_i, column_i])
                attacked = True
                done = True
            else:
                done = True
        else:
            pass

    done = False
    for row_i in reverse_row:  # - +
        difference = row - row_i
        column_i = column + difference
        if column_i > 7 or column_i < 0:
            done = True
        if row_i < 0 or row_i > 7:
            done = True
        if not done:
            try:
                opponent = GameArray[row_i][column_i].piece.isupper() != piece_side
                piece = GameArray[row_i][column_i].piece.lower()
            except IndexError:
                opponent = False
                piece = False
            if piece == " ":
                continue
            elif piece != " " and not opponent:
                done = True
            elif opponent and piece == "r" or opponent and piece == "n" or opponent and piece == "k" or opponent and piece == "p":
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column_i])
                attacked = True
                done = True
            elif opponent and piece == "b":
                AttackingCoords.append([row_i, column_i])
                attacked = True
                done = True
            else:
                done = True
        else:
            pass

    # checks for knights in either of the 8 possible squares
    offset_list = [-2, -1, 1, 2]
    for offset_row in offset_list:
        for offset_col in offset_list:
            t_row = offset_row + row
            t_col = offset_col + column
            if abs(offset_row) == abs(offset_col):
                continue
            elif t_col > 7 or t_col < 0 or t_row > 7 or t_row < 0:
                continue
            else:
                try:
                    opponent = GameArray[t_row][t_col].piece.isupper() != piece_side
                    is_knight = GameArray[t_row][t_col].piece.lower() == "n"
                except LookupError:
                    is_knight = False
                    opponent = False
                if opponent and is_knight:
                    AttackingCoords.append([t_row, t_col])
                    attacked = True

    # checks for pawns, based on which side matters. If Check_Move_Legality == True, it will instead check pawn movement not pawn attack pattern
    if not CheckMoveLegality:
        pawn_col_list = [-1, 1]
        mult = [1]
    else:
        pawn_col_list = [0]
        mult = [1, 2]
    pawn_direct = -1
    if piece_side:
        pawn_direct = 1
    for multiplier in mult:
        for i in pawn_col_list:
            pawn_direct *= multiplier
            pawn_row = row + pawn_direct
            pawn_col = i + column
            try:
                pawn_check = GameArray[pawn_row][pawn_col].piece.lower() == "p"
                opponent = GameArray[pawn_row][pawn_col].piece.isupper() != piece_side
            except IndexError:
                pawn_check = False
                opponent = False
            if pawn_check and opponent:
                AttackingCoords.append([pawn_row, pawn_col])
                attacked = True

    # Checks for kings
    for row_offset in [-1, 0, 1]:
        for col_offset in [-1, 0, 1]:
            k_col = col_offset + column
            k_row = row_offset + row
            if row_offset == 0 and col_offset == 0:
                continue
            elif k_col > 7 or k_col < 0:
                continue
            elif k_row > 7 or k_row < 0:
                continue
            else:
                square_is_king = GameArray[k_row][k_col].piece.lower() == "k"
                is_enemy_king = GameArray[k_row][k_col].piece.isupper() != piece_side
                if square_is_king and is_enemy_king:  # Enemy king found next to SOI
                    attacked = True

    if attacked:
        return True
    else:
        return False


def put_king_in_check(k_row: int, k_col: int, row_1: int, col_1: int, row_2: int, col_2: int, piece_type: str, king_side: bool) -> bool:
    test_array = copy.deepcopy(GameArray)
    test_array[row_1][col_1].piece = " "
    test_array[row_2][col_2].piece = piece_type
    in_check = under_attack(king_side, k_row, k_col)
    print(875, in_check)
    return in_check


def has_moves(row: int, col: int) -> bool:
    """Checks if the piece at the coordinates has any legal moves"""
    piece_type = GameArray[row][col].piece
    piece_side = piece_type.isupper()
    king_col = None
    king_row = None
    king_side = None
    print(886, f"called has_moves at ({row},{col}) (row, col)")

    for i in range(8):  # Finds the relevant king, to check if the king is put in check by any of these potential moves
        for j in range(8):
            found_king = GameArray[i][j].piece
            king_side = found_king.isupper()
            if found_king == "k" and king_side == piece_side or found_king == "K" and king_side == piece_side:
                king_col = j
                king_row = i

    if piece_type == " ":  # Empty square has no moves
        return False

    elif piece_type.lower() == "k":  # Checks if a king has any legal moves
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                k_col = col_offset + col
                k_row = row_offset + row
                if row_offset == 0 and col_offset == 0:
                    continue
                elif k_col > 7 or k_col < 0:
                    continue
                elif k_row > 7 or k_row < 0:
                    continue
                else:
                    square_is_attacked = under_attack(piece_side, k_row, k_col)
                    square_piece_legal_enemy = GameArray[k_row][k_col].piece != " " and GameArray[k_row][k_col].piece.isupper() != GameArray[k_row][k_col].piece.isupper() and not under_attack(not Side, k_row, k_col)
                    square_piece_empty = GameArray[k_row][k_col].piece == " "
                    if square_piece_empty or square_piece_legal_enemy:  # If king has legal move
                        if not square_is_attacked:
                            print(914, f"legal king move to ({k_row},{k_col}) (row, col) from ({row}, {col}) piece_type:{piece_type}")
                            return True

    elif piece_type.lower() == "n":  # Checks if a knight has any legal moves
        offset_list = [-2, -1, 1, 2]
        for offset_row in offset_list:
            for offset_col in offset_list:
                t_row = offset_row + row
                t_col = offset_col + col
                if abs(offset_row) == abs(offset_col):
                    continue
                elif t_col > 7 or t_col < 0 or t_row > 7 or t_row < 0:
                    continue
                else:
                    try:
                        is_enemy = GameArray[t_row][t_col].piece.isupper() != piece_side
                        is_empty = GameArray[t_row][t_col].piece.lower() == " "
                    except LookupError:
                        is_empty = False
                        is_enemy = False
                    if is_enemy or is_empty:
                        return not put_king_in_check(king_row, king_col, row, col, t_row, t_col, piece_type, king_side)  # Put check here for the king (discovered etc.)

    elif piece_type.lower() == "p":
        if piece_side:
            pawn_direction = 1
        else:
            pawn_direction = -1
        if 7 >= row + pawn_direction >= 0:
            if GameArray[row + pawn_direction][col].piece == " ":  # Check if the pawn can move forward
                return True  # Put check here for the king (discovered etc.)
            else:
                for col_direct in [-1, 1]:
                    if 7 >= col_direct + col >= 0:
                        target_square = GameArray[row + pawn_direction][col + col_direct].piece
                        if target_square != " " and target_square.isupper() != piece_side:  # Check if the pawn can capture a piece
                            return not put_king_in_check(king_row, king_col, row, col, row + pawn_direction, col + col_direct, piece_type, king_side)

    elif piece_type.lower() == "r":
        scan = [1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7]
        for offset in scan:
            if 7 >= row + offset >= 0:
                target_square = GameArray[row + offset][col].piece
                is_enemy = target_square.isupper() != piece_side
                if target_square == " " or target_square != " " and is_enemy:
                    return not put_king_in_check(king_row, king_col, row, col, row + offset, col, piece_type, king_side)
                else:
                    continue
        for offset in scan:
            if 7 >= col + offset >= 0:
                target_square = GameArray[row][col + offset].piece
                is_enemy = target_square.isupper() != piece_side
                if target_square == " " or target_square != " " and is_enemy:
                    return not put_king_in_check(king_row, king_col, row, col, row, col + offset, piece_type, king_side)
                else:
                    continue

    elif piece_type.lower() == "b":
        scan = [1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7]
        diag_scan = [1, -1]
        for offset in scan:
            for diag_mult in diag_scan:
                bc_row = row + offset * diag_mult
                bc_col = col + offset
                if 7 >= bc_row >= 0 and 7 >= bc_col >= 0:
                    target_square = GameArray[bc_row][bc_col].piece
                    is_enemy = target_square.isupper() != piece_side
                    if target_square == " " or target_square != " " and is_enemy:
                        return not put_king_in_check(king_row, king_col, row, col, row + offset * diag_mult, col + offset, piece_type, king_side)
                    else:
                        continue

    elif piece_type.lower() == "q":
        scan = [1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7]
        diag_scan = [1, -1]
        for offset in scan:
            if 7 >= row + offset >= 0:
                target_square = GameArray[row + offset][col].piece
                is_enemy = target_square.isupper() != piece_side
                if target_square == " " or target_square != " " and is_enemy:
                    return not put_king_in_check(king_row, king_col, row, col, row + offset, col, piece_type, king_side)
                else:
                    continue
        for offset in scan:
            if 7 >= col + offset >= 0:
                target_square = GameArray[row][col + offset].piece
                is_enemy = target_square.isupper() != piece_side
                if target_square == " " or target_square != " " and is_enemy:
                    return not put_king_in_check(king_row, king_col, row, col, row, col + offset, piece_type, king_side)
                else:
                    continue
        for offset in scan:
            for diag_mult in diag_scan:
                if 7 >= row + offset >= 0:
                    target_square = GameArray[row + offset * diag_mult][col + offset].piece
                    is_enemy = target_square.isupper() != piece_side
                    if target_square == " " or target_square != " " and is_enemy:
                        return not put_king_in_check(king_row, king_col, row, col, row + offset * diag_mult, col + offset, piece_type, king_side)
                    else:
                        continue
    return False  # if it gets to this point, no moves were found for the piece


def is_checkmate(checking_piece: str, a_row: int, a_col: int, k_row: int, k_col: int) -> bool:
    skip_block_checks = False
    if GameArray[k_row][k_col].piece.lower() != "k":
        return False
    if checking_piece.isupper == GameArray[k_row][k_col].piece.isupper():
        return False
    if checking_piece.lower() == "n":  # if the checking piece is a knight, no need to check for blocking moves
        skip_block_checks = True
    if under_attack(Side, a_row, a_col):  # if the checking piece can be captured, it's not check
        print(1043, "can capture attacker")
        return False
    for row_offset in [-1, 0, 1]:
        for col_offset in [-1, 0, 1]:
            col = col_offset + k_col
            row = row_offset + k_row
            if row_offset == 0 and col_offset == 0:
                continue
            elif 7 >= col >= 0:
                continue
            elif 7 >= row >= 0:
                continue
            else:
                square_piece_legal = GameArray[row][col].piece != " " and GameArray[row][col].piece.isupper() != GameArray[k_row][k_col].piece.isupper() and not under_attack(not Side, row, col)
                square_piece_empty = GameArray[row][col].piece == " " and not under_attack(not Side, row, col)
                if square_piece_empty or square_piece_legal:  # if empty space adjacent, and not under check, the king can move out of check
                    return False
    if not skip_block_checks:
        potential_blockers = calculate_squares_between(Side, a_row, a_col, k_row, k_col)
        for i in range(len(potential_blockers)):
            row_1 = potential_blockers[i][0][0]
            row_2 = potential_blockers[i][1][0]
            col_1 = potential_blockers[i][0][1]
            col_2 = potential_blockers[i][1][1]
            moving_piece = GameArray[row_1][col_1].piece
            moving_move = GameArray[row_1][col_1].move
            GameArray[row_2][col_2].piece = GameArray[row_1][col_1].piece
            GameArray[row_2][col_2].move = GameArray[row_1][col_1].move
            GameArray[row_1][col_1].piece = " "
            GameArray[row_1][col_1].move = 0
            if not under_attack(Side, k_row, k_col):
                return True
            else:
                GameArray[row_2][col_2].piece = " "
                GameArray[row_2][col_2].move = 0
                GameArray[row_1][col_1].piece = moving_piece
                GameArray[row_1][col_1].move = moving_move
        return True
    else:
        return True


def is_stalemate() -> bool:
    white_stalemated = True
    black_stalemated = True
    for i in range(8):
        for j in range(8):
            if GameArray[i][j].piece.isupper():
                if has_moves(i, j):
                    print(1068, f"white side has moves from piece at ({i}, {j})")
                    white_stalemated = False
            if GameArray[i][j].piece.islower():
                if has_moves(i, j):
                    print(1072, f"black side has moves from piece at ({i}, {j})")
                    black_stalemated = False

    return white_stalemated or black_stalemated


def calculate_squares_between(side: bool, a_row: int, a_col: int, k_row: int, k_col: int) -> list[list[list[int]]]:
    """Returns a list of all pieces that could theoretically block the line of attack between the coordinates that are
    passed in. The output is structured like this: the primary list holds the secondary lists. the secondary lists each
    hold two 3rd tier lists, each one of which contains a pair of coords [row, col] the therefor [0][0][0] would get the
    first pair of coordinates, the first coordinate (which is the starting position of a piece that could block check)
    and then grab the row from that coord"""
    global CheckMoveLegality
    CheckMoveLegality = True
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
        if under_attack(side, pos_move_row, pos_move_col):
            for coord in AttackingCoords:
                coord_pair = [coord, [pos_move_row, pos_move_col]]
                move_output.append(coord_pair)

    CheckMoveLegality = False
    return move_output  # This is a list of all potential pieces (their coordinates) that could theoretically block the line of attack between the two given coordinate sets, paired with the square they would move to


def piece_move(column_1: int, column_2: int, row_1: int, row_2: int, piece_type) -> bool:
    """Moves piece from coord_1 to coord_2, and checks for legality, and game results. Returns False if illegal"""
    global MoveCount, MoveList, Side, GameArray, Root, ContentFrame, GameEnd, CheckmateLabel, MoveInputList
    undo = False
    k_row = None
    k_col = None
    ended = False
    promotion = None
    enemy_k_row = None
    enemy_k_col = None

    backup_piece_1 = GameArray[row_1][column_1].piece  # Storing piece data so that the move can be reverted if it results in an illegal position
    backup_move_1 = GameArray[row_1][column_1].move
    backup_piece_2 = GameArray[row_2][column_2].piece
    backup_move_2 = GameArray[row_2][column_2].move

    pgn_str = " "
    pgn_target = GameArray[row_2][column_2].piece.upper()
    pgn_column = index_column(column_2)  # outputs pgn type for each move
    pgn_column_start = index_column(column_1)
    pgn_1 = piece_type.upper()

    if piece_type.lower() == "p":  # pawn takes notation
        if pgn_target != " " and pgn_target != "P":
            pgn_1 = f"{pgn_column_start}x{pgn_target}"
        elif pgn_target != " " and pgn_target == "P":
            pgn_1 = f"{pgn_column_start}x"
        else:
            pgn_1 = ""

    if piece_type.isupper() == Side:  # Verifying the piece is the appropriate piece for the turn
        if backup_piece_1.lower() == "p":  # Checking if the piece is a pawn eligible for promotion
            if Side and row_2 == 7 or not Side and row_2 == 0:
                try:
                    promotion = MoveInput[4].casefold()
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

        GameArray[row_2][column_2].move = backup_move_1  # normal movement block
        GameArray[row_1][column_1].piece = " "
        GameArray[row_1][column_1].move = 0
    else:
        print("wrong turn/piece")
        return False

    # check if king (white or black depending on Side) is put in check
    for row_i in range(8):
        for col_i in range(8):
            if GameArray[row_i][col_i].piece.lower() == "k" and GameArray[row_i][col_i].piece.isupper() == Side:
                k_row = row_i
                k_col = col_i
            if GameArray[row_i][col_i].piece.lower() == "k" and GameArray[row_i][col_i].piece.isupper() != Side:
                enemy_k_row = row_i
                enemy_k_col = col_i
    print(Side, k_row, k_col)
    if k_row is None or k_col is None or enemy_k_row is None or enemy_k_col is None:
        undo = True
    else:
        if under_attack(Side, k_row, k_col) or undo:
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

    if under_attack(not Side, enemy_k_row, enemy_k_col):
        for coords in AttackingCoords:
            print(coords)
            attacker = GameArray[coords[0]][coords[1]].piece
            a_row = coords[0]
            a_col = coords[1]
            if is_checkmate(attacker, a_row, a_col, enemy_k_row, enemy_k_col):
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
    if not ended and is_stalemate():
        pgn_str = "Stalemate: draw"
        ended = True
    if not ended and is_threefold(current_fen):
        pgn_str = "Threefold Repetition: draw"
        ended = True
    if ended:
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

    if MoveInput.lower() == "o-o" or MoveInput.lower() == "o-o-o":  # compiles each move into one list of moves
        if piece_type.lower() == "r":
            if Side:
                MoveList.append(MoveInput.upper())
            else:
                MoveList.append(MoveInput.lower())
            MoveInputList.append(f"{piece_type}{MoveInput}")
            MoveCount += 1
            Side = not Side
            return True
    else:
        Side = not Side
        MoveInputList.append(f"{piece_type}{MoveInput}")
        MoveList.append(f"{pgn_1}{pgn_column}{row_2 + 1}")
        MoveCount += 1
        return True


def save_game():
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
    legal_target = (piece_type.isupper() != target_piece.isupper() or target_piece == " ") and piece_type.lower() == "r"

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
    legal_target = (piece_type.isupper() != target_piece.isupper() or target_piece == " ") and piece_type.lower() == "b"  # true if legal move

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
    legal_target = (piece_type.isupper() != target_piece.isupper() or target_piece == " ") and piece_type.lower() == "q"  # true if legal move

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
    start_column = column_index(MoveInput[0])
    start_row = int(MoveInput[1]) - 1
    target_column = column_index(MoveInput[2])
    target_row = int(MoveInput[3]) - 1
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    legal_target = (target_piece.isupper() != piece_type.isupper() or target_piece == " ") and piece_type.lower() == "n"  # checks if the target square is empty or an opponent's piece

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
    legal_move = legal_target and piece_type.lower() == "k"  # checks if it's a legal move basically
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
    row_distance = 2 >= abs(start_row - target_row) >= 1
    right_way = pawn_side * abs(start_row - target_row) + start_row == target_row
    is_diag = abs(start_row - target_row) == abs(start_column - target_column) == 1
    is_opponent = piece_type.isupper() != target_piece.isupper() and target_piece != " "

    legal_target_attack = is_diag and right_way and is_opponent  # True if legal for attacking a piece directly diagonal one square left or right
    legal_target_move = is_straight and right_way and empty_target and row_distance

    print(1290, is_diag, right_way, is_opponent, "\n", is_straight, right_way, empty_target, row_distance)

    if legal_target_attack or legal_target_move:  # Normal move or attack
        return piece_move(start_column, target_column, start_row, target_row, piece_type)

    # En Passant logic:
    try:
        last_move_row_1 = int(MoveInputList[-1][2]) - 1
        last_move_row_2 = int(MoveInputList[-1][4]) - 1
        last_move_double = abs(last_move_row_1 - last_move_row_2) == 2
        last_move_piece = MoveInputList[-1][0].lower() == "p"
        last_move_col = column_index(MoveInputList[-1][1])
        print(1303, MoveInputList[-1])
    except ValueError:
        last_move_double = False
        print(1306, MoveInputList[-1])
    except IndexError:
        last_move_double = False
        print(1309, "first pawn move, illegal")

    if last_move_piece and last_move_double:
        if start_row == 4 and Side or start_row == 3 and not Side:  # The only two rows you can do en passant from
            passant_row = True
        for shift in [-1, 1]:
            if last_move_col + shift == start_column:
                passant_col = True
        if passant_col and passant_row:
            piece_move(start_column, target_column, start_row, target_row, piece_type)  # Moves the pawn
            print(1299, last_move_col, last_move_row_2)
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
    checks = not under_attack(king.isupper(), i, 4) and not under_attack(king.isupper(), i, king_j) and not under_attack(king.isupper(), i, rook_j)
    clear = GameArray[i][rook_j].piece == " " and GameArray[i][king_j].piece == " " and extra_clear
    print(1350, king_legal, rook_legal, checks, clear, GameArray[i][4].move == 0, GameArray[i][4].piece == king)

    if king_legal and rook_legal and checks and clear:
        piece_move(4, king_j, i, i, king)
        piece_move(rook_i, rook_j, i, i, rook)
        return True
    else:
        return False


if __name__ == "__main__":
    game_init("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq")
    save_game()
