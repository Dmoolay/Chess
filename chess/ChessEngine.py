class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.LogMove = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # coordinates for the square where en passant is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        # hard copy of currentCastlingRights:
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.LogMove.append(move)
        self.whiteToMove = not self.whiteToMove
        # update the King location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion:
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # En Passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing the pawn that "behind"

        # update the 'enpassantPossible' tuple variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:  # only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:  # all we need to do is moving the Rook
            if move.endCol - move.startCol == 2:  # King side castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # move the Rook
                self.board[move.endRow][move.endCol + 1] = '--'  # erase old Rook
            else:  # Queen side castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # move the Rook
                self.board[move.endRow][move.endCol - 2] = '--'  # erase old Rook

        # update castling rights - whenever it is a Rook or a King move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    # indo the last move made:
    def undoMove(self):
        if len(self.LogMove) != 0:
            move = self.LogMove.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update the King location
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # leave lending square "empty"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo 2 square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undo the castling right
            self.castleRightsLog.pop()  # remove the castling of the last move we are undoing
            newRights = self.castleRightsLog[-1]  # update the castling right to the last in list.
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # King side castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]  # move the Rook
                    self.board[move.endRow][move.endCol - 1] = '--'  # erase old Rook
                else:  # Queen side castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]  # move the Rook
                    self.board[move.endRow][move.endCol + 1] = '--'  # erase old Rook

    '''
    Update the castle rights given the move
    '''

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False

    '''
    All moves considering checks
    '''

    def getValidMoves(self):
        # for log in self.castleRightsLog:
        #     print(log.wks, log.bks, log.wqs, log.bqs, end=", ")
        # print()
        # print(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs, end=", ")
        # print()
        # print(self.whiteKingLocation[0],self.whiteKingLocation[1],self.blackKingLocation[0],self.blackKingLocation[1], end=", ")
        # print()
        tempEnpassantPossible = self.enpassantPossible
        # copy the current castling rights
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        # (1) Generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # (2) for each move, make the move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # (3) Generate all opponent's moves
            # (4) for each of your opponent's moves, see if they attack our king
            self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
            if self.inCheck():
                moves.remove(moves[i])  # (5) if they still attack our king, it's not a valid move
            self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves

    '''
    Determine if the current player is in check
    '''

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
        Determine if the enemy can attack the square (r,c)
    '''

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn again
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

    '''
    All moves possible for the player
    '''

    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  # call the right function for each piece.
        return moves

    '''
    get all possible moves for every piece
    '''

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r + 1, c + 1), (r, c + 1), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r + 1, c + 1), (r - 1, c + 1), self.board))
            if c - 1 >= 0:  # captured to the left
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r + 1, c + 1), (r, c), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r + 1, c + 1), (r, c), self.board, isEnpassantMove=True))

            if c + 1 <= 7:  # captured to the right
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r + 1, c + 1), (r, c + 2), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r + 1, c + 1), (r, c + 2), self.board, isEnpassantMove=True))

        else:
            if self.board[r + 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r + 1, c + 1), (r + 2, c + 1), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r + 1, c + 1), (r + 3, c + 1), self.board))
            if c - 1 >= 0:  # captured to the left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r + 1, c + 1), (r + 2, c), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r + 1, c + 1), (r + 2, c), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # captured to the right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r + 1, c + 1), (r + 2, c + 2), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r + 1, c + 1), (r + 2, c + 2), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        direction = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up,left,down,right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):  # can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # still on board
                    CurrentCell = self.board[endRow][endCol]
                    if CurrentCell == "--":  # empty cell valid
                        moves.append(Move((r + 1, c + 1), (endRow + 1, endCol + 1), self.board))
                    elif CurrentCell[0] == enemyColor:  # can capture enemy piece
                        moves.append(Move((r + 1, c + 1), (endRow + 1, endCol + 1), self.board))
                        break
                    else:  # piece on my team
                        break
                else:  # end of board
                    break

    def getKnightMoves(self, r, c, moves):
        possibleMoves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (1, -2), (1, 2), (-1, -2), (-1, 2))
        allyColor = "w" if self.whiteToMove else "b"
        for m in possibleMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # still on board
                CurrentCell = self.board[endRow][endCol]
                if CurrentCell[0] != allyColor:  # the cell is with enemy piece or empty
                    moves.append(Move((r + 1, c + 1), (endRow + 1, endCol + 1), self.board))

    def getBishopMoves(self, r, c, moves):
        direction = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonals directions
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):  # can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # still on board
                    CurrentCell = self.board[endRow][endCol]
                    if CurrentCell == "--":  # empty cell valid
                        moves.append(Move((r + 1, c + 1), (endRow + 1, endCol + 1), self.board))
                    elif CurrentCell[0] == enemyColor:  # can capture enemy piece
                        moves.append(Move((r + 1, c + 1), (endRow + 1, endCol + 1), self.board))
                        break
                    else:  # piece on my team
                        break
                else:  # end of board
                    break

    def getQueenMoves(self, r, c, moves):  # can move all directions, i.e. like Rook and Bishop combine
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        possibleMoves = ((-1, -1), (-1, 1), (1, -1), (1, 1), (1, 0), (0, 1), (-1, 0), (0, -1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + possibleMoves[i][0]
            endCol = c + possibleMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # still on board
                CurrentCell = self.board[endRow][endCol]
                if CurrentCell[0] != allyColor:  # the cell is with enemy piece or empty
                    moves.append(Move((r + 1, c + 1), (endRow + 1, endCol + 1), self.board))

    '''
    Generate all valid castling moves for the king at (r, c) and add them to the list of moves
    '''

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # we cant cstle while we are in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if (not self.squareUnderAttack(r, c + 1)) and (not self.squareUnderAttack(r, c + 2)):
                moves.append(Move((r+1, c+1), (r+1, c + 3), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if (not self.squareUnderAttack(r, c - 1)) and (not self.squareUnderAttack(r, c - 2)):
                moves.append(Move((r+1, c+1), (r+1, c - 1), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # map key to value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0] - 1
        self.startCol = startSq[1] - 1
        self.endRow = endSq[0] - 1
        self.endCol = endSq[1] - 1
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn Promotion
        self.isPawnPromotion = (
                (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7))

        # En Passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        # castle move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    overriding the equal method -  for making move not only with the mouse
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
