# Importing Modules

from flask import Flask, redirect, render_template, session, request, flash
from flask_session import Session
from tempfile import mkdtemp
from requests import get
from cs50 import SQL
from random import choice
from string import ascii_uppercase, digits

from solve import solutionWork, solveBoard
from tools import convertBoard, blankBoard, solutionCorrect, _2D_to_1D


# Configure application

app = Flask(__name__)


# Ensure templates are auto-reloaded

app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database

db = SQL("sqlite:///sudoku.db")


# Defining functions for app routes

@app.route('/')
def index():
    return redirect('/solve')


@app.route('/solve', methods=['GET', 'POST'])
def solve():
    if request.method == 'POST':
        if request.form.get('submit') == 'unsolve':
            if session.get('upload'):
                board = convertBoard(int(db.execute('SELECT id FROM boards WHERE name=:code', code=session.get('code'))[0]['id']), db)[0]
                
                # Change Code Session
                session['code'] = None
                session['upload'] = False
            
            else:
                board = convertBoard(session.get('board_id'), db)[0]
            
            return render_template('solve-back.html', board=board)
            
        if request.form.get('submit') == 'reset':
            return render_template('solve.html')
            
        if request.form.get('submit') == 'clear':
            return render_template('solve.html')
        
        else:
            sudoku_board = blankBoard()
                    
            filled_cells = 0
            count = 0
            
            for i in range(9):
                for j in range(9):
                    try:
                        num = int(request.form.get(str(count)))
                        if not 1 <= num <= 9:
                            flash('All input values must be integers from 1 through 9')
                            return redirect('/solve')
                        sudoku_board[i][j] = num
                        filled_cells += 1
                    except:
                        if request.form.get(str(count)) == '':
                            pass
                        else:
                            flash('All input values must be integers from 1 through 9')
                            return redirect('/solve')
                    count += 1
            

            # Check valid
                
            if not solutionWork(_2D_to_1D(sudoku_board)):
                flash('Board Invalid')
                return redirect('/solve')
                
            
            # Make Board
            
            name = None
            
            while True:
                name = ''.join(choice(ascii_uppercase + digits) for _ in range(5))
                if len(db.execute('SELECT * FROM boards WHERE name=:name', name=name)) == 0:
                    break
                
            db.execute('INSERT INTO boards (name, difficulty) VALUES (:name, 0)', name=name)
            
            
            # Store Board
            
            board_id = int(db.execute('SELECT id FROM boards WHERE name=:name', name=name)[0]['id'])
            
            cell_num = 0
            
            for i in range(9):
                for j in range(9):
                    if sudoku_board[i][j] != 0:
                        db.execute('INSERT INTO cells VALUES (:board_id, :cell_num, :value)', board_id=board_id, cell_num=cell_num, value=sudoku_board[i][j])
                    cell_num += 1
            
            
            # Store board_id
            session['board_id'] = int(board_id)
            
            # Get board
            board, givens = convertBoard(session.get('board_id'), db)
            
            # Solve board
            board = solveBoard(_2D_to_1D(board))

            # Show board
            return render_template('solved.html', board=board, givens=givens, code=name)

    else:
        if session.get('code') != None:
            # Get board
            board, givens = convertBoard(int(db.execute('SELECT id FROM boards WHERE name=:name', name=session.get('code'))[0]['id']), db)

            # Code
            name = session.get('code')
            
            # Solve board
            board = solveBoard(_2D_to_1D(board))
            
            # Show board
            return render_template('solved.html', board=board, givens=givens, code=name)
        
        else:
            flash('Tip: To advance to the next cell, click the "tab" button on your key board. To go back one cell, click "shift + tab"')
            return render_template('solve.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if request.form.get('code') == '':
            flash('Code Not Entered')
            return redirect('/upload')
        
        if len(db.execute('SELECT * FROM boards WHERE name=:name', name=request.form.get('code'))) != 1 and len(db.execute('SELECT * FROM play_boards WHERE name=:name', name=request.form.get('code'))) != 1:
            flash('Code Invalid')
            return redirect('/upload')
       
        session['code'] = request.form.get('code')
        
        session['upload'] = True
        
        if request.form.get('type') == 'play':
            if len(db.execute('SELECT * FROM play_boards WHERE name=:name', name=request.form.get('code'))) != 1:
                flash('Code Invalid. You may have selected "For Play" instead of "For Solve".')
                return redirect('/upload')
            return redirect('/play')
        
        elif request.form.get('type') == 'solve':
            if len(db.execute('SELECT * FROM boards WHERE name=:name', name=request.form.get('code'))) != 1:
                flash('Code Invalid. You may have selected "For Solve" instead of "For Play".')
                return redirect('/upload')
            return redirect('/solve')
        
    else:
        return render_template('upload.html')
        

@app.route('/play', methods=['GET', 'POST'])
def play():
    if session.get('code'):
        code = session.get('code')
        try:
            play_board_id = db.execute('SELECT play_board_id FROM play_boards WHERE name=:code', code=code)[0]['play_board_id']
            level = int(db.execute('SELECT difficulty FROM boards WHERE id=:play_board_id', play_board_id=play_board_id)[0]['difficulty'])
        except:
            return redirect('/play/easy')
        
        if level == 1:
            return redirect('/play/easy')
        elif level == 2:
            return redirect('/play/medium')
        elif level == 3:
            return redirect('/play/hard')
            
    else:
        return redirect('/play/easy')  # Defualts to easy board
    

@app.route('/play/easy', methods=['GET', 'POST'])
def easy():
    if request.method == 'POST':
        # Get Board
        converted = convertBoard(session.get('play_board_id'), db)

        if request.form.get('submit') == 'clear':
            return render_template('play.html', board=converted[0], givens=converted[1], level='Easy', footer_message='Enter numbers')
        
        sudoku_board = converted[0]
        
        valid = True
        message = None
        
        filled_cells = 0
        count = 0
        
        for i in range(9):
            for j in range(9):
                try:
                    num = int(request.form.get(str(count)))
                    if not 1 <= num <= 9:
                        valid = False
                    sudoku_board[i][j] = num
                    filled_cells += 1
                except:
                    if request.form.get(str(count)) == '' or request.form.get(str(count)) is None:
                        pass
                    else:
                        valid = False
                count += 1
        
        
        # Make Board
        
        name = None
        
        while True:
            name = ''.join(choice(ascii_uppercase + digits) for _ in range(5))
            if len(db.execute('SELECT * FROM play_boards WHERE name=:name', name=name)) == 0:
                break
            
        db.execute('INSERT INTO play_boards (name, play_board_id) VALUES (:name, :play_board_id)', name=name, play_board_id=session.get('play_board_id'))
        
        
        # Store Board
        
        board_id = int(db.execute('SELECT id FROM play_boards WHERE name=:name', name=name)[0]['id'])
        
        cell_num = 0
        
        for i in range(9):
            for j in range(9):
                if sudoku_board[i][j] != 0:
                    db.execute('INSERT INTO play_cells VALUES (:board_id, :cell_num, :value)', board_id=board_id, cell_num=cell_num, value=sudoku_board[i][j])
                cell_num += 1
        
        
        # Checking, Saving, or Solving Board
        
        if request.form.get('submit') == 'save':
            flash('Board Saved! Make sure to save your progress by re-clicking the "Save Game" button before leaving the site. Copy the board code to use it later.')
            return render_template('play.html', board=sudoku_board, givens=converted[1], level='Easy', footer_message=f'Board Code: {name}')
        
        elif request.form.get('submit') == 'solution':
            session['code'] = db.execute('SELECT name FROM boards WHERE id=:id', id=int(session.get('play_board_id')))[0]['name']
            return redirect('/solve')
            
        elif request.form.get('submit') == 'check':
            if not valid:
                flash('All input values must be integers from 1 through 9')
                return render_template('play.html', board=sudoku_board, givens=converted[1], level='Easy', footer_message='Enter numbers')
            
            else:
                # Check if board was solved correctly
                
                # Check if board contains zero; meaning that board isn't completely done
                
                done = True
                
                for row in range(9):
                    if 0 in sudoku_board[row]:
                        done = False
                        break
                    
                
                # Check if solution works at current state of board if not done
                
                if not done:
                    work = solutionWork(_2D_to_1D(sudoku_board))
                    if work:
                        flash('Looks Correct so Far! Keep Going.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Easy', footer_message='Enter numbers')
                    else:
                        flash('Board is not solved correctly')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Easy', footer_message='Enter numbers')
                        
                # Check if solution is correct if board is done
                
                else:
                    if solutionCorrect(sudoku_board):
                        flash('Outstanding job, you solved the puzzle! Click on the "New Board" button for a new board.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Easy', footer_message='Solved!')
                    else:
                        flash('Board is not solved correctly. Look for repetitions of values in rows, columns, and boxes.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Easy', footer_message='Enter numbers')
                
            
    else:
        if session.get('code'):
            # Getting code and id of board that user is playing upon
            
            code = session.get('code')
            play_board_id = db.execute('SELECT play_board_id FROM play_boards WHERE name=:code', code=code)[0]['play_board_id']
            
            
            # Storing play_board_id
            
            session['play_board_id'] = play_board_id
            
            
            # Getting data required for rendering play.html
            
            givens = convertBoard(play_board_id, db)[1]
            play_board = convertBoard(int(db.execute('SELECT id FROM play_boards WHERE name=:code', code=code)[0]['id']), db, solve=False)[0]
            
            
            # Reseting session
            
            session['code'] = None
            
            return render_template('play.html', board=play_board, level='Easy', footer_message='Enter numbers', givens=givens)
            
        else:
            # Getting Easy Board to play with
            
            board_id = int(choice(db.execute('SELECT id FROM boards WHERE difficulty=1'))['id'])
            
            board = convertBoard(board_id, db)
            
            
            # Storing Board ID
            
            session['play_board_id'] = board_id
            
            flash('Tip: To advance to the next cell, click the "tab" button on your key board. To go back one cell, click "shift + tab"')
            
            return render_template('play.html', board=board[0], level='Easy', footer_message='Enter numbers', givens=board[1])
            
            
@app.route('/play/medium', methods=['GET', 'POST'])
def medium():
    if request.method == 'POST':
        # Get Board
        converted = convertBoard(session.get('play_board_id'), db)

        if request.form.get('submit') == 'clear':
            return render_template('play.html', board=converted[0], givens=converted[1], level='Medium', footer_message='Enter numbers')
        
        sudoku_board = converted[0]
        
        valid = True
        message = None
        
        filled_cells = 0
        count = 0
        
        for i in range(9):
            for j in range(9):
                try:
                    num = int(request.form.get(str(count)))
                    if not 1 <= num <= 9:
                        valid = False
                    sudoku_board[i][j] = num
                    filled_cells += 1
                except:
                    if request.form.get(str(count)) == '' or request.form.get(str(count)) is None:
                        pass
                    else:
                        valid = False
                count += 1
        
        
        # Make Board
        
        name = None
        
        while True:
            name = ''.join(choice(ascii_uppercase + digits) for _ in range(5))
            if len(db.execute('SELECT * FROM play_boards WHERE name=:name', name=name)) == 0:
                break
            
        db.execute('INSERT INTO play_boards (name, play_board_id) VALUES (:name, :play_board_id)', name=name, play_board_id=session.get('play_board_id'))
        
        
        # Store Board
        
        board_id = int(db.execute('SELECT id FROM play_boards WHERE name=:name', name=name)[0]['id'])
        
        cell_num = 0
        
        for i in range(9):
            for j in range(9):
                if sudoku_board[i][j] != 0:
                    db.execute('INSERT INTO play_cells VALUES (:board_id, :cell_num, :value)', board_id=board_id, cell_num=cell_num, value=sudoku_board[i][j])
                cell_num += 1
        
        
        # Checking, Saving, or Solving Board
        
        if request.form.get('submit') == 'save':
            flash('Board Saved! Make sure to save your progress by re-clicking the "Save Game" button before leaving the site. Copy the board code to use it later.')
            return render_template('play.html', board=sudoku_board, givens=converted[1], level='Medium', footer_message=f'Board Code: {name}')
        
        elif request.form.get('submit') == 'solution':
            session['code'] = db.execute('SELECT name FROM boards WHERE id=:id', id=int(session.get('play_board_id')))[0]['name']
            return redirect('/solve')
            
        elif request.form.get('submit') == 'check':
            if not valid:
                flash('All input values must be integers from 1 through 9')
                return render_template('play.html', board=sudoku_board, givens=converted[1], level='Medium', footer_message='Enter numbers')
            
            else:
                # Check if board was solved correctly
                
                # Check if board contains zero; meaning that board isn't completely done
                
                done = True
                
                for row in range(9):
                    if 0 in sudoku_board[row]:
                        done = False
                        break
                    
                
                # Check if solution works at current state of board if not done
                
                if not done:
                    work = solutionWork(_2D_to_1D(sudoku_board))
                    if work:
                        flash('Looks Correct so Far! Keep Going.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Medium', footer_message='Enter numbers')
                    else:
                        flash('Board is not solved correctly')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Medium', footer_message='Enter numbers')
                        
                # Check if solution is correct if board is done
                
                else:
                    if solutionCorrect(sudoku_board):
                        flash('Outstanding job, you solved the puzzle! Click on the "New Board" button for a new board.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Medium', footer_message='Solved!')
                    else:
                        flash('Board is not solved correctly. Look for repetitions of values in rows, columns, and boxes.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Medium', footer_message='Enter numbers')
                
            
    else:
        if session.get('code'):
            # Getting code and id of board that user is playing upon
            
            code = session.get('code')
            play_board_id = db.execute('SELECT play_board_id FROM play_boards WHERE name=:code', code=code)[0]['play_board_id']
            
            
            # Storing play_board_id
            
            session['play_board_id'] = play_board_id
            
            
            # Getting data required for rendering play.html
            
            givens = convertBoard(play_board_id, db)[1]
            play_board = convertBoard(int(db.execute('SELECT id FROM play_boards WHERE name=:code', code=code)[0]['id']), db, solve=False)[0]
            
            
            # Reseting session
            
            session['code'] = None
            
            return render_template('play.html', board=play_board, level='Medium', footer_message='Enter numbers', givens=givens)
            
        else:
            # Getting Easy Board to play with
            
            board_id = int(choice(db.execute('SELECT id FROM boards WHERE difficulty=2'))['id'])
            
            board = convertBoard(board_id, db)
            
            
            # Storing Board ID
            
            session['play_board_id'] = board_id
            
            flash('Tip: To advance to the next cell, click the "tab" button on your key board. To go back one cell, click "shift + tab"')
            
            return render_template('play.html', board=board[0], level='Medium', footer_message='Enter numbers', givens=board[1])
            
            
@app.route('/play/hard', methods=['GET', 'POST'])
def hard():
    if request.method == 'POST':
        # Get Board
        converted = convertBoard(session.get('play_board_id'), db)

        if request.form.get('submit') == 'clear':
            return render_template('play.html', board=converted[0], givens=converted[1], level='Hard', footer_message='Enter numbers')
        
        sudoku_board = converted[0]
        
        valid = True
        message = None
        
        filled_cells = 0
        count = 0
        
        for i in range(9):
            for j in range(9):
                try:
                    num = int(request.form.get(str(count)))
                    if not 1 <= num <= 9:
                        valid = False
                    sudoku_board[i][j] = num
                    filled_cells += 1
                except:
                    if request.form.get(str(count)) == '' or request.form.get(str(count)) is None:
                        pass
                    else:
                        valid = False
                count += 1
        
        
        # Make Board
        
        name = None
        
        while True:
            name = ''.join(choice(ascii_uppercase + digits) for _ in range(5))
            if len(db.execute('SELECT * FROM play_boards WHERE name=:name', name=name)) == 0:
                break
            
        db.execute('INSERT INTO play_boards (name, play_board_id) VALUES (:name, :play_board_id)', name=name, play_board_id=session.get('play_board_id'))
        
        
        # Store Board
        
        board_id = int(db.execute('SELECT id FROM play_boards WHERE name=:name', name=name)[0]['id'])
        
        cell_num = 0
        
        for i in range(9):
            for j in range(9):
                if sudoku_board[i][j] != 0:
                    db.execute('INSERT INTO play_cells VALUES (:board_id, :cell_num, :value)', board_id=board_id, cell_num=cell_num, value=sudoku_board[i][j])
                cell_num += 1
        
        
        # Checking, Saving, or Solving Board
        
        if request.form.get('submit') == 'save':
            flash('Board Saved! Make sure to save your progress by re-clicking the "Save Game" button before leaving the site. Copy the board code to use it later.')
            return render_template('play.html', board=sudoku_board, givens=converted[1], level='Hard', footer_message=f'Board Code: {name}')
        
        elif request.form.get('submit') == 'solution':
            session['code'] = db.execute('SELECT name FROM boards WHERE id=:id', id=int(session.get('play_board_id')))[0]['name']
            return redirect('/solve')
            
        elif request.form.get('submit') == 'check':
            if not valid:
                flash('All input values must be integers from 1 through 9')
                return render_template('play.html', board=sudoku_board, givens=converted[1], level='Hard', footer_message='Enter numbers')
            
            else:
                # Check if board was solved correctly
                
                # Check if board contains zero; meaning that board isn't completely done
                
                done = True
                
                for row in range(9):
                    if 0 in sudoku_board[row]:
                        done = False
                        break
                    
                
                # Check if solution works at current state of board if not done
                
                if not done:
                    work = solutionWork(_2D_to_1D(sudoku_board))
                    if work:
                        flash('Looks Correct so Far! Keep Going.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Hard', footer_message='Enter numbers')
                    else:
                        flash('Board is not solved correctly')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Hard', footer_message='Enter numbers')
                        
                # Check if solution is correct if board is done
                
                else:
                    if solutionCorrect(sudoku_board):
                        flash('Outstanding job, you solved the puzzle! Click on the "New Board" button for a new board.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Hard', footer_message='Solved!')
                    else:
                        flash('Board is not solved correctly. Look for repetitions of values in rows, columns, and boxes.')
                        return render_template('play.html', board=sudoku_board, givens=converted[1], level='Hard', footer_message='Enter numbers')
                
            
    else:
        if session.get('code'):
            # Getting code and id of board that user is playing upon
            
            code = session.get('code')
            play_board_id = db.execute('SELECT play_board_id FROM play_boards WHERE name=:code', code=code)[0]['play_board_id']
            
            
            # Storing play_board_id
            
            session['play_board_id'] = play_board_id
            
            
            # Getting data required for rendering play.html
            
            givens = convertBoard(play_board_id, db)[1]
            play_board = convertBoard(int(db.execute('SELECT id FROM play_boards WHERE name=:code', code=code)[0]['id']), db, solve=False)[0]
            
            
            # Reseting session
            
            session['code'] = None
            
            return render_template('play.html', board=play_board, level='Hard', footer_message='Enter numbers', givens=givens)
            
        else:
            # Getting Easy Board to play with
            
            board_id = int(choice(db.execute('SELECT id FROM boards WHERE difficulty=3'))['id'])
            
            board = convertBoard(board_id, db)
            
            
            # Storing Board ID
            
            session['play_board_id'] = board_id
            
            flash('Tip: To advance to the next cell, click the "tab" button on your key board. To go back one cell, click "shift + tab"')
            
            return render_template('play.html', board=board[0], level='Hard', footer_message='Enter numbers', givens=board[1])