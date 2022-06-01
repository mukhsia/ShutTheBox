from game import Game, rollProb
import math
import copy
import random


class SimulationNode:
    def __init__(self, game, parent, nodeType):
        self.state = game
        self.parent = parent
        self.nodeType = nodeType
        self.children = []
        self.maxScore = parent.maxScore if parent else game.getScore()
        self.games = 0
        self.average = 0

    def hasChildren(self):
        return len(self.children) > 0

    def getExplorationValue(self, c):
        #If node hasn't been simulated, we want to simulate. Also addressed division by 0 issue
        if self.games == 0:
            return 1000000
        else:
            return (self.maxScore - self.average)/self.maxScore + c * math.sqrt(math.log(self.parent.games)/self.games)

    def chooseChild(self, c):
        pass

    def generateChildren(self):
        pass

    def findDepth(self):
        if len(self.children) == 0:
            return 0
        else:
            max = 0
            for child in self.children:
                depth = child.findDepth()
                if depth > max:
                    max = depth
            return max+1


class RoundStartNode(SimulationNode):
    def __init__(self, game, parent):
        SimulationNode.__init__(self, game, parent, "ROUND_START_NODE")
        if self.parent:
            self.set = set(parent.state.tiles) - set(game.tiles)
        else:
            self.set = game.tiles

    def __deepcopy__(self, memodict={}):
        copy_node = RoundStartNode(self.state, self.parent)
        copy_node.state = copy.deepcopy(self.state)
        copy_node.parent = self.parent
        copy_node.nodeType = self.nodeType
        copy_node.maxScore = self.maxScore
        copy_node.games = self.games
        copy_node.average = self.average
        copy_node.set = self.set

        for child in self.children:
            child_copy = child.__deepcopy__(self, None)
            copy_node.children.append(child_copy)

        return copy_node

    def generateChildren(self):
        if len(self.children) == 0:
            self.children.append(PreRollNode(self.state, self, 2))
            if self.state.maxTileRemaining() <= 6:
                self.children.append(PreRollNode(self.state, self, 1))

    def chooseChild(self, c):
        #Chose child based on exploration value
        return max(self.children, key = lambda childNode: childNode.getExplorationValue(c))



class PreRollNode(SimulationNode):
    def __init__(self, game, parent, diceToRoll):
        SimulationNode.__init__(self, game, parent, "PRE_ROLL_NODE")
        self.dice = diceToRoll

    def __deepcopy__(self, parent, memodict={}):
        copy_node = PreRollNode(self.state, parent, self.dice)
        copy_node.state = copy.deepcopy(self.state)
        copy_node.parent = self.parent
        copy_node.nodeType = self.nodeType
        copy_node.maxScore = self.maxScore
        copy_node.games = self.games
        copy_node.average = self.average
        copy_node.dice = self.dice

        for child in self.children:
            child_copy = child.__deepcopy__(self, None)
            copy_node.children.append(child_copy)

        return copy_node

    def generateChildren(self):
        if len(self.children) == 0:
            for i in range(self.dice, 6*self.dice+1):
                self.children.append(PostRollNode(self.state, self, i))

    def chooseChild(self, c):
        #Chose randomly based on die roll to simulate realistic scenario
        rollValue = 0
        for i in range(self.dice):
            rollValue = rollValue + random.randint(1,6)
        for child in self.children:
            if child.roll == rollValue:
                return child

            

class PostRollNode(SimulationNode):
    def __init__(self, game, parent, rollValue):
        SimulationNode.__init__(self, game, parent, "POST_ROLL_NODE")
        self.roll = rollValue

    def __deepcopy__(self, parent, memodict={}):
        copy_node = PostRollNode(self.state, self.parent, self.roll)
        copy_node.state = copy.deepcopy(self.state)
        copy_node.parent = self.parent
        copy_node.nodeType = self.nodeType
        copy_node.maxScore = self.maxScore
        copy_node.games = self.games
        copy_node.average = self.average
        copy_node.roll = self.roll

        for child in self.children:
            child_copy = child.__deepcopy__(self, None)
            copy_node.children.append(child_copy)

        return copy_node

    def generateChildren(self):
        if len(self.children) == 0:
            validCombos = self.state.validCombos(self.roll)
            for combo in validCombos:
                newState = copy.deepcopy(self.state)
                newState.playCombo(combo)
                self.children.append(RoundStartNode(newState, self))

    def chooseChild(self, c):
        self.generateChildren()
        #If no children generated, this is terminal state
        if (len(self.children) == 0):
            return self
        #Otherwise chose child based on exploration value
        else:
            return max(self.children, key = lambda childNode: childNode.getExplorationValue(c))



class MonteCarlo:
    def __init__(self, game, simulationRounds):
        self.maxRounds = simulationRounds
        self.state = game
        self.rootNode = RoundStartNode(game, None)

    def __updateRoot__(self, newRoot):
        self.rootNode = newRoot
        self.state = newRoot.state

    def __simulateRound__(self, startNode):
        currentNode = copy.deepcopy(startNode)
        while currentNode:
            if currentNode.nodeType == "ROUND_START_NODE":
                #Check if all tiles shut - if so return optimal score of 0
                if currentNode.state.getScore() == 0:
                    return 0
                #Otherwise, decide dice to roll (must be 2 if 7,8, or 9 tile remaining, random otherwise)
                elif currentNode.state.maxTileRemaining() > 6:
                    currentNode = PreRollNode(currentNode.state, currentNode, 2)
                else:
                    diceToRoll = random.randint(1,2)
                    currentNode = PreRollNode(currentNode.state, currentNode, diceToRoll)
            elif currentNode.nodeType == "PRE_ROLL_NODE":
                #Do a random roll
                diceRoll = random.randint(currentNode.dice, 6*currentNode.dice)
                currentNode = PostRollNode(currentNode.state, currentNode, diceRoll)
            elif currentNode.nodeType == "POST_ROLL_NODE":
                validCombos = currentNode.state.validCombos(currentNode.roll)
                #Check valid combos - if none, game is over and return score. Otherwise, make random move from valid combos
                if len(validCombos) == 0:
                    return currentNode.state.getScore()
                else:
                    nextCombo = random.choice(validCombos)
                    currentNode.state.playCombo(nextCombo)
                    currentNode = RoundStartNode(currentNode.state, currentNode)
            else:
                #This shouldn't happen, but return board score otherwise
                return currentNode.state.getScore()

    def __updateScores__(self, node, score):
        while node:
            node.average = (node.average*node.games+score)/(node.games+1)
            node.games = node.games + 1
            node = node.parent

    def simulate(self, rounds, c):
        print("Simulating {} rounds...".format(rounds))
        for i in range(rounds):
            #print("Root count: {} av: {}".format(self.rootNode.games, self.rootNode.average))
            currentNode = self.rootNode
            #Use exploration value to search for optimal leaf
            while currentNode.hasChildren():
                currentNode = currentNode.chooseChild(c)
            ##Once leaf found, do simulation and propogate score if node isn't a win
            if currentNode.state.getScore() == 0:
                continue
            currentNode.generateChildren()
            """for subNode in currentNode.children:
                simulatedScore = self.__simulateRound__(subNode)
                self.__updateScores__(subNode, simulatedScore)"""
            childToSimulate = currentNode.chooseChild(c)
            simulatedScore = self.__simulateRound__(childToSimulate)
            self.__updateScores__(childToSimulate, simulatedScore)

    def updateDiceChoice(self, diceToRoll):
        if self.rootNode.nodeType == "ROUND_START_NODE":
            for subNode in self.rootNode.children:
                if subNode.dice == diceToRoll:
                    self.__updateRoot__(subNode)
                    return
            #If choice was never expanded, create child nodes and update
            self.rootNode.generateChildren()
            updateDiceChoice(newState)
        else:
            print("Root is not RoundStartNode to handle dice choice")

    
    def updateRollValue(self, rollValue):
        if self.rootNode.nodeType == "PRE_ROLL_NODE":
            for subNode in self.rootNode.children:
                if subNode.roll == rollValue:
                    self.__updateRoot__(subNode)
                    return
            #If choice was never expanded, create child nodes and update
            self.rootNode.generateChildren()
            updateRollValue(newState)
        else:
            print("Root is not PreRollNode to handle roll")
    
    def updateTileChoice(self, newState):
        if self.rootNode.nodeType == "POST_ROLL_NODE":
            for subNode in self.rootNode.children:
                if subNode.state.tiles == subNode.state.tiles:
                    self.__updateRoot__(subNode)
            #If choice was never expanded, create child nodes and update
            self.rootNode.generateChildren()
            updateTileChoice(newState)
        else:
            print("Root is not PostRollNode to handle tile choice")

    def rollDecision(self):
        if self.rootNode.nodeType != "ROUND_START_NODE":
            print("State is not prepared for a roll")
        else:
            choice = min(self.rootNode.children, key = lambda child: child.average)
            self.__updateRoot__(choice)
            return choice.dice
    
    def tileDecision(self, roll):
        if self.rootNode.nodeType != "PRE_ROLL_NODE":
            print("State is not prepared for a tile choice")
        else:
            #Adjust to roll, then make choice
            self.updateRollValue(roll)
            if len(self.rootNode.state.validCombos(roll)) == 0:
                return None
            elif len(self.rootNode.children) == 0:
                print(self.rootNode.state.tiles)
                print(self.rootNode.children)
                self.rootNode.generateChildren()
                choice = random.choice(self.rootNode.children)
                self.__updateRoot__(choice)
                return choice.set
            else:
                choice = min(self.rootNode.children, key = lambda child: child.average)
                self.__updateRoot__(choice)
                return choice.set
            

if __name__ == '__main__':
    mc = MonteCarlo(Game(2, 9), 2000)
    c = 1
    mc.simulate(200, c)
    while(mc.state.getScore() > 0):
        print("Score: {}\t Tiles:{}".format(mc.state.getScore(), mc.state.tiles))
        mc.simulate(200, c)
        #ROUND_START_STATE node
        diceUsed = mc.rollDecision()
        print(mc.rootNode.games)
        #PRE_ROLL_STATE node
        roll = mc.state.rollDice(diceUsed)
        tilesToShut = mc.tileDecision(roll)
        print(mc.rootNode.games)
        print("Roll: {}\t Shutting: {}".format(roll, tilesToShut))
        #Adjust c to less exploration and more exploitation as we get deeper
        c = c/2
        if tilesToShut == None:
            break
    print("Score: {}\t Tiles:{}".format(mc.state.getScore(), mc.state.tiles))


    