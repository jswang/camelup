# Camel Up Solver
<img src="docs/camel_up.png" width="500"><br>
Want to vanquish your enemies in Camel Up board game? Well look no further, this solver tells you the best move to make for any board config! <br>
So far this solver takes into account:
- Available bets based on players
- Ability to ally
- Boosting +1 or -1

Notably, it's missing:
- When to bet on overall winner
- When to bet on overall loser

May the odds ever be in your favor...especially now that you know the odds.

## Usage instructions
Note that everything is index by 0, this differs from the tiles on the board which are index by 1.

1. Start the game, then enter the game setup. Order matters
```python
python3 main.py --setup {RED: 0, YELLOW: 0, PURPLE: 1, BLUE: 2, GREEN: 2,  WHITE: 13, BLACK: 14}, --id=1, --n-players=2
# Prints
Camel Up!!!

red: tile: 0, stack: 0
yellow: tile: 0, stack: 1
blue: tile: 2, stack: 0
green: tile: 2, stack: 1
purple: tile: 1, stack: 0
white: tile: 13, stack: 0
black: tile: 14, stack: 0

positive boosters: []
negative boosters: []

Players: [Player 0: (points: 3, ally: None, bets: []), Player 1: (points: 3, ally: None, bets: [])]
Available bets: red: 5, yellow: 5, blue: 5, green: 5, purple: 5, white: 5, black: 5,
Winner bets: []
Loser bets: []

Enter Player 0 move:
```

2. Enter the other player's moves
```
bet <color>
ally <player_id>
boost <location> <1/-1>
roll <color> <amount>
winner
loser
print
```
3. When it's your turn to play, the optimal options will be calculate for you, then you enter what you did. It takes ~12s to calculate the optimal move. You'll get a printout like:
```
Calculating optimal move
100%|███████████████████████████████████████| 320760/320760 [00:04<00:00, 70470.56it/s]
100%|███████████████████████████████████████| 320760/320760 [00:04<00:00, 67013.47it/s]
100%|███████████████████████████████████████| 320760/320760 [00:04<00:00, 67704.38it/s]
1.94: Bet green
1.00: Roll dice
0.83: Ally Player 0
0.22: Boost location 3, 1
Enter your move:
```

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
### Optimizations
During any given round, 5/6 dice are rolled, and each die can come up 1/2/3. Thus, the number of possible ways a round could go are 6!*3^5 = 174690. Additionally, because the grey die can come up black or white, the total possible ways a round could go is 320760.
So, to save on calculation time, I added caching and used numpy arrays. These two changes led to a 75% reduction in runtime:

|          | Attempt #1 | Attempt #2 | Attempt #3 | Average | Average time to complete|
| -------- | ------ |  ------- |  ------- |  -------   | --- |
| Lists | 20907.40it/s| 20913.29it/s| 22610.74it/s| 21477 it/s| 15s |
| Lists + caching | 32674.42it/s| 33418.31it/s| 33383.27it/s| 33158 it/s| 9.5s |
| Arrays + caching |  83228.85it/s| 82605.14it/s| 81834.17it/s| 82555 it/s| 3.8s |
