# Sudoku Online

Sudoku Online is a web application that allows you to play sudoku puzzles of varying difficulty and input sudoku boards 

for the application to solve.

## Important URLs
Application URL: <URL HERE>

Video Demo: <URL HERE>

## Usage Instructions
### Solve
At the app route `/solve`, the defualt page, you can input sudoku boards for the application to solve. Once you input the board you want to solve, you can press the "solve"  
button. The application will solve your board and display it to

you. Here, it shows you a "Board Code", which you can save to your clipboard for future usage. It allows you re-upload the

board. I will go over the uploading steps in the "Upload" section. Some other functionalities include the "Reset" buttons,

which reset the Sudoku Board input field. The "Unsolve" button, displayed after the board has been solved, brings you back

to the original "Solve" screen with only your input displayed. This may be useful if you mistakenly press the "Solve" button.

### Play
At the app route `/play`, you are redirected to the defualt `/play/easy` screen, where you can try to solve an easy sudoku

puzzle by yourself. The "Check" button detects whether you have completely solved the board (there are no blank spaces) or if

the board is partially solved. If the board is completely solved, a flashed message alerts you if you have solved the board

succesfully, or if there are some mistakes in your board. If the board is partially solved, a flashed message alerts you if

you are on the right track, meaning there are no detected errors in your board, or if you made a mistake and you are on the 

wrong track. Some additional functionalities include the "Save Game" button, which saves all of your progress and gives you a

code to upload your board so you can resume from where you left off, the "See Answer" button, which redirects you to a solved 

version of the board you are trying to solve, or the "New Board" dropdown button, which allows you to play a new easy, medium, 

or hard board (at routes `/play/easy`, `/play/mediun`, `/play/hard`, respectively).

### Upload
At the app route `/upload`, you are able to upload the save code given to you at either the "Solve" screen after you solved 

a board, or at the "Play" screen after you clicked on the "Save Game" button. After you write the code in the "Board Code" box,

you chose from the dropdown menu whether the board is to Play with or to Solve. After you press the "Load Board" button, you 

are redirected to `/solve` or `/play` app routes and your progress is restored. 

## Technologies Used
 - Programming Languages: Python, JavaScript
 - Framework: Flask
 - Frontend Development: HTML5, CSS3
 - Database: SQLite3

## Solving Algorithm Explanation
Solves Sudoku Board through usage of Hidden Singles and Naked Singles logical techniques, and later resorts to Brute Force once coded

logical techniques have no effect, recursively solving sudoku board.

### Steps
 1. Checks if board is solvable
 2. Finds all possible values a single cell can obtain based on the given values in the cell's row, column, and box.
 3. Finds all "Hidden Singles" in board. A "Hidden Single" is when a specific cell is the only cell in a row, column,

    or box that can obtain a single value. You can read more about the "Hidden Singles" technique at [Learn Sudoku](https://www.learn-sudoku.com/hidden-singles.html).
 4. If a cell's value has been found, all the cells in the aformentioned cell's row, column, and box cannot obtain the

    found value. Therefore, in all of the other cells' candidate values, the found value will be removed. This allows us

    to slowly whittle down the number of candidate values for each cell.
 5. Steps 2 through 4 are repeated until there was no detected change in the candidate values for all cells. This means

    that the two coded functions meant for reducing the candidate values for the cells do not have an effect anymore.
 6. Once no change has been detected, the loop is broken and using a brute force algorithm that tries every possible

    combination of values, a single solution is found for the sudoku board.
 7. The solving function outputs the board as a 2 dimensional, 9 by 9 integer array.


### Implementation
 - `solve.py`

## Future Implementations
In order to make the solving algorithm more efficent, I might code more sudoku solving techniques as functions in my `solve.py`

file. For instance, the "pointing pairs" technique and the "naked pairs" technique. This will the solving algorithm to resort to the

"brute force" approach less, or at least give the "brute force" function more values, therefore decreasing the overall execution time.

## Credits
 - [Basic Sudoku Solving Techniques at Learn Sudoku](https://www.learn-sudoku.com/basic-techniques.html)
