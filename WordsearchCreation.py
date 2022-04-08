import random
from string import ascii_lowercase as letters
import itertools
from collections import namedtuple
import time
import json

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
    words.sort(key= lambda x: -len(x))
    solution = []
    undoStack = []
    while words:
        word = words[0]
        for _ in range(10):
            i = random.randrange(len(board))
            j = random.randrange(len(board))
            placeWord = random.choice([placeDown, placeRight])
            try:
                undo = placeWord(word, i, j, board)
            except ValueError:
                continue
            
            undoStack.append(placeWord)
            solution.append(Word(word, i, j, placeWord is placeRight))
            words.remove(word)
            break
        else:
            oldWord = solution.pop()
            words.insert(oldWord.word,0)
            undo = undoStack.pop()
            undo()

    return solution

def fillLooseLetters(board):
    it = range(len(board))
    for i, j in itertools.product(it, it):
        if board[i][j] == ' ':
            board[i][j] = random.choice(letters)

def flattenBoard(board : list[list[str]]) -> str:
    return ''.join([''.join(row) for row in board])

def storeWordsearch(boardString : str, size : int, solution : list[Word]) -> None:
    with open("wordsearches.txt", "a") as f:
        solutionDump = json.dumps(solution, separators=(',',':'))
        f.write(f"{size}\n")
        f.write(f"{boardString}\n")
        f.write(f"{solutionDump}\n\n")

def getWordsearches() -> list[tuple[int, str, list[Word]]]:
    with open("wordsearches.txt", "r") as f:
        raw = f.read()
    rawSearches = raw.split("\n\n")[:-1]
    rawData = [search.split("\n") for search in rawSearches]
    searches = [(int(s[0]), s[1], json.loads(s[2])) for s in rawData]
    # searches is list of (size, wordsearch, solution) tuples
    return searches

def generateWordSearch():
    print("> generating empty board")
    board = generateBoard(100)
    print("> generating words")
    words = generateWords(100)
    print("> placing words")
    start = time.time()
    solution = fillWords(board, words)
    duration = time.time()-start
    placedWordCount = len(solution)
    print("> populating letters")
    fillLooseLetters(board)
    
    boardString = flattenBoard(board)
    storeWordsearch(boardString, len(board), solution)
    return boardString, solution

if __name__ == "__main__":
    getWordsearches()
    board, solution = generateWordSearch()
    print(board)