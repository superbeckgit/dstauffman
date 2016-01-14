# -*- coding: utf-8 -*-
r"""
Pentago board game as a Python GUI.

Notes
-----
#.  Written by David C. Stauffer in MATLAB in January 2010, translated to Python in December 2015.
"""

#%% Imports
import doctest
from matplotlib.pyplot import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, Circle, Wedge
import numpy as np
import os
import pickle
import sys
import unittest
try: # pragma: no cover
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QLabel, QMessageBox
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
except ImportError: # pragma: no cover
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtGui import QApplication, QWidget, QToolTip, QPushButton, QLabel, QMessageBox
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from dstauffman     import get_images_dir, get_output_dir, Frozen, modd

#%% Constants
# color definitions
COLOR             = {}
COLOR['board']    = (1., 1., 0.)
COLOR['win']      = (1., 0., 0.)
COLOR['white']    = (1., 1., 1.)
COLOR['black']    = (0., 0., 0.)
COLOR['maj_edge'] = (0., 0., 0.)
COLOR['min_edge'] = (0., 0., 1.)
COLOR['next_wht'] = (0.6, 0.6, 1.0) # (0.8, 0.8, 0.8)
COLOR['next_blk'] = (0.0, 0.0, 0.4) # (0.4, 0.4, 0.4)
COLOR['win_wht']  = (1.0, 0.9, 0.9) # (1.0, 0.9, 0.9)
COLOR['win_blk']  = (0.2, 0.0, 0.0) # (0.6, 0.0, 0.0)

# player enumerations
PLAYER          = {}
PLAYER['white'] = 1
PLAYER['black'] = -1
PLAYER['none']  = 0
PLAYER['draw']  = 2

# sizes of the different pieces and squares
RADIUS           = {}
RADIUS['piece']  = 0.45;
RADIUS['win']    = 0.25;
RADIUS['square'] = 0.5;

# Gameplay options # TODO: implement these
OPTIONS                       = {}
OPTIONS['load_previous_game'] = 'Yes' # from ['Yes','No','Ask']
OPTIONS['name_white']         = 'Player 1'
OPTIONS['name_black']         = 'Player 2'
OPTIONS['plot_winning_moves'] = True

# TODO: this might be temporary
INT_TOKEN = -101

# all possible winning combinations
WIN = np.array([\
    [1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],\
    [1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],\
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],\
    [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0],\
    \
    [0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0],\
    [0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0],\
    [0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0],\
    [0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0],\
    [0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0],\
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],\
    \
    [0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],\
    [0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0],\
    [0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,1,0],\
    [0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,1,0,1,0,0],\
    [0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],\
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0],\
    \
    [0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],\
    [0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0],\
    [0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,1,1,0,0,0],\
    [0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,1],\
    [0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0],\
    [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0],\
    \
    [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0],\
    [0,0,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0],\
    [0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],\
    [0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0],\
    [0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0],\
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0],\
    \
    [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0],\
    [0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],\
    [0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],\
    [0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],\
    [0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0],\
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0],\
], dtype=bool)

# boolean flag for whether to log extra information or not
LOGGING = True

#%% _rotate_board
def _rotate_board(board, quadrant, direction, inplace=True):
    r"""
    Rotates the specified board position.

    Notes
    -----
    #.  Modifies board in-place.
    """
    # determine if 6x6 board or 36xN
    (r, c) = board.shape

    if r == 6 and c == 6:
        assert inplace, '6x6 boards must be modified inplace.'
        # get quad
        if quadrant == 1:
            old_sub = board[0:3, 0:3]
        elif quadrant == 2:
            old_sub = board[0:3, 3:6]
        elif quadrant == 3:
            old_sub = board[3:6, 0:3]
        elif quadrant == 4:
            old_sub = board[3:6, 3:6]
        else:
            raise ValueError('Unexpected value for quadrant.')

        # rotate quad
        if direction == -1:
            new_sub = np.rot90(old_sub)
        elif direction == 1:
            new_sub = np.rot90(old_sub, 3)
        else:
            raise ValueError('Unexpected value for dir')

        # update rotated quad
        if quadrant == 1:
            board[0:3, 0:3] = new_sub
        elif quadrant == 2:
            board[0:3, 3:6] = new_sub
        elif quadrant == 3:
            board[3:6, 0:3] = new_sub
        elif quadrant == 4:
            board[3:6, 3:6] = new_sub

    elif r == 36:
        # get quad
        if quadrant == 1:
            ix_old = np.array([ 0,  1,  2,  6,  7,  8, 12, 13, 14])
        elif quadrant == 2:
            ix_old = np.array([ 3,  4,  5,  9, 10, 11, 15, 16, 17])
        elif quadrant == 3:
            ix_old = np.array([18, 19, 20, 24, 25, 26, 30, 31, 32])
        elif quadrant == 4:
            ix_old = np.array([21, 22, 23, 27, 28, 29, 33, 34, 35])
        else:
            raise ValueError('Unexpected value for quad')
        # rotate quad
        if direction == -1:
            ix_new = ix_old[np.array([2, 5, 8, 1, 4, 7, 0, 3, 6])]
        elif direction == 1:
            ix_new = ix_old[np.array([6, 3, 0, 7, 4, 1, 8, 5, 2])]
        else:
            raise ValueError('Unexpected value for dir')
        # update placements
        if inplace:
            board[ix_old, :]     = board[ix_new, :]
        else:
            new_board            = board.copy()
            new_board[ix_old, :] = board[ix_new, :]
            return new_board
    else:
        raise ValueError('Unexpected size of board.')

#%% Calculated constants
# get all possible rotation to win states
ONE_OFF = np.hstack(( \
    _rotate_board(WIN, 1, -1, inplace=False), \
    _rotate_board(WIN, 2, -1, inplace=False), \
    _rotate_board(WIN, 3, -1, inplace=False), \
    _rotate_board(WIN, 4, -1, inplace=False), \
    _rotate_board(WIN, 1,  1, inplace=False), \
    _rotate_board(WIN, 2,  1, inplace=False), \
    _rotate_board(WIN, 3,  1, inplace=False), \
    _rotate_board(WIN, 4,  1, inplace=False)))

#%% Classes - Moves
class Move(Frozen):
    r"""
    Class that keeps track of each individual move.
    """
    def __init__(self, row, column, quadrant, direction, power=None):
        self.row       = row
        self.column    = column
        self.quadrant  = quadrant
        self.direction = direction
        self.power     = power

    def __eq__(self, other):
        r"""Equality is based on row, column, quadrant and direction, but not on power."""
        return (self.row == other.row and self.column == other.column and self.quadrant == other.quadrant \
            and self.direction == other.direction)

    def __ne__(self, other):
        r"""Inequality is based on row, column, quadrant and direction, but not on power."""
        return not self.__eq__(other)

    def __lt__(self, other):
        r"""Sorts by power, then row, then column, then quadrant, then direction."""
        if self.power is None:
            if other.power is not None:
                return True
        else:
            if other.power is None:
                return False
            else:
                if self.power < other.power:
                    return True
                elif self.power > other.power:
                    return False
        if self.row < other.row:
            return True
        elif self.row > other.row:
            return False
        if self.column < other.column:
            return True
        elif self.column > other.column:
            return False
        if self.quadrant < other.quadrant:
            return True
        elif self.quadrant > other.quadrant:
            return False
        if self.direction < other.direction:
            return True
        elif self.direction < other.direction:
            return False
        return False # make True if __le__

    def __hash__(self):
        r"""Hash uses str instead of repr, and thus power does not distinguish values."""
        return hash(self.__str__())

    def __str__(self):
        r"""String returns values except for power."""
        return 'row: {}, col: {}, quad: {}, dir: {}'.format(self.row, self.column, self.quadrant, self.direction)

    def __repr__(self):
        r"""Repr returns all values, including power."""
        return '<' + self.__str__() + ', pwr: {}'.format(self.power) + '>'
        
    @staticmethod
    def get_pos(move_list):
        r"""Converts the move list into position numbers."""
        pos = []
        for this_move in move_list:
            pos.append(this_move.row + 6 * this_move.column)
        return pos
        
    @staticmethod
    def get_rot(move_list):
        r"""Converts the quadrant rotation and direction into a representative number."""
        rot = []
        for this_move in move_list:
            rot.append(this_move.quadrant + 4 * (this_move.direction == 1))
        return rot

#%% Classes - GameStats
class GameStats(Frozen):
    r"""
    Class that keeps track of all the moves in a game.
    """
    def __init__(self, number, first_move, winner=PLAYER['none'], move_list=None):
        self.number     = number
        self.first_move = first_move
        self.winner     = winner
        if move_list is None:
            self.move_list = []
        else:
            self.move_list = move_list

    def add_move(self, move):
        r"""Adds the given move to the game move history."""
        assert isinstance(move, Move), 'The specified move must be an instance of class Move.'
        self.move_list.append(move)

    def remove_moves(self, cur_move=None):
        r"""Removes the moves from the current move number to the end of the list."""
        if cur_move is None:
            self.move_list.pop()
        else:
            del(self.move_list[cur_move:])

    @property
    def num_moves(self):
        return len(self.move_list)

    @staticmethod
    def save(filename, game_hist):
        r"""Saves a list of GameStats objects to disk."""
        with open(filename, 'wb') as file:
            pickle.dump(game_hist, file)

    @staticmethod
    def load(filename):
        r"""Loads a list of GameStats objects to disk."""
        with open(filename, 'rb') as file:
            game_hist = pickle.load(file)
        return game_hist

#%% Dynamic globals
cur_move    = 0
cur_game    = 0
board       = PLAYER['none'] * np.ones((6, 6), dtype=int)
move_status = {'ok': False, 'pos': None, 'patch_object': None}
game_hist   = []
game_hist.append(GameStats(number=cur_game, first_move=PLAYER['white']))

#%% Debugging
board = np.array([\
    [0,-1, 0, 0, 0, 0],\
    [0, 1, 0, 1, 1, 1],\
    [0, 0, 0, 0, 0, 0],\
    [0,-1, 0, 0, 0, 0],\
    [0,-1, 1,-1,-1,-1],\
    [0, 1, 0, 0, 0, 0]], dtype=int)
    
#%% Classes - RotationButton
class RotationButton(QPushButton):
    def __init__(self, text, parent, quadrant, direction):
        super(RotationButton, self).__init__(text, parent)
        self.quadrant  = quadrant
        self.direction = direction
        self.overlay   = None
        
    def paintEvent(self, event):
        # call super method
        QPushButton.paintEvent(self, event)
        # create painter and load base image
        painter = QtGui.QPainter(self)
        pixmap_key = str(self.quadrant) + ('L' if self.direction == -1 else 'R')
        pixmap = IMAGES[pixmap_key].pixmap(QtCore.QSize(71, 71))
        if self.overlay is None:
            painter.drawPixmap(0, 0, pixmap)            
        else:
            # optionally load the overlaid image
            overlay_pixmap = IMAGES[self.overlay].pixmap(QtCore.QSize(71, 71))
            painter.drawPixmap(0, 0, overlay_pixmap)
            painter.setCompositionMode(painter.CompositionMode_SourceOver)
            painter.drawPixmap(0, 0, pixmap)
        painter.end()

#%% Classes - PentagoGui
class PentagoGui(QWidget):
    r"""
    The Pentago GUI.
    """
    def __init__(self, **kwargs):
        super(PentagoGui, self).__init__(**kwargs)
        self.init()

    def init(self):
        r"""Creates the actual GUI."""

        #%% properties
        QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        #%% Text
        # Pentago
        lbl_pentago = QLabel('Pentago', self)
        lbl_pentago.setGeometry(360, 51, 220, 40)
        lbl_pentago.setAlignment(QtCore.Qt.AlignCenter)
        lbl_pentago.setStyleSheet('font-size: 18pt; font: bold;')
        # Score
        lbl_score = QLabel('Score:', self)
        lbl_score.setGeometry(50, 220, 220, 40)
        lbl_score.setAlignment(QtCore.Qt.AlignCenter)
        lbl_score.setStyleSheet('font-size: 12pt; font: bold;')
        # Move
        lbl_move = QLabel('Move:', self)
        lbl_move.setGeometry(740, 220, 220, 40)
        lbl_move.setAlignment(QtCore.Qt.AlignCenter)
        lbl_move.setStyleSheet('font-size: 12pt; font: bold;')
        # White Wins
        lbl_white = QLabel('White Wins:', self)
        lbl_white.setGeometry(50, 280, 80, 20)
        # Black Wins
        lbl_black = QLabel('Black Wins:', self)
        lbl_black.setGeometry(50, 310, 80, 20)
        # Games Tied
        lbl_games = QLabel('Games Tied:', self)
        lbl_games.setGeometry(50, 340, 80, 20)
        # Changeable labels
        self.lbl_white_wins = QLabel('0', self)
        self.lbl_white_wins.setGeometry(140, 280, 60, 20)
        self.lbl_white_wins.setAlignment(QtCore.Qt.AlignRight)
        self.lbl_black_wins = QLabel('0', self)
        self.lbl_black_wins.setGeometry(140, 310, 60, 20)
        self.lbl_black_wins.setAlignment(QtCore.Qt.AlignRight)
        self.lbl_games_tied = QLabel('0', self)
        self.lbl_games_tied.setGeometry(140, 340, 60, 20)
        self.lbl_games_tied.setAlignment(QtCore.Qt.AlignRight)

        #%% Axes
        # board
        self.wid_board = QWidget(self)
        self.wid_board.setGeometry(260, 140, 420, 420)
        fig = Figure(figsize=(4.2, 4.2), dpi=100, frameon=False)
        self.board_canvas = FigureCanvas(fig)
        self.board_canvas.setParent(self.wid_board)
        self.board_canvas.mpl_connect('button_release_event', lambda event: _mouse_click_callback(self, event))
        self.board_axes = Axes(fig, [0., 0., 1., 1.])
        self.board_axes.invert_yaxis()
        self.board_axes.set_axis_off()
        fig.add_axes(self.board_axes)

        # current move
        self.wid_move = QWidget(self)
        self.wid_move.setGeometry(780, 700-350-71, 70, 70)
        fig = Figure(figsize=(.7, .7), dpi=100, frameon=False)
        self.move_canvas = FigureCanvas(fig)
        self.move_canvas.setParent(self.wid_move)
        self.move_axes = Axes(fig, [0., 0., 1., 1.])
        self.move_axes.set_xlim(-RADIUS['square'], RADIUS['square'])
        self.move_axes.set_ylim(-RADIUS['square'], RADIUS['square'])
        self.move_axes.set_axis_off()
        fig.add_axes(self.move_axes)

        #%% Buttons
        # Undo button
        self.btn_undo = QPushButton('Undo', self)
        self.btn_undo.setToolTip('Undoes the last move.')
        self.btn_undo.setGeometry(350, 600, 60, 30)
        self.btn_undo.setStyleSheet('color: yellow; background-color: #990000; font: bold;')
        self.btn_undo.clicked.connect(self.btn_undo_function)
        # New Game button
        self.btn_new = QPushButton('New Game', self)
        self.btn_new.setToolTip('Starts a new game.')
        self.btn_new.setGeometry(430, 600, 80, 50)
        self.btn_new.setStyleSheet('color: yellow; background-color: #006633; font: bold;')
        self.btn_new.clicked.connect(self.btn_new_function)
        # Redo button
        self.btn_redo = QPushButton('Redo', self)
        self.btn_redo.setToolTip('Redoes the last move.')
        self.btn_redo.setGeometry(530, 600, 60, 30)
        self.btn_redo.setStyleSheet('color: yellow; background-color: #000099; font: bold;')
        self.btn_redo.clicked.connect(self.btn_redo_function)

        # 1R button
        self.btn_1R = RotationButton('', self, quadrant=1, direction=1)
        self.btn_1R.setToolTip('Rotates quadrant 1 to the right 90 degrees.')
        self.btn_1R.setIconSize(QtCore.QSize(71, 71))
        self.btn_1R.setGeometry(260, 49, 71, 71)
        self.btn_1R.clicked.connect(self.btn_1R_function)
        # 2R button
        self.btn_2R = RotationButton('', self, quadrant=2, direction=1)
        self.btn_2R.setToolTip('Rotates quadrant 2 to the right 90 degrees.')
        self.btn_2R.setIconSize(QtCore.QSize(71, 71))
        self.btn_2R.setGeometry(700, 139, 71, 71)
        self.btn_2R.clicked.connect(self.btn_2R_function)
        # 3R button
        self.btn_3R = RotationButton('', self, quadrant=3, direction=1)
        self.btn_3R.setToolTip('Rotates quadrant 3 to the right 90 degrees.')
        self.btn_3R.setIconSize(QtCore.QSize(71, 71))
        self.btn_3R.setGeometry(170, 489, 71, 71)
        self.btn_3R.clicked.connect(self.btn_3R_function)
        # 4R button
        self.btn_4R = RotationButton('', self, quadrant=4, direction=1)
        self.btn_4R.setToolTip('Rotates quadrant 4 to the right 90 degrees.')
        self.btn_4R.setIconSize(QtCore.QSize(71, 71))
        self.btn_4R.setGeometry(610, 579, 71, 71)
        self.btn_4R.clicked.connect(self.btn_4R_function)
        # 1L button
        self.btn_1L = RotationButton('', self, quadrant=1, direction=-1)
        self.btn_1L.setToolTip('Rotates quadrant 1 to the left 90 degrees.')
        self.btn_1L.setIconSize(QtCore.QSize(71, 71))
        self.btn_1L.setGeometry(170, 139, 71, 71)
        self.btn_1L.clicked.connect(self.btn_1L_function)
        # 2L button
        self.btn_2L = RotationButton('', self, quadrant=2, direction=-1)
        self.btn_2L.setToolTip('Rotates quadrant 2 to the left 90 degrees.')
        self.btn_2L.setIconSize(QtCore.QSize(71, 71))
        self.btn_2L.setGeometry(610, 49, 71, 71)
        self.btn_2L.clicked.connect(self.btn_2L_function)
        # 3L button
        self.btn_3L = RotationButton('', self, quadrant=3, direction=-1)
        self.btn_3L.setToolTip('Rotates quadrant 3 to the left 90 degrees.')
        self.btn_3L.setIconSize(QtCore.QSize(71, 71))
        self.btn_3L.setGeometry(260, 579, 71, 71)
        self.btn_3L.clicked.connect(self.btn_3L_function)
        # 4L button
        self.btn_4L = RotationButton('', self, quadrant=4, direction=-1)
        self.btn_4L.setToolTip('Rotates quadrant 4 to the left 90 degrees.')
        self.btn_4L.setIconSize(QtCore.QSize(71, 71))
        self.btn_4L.setGeometry(700, 489, 71, 71)
        self.btn_4L.clicked.connect(self.btn_4L_function)
        # buttons dictionary for use later
        self.rot_buttons = {1:self.btn_1L, 2:self.btn_2L, 3:self.btn_3L, 4:self.btn_4L, \
            5:self.btn_1R, 6:self.btn_2R, 7:self.btn_3R, 8:self.btn_4R}

        #%% Call wrapper to initialize GUI
        wrapper(self)

        #%% GUI properties
        self.setGeometry(520, 380, 1000, 700)
        self.setWindowTitle('Pentago')
        self.setWindowIcon(QtGui.QIcon(os.path.join(get_images_dir(),'pentago.png')))
        self.show()

    #%% Other callbacks
    def closeEvent(self, event):
        """Things in here happen on GUI closing."""
        close_immediately = True
        filename = os.path.join(get_output_dir(), 'pentago.p')
        if close_immediately:
            GameStats.save(filename, game_hist)
            event.accept()
        else:
            # Alternative with user choice
            reply = QMessageBox.question(self, 'Message', \
                "Are you sure to quit?", QMessageBox.Yes | \
                QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                GameStats.save(filename, game_hist)
                event.accept()
            else:
                event.ignore()

    #%% Button callbacks
    def btn_undo_function(self):
        """Functions that executes on undo button press."""
        # declare globals
        global cur_move, cur_game, board
        # get last move
        last_move = game_hist[cur_game].move_list[cur_move-1]
        if LOGGING:
            print('Undoing move = {}'.format(last_move))
        # undo rotation
        _rotate_board(board, last_move.quadrant, -last_move.direction)
        # delete piece
        board[last_move.row, last_move.column] = PLAYER['none']
        # update current move
        cur_move -= 1
        # call GUI wrapper
        wrapper(self)

    def btn_new_function(self):
        """Functions that executes on new game button press."""
        # declare globals
        global cur_move, cur_game, board
        # update values
        last_lead = game_hist[cur_game].first_move
        next_lead = PLAYER['black'] if last_lead == PLAYER['white'] else PLAYER['white']
        assert len(game_hist) == cur_game + 1
        cur_game += 1
        cur_move = 0
        game_hist.append(GameStats(number=cur_game, first_move=next_lead, winner=PLAYER['none']))
        board = PLAYER['none'] * np.ones((6, 6), dtype=int)
        # call GUI wrapper
        wrapper(self)

    def btn_redo_function(self):
        """Functions that executes on redo button press."""
        # declare globals
        global cur_move, cur_game, board
        # get next move
        redo_move = game_hist[cur_game].move_list[cur_move]
        if LOGGING:
            print('Redoing move = {}'.format(redo_move))
        # place piece
        board[redo_move.row, redo_move.column] = _calc_cur_move(cur_move, cur_game)
        # redo rotation
        _rotate_board(board, redo_move.quadrant, redo_move.direction)
        # update current move
        cur_move += 1
        # call GUI wrapper
        wrapper(self)

    def btn_1R_function(self):
        """Functions that executes on 1R button press."""
        _execute_move(quadrant=1, direction=1)
        wrapper(self)

    def btn_2R_function(self):
        """Functions that executes on 2R button press."""
        _execute_move(quadrant=2, direction=1)
        wrapper(self)

    def btn_3R_function(self):
        """Functions that executes on 3R button press."""
        _execute_move(quadrant=3, direction=1)
        wrapper(self)

    def btn_4R_function(self):
        """Functions that executes on 4R button press."""
        _execute_move(quadrant=4, direction=1)
        wrapper(self)

    def btn_1L_function(self):
        """Functions that executes on 1L button press."""
        _execute_move(quadrant=1, direction=-1)
        wrapper(self)

    def btn_2L_function(self):
        """Functions that executes on 2L button press."""
        _execute_move(quadrant=2, direction=-1)
        wrapper(self)

    def btn_3L_function(self):
        """Functions that executes on 3L button press."""
        _execute_move(quadrant=3, direction=-1)
        wrapper(self)

    def btn_4L_function(self):
        """Functions that executes on 4L button press."""
        _execute_move(quadrant=4, direction=-1)
        wrapper(self)

#%% _mouse_click_callback
def _mouse_click_callback(self, event):
    r"""
    Function that executes on mouse click on the board axes.  Ends up placing a piece on the board.
    """
    # ignore events that are outside the axes
    if event.xdata is None or event.ydata is None:
        if LOGGING:
            print('Click is off the board.')
        return
    # test for a game that has already been concluded
    if game_hist[cur_game].winner != PLAYER['none']:
        if LOGGING:
            print('Game is over.')
        move_status['ok'] = False
        move_status['pos'] = None
        return
    # alias the rounded values of the mouse click location
    x = np.round(event.ydata).astype(int)
    y = np.round(event.xdata).astype(int)
    if LOGGING:
        print('Clicked on (x,y) = ({}, {})'.format(x, y))
    # get axes limits
    (m, n) = board.shape
    # ignore values that are outside the board
    if x < 0 or y < 0 or x >= m or y >= n:
        if LOGGING:
            print('Click is outside playable board.')
        return
    if board[x, y] == PLAYER['none']:
        # check for previous good move
        if move_status['ok']:
            if LOGGING:
                print('removing previous piece.')
            move_status['patch_object'].remove()
        move_status['ok'] = True
        move_status['pos'] = (x, y)
        if LOGGING:
            print('Placing current piece.')
        current_player = _calc_cur_move(cur_move, cur_game)
        if current_player == PLAYER['white']:
            move_status['patch_object'] = _plot_piece(self.board_axes, x, y, RADIUS['piece'], COLOR['next_wht'])
        elif current_player == PLAYER['black']:
            move_status['patch_object'] = _plot_piece(self.board_axes, x, y, RADIUS['piece'], COLOR['next_blk'])
        else:
            raise ValueError('Unexpected player to move next.')
    else:
        # delete a previously placed piece
        if move_status['ok']:
            move_status['patch_object'].remove()
        move_status['ok'] = False
        move_status['pos'] = None
    # redraw the board
    self.board_canvas.draw()

#%% _calc_cur_move
def _calc_cur_move(cur_move, cur_game):
    r"""
    Calculates whose move it is based on the turn and game number.

    Parameters
    ----------
    cur_move : int
        Current move number
    cur_game : int
        Current game number

    Returns
    -------
    move : int
        Current move, from {1=white, -1=black}

    Examples
    --------
    >>> from dstauffman.games.pentago import _calc_cur_move
    >>> move = _calc_cur_move(0, 0)
    >>> print(move)
    1

    """
    if np.mod(cur_move + cur_game, 2) == 0:
        move = PLAYER['white']
    else:
        move = PLAYER['black']
    return move

#%% _execute_move
def _execute_move(*, quadrant, direction):
    r"""
    Tests and then executes a move.
    """
    global board, cur_move
    if move_status['ok']:
        if LOGGING:
            print('Rotating Quadrant {} in Direction {}.'.format(quadrant, direction))
        # delete gray piece
        move_status['patch_object'].remove()
        move_status['patch_object'] = None
        # add new piece to board
        board[move_status['pos'][0], move_status['pos'][1]] = _calc_cur_move(cur_move, cur_game)
        # rotate board
        _rotate_board(board, quadrant, direction)
        # increment move list
        assert game_hist[cur_game].num_moves >= cur_move, \
            'Number of moves = {}, Current Move = {}'.format(game_hist[cur_game].num_moves, cur_move)
        this_move = Move(move_status['pos'][0], move_status['pos'][1], quadrant, direction)
        if game_hist[cur_game].num_moves == cur_move:
            game_hist[cur_game].add_move(this_move)
        else:
            game_hist[cur_game].move_list[cur_move] = this_move
            game_hist[cur_game].remove_moves(cur_move+1)
        # increment current move
        cur_move += 1
        # reset status for next move
        move_status['ok'] = False
        move_status['pos'] = None
    else:
        if LOGGING:
            print('No move to execute.')

#%% _check_for_win
def _check_for_win(board):
    r"""
    Checks for a win.
    """
    # find white and black wins
    white = np.nonzero(np.sum(np.expand_dims(board.ravel() == PLAYER['white'], axis=1) * WIN, axis=0) == 5)[0]
    black = np.nonzero(np.sum(np.expand_dims(board.ravel() == PLAYER['black'], axis=1) * WIN, axis=0) == 5)[0]

    # determine winner
    if len(white) == 0:
        if len(black) == 0:
            winner = PLAYER['none']
        else:
            winner = PLAYER['black']
    else:
        if len(black) == 0:
            winner = PLAYER['white']
        else:
            winner = PLAYER['draw']

    # check for a full game board after determining no other win was found
    if winner == PLAYER['none'] and not np.any(board == PLAYER['none']):
        winner = PLAYER['draw']

    # find winning pieces on the board
    if winner == PLAYER['none']:
        win_mask = np.zeros((6,6), dtype=bool)
    else:
        if LOGGING:
            print('Win detected.  Winner is {}.'.format(list(PLAYER.keys())[list(PLAYER.values()).index(winner)]))
        win_mask = np.reshape(np.sum(WIN[:, white], axis=1) + np.sum(WIN[:, black], axis=1), (6, 6)) != 0

    # update statistics
    game_hist[cur_game].winner = winner

    return (winner, win_mask)

#%% _find_moves
def _find_moves(board):
    r"""
    Finds the best current move.

    Notes
    -----
    #.  Currently this function is only trying to find a win in one move situation.

    Examples
    --------

    >>> from dstauffman.games.pentago import _find_moves
    >>> import numpy as np
    >>> board = np.reshape(np.hstack((np.array([0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1]), np.zeros(24, dtype=int))), (6, 6))
    >>> (white_moves, black_moves) = _find_moves(board)
    >>> print(white_moves) # doctest: +SKIP
    # TODO: write the correct answer

    >>> print(black_moves)
    []

    """
    # expand the board to a linear 2D matrix
    big_board = np.expand_dims(board.ravel(), axis=1)

    # check for wins that shouldn't exist
    test = big_board * WIN
    score = np.sum(test, axis=0)
    if np.any(np.abs(score) >= 5):
        raise ValueError('Board should not already be in a winning position.')

    # cross reference two matrices with element-wise multiplication
    test = big_board * ONE_OFF

    # find score
    score = np.sum(test, axis=0)

    # find white and black rotate to win moves
    rot_white = np.nonzero(score >=  5)[0]
    rot_black = np.nonzero(score <= -5)[0]

    # find white and black one off potentials
    white = np.nonzero((score >=  4) & (score <  5))[0]
    black = np.nonzero((score <= -4) & (score > -5))[0]

    # see if the remaining piece is an open square
    if len(white) > 0:
        pos_white = ONE_OFF[:, white]
        needed    = np.logical_xor(pos_white, big_board)
        free      = np.logical_and(needed, np.logical_not(big_board))
        ix_white  = white[np.any(free, axis=0)]
    else:
        ix_white  = np.array([], dtype=int)
    if len(black) > 0:
        pos_black = ONE_OFF[:, black]
        needed    = np.logical_xor(pos_black, big_board)
        free      = np.logical_and(needed, np.logical_not(big_board))
        ix_black  = black[np.any(free, axis=0)]
    else:
        ix_black  = np.array([], dtype=int)

    # find winning moves
    # placement winning moves
    white_set = _get_move_from_one_off(big_board, ix_white, ONE_OFF)
    black_set = _get_move_from_one_off(big_board, ix_black, ONE_OFF)
    # rotation only winning moves
    #white_rotations = _get_move_from_one_off(big_board, rot_white, ONE_OFF)
    #black_rotations = _get_move_from_one_off(big_board, rot_black, ONE_OFF)

    # combine the possible moves
    #white_set = white_set | white_rotations
    #black_set = black_set | black_rotations

    # convert to list, sort by power, such that ties go at the end
    white_moves = sorted(list(white_set))
    black_moves = sorted(list(black_set))

    return (white_moves, black_moves)

#    [xwr, ywr, qwr, dwr] =
#    [xbr, ybr, qbr, dbr] =
#
#    # Add moves that are just a place anywhere and rotate to win
#    empty = np.nonzero(big_board == PLAYER.none)[0]
#    # white
#    pos_wr = np.ones((1, len(qwr)), dtype=int) * empty
#    xwr = modd(pos_wr.ravel(), 6)
#    ywr = np.ceil(pos_wr.ravel() / 6).astype(int)
#    qwr = repmat(qwr,length(empty),1);
#    qwr = qwr(:)';
#    dwr = repmat(dwr,length(empty),1);
#    dwr = dwr(:)';
#    # black
#    pos_br = repmat(empty,1,length(qbr));
#    xbr = mod(pos_br(:)',6);
#    xbr(xbr == 0) = 6;
#    ybr = ceil(pos_br(:)'/6);
#    qbr = repmat(qbr,length(empty),1);
#    qbr = qbr(:)';
#    dbr = repmat(dbr,length(empty),1);
#    dbr = dbr(:)';
#    # white win moves
#    moves.white.x    = [xwp, xwr];
#    moves.white.y    = [ywp, ywr];
#    moves.white.quad = [qwp, qwr];
#    moves.white.dir  = [dwp, dwr];
#    moves.white.pwr  = 5*ones(size(moves.white.x));
#    # mark moves that are really a tie, instead of a win
#    white_moves.white.pwr(ismember([qwp+4*dwp,qwr+4*dwr],qbr+4*dbr)) = np.nan

#    # black win moves
#    moves.black.x    = [xbp, xbr];
#    moves.black.y    = [ybp, ybr];
#    moves.black.quad = [qbp, qbr];
#    moves.black.dir  = [dbp, dbr];
#    moves.black.pwr  = 5*ones(size(moves.black.x));
#    # mark moves that are really a tie, instead of a win
#    moves.black.pwr(ismember([qbp+4*dbp,qbr+4*dbr],qwr+4*dwr)) = nan;
#    # resort ties at end
#    moves.black = resort_moves(moves.black);

#%% _get_move_from_one_off
def _get_move_from_one_off(big_board, ix, ONE_OFF):
    r"""
    Turns the given index into a Move instance.
    """
    # preallocate x & y to NaNs in case the winning move is just a rotation
    row = INT_TOKEN * np.ones(len(ix), dtype=int)
    column = row.copy()

    # find missing piece
    pos_ix = np.logical_and(np.logical_xor(np.abs(big_board), ONE_OFF[:,ix]), ONE_OFF[:,ix])

    assert np.all(np.sum(pos_ix, axis=0) <= 1), 'Only exactly one or fewer places should be found.'
    assert np.all(np.sum(pos_ix, axis=0) == 1), 'Exactly one place was not found.' # TODO: 0 is okay later

    # pull out element number from 0 to 35
    (one_off_row, one_off_col) = np.nonzero(pos_ix)
    # convert to row and column
    row[one_off_col]    = one_off_row//6
    column[one_off_col] = np.mod(one_off_row, 6)

    # get quadrant and rotation number
    # based on order that ONE_OFF was built, so permutations of first quads 1,2,3,4, second left,right;
    num = np.ceil(ix/WIN.shape[1]).astype(int)

    # pull out quadrant number
    quadrant = modd(num, 4)

    # pull out rotation direction
    direction = -1 * np.ones(len(ix), dtype=int)
    direction[num < 5] = 1

    # convert to a move class
    move = set()
    for i in range(len(ix)):
        move.add(Move(row[i], column[i], quadrant[i], direction[i]))
    return move

#%% _update_game_stats
def _update_game_stats(self, results):
    r"""
    Updates the game stats on the left of the GUI.
    """
    # calculate the number of wins
    white_wins = np.sum(results == PLAYER['white'])
    black_wins = np.sum(results == PLAYER['black'])
    games_tied = np.sum(results == PLAYER['draw'])

    # update the gui
    self.lbl_white_wins.setText("{}".format(white_wins))
    self.lbl_black_wins.setText("{}".format(black_wins))
    self.lbl_games_tied.setText("{}".format(games_tied))

#%% _display_controls
def _display_controls(self):
    r"""
    Determines what controls to display on the GUI.
    """
    # show/hide New Game Button
    if game_hist[cur_game].winner == PLAYER['none']:
        self.btn_new.hide()
    else:
        self.btn_new.show()

    # show/hide Undo Button
    if cur_move > 0:
        self.btn_undo.show()
    else:
        self.btn_undo.hide()

    # show/hide Redo Button
    if game_hist[cur_game].num_moves > cur_move:
        self.btn_redo.show()
    else:
        self.btn_redo.hide()

#%% _plot_cur_move
def _plot_cur_move(ax, move):
    r"""
    Plots the piece corresponding the current players move.
    """
    # local alias
    half_box_size = RADIUS['square']

    # fill background
    ax.add_patch(Rectangle((-half_box_size, -half_box_size), 2*half_box_size, 2*half_box_size, \
        facecolor=COLOR['board'], edgecolor='k'))

    # draw the piece
    if move == PLAYER['white']:
        _plot_piece(ax, 0, 0, RADIUS['piece'], COLOR['white'])
    elif move == PLAYER['black']:
        _plot_piece(ax, 0, 0, RADIUS['piece'], COLOR['black'])
    elif move == PLAYER['none']:
        pass
    else:
        raise ValueError('Unexpected player.')

    # turn the axes back off (they get reinitialized at some point)
    ax.set_axis_off()

#%% _plot_picee
def _plot_piece(ax, vc, hc, r, c, half=False):
    r"""
    Plots a piece on the board.

    Parameters
    ----------
    ax, object
        Axis to plot on
    vc, float
        Vertical center (Y-axis or board row)
    hc, float
        Horizontal center (X-axis or board column)
    r, float
        radius
    c, 3-tuple
        RGB triplet color
    half, bool optional, default is false
        flag for plotting half a piece

    Returns
    -------
    fill_handle, object
        handle to the piece

    Examples
    --------
    >>> from dstauffman.games.pentago import _plot_piece
    >>> import matplotlib.pyplot as plt
    >>> fig = plt.figure()
    >>> ax = fig.add_subplot(111)
    >>> _ = ax.set_xlim(0.5, 1.5)
    >>> _ = ax.set_ylim(0.5, 1.5)
    >>> obj = _plot_piece(ax, 1, 1, 0.45, (0, 0, 1))
    >>> plt.show(block=False)

    >>> plt.close()

    """

    # theta angle to sweep out 2*pi
    if half:
        piece = Wedge((hc, vc), r, 270, 90, facecolor=c, edgecolor='k')
    else:
        piece = Circle((hc, vc), r, facecolor=c, edgecolor='k')

    # plot piece
    ax.add_patch(piece)
    return piece

#%% _plot_board
def _plot_board(ax):
    r"""
    Plots the board (and the current player move).
    """
    # get axes limits
    (m, n) = board.shape
    s = RADIUS['square']
    xmin = 0 - s
    xmax = m - 1 + s
    ymin = 0 - s
    ymax = n - 1 + s

    # fill background
    ax.add_patch(Rectangle((-xmin-1, -ymin-1), xmax-xmin, ymax-ymin, facecolor=COLOR['board'], \
        edgecolor=COLOR['maj_edge']))

    # draw minor horizontal lines
    ax.plot([1-s, 1-s], [ymin, ymax], color=COLOR['min_edge'])
    ax.plot([2-s, 2-s], [ymin, ymax], color=COLOR['min_edge'])
    ax.plot([4-s, 4-s], [ymin, ymax], color=COLOR['min_edge'])
    ax.plot([5-s, 5-s], [ymin, ymax], color=COLOR['min_edge'])
    # draw minor vertical lines
    ax.plot([xmin, xmax], [1-s, 1-s], color=COLOR['min_edge'])
    ax.plot([xmin, xmax], [2-s, 2-s], color=COLOR['min_edge'])
    ax.plot([xmin, xmax], [4-s, 4-s], color=COLOR['min_edge'])
    ax.plot([xmin, xmax], [5-s, 5-s], color=COLOR['min_edge'])
    # draw major quadrant lines
    ax.plot([3-s, 3-s], [ymin, ymax], color=COLOR['maj_edge'], linewidth=2)
    ax.plot([xmin, xmax], [3-s, 3-s], color=COLOR['maj_edge'], linewidth=2)

    # loop through and place marbles
    for i in range(m):
        for j in range(n):
            if board[i, j] == PLAYER['none']:
                pass
            elif board[i, j] == PLAYER['white']:
                _plot_piece(ax, i, j, RADIUS['piece'], COLOR['white'])
            elif board[i, j] == PLAYER['black']:
                _plot_piece(ax, i, j, RADIUS['piece'], COLOR['black'])
            else:
                raise ValueError('Bad board position.')

#%% _plot_win
def _plot_win(ax, mask):
    r"""
    Plots the winning pieces in red.

    Parameters
    ----------
    ax : object
        Axis to plot on
    mask : 2D bool ndarray
        Mask for which squares to plot the win

    Examples
    --------
    >>> from dstauffman.games.pentago import _plot_win
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> fig = plt.figure()
    >>> ax = fig.add_subplot(111, aspect='equal')
    >>> _ = ax.set_xlim(-0.5, 5.5)
    >>> _ = ax.set_ylim(-0.5, 5.5)
    >>> ax.invert_yaxis()
    >>> mask = np.zeros((6, 6), dtype=bool)
    >>> mask[0, 0:5] = True
    >>> _plot_win(ax, mask)
    >>> plt.show(block=False)

    >>> plt.close()

    """
    (m, n) = mask.shape
    for i in range(m):
        for j in range(n):
            if mask[i, j]:
                _plot_piece(ax, i, j, RADIUS['win'], COLOR['win'])


#%% _plot_possible_win
def _plot_possible_win(ax, rot_buttons, white_moves, black_moves):
    r"""
    Plots the possible wins on the board.

    Examples
    --------

    >>> from dstauffman.games.pentago import _plot_possible_win, _find_moves
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> fig = plt.figure()
    >>> ax = fig.add_subplot(111, aspect='equal')
    >>> _ = ax.set_xlim(-0.5, 5.5)
    >>> _ = ax.set_ylim(-0.5, 5.5)
    >>> ax.invert_yaxis()
    >>> board = np.reshape(np.hstack((0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, np.zeros(24))), (6, 6))
    >>> (white_moves, black_moves) = _find_moves(board)
    >>> _plot_possible_win(ax, white_moves, black_moves) # doctest: +SKIP
    >>> plt.show(block=False)
    
    >>> plt.close()

    """
    # find set of positions to plot
    pos_white = set(Move.get_pos(white_moves))
    pos_black = set(Move.get_pos(black_moves))
    # find intersecting positions
    pos_both  = pos_white & pos_black
    
    # plot the whole pieces
    for pos in pos_white ^ pos_both:
        _plot_piece(ax, np.mod(pos, 6), pos//6, RADIUS['win'], COLOR['win_wht'])
    for pos in pos_black ^ pos_both:
        _plot_piece(ax, np.mod(pos, 6), pos//6, RADIUS['win'], COLOR['win_blk'])

    # plot the half pieces, with the current players move as whole
    next_move = _calc_cur_move(cur_move, cur_game)
    if next_move == PLAYER['white']:
        for pos in pos_both:
            _plot_piece(ax, np.mod(pos, 6), pos//6, RADIUS['win'], COLOR['win_wht'])
            _plot_piece(ax, np.mod(pos, 6), pos//6, RADIUS['win'], COLOR['win_blk'], half=True)
    elif next_move == PLAYER['black']:
        for pos in pos_both:
            _plot_piece(ax, np.mod(pos, 6), pos//6, RADIUS['win'], COLOR['win_blk'])
            _plot_piece(ax, np.mod(pos, 6), pos//6, RADIUS['win'], COLOR['win_wht'], half=True)
    else:
        raise ValueError('Unexpected next player.')

    # find set of quadrant rotations
    rot_white = set(Move.get_rot(white_moves))
    rot_black = set(Move.get_rot(black_moves))
    # find intersection rotations
    rot_both  = rot_white & rot_black

    # update the overlay information in the buttons
    for this_rot in rot_white ^ rot_both:
        rot_buttons[this_rot].overlay = 'wht'
    for this_rot in rot_black ^ rot_both:
        rot_buttons[this_rot].overlay = 'blk'
    if next_move == PLAYER['white']:
        for rot in rot_both:
            rot_buttons[this_rot].overlay = 'w_b'
    else:
        for rot in rot_both:
            rot_buttons[this_rot].overlay = 'b_w'
      
#%% _load_images      
def _load_images():
    r"""Loads the images for use later on."""
    # TODO: needs a QApplication to exist first.  Play around with making this earlier.
    images_dir = get_images_dir()
    images        = {}
    images['1R']  = QtGui.QIcon(os.path.join(images_dir, 'right1.png'))
    images['2R']  = QtGui.QIcon(os.path.join(images_dir, 'right2.png'))
    images['3R']  = QtGui.QIcon(os.path.join(images_dir, 'right3.png'))
    images['4R']  = QtGui.QIcon(os.path.join(images_dir, 'right4.png'))
    images['1L']  = QtGui.QIcon(os.path.join(images_dir, 'left1.png'))
    images['2L']  = QtGui.QIcon(os.path.join(images_dir, 'left2.png'))
    images['3L']  = QtGui.QIcon(os.path.join(images_dir, 'left3.png'))
    images['4L']  = QtGui.QIcon(os.path.join(images_dir, 'left4.png'))
    images['wht'] = QtGui.QIcon(os.path.join(images_dir, 'blue_button.png'))
    images['blk'] = QtGui.QIcon(os.path.join(images_dir, 'cyan_button.png'))
    images['w_b'] = QtGui.QIcon(os.path.join(images_dir, 'blue_cyan_button.png'))
    images['b_w'] = QtGui.QIcon(os.path.join(images_dir, 'cyan_blue_button.png'))
    return images

#%% move_wrapper
def wrapper(self):
    r"""
    Acts as a wrapper to everything the GUI needs to do.
    """
    # clean up an existing artifacts
    self.board_axes.clear()
    self.move_axes.clear()

    # plot the current move
    _plot_cur_move(self.move_axes, _calc_cur_move(cur_move, cur_game))
    self.move_canvas.draw()

    # draw turn arrows in default colors
    for button in self.rot_buttons.values():
        button.overlay = None

    # draw the board
    _plot_board(self.board_axes)

    # check for win
    (winner, win_mask) = _check_for_win(board)

    # plot win
    _plot_win(self.board_axes, win_mask)

    # display relevant controls
    _display_controls(self)

    # plot possible winning moves (includes updating turn arrows)
    if winner == PLAYER['none']:
        (white_moves, black_moves) = _find_moves(board)
        _plot_possible_win(self.board_axes, self.rot_buttons, white_moves, black_moves)

    # redraw with the final board
    self.board_axes.set_axis_off()
    self.board_canvas.draw()

    # update game stats on GUI
    results = [x.winner for x in game_hist]
    _update_game_stats(self, results=np.array(results)) # TODO: make better?
    self.update()

#%% Unit Test
def _main():
    """Unit test function."""
    pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = 'test'
    if mode == 'run':
        # Runs the GUI application
        app = QApplication(sys.argv)
        # load the images
        IMAGES = _load_images()
        # instatiates the GUI
        gui = PentagoGui()
        gui.show()
        sys.exit(app.exec_())
    elif mode == 'test':
        _main()
        # open a qapp
        if QApplication.instance() is None:
            qapp = QApplication(sys.argv)
        else:
            qapp = QApplication.instance()
        # run the tests
        unittest.main(module='dstauffman.games.test_pentago', exit=False)
        doctest.testmod(verbose=False)
        # close the qapp
        qapp.closeAllWindows()
    elif mode == 'null':
        pass
    else:
        raise ValueError('Unexpected mode of "{}".'.format(mode))
