import random
import itertools

class Game(object):
  def __init__(self, players, numTiles):
    self.players = players
    self.tiles = []
    for i in range(numTiles):
      self.tiles.append(i+1) 
  
  def __deepcopy__(self, memodict={}):
    copy_game =  Game(self.players, 0)
    
    for tile in self.tiles:
      copy_game.tiles.append(tile)

    return copy_game

  def rollDice(self, numDice):
    roll = 0 
    for i in range(numDice):
      roll += random.randint(1, 6)
    #print('Dice roll: ', roll)
    return roll

  def rollCombos(self, roll):
    valid = []
    for i in range(len(self.tiles)+1):
      for combo in itertools.combinations(self.tiles, i):
        if sum(combo) == roll:
          valid.append(combo)
    #print('All roll combinations: ', valid)
    return valid

  def validCombos(self, roll):
    valid = []
    allCombos = self.rollCombos(roll)
    # Check all combos and see if every tile exists in current tiles. If so, it's a valid move
    for combo in allCombos:
      if set(self.tiles).issuperset(set(combo)):
        valid.append(combo)
    return valid

  def playCombo(self, combo):
    for value in combo:
      self.tiles.remove(value)
    #print('tiles remaining: ', self.tiles)
    return self

  def getScore(self):
    return sum(self.tiles)

  def maxTileRemaining(self):
    return max(self.tiles)

def rollProb(diceRolled, desiredValue):
    """
    Method to compute roll probability, formula for 2 dice from WolframAlpha (line 16): https://mathworld.wolfram.com/Dice.html
    """
    if diceRolled == 1:
        return 1/6
    elif diceRolled == 2:
        if desiredValue >= 2 and desiredValue <= 12:
            return (6-abs(desiredValue-7))/36
        else:
            print("Invalid roll value - must be between 2 and 12 for 2 dice")
            return None
    else:
        print("Invalid number of dice - must be 1 or 2")
        return None

if __name__ == '__main__':
  game = Game(2, 9)
  roll = game.rollDice(2)
  combos = game.validCombos(roll)
  game.playCombo(combos)
  
