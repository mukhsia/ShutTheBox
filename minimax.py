from game import Game, rollProb
import math
import copy
import random

class Minimax:
    def __init__(self, players, maxDepth=100):
        self.players = players
        self.maxDepth = maxDepth

    def rollDecision(self, boxState):
        # If you have a 7,8,or 9 tiles left you have to roll two dice
        if boxState.maxTileRemaining() > 6:
            return 2
        else:
            return self.__minimaxRoll__(boxState, 1)[0]

    def tileDecision(self, roll, boxState):
        return self.__minimaxTiles__(roll, boxState, 1)[0]

    def __minimaxRoll__(self, boxState, currentDepth):
        """
        Helper function that does expected minimax for a dice roll

        Parameters:
            self (Minimax): Self explanatory
            boxState (Game): Current state of box and which tiles can be shut
            currentDepth (int): Current depth of search, used with self.maxDepth to truncate search

        Returns:
            array: Returns array of length two, with the first value being the optimal number of dice rolled 
                   and the second being the expected value of rolling that many dice
        """
        #If game is over, catch
        if boxState.getScore() == 0:
            return [None, 0]
        values = []
        # If you have a 7,8,or 9 tiles left you have to roll two dice. Otherwise can choose between 1 and 2
        validDiceToRoll = [2] if boxState.maxTileRemaining() > 6 else [1,2]
        for diceRolled in validDiceToRoll:
            expectedValue = 0
            for i in range(diceRolled, 6*diceRolled+1):
                probability = rollProb(diceRolled, i)
                expectedValue = expectedValue + probability*self.__minimaxTiles__(i, boxState, currentDepth)[1]
            values.append([diceRolled,expectedValue])
        return min(values, key = lambda value: value[1])

    def __minimaxTiles__(self, rollValue, boxState, currentDepth):
        """
        Helper function that does minimax for choosing which tiles to select given a roll value

        Parameters:
            self (Minimax): Self explanatory
            rollValue (int): Value of roll to check moves for
            boxState (Game): Current state of box and which tiles can be shut
            currentDepth (int): Current depth of search, used with self.maxDepth to truncate search

        Returns:
            array: Returns array of length two, with the first value being the best set to choose and the second being the best case value
        """
        validCombos = boxState.validCombos(rollValue)
        # If no valid combos, game is over
        if len(validCombos) == 0:
            return [None, boxState.getScore()]
        else:
            values = []
            for set in validCombos:
                nextState = copy.deepcopy(boxState)
                nextState.playCombo(set)
                # If max depth reached, just take score of next state. Otherwise, continue to recurse
                if currentDepth == self.maxDepth:
                    values.append([set, nextState.getScore()])
                else:
                    values.append([set, self.__minimaxRoll__(nextState, currentDepth+1)[1]])
            return min(values, key = lambda value: value[1])

if __name__ == '__main__':
    game = Game(2, 9)
    minimax = Minimax(2, 5)
    while(game.getScore() > 0):
        print("Score: {}\t Tiles:{}".format(game.getScore(), game.tiles))
        diceUsed = minimax.rollDecision(game)
        roll = game.rollDice(diceUsed)
        tilesToShut = minimax.tileDecision(roll, game)
        print("Roll: {}\t Shutting: {}".format(roll, tilesToShut))
        if tilesToShut != None:
            game.playCombo(tilesToShut)
        else:
            break
    print("Final score: {}".format(game.getScore()))






