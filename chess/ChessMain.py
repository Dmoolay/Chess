import pygame as p
from chess import ChessEngine

WIDTH = HEIGHT = 512
DIM = 8
SQ_SIZE = HEIGHT // DIM
MAX_FPS = 15
IMAGES = {}
colors = [p.Color(192, 192, 192), p.Color(204, 102, 0)]


def load_images():
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR"]
    for aa in pieces:
        IMAGES[aa] = p.transform.scale(p.image.load("images/" + aa + ".png"), (SQ_SIZE - 10, SQ_SIZE - 10))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH + 2 * SQ_SIZE, HEIGHT + 2 * SQ_SIZE))
    clock = p.time.Clock()
    screen.fill(p.Color(204, 255, 209))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag for when a move is made, and we need to compute all possible moves again
    animate = False  # flag variable for when we should animate a move
    load_images()
    sqSelected = ()  # tuple(row,col), keep tracking on the last click of the user
    playerClick = []  # keep track on the player clicks, two tuples [(6,4),(4,4)]
    gameOver = False
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler:
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x,y) location of the mouse click
                    col = (location[0] // SQ_SIZE)
                    row = (location[1] // SQ_SIZE)
                    if sqSelected == (row,
                                      col) or row == 0 or row == 9 or col == 0 or col == 9:  # player click on the same square, deselect the click
                        sqSelected = ()
                        playerClick = []
                    else:
                        sqSelected = (row, col)
                        playerClick.append(sqSelected)  # append for both 1st and 2nd click
                    if len(playerClick) == 2:  # after the 2nd click
                        move = ChessEngine.Move(playerClick[0], playerClick[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset player click for the next player turn
                                playerClick = []
                        if not moveMade:  # save the last click if the player want to change piece to move
                            playerClick = [sqSelected]
            # keyboard handler:
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    if gameOver:
                        gameOver = False
                if e.key == p.K_r:  # reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClick = []
                    moveMade = False  # flag for when a move is made, and we need to compute all possible moves again
                    animate = False  # flag variable for when we should animate a move
                    if gameOver:
                        gameOver = False


        if moveMade:
            if animate:
                AnimateMove(gs.LogMove[-1], screen, gs.board, clock, gs)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        DrawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black win by checkmate!')
            else:
                drawText(screen, 'White win by checkmate!')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate!')

        clock.tick(MAX_FPS)
        p.display.flip()


'''
Highlight the square selected and moves for the piece selected
'''


def highlightSquare(screen, gs, validMoves, sqSelected):
    # highlight the end square of the last move
    if len(gs.LogMove) > 0:
        move1 = gs.LogMove[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)  # transparency value --> 0 transparent; 255 opaque
        s.fill(p.Color('Green'))
        screen.blit(s, (move1.endCol * SQ_SIZE+SQ_SIZE, move1.endRow * SQ_SIZE+SQ_SIZE))

    # highlight the selected square and his moves
    if sqSelected != ():
        r, c = sqSelected
        # if inside if statement, first check if it W/B turn, then check if sqSelected is a piece that can be moved
        if gs.board[r - 1][c - 1][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value --> 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r - 1 and move.startCol == c - 1:
                    screen.blit(s, (SQ_SIZE * move.endCol + SQ_SIZE, SQ_SIZE * move.endRow + SQ_SIZE))


def DrawGameState(screen, gs, validMoves, sqSelected):  # responsible for all the graphic in the current state of the game
    DrawBoard(screen, gs)
    highlightSquare(screen, gs, validMoves, sqSelected)
    DrawPieces(screen, gs.board)


def DrawBoard(screen, gs):  # Draw the board of the game
    font = p.font.Font(None, 30)
    colors = [p.Color(192, 192, 192), p.Color(204, 102, 0)]
    screen.fill(p.Color(204, 255, 209))
    for i in range(DIM):
        text_surface1 = font.render(str(DIM - i), True, (0, 0, 0))
        text_surface2 = font.render(chr(i + 65), True, (0, 0, 0))
        screen.blit(text_surface1, (HEIGHT // SQ_SIZE + 30, i * SQ_SIZE + 1.5 * SQ_SIZE - 10))
        screen.blit(text_surface2, (i * SQ_SIZE + 1.5 * SQ_SIZE - 10, HEIGHT // SQ_SIZE + 30))
        for j in range(DIM):
            color = colors[((i + j) % 2)]
            p.draw.rect(screen, color, p.Rect(j * SQ_SIZE + SQ_SIZE, i * SQ_SIZE + SQ_SIZE, SQ_SIZE, SQ_SIZE))

    if gs.whiteToMove:
        text_surface1 = font.render("White turn", True, (0, 0, 0))
        screen.blit(text_surface1, (HEIGHT // SQ_SIZE + 30, 8 * SQ_SIZE + 1.5 * SQ_SIZE - 10))
    else:
        text_surface1 = font.render("Black turn", True, (0, 0, 0))
        screen.blit(text_surface1, (HEIGHT // SQ_SIZE + 30, 8 * SQ_SIZE + 1.5 * SQ_SIZE - 10))


def DrawPieces(screen, board):  # Draw the pieces on the board for the current game
    for i in range(DIM):
        for j in range(DIM):
            piece = board[i][j]
            if piece != "--":
                screen.blit(IMAGES[piece],
                            p.Rect(j * SQ_SIZE + SQ_SIZE + 5, i * SQ_SIZE + SQ_SIZE + 5, SQ_SIZE, SQ_SIZE))


'''
Animating the move
'''


def AnimateMove(move, screen, board, clock, gs):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSqure = 10  # frames to move one squre
    frameCount = (abs(dR) + abs(dC)) * framePerSqure
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        DrawBoard(screen, gs)
        DrawPieces(screen, board)
        # erase the piece moved from his ending squre
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE + SQ_SIZE, move.endRow * SQ_SIZE + SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            endSquare = p.Rect(move.endCol * SQ_SIZE + SQ_SIZE + 5, move.endRow * SQ_SIZE + SQ_SIZE + 5, SQ_SIZE,
                               SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved],
                    p.Rect(c * SQ_SIZE + SQ_SIZE + 5, r * SQ_SIZE + SQ_SIZE + 5, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2+SQ_SIZE, HEIGHT/2 - textObject.get_height()/2+SQ_SIZE)
    screen.blit(textObject, textLocation)
    # add shadow affect
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
