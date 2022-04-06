import random
from string import ascii_lowercase as letters
import itertools
from collections import namedtuple

def generateWords(count : int) -> list[str]:
    """ uses numbers for debugging purposes """
    words = []
    for _ in range(count):
        length = int(random.triangular(4, 24, 9))
        newWord = str(random.randrange(10**length))
        newWord = "0"*(length-len(newWord)) + newWord

        words.append(newWord)
    
    return words

def generateBoard(size : int) -> list[list[str]]:
    return [[' ' for _ in range(size)] for _ in range(size)]

def placeDown(word : str, i : int, j: int, board : list[list[str]]):
    """ 
    returns function to undo the placement
    raises Value error if word cannot be placed in given position
    """
    if i > len(board) - len(word):
        raise ValueError
    
    replacedString = ""
    for placement in range(i, i+len(word)):
        if board[placement][j] not in (' ', word[placement-i]):
            raise ValueError
        else:
            replacedString += board[i][placement]
    
    for placement in range(i, i+len(word)):
        board[placement][j] = word[placement-i]
    
    def undo():
        for placement in range(i, i+len(word)):
            board[placement][j] = replacedString[placement-i]

    return undo


def placeRight(word : str, i : int, j: int, board : list[list[str]]):
    """ 
    TODO reduce all the shared code with the above method
    returns function to undo the placement
    raises Value error if word cannot be placed in given position
    """
    if j > len(board) - len(word):
        raise ValueError
    
    replacedString = ""
    for placement in range(j, j+len(word)):
        if board[i][placement] not in (' ', word[placement-j]):
            raise ValueError
        else:
            replacedString += board[i][placement-j]
    
    for placement in range(j, j+len(word)):
        board[i][placement] = word[placement-j]
    
    def undo():
        for placement in range(j, j+len(word)):
            board[i][placement] = replacedString[placement-j]

    return undo

Word = namedtuple('Word', 'word i j isRight')

def fillWords(board: list[list[str]], words : list[str]) -> list[Word]:
    if not words:
        print(board)
        return []
    word = random.choice(words)
    words.remove(word)
    randomI = list(range(len(board)))
    randomJ = list(range(len(board)))
    random.shuffle(randomI)
    random.shuffle(randomJ)
    for i, j in itertools.product(randomI, randomJ):
        placementOptions = [placeDown, placeRight]
        random.shuffle(placementOptions)
        for placeWord in placementOptions:  # either place left or down
            try:
                undo = placeWord(word, i, j, board)
            except ValueError:
                continue  # if placement fails, try the next option
            
            try:
                s = fillWords(board, words) + [Word(word, i, j, placeWord is placeRight)]
                print(s)
                return s 
            except ValueError:
                undo()  # undo the placement and try next option
    
    raise ValueError(f"board cannot be filled with the given words")

def fillLooseLetters(board):
    it = range(len(board))
    for i, j in itertools.product(it, it):
        if board[i][j] == ' ':
            board[i][j] = random.choice(letters)


def generateWordSearch():
    print("> generating empty board")
    board = generateBoard(10**4)
    print("> generating words")
    words = generateWords(10**6)
    print("> placing words")
    solution = fillWords(board, words)
    print("> populating letters")
    fillLooseLetters(board)
    return board, solution


board, solution = generateWordSearch()
print(board)