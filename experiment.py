from game import Game, rollProb
from minimax import Minimax
import ShutTheBox_QLearning as qlearn
import montecarlo as mcts
import argparse
import numpy as np
import psutil           # For getting number of CPUs
from multiprocessing import Pool
from profilehooks import profile, timecall # For timing info
from statistics import mean, pstdev

# Experiment config variables
CPU_NUM = psutil.cpu_count(logical=False)
MCTS_ROUNDS = 1000 # Rounds of each mcts simulation
MINIMAX_MAXDEPTH = 10 # Maxdepth of the mini(max)-mizing search

# @profile
@timecall(immediate=True)
def mcts_multiproc(n):
    results = None
    with Pool(CPU_NUM) as pool:
        results = pool.starmap(mcts_experiment, np.repeat([(1, MCTS_ROUNDS, MCTS_ROUNDS*10)], n, axis=0))
    return results

@profile(immediate=True)
# @timecall(immediate=True)
def mcts_seq(n):
    results = []
    for _ in range(n):
        results.append(mcts_experiment(1, MCTS_ROUNDS, MCTS_ROUNDS*10))
    return results

# @profile
@timecall(immediate=True)
def minimax_multiproc(n):
    with Pool(CPU_NUM) as pool:
        results = pool.map(minimax_experiment, np.repeat(MINIMAX_MAXDEPTH, n))
    return results

@profile(immediate=True)
def minimax_seq(n):
    results = []
    for _ in range(n):
        results.append(minimax_experiment(MINIMAX_MAXDEPTH))
    return results

def display_results(results):
    if None == results:
        print("results is None somehow")
    else:
        print("Results:")
        [print(f"{i+1}: Score: {result[0]}; Tiles: {result[1]}") for i, result in enumerate(results)]
        #[print(f"{i+1}: Score: {result[0]}; Tiles: {result[1]}") for i, result in enumerate(results)]
        scores = list(map(lambda r: r[0],results))
        wins = len(list(filter(lambda score: score == 0, scores)))
        print("Av: {}\tStdDv: {} Win%: {}".format(mean(scores), pstdev(scores), wins/len(scores)))

def mcts_experiment(c, n, max_iter):
    mc = mcts.MonteCarlo(Game(2, 9), max_iter)
    mc.simulate(n, c)
    while(mc.state.getScore() > 0):
        print("Score: {}\t Tiles:{}".format(mc.state.getScore(), mc.state.tiles))
        mc.simulate(n, c)
        #ROUND_START_STATE node
        diceUsed = mc.rollDecision()
        print(mc.rootNode.games)
        #PRE_ROLL_STATE node
        roll = mc.state.rollDice(diceUsed)
        tilesToShut = mc.tileDecision(roll)
        print(mc.rootNode.games)
        #Adjust c to less exploration and more exploitation as we get deeper
        c = c/2
        if None == tilesToShut:
            break
    return [mc.state.getScore(), mc.state.tiles]

def minimax_experiment(maxdepth):
    game = Game(2, 9)
    minimax = Minimax(2, maxdepth)
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
    return [game.getScore(), game.tiles]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform experiments with Shut Box solution searching algorithms; Optionally prints graphs", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "algorithm_type", 
        type=str, 
        choices=["mcts","minimax","qlearn"],
        help="Algorithm type of the experiment to run"
    )
    parser.add_argument(
        "--iteration",
        type=int,
        default=200,
        help="Number of iterations of the experiment"
    )

    parser.add_argument(
        "--multiproc",
        type=str,
        choices=["on","off"],
        default="off",
        help="Use multiprocessing to attempt to speed up experiment (mcts, minimax)."
    )

    parser.add_argument(
        "--drawgraph",
        type=str,
        choices=["on","off"],
        default="off",
        help="Additionally calls any graph plotting/ saving functions if available"
    )
    
    args = parser.parse_args()
    results = None
    n = args.iteration
    if "mcts" == args.algorithm_type:
        if "on" == args.multiproc:
            results = mcts_multiproc(n)
        else:
            results = mcts_seq(n)
        display_results(results)
    elif "minimax" == args.algorithm_type:
        if "on" == args.multiproc:
            results = minimax_multiproc(n)
        else:
            results = minimax_seq(n)
        display_results(results)        
    elif "qlearn" == args.algorithm_type:
        qlearn.main()


