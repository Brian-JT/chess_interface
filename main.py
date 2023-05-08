from tkinter import *
from tkinter import ttk
import datetime


global MoveInput, MoveCount, MoveList, Side, Material, WhitePieces, BlackPieces, Root, InputGui, GameArray, \
    BoardCanvas, InputEntry, WhiteColor, BlackColor, WhiteHighlight, BlackHighlight, ContentFrame, GameEnd, \
    CheckmateLabel, DarkModeBackground, DarkModeForeground, CheckMoveLegality, AttackingCoords, BlockingTargetList


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
    global MoveInput, BoardCanvas, InputEntry, MoveList, GameEnd
    MoveInput = str(InputGui.get())
    check_move_input()
    print(MoveInput)
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
        board_setup()
        display_game()
        InputEntry.delete(0, END)
        if MoveInput == "exit":
            Root.quit()
        return

    else:  # Standard move main loop (checks input, plays move, erases the board, redraws the board, erases input value)
        print("Standard move:")
        play_move()
        blank_board()
        display_game()
        InputEntry.delete(0, END)
        return


def board_setup():
    """Sets up the Game Array, fresh"""
    global MoveCount, MoveList, Side, Material, WhitePieces, BlackPieces, GameArray, CheckMoveLegality
    Side = True  # True = white's turn
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    CheckMoveLegality = False  # Used to modify under_check function to instead check for legal moves to a certain square
    Material = 0  # material advantage (positive is white)
    MoveList = []  # A list of moves played in each game, stored as a list of strings
    MoveCount = 0  # Each turn from each player adds 1
    piece_list = ["r", "n", "b", "q", "k", "b", "n", "r"]  # the standard layout of the back rank of the chess board
    WhitePieces = [piece for piece in fen if piece.isupper() and piece.isalpha()]  # Generates a list of existing pieces on the board that are white
    BlackPieces = [piece for piece in fen if piece.islower() and piece.isalpha()]  # Since it's symmetric, it just turns them all lowercase for initialization
    array_from_fen(fen)


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


def game_init():
    """Initiates the Tkinter event loop (and thus the entire game)"""
    global Root, InputGui, BoardCanvas, InputEntry, WhiteColor, BlackColor, WhiteHighlight, \
        BlackHighlight, ContentFrame, GameEnd, DarkModeBackground, DarkModeForeground
    board_setup()
    GameEnd = False
    WhiteColor = "#C3C3C2"  # Default white piece color
    BlackColor = "#000101"  # Default black piece color
    WhiteHighlight = "#000101"  # Default highlights
    BlackHighlight = "#C3C3C2"
    DarkModeBackground = "#333537"
    DarkModeForeground = "#989998"

    Root = Tk()  # Graphical display initiation/loop
    Root.title("Chess v0.03")  # Assigns title of the window

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

    BoardCanvas = Canvas(ContentFrame, width=400, height=399, background=DarkModeBackground, highlightthickness=0)
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
            x1 = i * 100
            x2 = x1 + 50
            y1 = j * 100
            y2 = y1 + 50
            BoardCanvas.create_rectangle(x1, y1, x2, y2, width=0, fill="#566975", activefill="#8a9da8")
            BoardCanvas.create_rectangle(x1 + 50, y1 + 50, x2 + 50, y2 + 50, width=0, fill="#566975", activefill="#8a9da8")

    for j in range(0, 7):  # Creates the grid of dark squares
        for i in range(0, 5):
            x1 = i * 100 - 50
            x2 = x1 + 50
            y1 = j * 100
            y2 = y1 + 50
            BoardCanvas.create_rectangle(x1, y1, x2, y2, width=0, fill="#455561", activefill="#798fa0")
            BoardCanvas.create_rectangle(x1 + 50, y1 + 50, x2 + 50, y2 + 50, width=0, fill="#455561", activefill="#798fa0")


def draw_pawn(row: int, column: int, color: bool):
    """Draws a pawn at the coordinates passed in, on the board canvas"""
    global BoardCanvas
    row *= 50
    column *= 50
    a = 22 + column
    b = 21 + row

    c = 30 + column
    d = 45 + row

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
    row *= 50
    column *= 50
    a = 16 + column
    b = 15 + row

    c = 36 + column
    d = 45 + row

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
    row *= 50
    column *= 50
    a = 15 + column
    b = 20 + row

    c = 35 + column
    d = 35 + row

    e = 11 + column
    f = 10 + row

    g = 38 + column
    h = 20 + row

    i = 11 + column
    j = 35 + row

    k = 38 + column
    l_ = 45 + row

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
    row *= 50
    column *= 50
    a = 15 + column
    b = 15 + row

    c = 38 + column
    d = 45 + row

    e = 25.5 + column
    f = 15 + row

    g = 25.5 + column
    h = 8 + row

    i = 28.5 + column
    j = 15 + row

    k = 30.5 + column
    l_ = 8 + row

    m = 22.5 + column
    n = 15 + row

    o = 20.5 + column
    p = 8 + row

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
    row *= 50
    column *= 50
    a = 15 + column
    b = 15 + row

    c = 35 + column
    d = 27.5 + row

    e = 20 + column
    f = 27.5 + row

    g = 30 + column
    h = 32.5 + row

    i = 15 + column
    j = 32.5 + row

    k = 35 + column
    l_ = 45 + row

    m = 25.5 + column
    n = 15 + row

    o = 25.5 + column
    p = 8 + row

    q = 28.5 + column
    r = 15 + row

    s = 30.5 + column
    t = 8 + row

    u = 22.5 + column
    v = 15 + row

    w = 20.5 + column
    x = 8 + row

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
    row *= 50
    column *= 50
    a = 12 + column
    b = 35 + row

    c = 41 + column
    d = 45 + row

    e = 20 + column
    f = 10 + row

    g = 33 + column
    h = 35 + row

    i = 20 + column
    j = 15 + row

    k = 15 + column
    l_ = 25 + row

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
    if MoveInput == "restart" or MoveInput == "exit" or MoveInput == "flip" or MoveInput == "o-o" or MoveInput == "o-o-o":  # Checks if input is a special case
        print(383)
        return MoveInput

    valid_len = len(MoveInput) == 4 or len(MoveInput) == 5
    if len(MoveInput) == 5:
        try:
            MoveInput[4]
        except IndexError:
            MoveInput += "q"

    if valid_len and MoveInput[0].isalpha() and MoveInput[2].isalpha() and \
            MoveInput[1].isnumeric() and MoveInput[3].isnumeric():  # Checks if format is proper coordinate notation
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
            print(398)
    else:
        MoveInput = "invalid"
        print(401)
    return MoveInput


def play_move():
    piece = check_move_input().lower()
    print(404, piece)
    if piece == "exit":
        return
    elif piece == "invalid":
        return
    elif piece == "o-o":
        castle(False)
    elif piece == "o-o-o":
        castle(True)
    elif piece == "q":
        queen_move()
    elif piece == "r":
        rook_move()
    elif piece == "b":
        bishop_move()
    elif piece == "p":
        pawn_move()
    elif piece == "k":
        king_move()
    elif piece == "n":
        knight_move()
    else:
        print("invalid move 424")
        return


def display_game():
    """Displays the game board in ascii or graphically"""
    material_update()
    material_side = ""
    display_side = True  # Used to select which way the board will display (True is white perspective)

    if Material > 0:
        print(f"Material:{material_side}{Material}\n")
    for i in range(1, 9):
        print("\n", [GameArray[-i][j].piece for j in range(8)], 9 - i)
    print("   a    b    c    d    e    f    g    h  \n")
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
                print(465)
                continue
            elif piece != " " and not opponent:
                print(468)
                done = True
            elif opponent and piece == "p" or piece == "n" and opponent or piece == "b" and opponent:
                print(471)
                done = True
            elif opponent and piece == "r":
                AttackingCoords.append([row_i, column])
                print(474)
                attacked = True
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column])
                print(477)
                attacked = True
                done = True
            elif opponent and piece == "k" and row_i == row + 1:
                AttackingCoords.append([row_i, column])
                print(480)
                attacked = True
                done = True
            else:
                done = True
        else:
            print(483)

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
                print(491)
                continue
            elif piece != " " and not opponent:
                print(494)
                done = True
            elif opponent and piece == "p" or piece == "n" and opponent or piece == "b" and opponent:
                print(497)
                done = True
            elif opponent and piece == "r":
                AttackingCoords.append([row_i, column])
                print(500)
                attacked = True
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column])
                print(503)
                attacked = True
                done = True
            elif opponent and piece == "k" and row_i == row + 1:
                AttackingCoords.append([row_i, column])
                print(506)
                attacked = True
                done = True
            else:
                done = True
        else:
            print(509)

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
                print(517)
                continue
            elif piece != " " and not opponent:
                print(520)
                done = True
            elif opponent and piece == "p" or piece == "n" and opponent or piece == "b" and opponent:
                print(523)
                done = True
            elif opponent and piece == "r":
                AttackingCoords.append([row, column_i])
                print(526)
                attacked = True
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row, column_i])
                print(526)
                attacked = True
                done = True
            elif opponent and piece == "k" and column_i == row + 1:
                AttackingCoords.append([row, column_i])
                print(532)
                attacked = True
                done = True
            else:
                done = True
        else:
            print(535)

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
                print(543)
                continue
            elif piece != " " and not opponent:
                print(546)
                done = True
            elif opponent and piece == "p" or piece == "n" and opponent or piece == "b" and opponent:
                print(549)
                done = True
            elif opponent and piece == "r":
                AttackingCoords.append([row, column_i])
                print(552)
                attacked = True
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row, column_i])
                print(555)
                attacked = True
                done = True
            elif opponent and piece == "k" and column_i == row + 1:
                AttackingCoords.append([row, column_i])
                print(558)
                attacked = True
                done = True
            else:
                done = True
        else:
            print(561)

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
                print(574)
                continue
            elif piece != " " and not opponent:
                print(577)
                done = True
            elif opponent and piece == "r" or opponent and piece == "n" or opponent and piece == "k" or opponent and piece == "p":
                print(580)
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column_i])
                print(583)
                attacked = True
                done = True
            elif opponent and piece == "b":
                AttackingCoords.append([row_i, column_i])
                print(586)
                attacked = True
                done = True
            else:
                done = True
        else:
            print(589)

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
                print(601)
                continue
            elif piece != " " and not opponent:
                print(604)
                done = True
            elif opponent and piece == "r" or opponent and piece == "n" or opponent and piece == "k" or opponent and piece == "p":
                print(607)
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column_i])
                print(610)
                attacked = True
                done = True
            elif opponent and piece == "b":
                AttackingCoords.append([row_i, column_i])
                print(613)
                attacked = True
                done = True
            else:
                done = True
        else:
            print(616)

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
                print(628)
                continue
            elif piece != " " and not opponent:
                print(630)
                done = True
            elif opponent and piece == "r" or opponent and piece == "n" or opponent and piece == "k" or opponent and piece == "p":
                print(634)
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column_i])
                print(637)
                attacked = True
                done = True
            elif opponent and piece == "b":
                AttackingCoords.append([row_i, column_i])
                print(640)
                attacked = True
                done = True
            else:
                done = True
        else:
            print(643)

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
                print(655)
                continue
            elif piece != " " and not opponent:
                print(658)
                done = True
            elif opponent and piece == "r" or opponent and piece == "n" or opponent and piece == "k" or opponent and piece == "p":
                print(661)
                done = True
            elif opponent and piece == "q":
                AttackingCoords.append([row_i, column_i])
                print(664)
                attacked = True
                done = True
            elif opponent and piece == "b":
                AttackingCoords.append([row_i, column_i])
                print(667)
                attacked = True
                done = True
            else:
                done = True

    # checks for knights in either of the 8 possible squares
    offset_list = [-2, -1, 1, 2]
    for offset_row in offset_list:
        for offset_col in offset_list:
            t_row = offset_row + row
            t_col = offset_col + column
            if abs(offset_row) == abs(offset_col):
                print(675)
                continue
            elif t_col > 7 or t_col < 0 or t_row > 7 or t_row < 0:
                print(678)
                continue
            else:
                try:
                    opponent = GameArray[t_row][t_col].piece.isupper() != piece_side
                    is_knight = GameArray[t_row][t_col].piece.lower() == "n"
                except LookupError:
                    is_knight = False
                    opponent = False
                if opponent and is_knight:
                    print(688, t_row, t_col, opponent, is_knight)
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
                print(698, pawn_row, pawn_col)
                AttackingCoords.append([pawn_row, pawn_col])
                attacked = True
    if attacked:
        return True
    else:
        return False


def is_checkmate(checking_piece: str, a_row: int, a_col: int, k_row: int, k_col: int) -> bool:
    skip_block_checks = False
    print(907, "in is_checkmate")
    if checking_piece.lower() == "n":  # if the checking piece is a knight, no need to check for blocking moves
        skip_block_checks = True
        print(754, "can't block checker")
    if under_attack(Side, a_row, a_col):  # if the checking piece can be captured, it's not check
        print(756, "can capture checker", a_row, a_col, Side)
        return False
    for row_offset in [-1, 0, 1]:
        print(915)
        for col_offset in [-1, 0, 1]:
            print(917, row_offset, col_offset)
            col = col_offset + k_col
            row = row_offset + k_row
            print(920, f"checking possible king moves: {row}, {col}. king starts at {k_row}, {k_col}")
            if row_offset == 0 and col_offset == 0:
                print(922)
                continue
            elif col > 7 or col < 0:
                print(925)
                continue
            elif row > 7 or row < 0:
                print(928)
                continue
            else:
                print(931)
                if GameArray[row][col].piece == " " and not under_attack(not Side, row, col):  # if empty space adjacent, and not under check, the king can move out of check
                    print(933)
                    return False
    print(935, "skip block checks?", skip_block_checks)
    if not skip_block_checks:
        potential_blockers = calculate_squares_between(Side, a_row, a_col, k_row, k_col)
        print(938, potential_blockers)
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
                print(951)
                return True
            else:
                GameArray[row_2][col_2].piece = " "
                GameArray[row_2][col_2].move = 0
                GameArray[row_1][col_1].piece = moving_piece
                GameArray[row_1][col_1].move = moving_move
        return True
    else:
        print(959)
        return True


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
                print(move_output)

    CheckMoveLegality = False
    return move_output  # This is a list of all potential pieces (their coordinates) that could theoretically block the line of attack between the two given coordinate sets, paired with the square they would move to


def piece_move(column_1: int, column_2: int, row_1: int, row_2: int, piece_type):
    """Moves the piece from row and column 1 into row and column 2, leaving behind an empty tile object."""
    global MoveCount, MoveList, Side, GameArray, Root, ContentFrame, GameEnd, CheckmateLabel
    k_row = None
    k_col = None
    enemy_k_row = None
    enemy_k_col = None
    promotion = None
    undo = False
    pgn_target = GameArray[row_2][column_2].piece.upper()
    backup_piece_1 = GameArray[row_1][column_1].piece  # Storing piece data so that the move can be reverted if it results in an illegal position
    backup_move_1 = GameArray[row_1][column_1].move
    backup_piece_2 = GameArray[row_2][column_2].piece
    backup_move_2 = GameArray[row_2][column_2].move

    if piece_type.isupper() == Side:  # Verifying the piece is the appropriate piece for the turn
        if backup_piece_1.lower() == "p":  # Checking if the piece is a pawn eligible for promotion
            if Side and row_2 == 7 or not Side and row_2 == 0:
                try:
                    promotion = MoveInput[4].casefold()
                    print(1027, promotion)
                except TypeError:
                    print(1029)
                    promotion = "q"
                except IndexError:
                    print(1032)
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
        return

    # check if king (white or black depending on Side) is put in check
    for row_i in range(8):
        for col_i in range(8):
            if GameArray[row_i][col_i].piece.lower() == "k" and GameArray[row_i][col_i].piece.isupper() == Side:
                print("assigned friend king")
                k_row = row_i
                k_col = col_i
            if GameArray[row_i][col_i].piece.lower() == "k" and GameArray[row_i][col_i].piece.isupper() != Side:
                print("assigned enemy king")
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
            return

    if under_attack(not Side, enemy_k_row, enemy_k_col):
        print("Check!")
        print(f"is_checkmate({piece_type}, {row_2}, {column_2}, {enemy_k_row}, {enemy_k_col})")
        if is_checkmate(piece_type, row_2, column_2, enemy_k_row, enemy_k_col):
            print("Checkmate!")
            if Side:
                color = "white"
            else:
                color = "black"
            MoveList.append(f"Checkmate: {color} wins")
            save_game()
            display_game()
            CheckmateLabel = ttk.Label(ContentFrame, text=f"Checkmate: {color} wins", style="TLabel")
            CheckmateLabel.grid(column=2, row=2, sticky="N")
            GameEnd = True

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

    if Side:
        print("\nBlack to move")
    if not Side:
        print("\nWhite to move")

    if MoveInput.lower() == "o-o" or MoveInput.lower() == "o-o-o":  # compiles each move into one list of moves
        if piece_type.lower() == "r":
            if Side:
                MoveList.append(MoveInput.upper())
            else:
                MoveList.append(MoveInput.lower())
            MoveCount += 1
            Side = not Side
        print(MoveInput, 795)
    else:
        Side = not Side
        MoveList.append(f"{pgn_1}{pgn_column}{row_2 + 1}")
        MoveCount += 1
        print(800)

    print(MoveList)


def save_game():
    pgn_str = ""
    if MoveCount > 0:
        now = datetime.datetime.now()
        for move in MoveList:
            pgn_str += str(move)
            pgn_str += " "
        previous_games = open("pgn_log.txt", "a")
        pgn_str = str(now) + ": " + pgn_str + f"Move count:{MoveCount} \n\n"
        previous_games.write(pgn_str)
        previous_games.close()


def rook_move():
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
                return
        piece_move(start_column, target_column, start_row, target_row, piece_type)
        return

    elif start_row == target_row and legal_target:
        for i in range(1, move_length):
            column_i = i * column_direction
            if GameArray[target_row][column_i].piece != " ":
                return
        piece_move(start_column, target_column, start_row, target_row, piece_type)
        return
    else:
        return


def bishop_move():
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
                           piece_type.isupper() != target_piece.isupper() or target_piece == " ") and piece_type.lower() == "b"  # true if legal move

    if target_row < start_row:
        row_direction = -1
    if target_column < start_column:
        column_direction = -1

    if (target_row - start_row) * row_direction == (target_column - start_column) * column_direction and legal_target:
        for i in range(1, move_length):
            row_i = i * row_direction + start_row
            column_i = i * column_direction + start_column
            if GameArray[row_i][column_i].piece != " ":
                return
        piece_move(start_column, target_column, start_row, target_row, piece_type)
        return
    else:
        return


def queen_move():
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
                return
        piece_move(start_column, target_column, start_row, target_row, piece_type)  # updates board array
        return

    elif start_row == target_row and legal_target:  # true if the queen is only moving along the same row
        for i in range(1, move_length):
            column_i = start_column + (column_direction * i)
            if GameArray[target_row][column_i].piece != " ":  # checks that every square along the way is empty
                return
        piece_move(start_column, target_column, start_row, target_row, piece_type)  # updates board array
        return

    elif start_row != target_row and start_column != target_column:  # case where the target square is on a diagonal
        if (target_row - start_row) * row_direction == (
                target_column - start_column) * column_direction and legal_target:  # checks that it's on a proper diagonal, and if legal target
            for i in range(1, move_length):
                row_i = (i * row_direction) + start_row
                column_i = (i * column_direction) + start_column
                if GameArray[row_i][column_i].piece != " ":  # checks that each square along the path is empty
                    return
            piece_move(start_column, target_column, start_row, target_row, piece_type)  # updates the board array
            return

        else:
            return

    else:
        return


def knight_move():
    """Logic for legal knight moves"""
    start_column = column_index(MoveInput[0])
    start_row = int(MoveInput[1]) - 1
    target_column = column_index(MoveInput[2])
    target_row = int(MoveInput[3]) - 1
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    legal_target = (
                           target_piece.isupper() != piece_type.isupper() or target_piece == " ") and piece_type.lower() == "n"  # checks if the target square is empty or an opponent's piece

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
        piece_move(start_column, target_column, start_row, target_row, piece_type)
        return
    else:
        return


def king_move():
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
        piece_move(start_column, target_column, start_row, target_row, piece_type)
    return


def pawn_move():
    """Logic for legal pawn moves"""
    start_column = column_index(MoveInput[0])
    start_row = int(MoveInput[1]) - 1
    target_column = column_index(MoveInput[2])
    target_row = int(MoveInput[3]) - 1
    piece_type = GameArray[start_row][start_column].piece
    target_piece = GameArray[target_row][target_column].piece
    legal_target = (
                           piece_type.isupper() != target_piece.isupper() or target_piece == " ") and piece_type.lower() == "p"  # true if legal move
    first_move = GameArray[start_row][start_column].move == 0
    pawn_side = 1  # used to determine which direction the pawn can move
    if piece_type.islower():
        pawn_side = -1

    if legal_target:
        if start_row + pawn_side == target_row or first_move and start_row + 2 * pawn_side == target_row:
            piece_move(start_column, target_column, start_row, target_row, piece_type)
    return


def castle(long: bool):
    global MoveCount, Side
    i = 0  # row
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
        print(1012)
    if not long:
        king_j = 6
        rook_i = 7
        rook_j = 5
        extra_clear = True
        print(1018)

    king_legal = GameArray[i][4].piece == king and GameArray[i][4].move == 0
    rook_legal = GameArray[i][rook_i].piece == rook and GameArray[i][rook_i].move == 0
    checks = not under_attack(king.isupper(), i, 4) and not under_attack(king.isupper(), i, king_j) and not under_attack(king.isupper(), i, rook_j)
    clear = GameArray[i][rook_j].piece == " " and GameArray[i][king_j].piece == " " and extra_clear
    print(1350, king_legal, rook_legal, checks, clear, GameArray[i][4].move == 0, GameArray[i][4].piece == king)
    if king_legal and rook_legal and checks and clear:
        piece_move(4, king_j, i, i, king)
        piece_move(rook_i, rook_j, i, i, rook)
        print(1033)


if __name__ == "__main__":
    game_init()
    save_game()
