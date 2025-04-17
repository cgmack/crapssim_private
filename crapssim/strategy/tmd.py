"""The TMD startegy uses a mix of come and don't come bets to balance the upside of 
rolling point numbers and the risk of a 7."""


# Expand the base A0 strategy with a progression. Rework with latest codebase and debug output

from crapssim.table import Player
from crapssim.bet import PassLine, DontPass, Place, Come, DontCome, Odds
from crapssim.strategy.tools import Strategy
from crapssim.strategy.single_bet import BetPassLine, BetCome, BetDontCome, StrategyMode
from crapssim.strategy.odds import PassLineOddsMultiplier, ComeOddsMultiplier, DontComeOddsMultiplier
from crapssim.strategy.tools import AddIfTrue
import typing



class TMD(Strategy):
    """The TMD startegy used a mix of come and don't come bets to balance risk 7 with upside of 
    rolling point numbers. It also uses a progression on DONTCOME loses to chase and recover from losses. 
    The Progression starts at 1 and increases to max of max_loss_progression. Resets to 1 on a DONTCOME win. 
    There is also an option to add odds to PASSLINE, COME, and DONTCOME bets with the odds_multiplier.
    It works like this:
     - Betting starts with a PASSLINE of base_amount * progression. (progression starts at 1)
     - After point is set, a DONTCOME bet of base_amount * dc_multiplier * progression is placed.
     - After the DONTCOME is set on a number, add a COME bet of base_amount * progression.
     - Keep adding COME bets of base_amount * progression until the point or DONTCOME number is rolled.
     - If at any time the point is rolled, place a new PASSLINE bet of base_amount * progression and continue. 
     - If at any time the DONTCOME loses, increase progression by one (up to max of max_loss_progression) and make a new DONTCOME bet of base_amount * dc_multiplier * progression. 
     - If DONTCOME wins, Set progression to 1, make a new DC bet of base_amount * dc_multiplier. 
    """

    def __init__(self, base_amount: float, dc_multiplier: int, max_loss_progression: int, odds_multiplier: dict[int, int] | int | None, verbose: bool):
        """Creates the TMD strategy with all bet amounts being created from the given
        base_amount times the current loss progression up to max_loss_progression. 
        Setting max_loss_progression to 1 disables the progression.
        PASSLINE and COME bets use base_amount*progression. 
        DONTCOME bets use base_amount * dc_multiplier * progression
        ODDS bets use the odds_multiplier, if supplied, to set the odds bet amount.

        Parameters
        ----------
        base_amount
            the base amount for PassLine, Don't Come, and Come Bets
        """
        self.base_amount = float(base_amount)
        self.dc_multiplier = int(dc_multiplier)
        self.max_loss_progression = int(max_loss_progression)
        self.odds_multiplier = odds_multiplier = None # e.g. 3 --OR-- {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3} --OR-- None 
        self.dc_loss_streak: int = 0
        self.verbose= verbose # prints single row sumaries of bets and results
        self.debug = False # prints detailed debug output 

    # def build_bets_and_results_string(player):
        
    #     bets_string = ""
    #     bet_results_string = ""

    #     # Passline Bet
    #     point_string = "-"
    #     if table.point.number:
    #         point_string = str(table.point.number)
    #     pl_bets = player.get_bets_by_type((PassLine))
    #     for b in pl_bets:
    #         # Current Bets Placed
    #         passline_odds_string = ""
    #         passline_odds_result_string = ""
    #         odds_bets = player.get_bets_by_type((Odds))
    #         for ob in odds_bets:
    #             if ob.base_type == PassLine:
    #                 passline_odds_string = "+" + str(round(ob.amount))
    #                 passline_odds_result = ob.get_result(player.table)
    #                 passline_odds_result_string = str(passline_odds_result.amount)
    #         bets_string = bets_string + "PL("+point_string+"):"+str(round(b.amount))+passline_odds_string

    #         # Current Results
    #         bet_result = b.get_result(player.table)
    #         if bet_result.amount > 0:
    #             bet_results_string = bet_results_string + "PL:W" + str(round(bet_result.amount)) + "+" + passline_odds_result_string
    #         elif bet_result.amount < 0:
    #             bet_results_string = bet_results_string + "PL:L" + str(round(bet_result.amount)) + passline_odds_result_string    

    #     # DontPass Bet
    #     dp_bets = player.get_bets_by_type((DontPass))
    #     for b in dp_bets:
    #         bets_string = bets_string + "DP("+point_string+"):"+str(b.amount)
        
    #     # DontCome Bet
    #     dc_bets = player.get_bets_by_type((DontCome))
    #     dontcome_odds_result_string = ""
    #     for b in dc_bets:
    #         dc_number = str(b.number) if b.number else "-"
    #         odds_bets = player.get_bets_by_type((Odds))
    #         for ob in odds_bets:
    #             if ob.base_type == DontCome and ob.number == b.number:
    #                 dontcome_odds_bet_string = str(ob.amount)
    #                 dontcome_odds_result = ob.get_result(player.table)
    #                 dontcome_odds_result_string = str(dontcome_odds_result.amount)
    #         bets_string = bets_string + " DC("+dc_number+"):"+str(b.amount) #+ "+" + dontcome_odds_bet_string

    #         # Current Results
    #         bet_result = b.get_result(player.table)
    #         if bet_result.amount > 0:
    #             bet_results_string = bet_results_string + " DC(" + str(b.number) + "):W" + str(round(bet_result.amount)) + "+" + dontcome_odds_result_string
    #         elif bet_result.amount < 0:
    #             bet_results_string = bet_results_string + " DC(" + str(b.number) + "):L" + str(round(bet_result.amount)) + dontcome_odds_result_string
        
    #     # Come Bet
    #     cb_bets = player.get_bets_by_type((Come))
    #     for b in cb_bets:
    #         cb_number = str(b.number) if b.number else "-"        
    #         come_odds_result_string = ""
    #         odds_bets = player.get_bets_by_type((Odds))
    #         for ob in odds_bets:
    #             if ob.base_type == Come and ob.number == b.number:
    #                 bets_string = bets_string + "+" + str(round(ob.amount))
    #                 come_odds_result = ob.get_result(player.table)
    #                 come_odds_result_string = str(come_odds_result.amount)
    #         bets_string = bets_string + " CB("+cb_number+"):"+str(round(b.amount)) + "+" + come_odds_result_string

    #         # Current Results
    #         bet_result = b.get_result(player.table)
    #         if bet_result.amount > 0:
    #             bet_results_string = bet_results_string + " CB(" + str(b.number) + "):W" + str(round(bet_result.amount)) + "+" + come_odds_result_string
    #         elif bet_result.amount < 0:
    #             bet_results_string = bet_results_string + " CB(" + str(b.number) + "):L" + str(round(bet_result.amount)) + come_odds_result_string    
        

    #     # Place Bet
    #     pc_bets = player.get_bets_by_type((Place))
    #     for b in pc_bets:
    #         pc_number = str(b.number) if b.number else "-"
    #         bets_string = bets_string + " PC("+pc_number+"):"+str(b.amount)

    #     final_bets_string = str(table.dice.n_rolls) + " " + player.name +" "+ str(round(player.bankroll)) + " P:" + point_string + " " + bets_string
    #     final_bet_results_string = str(table.dice.n_rolls) + " " + player.name +" "+ str(round(player.bankroll)) + " D:" + str(table.dice.total) + " " + bet_results_string

    #     return final_bets_string, final_bet_results_string

    # def build_bets_string(player):
    #     final_bets_string, final_bet_results_string = build_bets_and_results_string(player)
    #     return final_bets_string

    # def build_bet_result_string(player):
    #     final_bets_string, final_bet_results_string = build_bets_and_results_string(player)
    #     return final_bet_results_string

    def completed(self, player: Player) -> bool:
        """The strategy is completed if the player can no longer make the initial PassLine bet
        because their bankroll is too low, and they have no more bets on the table.

        Parameters
        ----------
        player

        Returns
        -------

        """
        return player.bankroll < self.base_amount and len(player.bets) == 0

    def after_roll(self, player: Player) -> None:
        """Update the dc_loss_streak based on how many DC bets are lost. 
        Set dc_loss_streak to 0 on a DC win.

        Parameters
        ----------
        player
        """

        # Maintain a count of dc_losses in a row. Reset to zero on a DC win.
        dc_bets = player.get_bets_by_type((DontCome))
        if len(dc_bets) == 1:
            # We should only ever have one DC bet on the table, so we only look at dc_bets[0]
            if dc_bets[0].get_result(player.table).lost: 
                self.dc_loss_streak += 1
            elif dc_bets[0].get_result(player.table).won:
                self.dc_loss_streak = 0
        elif len(dc_bets) > 1:
            print("  *** WARNING *** UNEXPECTED CONDITION: MULTIPLE DC BETS *** WARNING ***")

        # if self.verbose: print("AR:" + build_bet_result_string(player) , " DCLS: ", self.dc_loss_streak , "\n")
        
    def update_bets(self, player: Player) -> None:
        """If the point is off bet the PASSLINE. 
        If the point is on and there is no DONTCOME, place a DONTCOME bet. 
        Otherwise, (there is a POINT established and one DONTCOME estabished), place a COME bet.
        Continue to add COME bets until the point or DONTCOME number is rolled. Repeat.

        Parameters
        ----------
        player
            Player to place the bets for.
        """

        # DC loss count to establish the progression level 
        if self.max_loss_progression > 1:
            if self.dc_loss_streak < self.max_loss_progression:
                progression = self.dc_loss_streak + 1
            else:
                progression = self.max_loss_progression            
        else:
            progression = 1
        
        # Core strategy logic
        if self.debug:
            print("**********************************")
            print("*** STARTING UPDATE BETS LOGIC ***")
        # if self.verbose: print("BB:" + build_bets_string(player))

        if player.table.point.status == "Off":

            if self.debug:
                print("  - POINT IS OFF")
                print("  - SETTING PASSLINE")
            BetPassLine(self.base_amount*progression).update_bets(player)

        elif len(player.get_bets_by_type((DontCome))) == 0:

            if self.debug:
                print("  - POINT IS ON")
                print("  - DC IS NOT SET")
                print("  - SETTING DC")            
            BetDontCome(self.base_amount*self.dc_multiplier*progression).update_bets(player)
        else:

            if self.debug:
                print("  - POINT IS ON")
                print("  - DC IS SET")
                print("  - SETTING COME")            
            #BetCome(self.base_amount*progression, StrategyMode.ADD_IF_POINT_ON).update_bets(player)   
            BetCome(self.base_amount).update_bets(player)     
            #AddIfTrue(Come(self.base_amount*progression),lambda p: len(p.get_bets_by_type((DontCome,))) == 1).update_bets(player)

        # Add Odds
        if self.odds_multiplier:
            PassLineOddsMultiplier(self.odds_multiplier).update_bets(player)
            ComeOddsMultiplier(self.odds_multiplier).update_bets(player)
            DontComeOddsMultiplier(self.odds_multiplier).update_bets(player)

        if self.debug:
            print("***** BETTING LOGIC COMPLETE *****")
            print(">> BETS:", player.bets)
            print("**********************************")        
        # if self.verbose: print("AB:" + build_bets_string(player))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_amount={self.base_amount})"