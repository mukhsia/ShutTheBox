import csv
from statistics import mean
from statistics import pstdev
from itertools import combinations
import random

random.seed()


class diceRoll(object):
    def __init__(self):
        self.qvalue = 0
        self.rolls = {}
        self.initRolls()

    def initRolls(self):
        tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        comboStates = []
        for i in range(1, 13):
            roll = i
            choices = {}
            for j in range(1, 10):
                for combo in combinations(tiles, j):
                    if sum(combo) == roll:
                        choices.update({combo: 0})
                    choices.update({(): 0})
            if len(choices) > 0:
                comboStates.append({roll: choices})

        for state in comboStates:
            self.rolls.update(state)


class qtable(object):
    def __init__(self):
        self.rollTable = {}
        self.eta = 0.2
        self.gamma = 0.9
        self.initTables()

    def initTables(self):
        tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        rollStates = []

        for i in range(0, 10):
            combos = combinations(tiles, i)
            for combo in combos:
                rollStates.append(combo)

        # key = Tuple of current tiles
        # value = [1-dice, 2-dice]
        for state in rollStates:
            dice1 = diceRoll()
            dice2 = diceRoll()
            self.rollTable.update({state: [dice1, dice2]})

        # preset final state to high values so it will be preferred during updates
        # no rolls will actually be done once final state is reached
        self.rollTable[()][0].qvalue = 100
        self.rollTable[()][1].qvalue = 100
        for i in range(1, 7):
            for key in self.rollTable[()][0].rolls[i]:
                self.rollTable[()][0].rolls[i][key] = 100

        for i in range(2, 13):
            for key in self.rollTable[()][1].rolls[i]:
                self.rollTable[()][1].rolls[i][key] = 100

    def updateRollTable(self, state1, dice, roll, rollChoice, state2, reward):

        maxAction = 0
        if self.rollTable[state2][0].qvalue > self.rollTable[state2][1].qvalue:
            maxAction = 0
        else:
            maxAction = 1

        maxRoll = 0
        maxRollChoice = ()
        for keys in self.rollTable[state2][maxAction].rolls.keys():
            bestChoice = 0
            for key in self.rollTable[state2][maxAction].rolls[keys].keys():
                if self.rollTable[state2][maxAction].rolls[keys][key] >= bestChoice:
                    bestChoice = self.rollTable[state2][maxAction].rolls[keys][key]
                    maxRollChoice = key
                    maxRoll = keys

        # Update Q-values based on update equation
        if dice == 1:
            self.rollTable[state1][0].qvalue = self.rollTable[state1][0].qvalue + self.eta * (
                    reward + self.gamma * self.rollTable[state2][maxAction].qvalue - self.rollTable[state1][0].qvalue)

            if rollChoice is not -1:
                self.rollTable[state1][0].rolls[roll][rollChoice] = self.rollTable[state1][0].rolls[roll][
                                                                        rollChoice] + self.eta * (
                                                                            reward + self.gamma *
                                                                            self.rollTable[state2][maxAction].rolls[
                                                                                maxRoll][maxRollChoice] -
                                                                            self.rollTable[state1][0].rolls[roll][
                                                                                rollChoice])

        if dice == 2:
            self.rollTable[state1][1].qvalue = self.rollTable[state1][1].qvalue + self.eta * (
                    reward + self.gamma * self.rollTable[state2][maxAction].qvalue - self.rollTable[state1][1].qvalue)
            if rollChoice is not -1:
                self.rollTable[state1][1].rolls[roll][rollChoice] = self.rollTable[state1][1].rolls[roll][
                                                                        rollChoice] + self.eta * (
                                                                            reward + self.gamma *
                                                                            self.rollTable[state2][maxAction].rolls[
                                                                                maxRoll][maxRollChoice] -
                                                                            self.rollTable[state1][1].rolls[roll][
                                                                                rollChoice])

    # return action to take based on epsilon greedy algorithm
    def greedyDice(self, state, epsilon):
        percent = (1 - epsilon) * 100
        if random.randint(1, 100) > percent:
            choices = [1, 2]
            return choices[random.randint(0, 1)]
        else:
            maxAction = 0
            if self.rollTable[state][0].qvalue > self.rollTable[state][1].qvalue:
                maxAction = 1
            else:
                maxAction = 2

            return maxAction

    def greedyCombo(self, roll, dice, state, choices, epsilon):
        percent = (1 - epsilon) * 100
        randomChoice = random.randint(1, 100)
        if randomChoice > percent:
            index = random.randint(0, len(choices) - 1)
            return choices[index]

        # else:
        maxVal = self.rollTable[state][dice - 1].rolls[roll][choices[0]]
        for choice in choices:
            if self.rollTable[state][dice - 1].rolls[roll][choice] >= maxVal:
                maxVal = self.rollTable[state][dice - 1].rolls[roll][choice]
                maxChoice = choice

        return maxChoice


if __name__ == "__main__":
    table = qtable()

    """******************************************************************************************"""
    print("Running Training Episodes ", end='')

    eps = 0.5
    trainingRewards = []

    for N in range(100000):
        gameState = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        gameOver = False

        # decay epsilon
        if N != 0:
            if N % 1000 == 0:
                eps -= 0.005
        if eps < 0:
            eps = 0

        rewardSum = 0
        while not gameOver:
            reward = 0
            state1 = tuple(gameState)

            if any(item in state1 for item in [7, 8, 9]):
                dice = 2
            else:
                dice = table.greedyDice(state1, eps)

            # Roll the dice
            roll = 0
            if dice == 1:
                roll = random.randint(1, 6)
            else:
                roll_1 = random.randint(1, 6)
                roll_2 = random.randint(1, 6)
                roll = roll_1 + roll_2

            choice = ()
            valid = []
            for i in range(len(state1) + 1):
                for combo in combinations(state1, i):
                    if sum(combo) == roll:
                        valid.append(combo)

            if len(valid) == 0:
                # table.updateRollTable(state1, dice, roll, choice, state1, reward)
                gameOver = True
                break

            choice = table.greedyCombo(roll, dice, state1, valid, eps)

            for item in choice:
                gameState.remove(item)
                reward += item
                rewardSum += item

            if len(gameState) == 0:
                reward += 100
                rewardSum += 100
                gameOver = True

            table.updateRollTable(state1, dice, roll, choice, tuple(gameState), reward)

        trainingRewards.append(rewardSum)

        if N % 5000 == 0:
            print(". ", end='')

    print("\n\nTraining-Average: " + str(mean(trainingRewards)))
    print("Training-Standard-Deviation: " + str(pstdev(trainingRewards)))
    winCount = 0
    for reward in trainingRewards:
        if reward == 145:
            winCount += 1
    winPercent = (winCount / 100000) * 100
    print("Training-Wins: %d out of 100,000 games" % winCount)
    print("Training-Win-Percentage: %f" % winPercent)

    storedRewards = []
    for i in range(len(trainingRewards)):
        if i % 1000 == 0:
            storedRewards.append(trainingRewards[i])
    print("Rewards at every 100 runs: " + str(storedRewards) + "\n")
    """******************************************************************************************"""

    """******************************************************************************************"""
    realRewards = []
    print("Running Test Episodes ", end='')

    eps = 0

    for N in range(10000):
        gameState = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        gameOver = False

        rewardSum = 0
        while not gameOver:
            reward = 0
            state1 = tuple(gameState)

            # choose dice unless 7, 8, or 9 tiles are still up
            if any(item in state1 for item in [7, 8, 9]):
                dice = 2
            else:
                dice = table.greedyDice(state1, eps)

            roll = 0
            if dice == 1:
                roll = random.randint(1, 6)
            else:
                roll_1 = random.randint(1, 6)
                roll_2 = random.randint(1, 6)
                roll = roll_1 + roll_2

            choice = ()
            valid = []
            for i in range(len(state1) + 1):
                for combo in combinations(state1, i):
                    if sum(combo) == roll:
                        valid.append(combo)

            if len(valid) == 0:
                gameOver = True
                break

            choice = table.greedyCombo(roll, dice, state1, valid, eps)

            for item in choice:
                gameState.remove(item)
                reward += item
                rewardSum += item

            if len(gameState) == 0:
                reward += 100
                rewardSum += 100
                gameOver = True

        realRewards.append(rewardSum)

        if N % 500 == 0:
            print(". ", end='')

    print("\n\nTest-Average: " + str(mean(realRewards)))
    print("Test-Standard-Deviation: " + str(pstdev(realRewards)))
    winCount = 0
    for reward in realRewards:
        if reward == 145:
            winCount += 1
    winPercent = (winCount / 10000) * 100
    print("Test-Wins: %d out of 10,000 games" % winCount)
    print("Test-Win-Percentage: %f" % winPercent)
    """******************************************************************************************"""

    with open('TrainingRewards.csv', 'w', newline='') as csvfile:
        rewardWriter = csv.writer(csvfile)
        rewardWriter.writerow(trainingRewards)

    with open('RealRewards.csv', 'w', newline='') as csvfile:
        rewardWriter = csv.writer(csvfile)
        rewardWriter.writerow(realRewards)
        rewardWriter.writerow([mean(realRewards)])
        rewardWriter.writerow([pstdev(realRewards)])
