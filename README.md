# Camel Up Solver
Gives the best option to play for a given camel board

## Strategies
In each round a player has the option to do one of the following:
1. Choose available bet
2. Choose ally
3. Place tile
4. Roll dice (+1)
5. Bet on overall winner (TODO)
6. Bet on overall loser (TODO)

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

If you were to bet, the best bet is choosing yellow, which has an expected value of 2.


### 2. Choose ally
Look at who's still free to ally with. Calculate the expected value of the return of each of their existing bets. Pick the ally with the maximum expected bet value across that persons' existing bets.
For example, using the probabilities above, consider the situation:

|          | Me     | Player 1 | Player 2 | Player3 |
| -------- | ------ |  ------- |  ------- |  -------   |
| Status   | N/A    |  avail   |   avail  |  not avail |
| Bets     | N/A    | R:5      | B: 5     |  N/A |
| Expected Valuve | N/A |

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
