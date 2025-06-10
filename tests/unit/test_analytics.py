import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
import psycopg2
from crapssim.analytics import (
    fetch_simulation_data,
    calculate_avg_net_profit_loss_per_session,
    calculate_empirical_ev_per_dollar_risked,
    calculate_win_loss_push_rates,
    calculate_risk_of_ruin_percentage,
    calculate_standard_deviation_of_session_profit_loss,
    calculate_max_drawdown_percentage,
    calculate_percentage_sessions_target_reached,
    calculate_avg_sessions_to_ruin,
    calculate_ev_per_unit_risk,
    calculate_total_hedging_dollars_placed,
    calculate_percentage_of_total_bets_as_hedging,
    calculate_avg_rolls_per_session,
    calculate_hourly_dollar_win_loss_rate,
    calculate_effective_house_edge,
    generate_strategy_performance_summary,
    generate_strategy_risk_profile,
    generate_hedging_impact_and_usage,
    generate_comprehensive_strategy_comparison
)

class TestAnalytics(unittest.TestCase):

    def setUp(self):
        # Sample DataFrames for testing
        self.simulations_data = {
            'simulation_id': ['sim1', 'sim2'],
            'strategy_name': ['StrategyA', 'StrategyB'],
            'player_id': ['p1', 'p2'],
            'starting_bankroll_for_simulation': [1000.0, 500.0],
            'total_sessions_simulated': [10, 5],
            'total_rolls_simulated': [100, 50],
            'simulation_end_bankroll': [1050.0, 400.0],
            'did_ruin_occur_in_simulation': [False, True],
            'session_number_of_ruin': [None, 3]
        }
        self.simulations_df = pd.DataFrame(self.simulations_data)

        self.sessions_data = {
            'session_id': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10',
                           's11', 's12', 's13', 's14', 's15'],
            'simulation_id': ['sim1', 'sim1', 'sim1', 'sim1', 'sim1', 'sim1', 'sim1', 'sim1', 'sim1', 'sim1',
                              'sim2', 'sim2', 'sim2', 'sim2', 'sim2'],
            'session_number': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5],
            'starting_bankroll_session': [1000.0] * 10 + [500.0] * 5,
            'ending_bankroll_session': [1010.0, 990.0, 1020.0, 980.0, 1005.0, 1015.0, 995.0, 1030.0, 970.0, 1000.0,
                                        510.0, 480.0, 0.0, 450.0, 420.0],
            'net_profit_loss_session': [10.0, -10.0, 20.0, -20.0, 5.0, 15.0, -5.0, 30.0, -30.0, 0.0,
                                        10.0, -20.0, -500.0, -50.0, -80.0],
            'session_outcome': ['Win', 'Loss', 'Win', 'Loss', 'Win', 'Win', 'Loss', 'Win', 'Loss', 'Push',
                                'Win', 'Loss', 'Loss', 'Loss', 'Loss'],
            'total_rolls_in_session': [10, 12, 15, 8, 11, 13, 9, 14, 10, 12,
                                       10, 11, 5, 9, 8],
            'total_dollars_risked_in_session': [100.0, 120.0, 150.0, 80.0, 110.0, 130.0, 90.0, 140.0, 100.0, 120.0,
                                                100.0, 110.0, 50.0, 90.0, 80.0],
            'max_bankroll_during_session': [1020.0, 1000.0, 1030.0, 990.0, 1010.0, 1025.0, 1000.0, 1040.0, 980.0, 1000.0,
                                            520.0, 500.0, 500.0, 460.0, 430.0],
            'min_bankroll_during_session': [990.0, 980.0, 1000.0, 970.0, 995.0, 1005.0, 985.0, 1010.0, 960.0, 990.0,
                                            490.0, 470.0, 0.0, 440.0, 410.0],
            'did_target_130_reach': [False, False, False, False, False, False, False, False, False, False,
                                     False, False, False, False, False],
            'did_target_200_reach': [False, False, False, False, False, False, False, False, False, False,
                                     False, False, False, False, False],
            'total_hedging_dollars_placed_in_session': [0.0] * 15,
            'total_bets_placed_in_session': [100.0, 120.0, 150.0, 80.0, 110.0, 130.0, 90.0, 140.0, 100.0, 120.0,
                                             100.0, 110.0, 50.0, 90.0, 80.0]
        }
        self.sessions_df = pd.DataFrame(self.sessions_data)

        self.rolls_data = {
            'roll_id': ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10',
                        'r11', 'r12', 'r13', 'r14', 'r15', 'r16', 'r17', 'r18', 'r19', 'r20'],
            'session_id': ['s1'] * 10 + ['s11'] * 10,
            'simulation_id': ['sim1'] * 10 + ['sim2'] * 10,
            'player_id': ['p1'] * 10 + ['p2'] * 10,
            'roll_number_in_session': list(range(1, 11)) + list(range(1, 11)),
            'dice_roll_value': [7, 4, 11, 5, 6, 8, 9, 10, 3, 2,
                                7, 4, 11, 5, 6, 8, 9, 10, 3, 2],
            'current_bankroll_after_roll': [1005.0, 1000.0, 1010.0, 1005.0, 1000.0, 1005.0, 1010.0, 1015.0, 1010.0, 1005.0,
                                            505.0, 500.0, 510.0, 505.0, 500.0, 505.0, 510.0, 515.0, 510.0, 505.0],
            'cumulative_net_profit_loss_session_to_roll': [5.0, 0.0, 10.0, 5.0, 0.0, 5.0, 10.0, 15.0, 10.0, 5.0,
                                                           5.0, 0.0, 10.0, 5.0, 0.0, 5.0, 10.0, 15.0, 10.0, 5.0],
            'cumulative_dollars_risked_session_to_roll': [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0,
                                                          50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0],
            'point_status_after_roll': ['Off', 'On', 'Off', 'On', 'On', 'On', 'On', 'On', 'Off', 'Off',
                                        'Off', 'On', 'Off', 'On', 'On', 'On', 'On', 'On', 'Off', 'Off']
        }
        self.rolls_df = pd.DataFrame(self.rolls_data)

        self.bets_data = {
            'bet_event_id': ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'b10'],
            'bet_id': ['betA', 'betB', 'betC', 'betD', 'betE', 'betF', 'betG', 'betH', 'betI', 'betJ'],
            'session_id': ['s1'] * 5 + ['s2'] * 5,
            'simulation_id': ['sim1'] * 5 + ['sim1'] * 5,
            'player_id': ['p1'] * 10,
            'event_type': ['Place', 'Resolve', 'Place', 'Resolve', 'Place', 'Place', 'Resolve', 'Place', 'Resolve', 'Place'],
            'bet_type': ['PassLine', 'PassLine', 'Come', 'Come', 'Field', 'PassLine', 'PassLine', 'Come', 'Come', 'Field'],
            'bet_amount': [10.0, 0.0, 10.0, 0.0, 5.0, 10.0, 0.0, 10.0, 0.0, 5.0],
            'is_hedging_bet': [False] * 10,
            'roll_number_when_event_occurred': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            'profit_loss_from_bet_resolution': [None, 10.0, None, -10.0, None, None, 5.0, None, -5.0, None]
        }
        self.bets_df = pd.DataFrame(self.bets_data)

        self.mock_sim_data = {
            "simulations": self.simulations_df,
            "sessions": self.sessions_df,
            "rolls": self.rolls_df,
            "bets": self.bets_df
        }

    @patch('crapssim.analytics.get_db_connection')
    @patch('pandas.read_sql')
    def test_fetch_simulation_data(self, mock_read_sql, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_read_sql.side_effect = [
            self.simulations_df,
            self.sessions_df,
            self.rolls_df,
            self.bets_df
        ]

        data = fetch_simulation_data()
        self.assertFalse(data['simulations'].empty)
        self.assertFalse(data['sessions'].empty)
        self.assertFalse(data['rolls'].empty)
        self.assertFalse(data['bets'].empty)
        mock_get_db_connection.assert_called_once()
        self.assertEqual(mock_read_sql.call_count, 4)
        mock_conn.close.assert_called_once()

    def test_calculate_avg_net_profit_loss_per_session(self):
        result = calculate_avg_net_profit_loss_per_session(self.sessions_df)
        # Expected: (10-10+20-20+5+15-5+30-30+0 + 10-20-500-50-80) / 15 = -625 / 15 = -41.666666666666664
        self.assertAlmostEqual(result, -625.0 / 15.0)

    def test_calculate_empirical_ev_per_dollar_risked(self):
        result = calculate_empirical_ev_per_dollar_risked(self.sessions_df)
        # Total profit/loss: -625
        # Total dollars risked: sum of total_dollars_risked_in_session = 100+120+150+80+110+130+90+140+100+120 (sim1) + 100+110+50+90+80 (sim2) = 1140 + 430 = 1570
        # Expected: -625 / 1570 = -0.3980891719745223
        self.assertAlmostEqual(result, -625.0 / 1570.0)

    def test_calculate_win_loss_push_rates(self):
        result = calculate_win_loss_push_rates(self.sessions_df)
        # Wins: 5, Losses: 9, Push: 1. Total: 15
        self.assertAlmostEqual(result['Win_Rate_Percentage'], (6/15)*100)
        self.assertAlmostEqual(result['Loss_Rate_Percentage'], (8/15)*100)
        self.assertAlmostEqual(result['Push_Rate_Percentage'], (1/15)*100)

    def test_calculate_risk_of_ruin_percentage(self):
        result = calculate_risk_of_ruin_percentage(self.simulations_df)
        # One ruin out of two simulations
        self.assertAlmostEqual(result, 50.0)

    def test_calculate_standard_deviation_of_session_profit_loss(self):
        result = calculate_standard_deviation_of_session_profit_loss(self.sessions_df)
        # This will be a specific number based on the sample data
        expected_std = self.sessions_df['net_profit_loss_session'].std()
        self.assertAlmostEqual(result, expected_std)

    def test_calculate_max_drawdown_percentage(self):
        # Test with a single simulation's rolls data
        sim1_rolls_df = self.rolls_df[self.rolls_df['simulation_id'] == 'sim1'].copy()
        starting_bankroll_sim1 = self.simulations_df[self.simulations_df['simulation_id'] == 'sim1']['starting_bankroll_for_simulation'].iloc[0]
        result = calculate_max_drawdown_percentage(sim1_rolls_df, starting_bankroll_sim1)
        # Manually calculate for sim1_rolls_df:
        # Bankrolls: [1005.0, 1000.0, 1010.0, 1005.0, 1000.0, 1005.0, 1010.0, 1015.0, 1010.0, 1005.0]
        # Peaks:     [1005.0, 1005.0, 1010.0, 1010.0, 1010.0, 1010.0, 1010.0, 1015.0, 1015.0, 1015.0]
        # Drawdown:  [0, 5, 0, 5, 10, 5, 0, 0, 5, 10]
        # Drawdown %: [0, 5/1005, 0, 5/1010, 10/1010, 5/1010, 0, 0, 5/1015, 10/1015]
        # Max drawdown is 10/1010 or 10/1015. Let's use 10/1010 for simplicity in manual check.
        self.assertAlmostEqual(result, (10.0 / 1010.0) * 100) # Max drawdown is 10 from peak 1010

    def test_calculate_percentage_sessions_target_reached(self):
        # Assuming some sessions reached target 130% and 200%
        sessions_data_with_targets = self.sessions_data.copy()
        sessions_data_with_targets['did_target_130_reach'] = [True, False, True, False, False, True, False, False, False, False,
                                                              True, False, False, False, False]
        sessions_data_with_targets['did_target_200_reach'] = [False, False, False, False, False, False, False, False, False, False,
                                                              True, False, False, False, False]
        sessions_df_targets = pd.DataFrame(sessions_data_with_targets)

        result_130 = calculate_percentage_sessions_target_reached(sessions_df_targets, 'did_target_130_reach')
        self.assertAlmostEqual(result_130, (4/15)*100) # 4 sessions reached 130%

        result_200 = calculate_percentage_sessions_target_reached(sessions_df_targets, 'did_target_200_reach')
        self.assertAlmostEqual(result_200, (1/15)*100) # 1 session reached 200%

    def test_calculate_avg_sessions_to_ruin(self):
        result = calculate_avg_sessions_to_ruin(self.simulations_df)
        # Only sim2 had ruin at session 3
        self.assertAlmostEqual(result, 3.0)

    def test_calculate_ev_per_unit_risk(self):
        empirical_ev = -0.01
        std_dev = 10.0
        result = calculate_ev_per_unit_risk(empirical_ev, std_dev)
        self.assertAlmostEqual(result, -0.001)

        result_zero_std = calculate_ev_per_unit_risk(empirical_ev, 0.0)
        self.assertEqual(result_zero_std, 0.0)

    def test_calculate_total_hedging_dollars_placed(self):
        hedging_bets_data = self.bets_data.copy()
        hedging_bets_data['is_hedging_bet'] = [False, False, True, False, True, False, False, True, False, True]
        hedging_bets_df = pd.DataFrame(hedging_bets_data)
        result = calculate_total_hedging_dollars_placed(hedging_bets_df)
        # Expected: 10.0 (from betC) + 5.0 (from betE) + 10.0 (from betH) + 5.0 (from betJ) = 30.0
        self.assertAlmostEqual(result, 30.0)

    def test_calculate_percentage_of_total_bets_as_hedging(self):
        hedging_bets_data = self.bets_data.copy()
        hedging_bets_data['is_hedging_bet'] = [False, False, True, False, True, False, False, True, False, True]
        hedging_bets_df = pd.DataFrame(hedging_bets_data)
        result = calculate_percentage_of_total_bets_as_hedging(hedging_bets_df)
        # Total bets: 10+0+10+0+5+10+0+10+0+5 = 50
        # Total hedging: 10+5+10+5 = 30
        # Expected: (30/50)*100 = 60.0
        self.assertAlmostEqual(result, 60.0)

    def test_calculate_avg_rolls_per_session(self):
        result = calculate_avg_rolls_per_session(self.sessions_df)
        # Expected: (10+12+15+8+11+13+9+14+10+12 (sim1) + 10+11+5+9+8 (sim2)) / 15 = 114 + 43 / 15 = 157 / 15 = 10.466...
        self.assertAlmostEqual(result, 157.0 / 15.0)

    def test_calculate_hourly_dollar_win_loss_rate(self):
        avg_profit_loss = -40.0
        avg_rolls = 11.133333333333333
        rolls_per_hour = 90
        result = calculate_hourly_dollar_win_loss_rate(avg_profit_loss, avg_rolls, rolls_per_hour)
        # Expected: -40 * (90 / 11.133333333333333) = -40 * 8.0808... = -323.23...
        self.assertAlmostEqual(result, -40.0 * (90.0 / (167.0 / 15.0)))

    def test_calculate_effective_house_edge(self):
        total_profit_loss = -600.0
        total_dollars_risked = 1670.0
        result = calculate_effective_house_edge(total_profit_loss, total_dollars_risked)
        # Expected: -(-600 / 1670) * 100 = (600 / 1670) * 100 = 35.928...
        self.assertAlmostEqual(result, (600.0 / 1670.0) * 100)

    def test_generate_strategy_performance_summary(self):
        summary_df = generate_strategy_performance_summary(self.mock_sim_data)
        self.assertFalse(summary_df.empty)
        self.assertEqual(len(summary_df), 2) # Two strategies: StrategyA, StrategyB
        self.assertIn('Strategy_Name', summary_df.columns)
        self.assertIn('Avg_Net_Profit_Loss_Per_Session', summary_df.columns)
        self.assertIn('Empirical_EV_Per_Dollar_Risked', summary_df.columns)
        self.assertIn('Win_Rate_Percentage', summary_df.columns)

        # Verify values for StrategyA
        strategy_a_row = summary_df[summary_df['Strategy_Name'] == 'StrategyA'].iloc[0]
        # Sessions for StrategyA: s1-s10
        strategy_a_sessions = self.sessions_df[self.sessions_df['simulation_id'] == 'sim1']
        self.assertAlmostEqual(strategy_a_row['Avg_Net_Profit_Loss_Per_Session'], calculate_avg_net_profit_loss_per_session(strategy_a_sessions))
        self.assertAlmostEqual(strategy_a_row['Empirical_EV_Per_Dollar_Risked'], calculate_empirical_ev_per_dollar_risked(strategy_a_sessions))
        self.assertAlmostEqual(strategy_a_row['Win_Rate_Percentage'], calculate_win_loss_push_rates(strategy_a_sessions)['Win_Rate_Percentage'])
        self.assertEqual(strategy_a_row['Total_Sessions_Simulated'], 10)
        self.assertAlmostEqual(strategy_a_row['Total_Dollars_Risked'], strategy_a_sessions['total_dollars_risked_in_session'].sum())

    def test_generate_strategy_risk_profile(self):
        risk_profile_df = generate_strategy_risk_profile(self.mock_sim_data)
        self.assertFalse(risk_profile_df.empty)
        self.assertEqual(len(risk_profile_df), 2) # Two strategies
        self.assertIn('Risk_Of_Ruin_Percentage', risk_profile_df.columns)
        self.assertIn('Max_Drawdown_Percentage', risk_profile_df.columns)

        # Verify values for StrategyB (which had ruin)
        strategy_b_row = risk_profile_df[risk_profile_df['Strategy_Name'] == 'StrategyB'].iloc[0]
        strategy_b_sims = self.simulations_df[self.simulations_df['strategy_name'] == 'StrategyB']
        strategy_b_sessions = self.sessions_df[self.sessions_df['simulation_id'] == 'sim2']
        strategy_b_rolls = self.rolls_df[self.rolls_df['simulation_id'] == 'sim2']

        self.assertAlmostEqual(strategy_b_row['Risk_Of_Ruin_Percentage'], calculate_risk_of_ruin_percentage(strategy_b_sims))
        self.assertAlmostEqual(strategy_b_row['Standard_Deviation_Of_Session_ProfitLoss'], calculate_standard_deviation_of_session_profit_loss(strategy_b_sessions))
        self.assertAlmostEqual(strategy_b_row['Max_Drawdown_Percentage'], calculate_max_drawdown_percentage(strategy_b_rolls, strategy_b_sims['starting_bankroll_for_simulation'].iloc[0]))
        self.assertAlmostEqual(strategy_b_row['Avg_Sessions_To_Ruin'], calculate_avg_sessions_to_ruin(strategy_b_sims))

    def test_generate_hedging_impact_and_usage(self):
        hedging_impact_df = generate_hedging_impact_and_usage(self.mock_sim_data)
        self.assertFalse(hedging_impact_df.empty)
        self.assertEqual(len(hedging_impact_df), 2) # Two strategies
        self.assertIn('Total_Hedging_Dollars_Placed', hedging_impact_df.columns)
        self.assertIn('Percentage_Of_Total_Bets_As_Hedging', hedging_impact_df.columns)

        # For simplicity, our sample data has no hedging, so these should be 0
        self.assertAlmostEqual(hedging_impact_df['Total_Hedging_Dollars_Placed'].sum(), 0.0)
        self.assertAlmostEqual(hedging_impact_df['Percentage_Of_Total_Bets_As_Hedging'].sum(), 0.0)

    def test_generate_comprehensive_strategy_comparison(self):
        comparison_df = generate_comprehensive_strategy_comparison(self.mock_sim_data)
        self.assertFalse(comparison_df.empty)
        self.assertEqual(len(comparison_df), 2) # Two strategies
        self.assertIn('Hourly_Dollar_Win_Loss_Rate', comparison_df.columns)
        self.assertIn('EV_Per_Unit_Risk', comparison_df.columns)

        # Verify values for StrategyA
        strategy_a_row = comparison_df[comparison_df['Strategy_Name'] == 'StrategyA'].iloc[0]
        strategy_a_sessions = self.sessions_df[self.sessions_df['simulation_id'] == 'sim1']
        strategy_a_rolls = self.rolls_df[self.rolls_df['simulation_id'] == 'sim1']
        strategy_a_sims = self.simulations_df[self.simulations_df['strategy_name'] == 'StrategyA']

        avg_profit_loss_a = calculate_avg_net_profit_loss_per_session(strategy_a_sessions)
        avg_rolls_a = calculate_avg_rolls_per_session(strategy_a_sessions)
        self.assertAlmostEqual(strategy_a_row['Hourly_Dollar_Win_Loss_Rate'], calculate_hourly_dollar_win_loss_rate(avg_profit_loss_a, avg_rolls_a))
        
        empirical_ev_a = calculate_empirical_ev_per_dollar_risked(strategy_a_sessions)
        std_dev_a = calculate_standard_deviation_of_session_profit_loss(strategy_a_sessions)
        self.assertAlmostEqual(strategy_a_row['EV_Per_Unit_Risk'], calculate_ev_per_unit_risk(empirical_ev_a, std_dev_a))
        self.assertAlmostEqual(strategy_a_row['Max_Drawdown_Percentage'], calculate_max_drawdown_percentage(strategy_a_rolls, strategy_a_sims['starting_bankroll_for_simulation'].iloc[0]))


if __name__ == '__main__':
    unittest.main()