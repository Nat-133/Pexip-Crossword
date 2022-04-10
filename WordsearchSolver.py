import math
import itertools
from dataclasses import dataclass
import threading

@dataclass
class Location:
    """
    represents the location of a string in the string representation of a grid 
    """
    index : int
    offset : int  # how far apart the chars are (either 1 or the row size)

class WordSearch:
    def __init__(self, grid):
        self.ROW_LENGTH = int(math.sqrt(len(grid)))
        self.stringGrid = grid
        self._grid = None
        self._rotatedGrid = None

        self.stringHashLength = 6
        self._letterLookup = None
        self.stringLookup = self.generateStringLookup()
    
    def generateStringLookup(self) -> dict[str, list[Location]]:
        _stringLookup = {}
        def addSubstrings(length):
            # adds all substrings of <length> from the grid to _stringLookup
            for i, c in enumerate(self.stringGrid):
                if length == 1:
                    # special case, when length=1, just don't add the down version.
                    try:
                        _stringLookup[c].append(Location(i, 1))
                    except KeyError:
                        _stringLookup[c] = [Location(i, 1)]
                    continue

                maxRightLength = min(self.stringHashLength, self.ROW_LENGTH - i%self.ROW_LENGTH)
                rightString = self.stringGrid[i:i+length]

                maxDownLength = min(self.stringHashLength, self.ROW_LENGTH - i//self.ROW_LENGTH)
                downString = self.stringGrid[i : i+length*self.ROW_LENGTH : self.ROW_LENGTH]

                keyValuePairs = []
                if length <= maxRightLength:
                    keyValuePairs += [(rightString, Location(i, 1))]
                if length <= maxDownLength:
                    keyValuePairs += [(downString, Location(i, self.ROW_LENGTH))]

                for s, location in keyValuePairs:
                    try:
                        _stringLookup[s].append(location)
                    except KeyError:
                        _stringLookup[s] = [location]
        
        threads = []
        # starts a thread for each substring length 
        # this removes the need for the shared dictionary elements to be protected with mutexes.
        # each thread has a mutually exclusive set of substrings.
        for i in range(1, self.stringHashLength+1):
            t = threading.Thread(target=addSubstrings, args=(i,))
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()
        return _stringLookup

    def is_present(self, word):
        return self.statisticallyFasterLookup(word)

    def statisticallyFasterLookup(self, word):
        """
        hashes all substrings in the grid with len <= self.stringHashLen
        uses that to cut down the number of checks needed
        optimised the stringHashlen with equasion:
            operations ~ 10^6 (10^8 / 25*26^(n-1)) + (2n-1) * 10^8
        haven't experimentally tested the speed, but generally,
        the slower finding a word is, the longer the hashLength should be
        """
        try:
            substring = word[:self.stringHashLength]
        except IndexError:
            substring = word  # if the string's length is less than hash length
        
        try:
            locations = self.stringLookup[substring]
        except KeyError:
            return False  # if the substring isn't in the dict, the word isn't there
        
        for location in locations:
            index = location.index
            offset = location.offset  
            # offset is how far apart the chars are in the word
            # will either be 1 for right, or ROW_LENGTH for down

            checkStart = index + len(substring)*offset
            checkEnd = index + len(word)*offset

            
            if offset == 1:
                # checks to make sure the word isn't wrapping around
                canFitRight = (index % self.ROW_LENGTH + len(word)) <= self.ROW_LENGTH
                if not canFitRight:
                    continue
            else:
                # checks to make sure the checkEnd is on the grid
                canFitDown = checkEnd <= len(self.stringGrid)
                if not canFitDown:
                    continue

            # the bits of the word that aren't covered by the hash lookup
            wordchars = word[len(substring):]
            gridchars = self.stringGrid[checkStart : checkEnd : offset]
            
            if wordchars == gridchars:
                return True
        return False 
    

    # below are my original attempts to solve the problem and their helper methods
    @property
    def rotatedGrid(self) -> list[str]:
        """ 
        A list of all the columns
        initialised when first referenced
        Only used in the bruteforce search 
        """
        
        if not self._rotatedGrid:
            self._rotatedGrid = [self.stringGrid[i::self.ROW_LENGTH] for i in range(self.ROW_LENGTH)]
        return self._rotatedGrid
    
    @property
    def grid(self) -> list[str]:
        """ 
        A list of all the rows
        initialised when first referenced
        Only used in the bruteforce search 
        """
        if not self._grid:
            self._grid = [self.stringGrid[i*self.ROW_LENGTH:(i+1)*self.ROW_LENGTH] 
                          for i in range(self.ROW_LENGTH)]
        return self._grid
    
    @property
    def letterLookup(self) -> dict[str, list[int]]:
        """
        a dictionary that matches letters to a list of indexes where the letter appears
        initialised when first referenced
        """
        if not self._letterLookup:
            self._letterLookup = {}
            for i,c in enumerate(self.stringGrid):
                try:
                    self._letterLookup[c].append(i)
                except KeyError:
                    self._letterLookup[c] = [i]

        return self._letterLookup

    def bruteforceCheck(self, word):
        """ it checks each letter in the grid twice """
        for option in itertools.chain(self.grid, self.rotatedGrid):
            if word in option:
                return True
        return False
    
    def lookupCheck(self, word):
        """ 
        only checks the correct starting characters, 
        so on average, should take 1/26 of the time of bruteforce method 
        (assuming uniform letter distribution)
        """
        for index in self.letterLookup[word[0]]:
            placementOptions = []
            maxDownIndex = index + len(word)*self.ROW_LENGTH
            maxRightIndex = index + len(word)

            canFitRight = (index % self.ROW_LENGTH + len(word)) > self.ROW_LENGTH
            placementOptions += [range(index, maxRightIndex)] if canFitRight else [] 

            canFitDown = maxDownIndex <= len(self.stringGrid)
            placementOptions += [range(index, maxDownIndex, self.ROW_LENGTH)] if canFitDown else []

            for placement in placementOptions:
                for wordi, boardi in enumerate(placement):
                    if self.stringGrid[boardi] != word[wordi]:
                        break
                else:
                    return True
        return False



    

if __name__ == "__main__":
    import WordsearchCreation
    import time

    wordsearches = WordsearchCreation.getWordsearches()
    grid = wordsearches[0][1]
    words = [w[0] for w in wordsearches[0][2]]
    ws = WordSearch(grid)
    print("initialised")
    start = time.time()
    check1 = all(ws.is_present(word) for word in words)
    end = time.time()
    print(f"finding ran in {end-start}s")

    randomWords = WordsearchCreation.generateWords(1000)
    randomWords = [word for word in randomWords if word not in "".join(words)]
    check2 = all(not ws.is_present(word) for word in randomWords)

    check3 = all(ws.is_present(word) == ws.bruteforceCheck(word) for word in itertools.chain(randomWords, words))
    print(f"all words found: {check1}")
    print(f"no false words found: {check2}")
    print(f"same as bruteforce: {check3}")