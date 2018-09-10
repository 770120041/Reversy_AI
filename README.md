# Reversy AI
A MCTS Reversy game AI implemeted by Jiang Wu, Zhe Liu and Wenlong Yan

## Usage 
run 'python reversi.py mcts mcts_eval_book' to compete between engine original mcts and optimized mcts

## Introduction
Our Reversy AI is implemented from the PyGame frame work, and the code in 'engine' folder is developed by us.
I mainly developed the way of how to optimize the initial MCTS algorithm.
We developed three engines at last:
1. The engine developed using original MCTS idea
2. The engine that evalute the importantce of the position in the boards with MCTS engine
3. the eigine that have recorded some playbooks and move a piece using the optimal solution with MCTS engine
4. the engine that combines engine 2 and 3 but have a balance of importance for them

Our AI engine ranked 3rd in the class competition

## Rules
Each player have 30 minutes for the game, thus you have to wait a bit longer in some case
