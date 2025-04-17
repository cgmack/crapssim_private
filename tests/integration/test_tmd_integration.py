import pytest

from crapssim.bet import Field, Odds, PassLine, Place, Come, DontCome
from crapssim.strategy.examples import IronCross
from crapssim.strategy.tmd import TMD
from crapssim.table import Table, TableUpdate


@pytest.mark.parametrize(
    "point, last_roll, strat_info, bets_before, dice_result, bets_after",
    [
        # HAPPY PATH SETUP, LOAD UP THE TABLE
        (None, None, None, [],                                                                                   None, [PassLine(amount=15.0)]),
        (8,    8,    None, [PassLine(amount=15.0)],                                                              (4,4), [PassLine(amount=15.0), DontCome(amount=60.0, number=None),]),
        (8,    4,    None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4)],                            (2,2), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=None)]),
        (8,    5,    None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5)],(2,3), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=None)]),
        (8,    6,    None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6)],(3,3), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=None)]),
        (8,    8,    None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8)],(4,4), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=None)]),
        (8,    9,    None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9)],(4,5), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=None)]),
        (8,    10,   None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10)],(5,5), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10), Come(amount=15.0, number=None)]),

        # HAPPY PATH, HIT EACH COME BET
        (8,    5,   None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10)],(2,3), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10), Come(amount=15.0, number=None)]),
        (8,    6,   None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10)],(2,4), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10), Come(amount=15.0, number=None)]),
        (8,    7,   None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10)],(3,4), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10), Come(amount=15.0, number=None)]),
        (8,    9,   None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10)],(3,6), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10), Come(amount=15.0, number=None)]),
        (8,    10,  None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10)],(5,5), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10), Come(amount=15.0, number=None)]),

        # HAPPY PATH, HIT THE POINT
        (8,    8,   None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10)],(4,4), [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10), Come(amount=15.0, number=None)]),

        # HAPPY PATH, 7 OUT HITS THE DC
        #(8,    7,   None, [PassLine(amount=15.0), DontCome(amount=60.0, number=4), Come(amount=15.0, number=5), Come(amount=15.0, number=6), Come(amount=15.0, number=8), Come(amount=15.0, number=9), Come(amount=15.0, number=10)],(4,3), [PassLine(amount=15.0)]),        
    ],
)
def test_ironcross_integration(
    point, last_roll, strat_info, bets_before, dice_result, bets_after
):
    table = Table()
    table.add_player(bankroll=float("inf"), strategy=TMD(15,4,5,None,False ))  # base_amount, dc_multiplier, max_loss_progression, odds_multiplier, verbose
    table.point.number = point
    table.last_roll = last_roll
    table.players[0].bets = bets_before
    table.dice.result = dice_result
    TableUpdate().run_strategies(table)
    assert table.players[0].bets == bets_after
