# coach

## Roster creation
The `util/coach.py` script is used for creating rosters for baseball games, taking into things like:
 * Making sure no player plays in the outfield two innings in a row, even across games.
 * Making sure players play each position equally.
 * Making sure to not place players in positions where they absolutely cannot be placed (ie. catcher or first base typically)
 
## Batting order optimization
The util/simulate_order.py script is used to find the optimal batting order in situations where there are run limits per inning. If there is a two-run limit in the first inning, for example, you do not want to do a typical order where you best batters start at the top. If you do this, a clean-up hitter might bat in 4 runs but only 1-2 score anyways on the play as the run limit is reached. The script takes into account a player's on base percentage.
evaluate_order.pyx uses Cython to speed things up.

I eventually re-wrote this in Rust (source code can be found here: https://github.com/dgrant/rust/blob/master/batting_order_simulation/src/main.rs)

## Django app
Ther rest of the folders are for the Django app, this is intended to replace the CSV input that is used for the two scripts above. This is still in progress.
