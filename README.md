# Camel Up Solver
Gives the best option to play for a given camel board. <br>
During any given round, 5/6 dice are rolled, and each die can come up 1/2/3. Thus, the number of possible ways a round could go are 6!*3^5 = 174690. Additionally, because the grey die can come up black or white, the total possible ways a round could go is 320760.

## Strategies
In each round a player has the option to do one of the following:
1. Choose available bet
2. Choose ally
3. Place tile
4. Roll dice (+1)
5. Bet on overall winner (TODO)
6. Bet on overall loser (TODO)

A player should select the move that maximizes the expected value.

### 1. Choose available bet
Based on available bets and probabilities of each camel coming in first, second, or not first or second, calculate the expected value of placing a new bet. Pick the bet with highest expected value.

For example, consider the following situation:
|          | Red     | Yellow | Blue | Green | Purple |
| -------- | ------- |  ------- |  ------- |  ------- |  ------- |
| P(1st place)          |  .4  |  .3  | .2   |  .1  |   0  |
| P(2nd place)          |  .1  |  .6  | .2   |  .1  |   0  |
| P(not 1st/2nd place)  |  .5  |  .1  | .6   |  .8  |   1  |
| Available bet         |   3  |   5  |  3   |   5  |   5  |
| Expected value        |  `(.4*3)+.1+(.5*-1)`<br>.8  | `(.3*5)+.6+(.1*-1)`<br>2 | `(.2*3)+.2+.6*-1`<br>.2  | `(.1*5)+.1+(.8*-1)`<br>-.2  |  `(0*5)+0+(1*-1)`<br>-1  |

If you were to bet, the best bet is to choose yellow, which has an expected value of 2.


### 2. Choose ally
Look at who's still free to ally with. Calculate the expected value of the return of each of their existing bets. Pick the ally with the maximum expected value.
For example, using the probabilities above, consider the situation:

|          | Me     | Player 1 | Player 2 | Player3 |
| -------- | ------ |  ------- |  ------- |  -------   |
| Status   | N/A    | avail   |  avail  |  not avail |
| Bets     | N/A    | R:5     | B: 5    |  N/A |
| Expected Value | N/A | `(.4*5)+.1+(.5*-1)`<br>1.6 | `(.2*5)+.2+.6*-1`<br>.6 | N/A |

If you were to ally, the best ally is Player 1, which has an expected value of 1.6

### 3. Place the booster
This one's a little more interesting. The value in placing a booster lies in the expected numer of times a camel lands on that booster during the round, and the change in expected value of your existing bets were you to place a booster. This applies to the global winner and loser.
<br> Calculating the payout is easy - based on the average number of landings per tile, you can calculate the expected value of the payout.
<br> Calculating the change in expected value of your existing bets is harder - you would need to recalculate the probability of winning for every possible booster placement. If there are n possible placements, and you can place +1 or -1, then the number of calculations you would have to run is: 2*n*320760!
<br> In practice, the following heuristic is used:
1. Choose the tile placement that maximizes the expected payout, call this value x.
2. Calculate the change in value of your existing bets if you were to place the tile that location. Take the sum of these changes in value, call this y.
3. Return x + y

### 4. Roll dice
This always has an expected value of 1.



## Development Notes
### Round simulation code
320760 iterations
- first attempt, lists to store tiles: 20907.40it/s + 20913.29it/s + 22610.74it/s
- second attempt, lists + caching: 32674.42it/s + 33418.31it/s + 33383.27it/s
- third attempt, arrays + cache: 83228.85it/s + 82605.14it/s 81834.17it/s



Y G
RPB          WX
----------------
correct:
first: [0.07398054620276842, 0.25419316623020327, 0.13835889761815687, 0.39801409153261, 0.1354532984162614]
second: [0.10978925052999126, 0.15208567153011598, 0.29945753834642724, 0.2764029180695847, 0.16226462152388077]

RED, YEllow, blue, green, purple
0.40963337, 0.06518893, 0.19502743, 0.02658686, 0.30356341,
0
512
34

0
51
342

0
0
51
3
42
