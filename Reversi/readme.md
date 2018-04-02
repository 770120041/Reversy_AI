## Reversi

#### How to use

Write your own engines using MCTS.

Example:
python reversi.py -a greedy -b random
python reversi.py -a greedy -b random -t 30 -v
python reversi.py -a human -b greedy -t 30



#### Rule

黑白棋（Othello/Reversi）

游戏说明
游戏规则：开局时，棋盘正中央的4格先置放黑白相隔的4枚棋子。通常黑子先行，双方轮流落子。只要落子和棋盘上任一枚己方的棋子在一条线上（横、直、斜线皆可）夹着对方棋子，就能将对方的这些棋子转变为己方（翻面即可）。如果在任一位置落子都不能夹住对手的任一颗棋子，就要让对手下子。当双方皆不能下子时，游戏就结束，子多的一方胜。
时间限制：每个玩家下棋和思考花费的总时间不能超过30分钟。

比赛说明
比赛规则：
1. 单循环赛（每个队与其他所有队伍都进行一场比赛，每两个队仅比赛一场，A与B比赛等同于B与A比赛）；
2. 每场比赛胜利的队伍记1分，失败的队伍不计分，单循环赛结束后按总分进行排名；
3. 每场比赛包括3局游戏，每局游戏胜利的队伍记该方棋子数目为该局得分，失败的队伍不计分，3局比赛后总分最高的该场比赛获胜，若双方总分相等则再加一局；若一方超时则判定本局游戏失败。

重要时间
组队报名时间：4月7日上午8点前
代码提交时间：5月12日上午8点前
报告提交时间：5月14日上午8点前

组队说明
组队人数：最多3人

代码说明
为保证公平性，使用Python语言，在同一台机器（配置：2 CPUs, 6 cores, 24 Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, 128G Mem, Ubuntu 14.04.5 LTS）上运行

报告说明
主要包含内容：
1. 方法介绍及技巧
2. 结果展示及分析
3. 参考及引用

-----
参考链接：
https://en.wikipedia.org/wiki/Reversi
https://www.wikihow.com/Play-Othello
http://www.othelloonline.org/