# Python scripts from the CS541 Artificial Intelligence final project
This was the version that I last saved before the final deliverables version is lost to me. 
The final deliverables which includes the project proposal and project paper was saved in a google drive used by the group;
Access to the Google Drive was lost due to expiration of student account email addresses.
There was no organization/ group repository as the group was experimenting with using an online Python collaboration tool that had Google Drive integration.

The project is to pursue a Machine-Learning related research project in a small group of 3-5 people. 
The group decided to measure effectiveness of some AI/ ML algorithms to 'solve' a problem.
The problem chosen is the dice game Shut The Box.
The algorithms chosen were:
- minimax
- Monte Carlo Tree Search
- Q-Learning

montecarlo.py was programmed by my friend from university [Lane Barton](https://github.com/lbiv4).
I programmed ShutTheBox_QLearning.py, experiment.py, and made changes to montecarlo.py in montecarlo_deepcopy_opt.py.
game.py and minimax.py was programmed by other group members.

## experiment.py
Program written to run the experiment using the Monte Carlo Tree Search and Minimax based programs.
Adds the function to set the number of experiment iterations and to use multiprocessing to attempt to speed up the Monte Carlo Tree Search and Minimax experiment.
profilehooks was used to get timing info (and performance) for functions which led to the MTCS program version which optimized recursive init copy calls to a faster deep-copying process.
Final version included an option to call the Q-Learning program.

## montecarlo_deepcopy_opt.py
Modified montecarlo.py program with deepcopy functions implemented to cut down experiment time which was in exponential time to linear time.

## ShutTheBox_QLearning.py
Based on https://en.wikipedia.org/wiki/Q-learning
Runs 100,000 game simulations as training and 10,000 game simulations as "real" testing.