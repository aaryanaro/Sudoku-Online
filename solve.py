from more_itertools import chunked

possible_values = [
    [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], [], 
    [], [], [], [], [], [], [], [], []
]

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


def getImpactedRows(index):
    """Finds impacted cells in row
    :param index: index of cell to find cells impacted by change in original cell
    :return: indexes in row of original cell
    """
    rows = list(range(index - index % 9, index - index % 9 + 9))
    return rows


def getImpactedColumns(index):
    """Finds impacted cells in column
    :param index: index of cell to find cells impacted by change in original cell
    :return: indexes in column of original cell
    """
    columns = list(range(index % 9, 81, 9))
    return columns


def getImpactedBoxes(index):
    """Finds impacted cells in box
    :param index: index of cell to find cells impacted by change in original cell
    :return: indexes in box of original cell
    """

    # Finds impacted cells in box using BOXES dictionary
    boxes = None
    for box in range(1, 10):
        if index in BOXES[box]:
            boxes = BOXES[box]
            break

    return boxes


def getImpactedCells(index):
    """Finds all cells that are impacted by index
    :param index: index of cell to find cells impacted by change in original cell
    :return: unique set of impacted cells, row cells impacted, column cells impacted, and box cells impacted
    """
    return list(set(getImpactedRows(index) + getImpactedColumns(index) + getImpactedBoxes(index)))


def solutionWork(board):
    """Checks if given board is solvable or not
    :param board: sudoku board to check
    :return: True if sudoku board is a solvable board, False if board is unsolvable
    """

    def countsValid(val_set):
        """Checks whether number of occurrences of a single value within a row, column, or box exceeds 1
        :param val_set: 9 integer array to validate
        :return: True if number of occurrences of all values in array doesn't exceed 1, False if contrary
        """
        arr = [val_set.count(x) for x in
               range(1, 10)]  # Getting number of occurrences of values 1 through 9 in given set
        if list(set(arr)) == [1] or list(set(arr)) == [0] or list(set(arr)) == [0, 1]:
            return True
        return False
    
    
    # Checking if rows are valid
    for start_index in range(0, 80, 9):  # Getting first index of every row
        row_indexes = getImpactedRows(start_index)  # Getting indexes that make up row

        row_values = []
        for cell in row_indexes:
            row_values.append(board[cell])

        if not countsValid(row_values):
            return False

    # Checking if columns are valid
    for start_index in range(9):  # Getting first index of every column
        column_indexes = getImpactedColumns(start_index)  # Getting indexes that make up column

        column_values = []
        for cell in column_indexes:
            column_values.append(board[cell])

        if not countsValid(column_values):
            return False

    # Checking if boxes are valid
    for box in range(1, 10):  # Getting box numbers for future reference
        box_indexes = BOXES[box]  # Getting indexes within box from BOXES hard-coded dictionary

        box_values = []
        for cell in box_indexes:
            box_values.append(board[cell])

        if not countsValid(box_values):
            return False

    # Returning True if board passes all tests
    return True


def solveBoard(board):
    """Solves sudoku board
    :param board: sudoku board
    :return: solved board
    """
    
    global possible_values
    
    def setupPossibleValues():
        """Enters all given values into possible_values array"""
        for index in range(len(board)):
            if board[index] != 0:  # if board at index is not empty, meaning it is already filled in or given
                possible_values[index].append(board[index])
    
    def getPossibleValues(index):
        """Finds all possible values a cell can obtain
        :param index: index of cell to find values of
        adds to possible_values array with findings
        """
        if len(possible_values[index]) == 1:
            return

        # call getImpactedCells() for index
        cells = getImpactedCells(index)

        # get values of all indexes that were returned excluding the zeros
        values = sorted(list(set(board[cell] for cell in cells)))
        if 0 in values:
            values.remove(0)

        # take them away from the list [1, 2, 3, 4, 5, 6, 7, 8, 9]
        possible = list(range(1, 10))
        for element in values:
            if element in values:
                possible.remove(element)

        # add possible values to possible_values array
        possible_values[index].clear()
        possible_values[index].extend(possible)
    
    def findHiddenSingles():
        """Finds all hidden singles and fills them in"""
        # Check every cell in every row for value that only cell can take up
        for start_index in range(0, 81, 9):
            row_indexes = getImpactedRows(start_index)

            row_values = []
            for cell in row_indexes:
                if len(possible_values[cell]) != 1:
                    row_values += possible_values[cell]

            hidden_singles = []
            for value in range(1, 10):
                if row_values.count(value) == 1:
                    hidden_singles.append(value)

            for cell in row_indexes:
                for value in hidden_singles:
                    if value in possible_values[cell]:
                        possible_values[cell] = [value]
                        break

        updateBoards()

        # Check every cell in every column for value that only cell can take up
        for start_index in range(9):
            column_indexes = getImpactedColumns(start_index)

            column_values = []
            for cell in column_indexes:
                if len(possible_values[cell]) != 1:
                    column_values += possible_values[cell]

            hidden_singles = []
            for value in range(1, 10):
                if column_values.count(value) == 1:
                    hidden_singles.append(value)

            for cell in column_indexes:
                for value in hidden_singles:
                    if value in possible_values[cell]:
                        possible_values[cell] = [value]
                        break

        updateBoards()

        # Check every cell in every box for value that only cell can take up
        for box in range(1, 10):
            box_indexes = BOXES[box]

            box_values = []
            for cell in box_indexes:
                if len(possible_values[cell]) != 1:
                    box_values += possible_values[cell]

            hidden_singles = []
            for value in range(1, 10):
                if box_values.count(value) == 1:
                    hidden_singles.append(value)

            for cell in box_indexes:
                for value in hidden_singles:
                    if value in possible_values[cell]:
                        possible_values[cell] = [value]
                        break

        updateBoards()
    
    def updateBoards():
        """Updates main board with singular values in possible_values array, deletes values from impacted cells that have been obtained already"""
        for cell in range(len(possible_values)):
            if len(possible_values[cell]) == 1:  # if only one value has been selected to go in cell
                val = possible_values[cell][0]  # selected value in cell

                # Update board with value in position it has to be in
                board[cell] = val

                # Update possible_values array
                cells = getImpactedCells(cell)  # finds all impacted cells by change in value of original cell
                for index in cells:
                    if val in possible_values[index] and len(
                            possible_values[index]) != 1:  # if the obtained value is in another cell
                        possible_values[index].remove(val)

    def recursiveSolve():
        """Solves board recursively after all other approaches can't progress
        :return: True if board was solved, False if board cannot be solved
        """
        def guessValid(guess, index):
            temp = board[:]
            temp[index] = guess

            return solutionWork(temp)

        def findBlank():
            for index in range(81):
                if board[index] == 0:
                    return index

            return False

        index = findBlank()
        if 0 not in board:
            return True

        for value in range(1, 10):
            if guessValid(value, index):
                board[index] = value
                if recursiveSolve():
                    return True

            board[index] = 0

        return False
    
    # Solving Board

    setupPossibleValues()
    for cell in range(81):
        getPossibleValues(cell)

    while True:
        temp = possible_values[:]
        updateBoards()
        findHiddenSingles()
        if temp == possible_values:
            break

    if 0 in board:  # board is not fully solved
        recursiveSolve()
    
    # Resets possible_values
    possible_values = [
        [], [], [], [], [], [], [], [], [], 
        [], [], [], [], [], [], [], [], [], 
        [], [], [], [], [], [], [], [], [], 
        [], [], [], [], [], [], [], [], [], 
        [], [], [], [], [], [], [], [], [], 
        [], [], [], [], [], [], [], [], [], 
        [], [], [], [], [], [], [], [], [], 
        [], [], [], [], [], [], [], [], [], 
        [], [], [], [], [], [], [], [], []
    ]
    
    # Returns solved board
    
    return list(chunked(board, 9))