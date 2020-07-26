def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).
    
  I used the following features in this model:
  - distance to the closest active ghost (active ghosts are non-scared ghosts)
  - current score in the game
  - distance to the closest scared ghost
  - number of capsules left
  - number of foods left
  - distance to the closest food

  My evaluation function computes a linear combination of 
  these features (or related features, since in some cases, I take
  the inverse of a feature)

  I kept the current score the same, because I saw no reason to modify it.

  I multiply the distance to the closest food by -1.5. This means that the 
  larger the distance pac-man has to the closest food, the more negative the
  score is.

  I take the inverse of the distance to the closest active ghost, and then 
  multiply it by -2. This means that the larger the distance to the closest
  active ghost, the les negative the score is, but the closer a ghost is, 
  the more negative the score becomes.

  I multiply distance to the closest scared ghost by -2, to motivate pac-man to 
  move towards scared ghosts. This coefficient is larger than the coefficient I
  used for food, even though the distance to the closest scared ghost will
  almost always be greater than the distance to the nearest food. I chose to
  use a larger coefficient here because:
   - pac-man gets a large number of points for eating a scared ghost
   - if the distance to the closest scared ghost is greater than the distance
     to the nearest food, it is usually because there are not many foods left
     on the board. This means that it's likely more beneficial for pac-man to go
     towards the scared ghost, because eating the scared ghost will likely net 
     pac-man more points than eating the remaining foods.

  I multiply the number of capsules left by a very high negative number - -20 - 
  in order to motivate pac-man to eat capsules that he passes. I didn't want
  pac-man to move toward capsules over food or over running away from ghosts, 
  but I DID want pac-man to eat them when he passed by them. When pac-man 
  passes by a capsule, the successor state where pac-man eats a capsule will
  gain +20 points, which is (usually) significant enough that pac-man eats 
  the capsule.

  I also multiply the number of foods left by -4, because pac-man should
  minimize the number of foods that are left on the board. 

  some results: 

  dan at staircar in ~/classes/ai/multiagent on main
  $ python pacman.py -l smallClassic -p ExpectimaxAgent -a evalFn=better -n 10 -q
  Pacman emerges victorious! Score: 1366
  Pacman died! Score: -198
  Pacman emerges victorious! Score: 1367
  Pacman emerges victorious! Score: 1737
  Pacman emerges victorious! Score: 1364
  Pacman emerges victorious! Score: 933
  Pacman emerges victorious! Score: 1743
  Pacman emerges victorious! Score: 1193
  Pacman emerges victorious! Score: 1373
  Pacman emerges victorious! Score: 1348
  Average Score: 1222.6
  Scores:        1366, -198, 1367, 1737, 1364, 933, 1743, 1193, 1373, 1348
  Win Rate:      9/10 (0.90)
    Record:        Win, Loss, Win, Win, Win, Win, Win, Win, Win, Win


  dan at staircar in ~/classes/ai/multiagent on main
  $ python pacman.py -l smallClassic -p ExpectimaxAgent -a evalFn=better -n 10
  Pacman emerges victorious! Score: 1139
  Pacman emerges victorious! Score: 1362
  Pacman emerges victorious! Score: 1770
  Pacman emerges victorious! Score: 1361
  Pacman emerges victorious! Score: 1234
  Pacman emerges victorious! Score: 1521
  Pacman emerges victorious! Score: 1755
  Pacman emerges victorious! Score: 1759
  Pacman emerges victorious! Score: 1759
  Pacman died! Score: 101
  Average Score: 1376.1
  Scores:        1139, 1362, 1770, 1361, 1234, 1521, 1755, 1759, 1759, 101
  Win Rate:      9/10 (0.90)
  Record:        Win, Win, Win, Win, Win, Win, Win, Win, Win, Loss

  ---
  I also experimented with using the actual maze-distance instead of the
  manhattan distance, but that turned out to be mostly useless. 
   
  """
  pos = currentGameState.getPacmanPosition()
  currentScore = scoreEvaluationFunction(currentGameState)

  if currentGameState.isLose(): 
    return -float("inf")
  elif currentGameState.isWin():
    return float("inf")

  # food distance
  foodlist = currentGameState.getFood().asList()
  manhattanDistanceToClosestFood = min(map(lambda x: util.manhattanDistance(pos, x), foodlist))
  distanceToClosestFood = manhattanDistanceToClosestFood

  # number of big dots
  # if we only count the number fo them, he'll only care about
  # them if he has the opportunity to eat one.
  numberOfCapsulesLeft = len(currentGameState.getCapsules())
  
  # number of foods left
  numberOfFoodsLeft = len(foodlist)
  
  # ghost distance

  # active ghosts are ghosts that aren't scared.
  scaredGhosts, activeGhosts = [], []
  for ghost in currentGameState.getGhostStates():
    if not ghost.scaredTimer:
      activeGhosts.append(ghost)
    else: 
      scaredGhosts.append(ghost)

  def getManhattanDistances(ghosts): 
    return map(lambda g: util.manhattanDistance(pos, g.getPosition()), ghosts)

  distanceToClosestActiveGhost = distanceToClosestScaredGhost = 0

  if activeGhosts:
    distanceToClosestActiveGhost = min(getManhattanDistances(activeGhosts))
  else: 
    distanceToClosestActiveGhost = float("inf")
  distanceToClosestActiveGhost = max(distanceToClosestActiveGhost, 5)
    
  if scaredGhosts:
    distanceToClosestScaredGhost = min(getManhattanDistances(scaredGhosts))
  else:
    distanceToClosestScaredGhost = 0 # I don't want it to count if there aren't any scared ghosts

  outputTable = [["dist to closest food", -1.5*distanceToClosestFood], 
                 ["dist to closest active ghost", 2*(1./distanceToClosestActiveGhost)],
                 ["dist to closest scared ghost", 2*distanceToClosestScaredGhost],
                 ["number of capsules left", -3.5*numberOfCapsulesLeft],
                 ["number of total foods left", 2*(1./numberOfFoodsLeft)]]

  score = 1    * currentScore + \
          -1.5 * distanceToClosestFood + \
          -2    * (1./distanceToClosestActiveGhost) + \
          -2    * distanceToClosestScaredGhost + \
          -20 * numberOfCapsulesLeft + \
          -4    * numberOfFoodsLeft
  return score
