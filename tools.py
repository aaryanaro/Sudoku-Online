from more_itertools import chunked

BOXES = {
    1: [0, 1, 2, 9, 10, 11, 18, 19, 20],
    2: [3, 4, 5, 12, 13, 14, 21, 22, 23],
    3: [6, 7, 8, 15, 16, 17, 24, 25, 26],
    4: [27, 28, 29, 36, 37, 38, 45, 46, 47],
    5: [30, 31, 32, 39, 40, 41, 48, 49, 50],
    6: [33, 34, 35, 42, 43, 44, 51, 52, 53],
    7: [54, 55, 56, 63, 64, 65, 72, 73, 74],
    8: [57, 58, 59, 66, 67, 68, 75, 76, 77],
    9: [60, 61, 62, 69, 70, 71, 78, 79, 80]
}


def blankBoard():
    return [[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]]
            
            

def convertBoard(id, db, solve=True):
    sudoku_board = blankBoard()

    given_cells = []
    
    count = 0
    
    if solve:
        for i in range(9):
            for j in range(9):
                if len(db.execute('SELECT value FROM cells WHERE cell=:count AND id=:id', count=count, id=id)) != 0:
                    sudoku_board[i][j] = int(db.execute('SELECT value FROM cells WHERE cell=:count AND id=:id', count=count, id=id)[0]['value'])
                    given_cells.append(count)
                count += 1
    else:
        for i in range(9):
            for j in range(9):
                if len(db.execute('SELECT value FROM play_cells WHERE cell=:count AND id=:id', count=count, id=id)) != 0:
                    sudoku_board[i][j] = int(db.execute('SELECT value FROM play_cells WHERE cell=:count AND id=:id', count=count, id=id)[0]['value'])
                    given_cells.append(count)
                count += 1

    return sudoku_board, given_cells
    
    
def solutionCorrect(board):
    """Checking if solution correct
    :param board: sudoku board to check; must be completely filled in
    :returns bool: True if correct, False if inncorect
    """
    
    # Getting box sums
    
    for box in range(1, 10):
        indexes = BOXES[box]
        values = [temp[indexes[index]] for index in range(len(indexes))]
        
        if sum(values) != 45:
            return False
            
    
    temp = list(chunked(board, 9))
    
    # Getting sums of rows
    
    for row in range(9):
        if sum(temp[row]) != 45:
            return False
            
    
    # Getting sums of columns
    
    for row in range(9):
        column_nums = []
        for column in range(9):
            column_nums.append(temp[column][row])
            
        if sum(column_nums) != 45:
            return False
            
    
    # Returning True if past all tests
    
    return True


def _2D_to_1D(board):
    temp = []
    
    for i in range(9):
        for j in range(9):
            temp.append(board[i][j])
            
    return temp