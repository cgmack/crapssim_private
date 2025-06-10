import uuid
import psycopg2
from psycopg2 import sql

class SimulationLogger:
    def __init__(self):
        self.simulation_data = []
        self.session_data = []
        self.roll_data = []
        self.bet_data = []

    def record_simulation_start(self, simulation_id: str, strategy_name: str, player_id: str, starting_bankroll: float):
        self.simulation_data.append({
            "simulation_id": simulation_id,
            "strategy_name": strategy_name,
            "player_id": player_id,
            "starting_bankroll_for_simulation": starting_bankroll,
            "total_sessions_simulated": None,  # To be updated at end
            "total_rolls_simulated": None,     # To be updated at end
            "simulation_end_bankroll": None,   # To be updated at end
            "did_ruin_occur_in_simulation": False, # To be updated at end
            "session_number_of_ruin": None     # To be updated at end
        })

    def record_session_start(self, session_id: str, simulation_id: str, session_number: int, starting_bankroll_session: float):
        self.session_data.append({
            "session_id": session_id,
            "simulation_id": simulation_id,
            "session_number": session_number,
            "starting_bankroll_session": starting_bankroll_session,
            "ending_bankroll_session": None,
            "net_profit_loss_session": None,
            "session_outcome": None,
            "total_rolls_in_session": None,
            "total_dollars_risked_in_session": 0.0,
            "max_bankroll_during_session": starting_bankroll_session,
            "min_bankroll_during_session": starting_bankroll_session,
            "did_target_130_reach": False,
            "did_target_200_reach": False,
            "total_hedging_dollars_placed_in_session": 0.0,
            "total_bets_placed_in_session": 0.0
        })

    def record_roll(self, roll_id: str, session_id: str, simulation_id: str, player_id: str,
                    roll_number_in_session: int, dice_roll_value: int, current_bankroll_after_roll: float,
                    cumulative_net_profit_loss_session_to_roll: float,
                    cumulative_dollars_risked_session_to_roll: float,
                    point_status_after_roll: str):
        self.roll_data.append({
            "roll_id": roll_id,
            "session_id": session_id,
            "simulation_id": simulation_id,
            "player_id": player_id, # Added player_id
            "roll_number_in_session": roll_number_in_session,
            "dice_roll_value": dice_roll_value,
            "current_bankroll_after_roll": current_bankroll_after_roll,
            "cumulative_net_profit_loss_session_to_roll": cumulative_net_profit_loss_session_to_roll,
            "cumulative_dollars_risked_session_to_roll": cumulative_dollars_risked_session_to_roll,
            "point_status_after_roll": point_status_after_roll
        })

    def update_roll(self, roll_id: str, dice_roll_value: int, current_bankroll_after_roll: float,
                    cumulative_net_profit_loss_session_to_roll: float,
                    cumulative_dollars_risked_session_to_roll: float,
                    point_status_after_roll: str):
        """Updates an existing roll record in the in-memory buffer."""
        for roll in self.roll_data:
            if roll["roll_id"] == roll_id:
                roll.update({
                    "dice_roll_value": dice_roll_value,
                    "current_bankroll_after_roll": current_bankroll_after_roll,
                    "cumulative_net_profit_loss_session_to_roll": cumulative_net_profit_loss_session_to_roll,
                    "cumulative_dollars_risked_session_to_roll": cumulative_dollars_risked_session_to_roll,
                    "point_status_after_roll": point_status_after_roll
                })
                break

    def record_bet_event(self, bet_event_id: str, bet_id: str, session_id: str, simulation_id: str,
                         player_id: str, event_type: str, bet_type: str, bet_amount: float,
                         is_hedging_bet: bool, roll_number_when_event_occurred: int,
                         profit_loss_from_bet_resolution: float = None):
        self.bet_data.append({
            "bet_event_id": bet_event_id,
            "bet_id": bet_id,
            "session_id": session_id,
            "simulation_id": simulation_id,
            "player_id": player_id,
            "event_type": event_type,
            "bet_type": bet_type,
            "bet_amount": bet_amount,
            "is_hedging_bet": is_hedging_bet,
            "roll_number_when_event_occurred": roll_number_when_event_occurred,
            "profit_loss_from_bet_resolution": profit_loss_from_bet_resolution
        })

    def record_session_end(self, session_id: str, ending_bankroll_session: float, net_profit_loss_session: float,
                           session_outcome: str, total_rolls_in_session: int, total_dollars_risked_in_session: float,
                           max_bankroll_during_session: float, min_bankroll_during_session: float,
                           did_target_130_reach: bool, did_target_200_reach: bool,
                           total_hedging_dollars_placed_in_session: float, total_bets_placed_in_session: float):
        for session in self.session_data:
            if session["session_id"] == session_id:
                session.update({
                    "ending_bankroll_session": ending_bankroll_session,
                    "net_profit_loss_session": net_profit_loss_session,
                    "session_outcome": session_outcome,
                    "total_rolls_in_session": total_rolls_in_session,
                    "total_dollars_risked_in_session": total_dollars_risked_in_session,
                    "max_bankroll_during_session": max_bankroll_during_session,
                    "min_bankroll_during_session": min_bankroll_during_session,
                    "did_target_130_reach": did_target_130_reach,
                    "did_target_200_reach": did_target_200_reach,
                    "total_hedging_dollars_placed_in_session": total_hedging_dollars_placed_in_session,
                    "total_bets_placed_in_session": total_bets_placed_in_session
                })
                break

    def record_simulation_end(self, simulation_id: str, total_sessions_simulated: int, total_rolls_simulated: int,
                              simulation_end_bankroll: float, did_ruin_occur_in_simulation: bool,
                              session_number_of_ruin: int = None):
        for sim in self.simulation_data:
            if sim["simulation_id"] == simulation_id:
                sim.update({
                    "total_sessions_simulated": total_sessions_simulated,
                    "total_rolls_simulated": total_rolls_simulated,
                    "simulation_end_bankroll": simulation_end_bankroll,
                    "did_ruin_occur_in_simulation": did_ruin_occur_in_simulation,
                    "session_number_of_ruin": session_number_of_ruin
                })
                break

    def flush_to_database(self, db_connection):
        """
        Flushes the collected in-memory data to the PostgreSQL database.
        Assumes db_connection is an active psycopg2 connection.
        """
        cur = db_connection.cursor()

        try:
            # Insert simulation data
            if self.simulation_data:
                sim_columns = self.simulation_data[0].keys()
                insert_sim_query = sql.SQL("INSERT INTO simulations ({}) VALUES ({})").format(
                    sql.SQL(', ').join(map(sql.Identifier, sim_columns)),
                    sql.SQL(', ').join(sql.Placeholder() * len(sim_columns))
                )
                cur.execute(insert_sim_query, tuple(self.simulation_data[0].values()))

            # Insert session data
            if self.session_data:
                session_columns = self.session_data[0].keys()
                insert_session_query = sql.SQL("INSERT INTO sessions ({}) VALUES ({})").format(
                    sql.SQL(', ').join(map(sql.Identifier, session_columns)),
                    sql.SQL(', ').join(sql.Placeholder() * len(session_columns))
                )
                cur.executemany(insert_session_query, [tuple(s.values()) for s in self.session_data])

            # Insert roll data
            if self.roll_data:
                roll_columns = self.roll_data[0].keys()
                # Use executemany for batch insert
                insert_roll_query = sql.SQL("INSERT INTO rolls ({}) VALUES ({})").format(
                    sql.SQL(', ').join(map(sql.Identifier, roll_columns)),
                    sql.SQL(', ').join(sql.Placeholder() * len(roll_columns))
                )
                cur.executemany(insert_roll_query, [tuple(r.values()) for r in self.roll_data])

            # Insert bet data
            if self.bet_data:
                bet_columns = self.bet_data[0].keys()
                # Use executemany for batch insert
                insert_bet_query = sql.SQL("INSERT INTO bets ({}) VALUES ({})").format(
                    sql.SQL(', ').join(map(sql.Identifier, bet_columns)),
                    sql.SQL(', ').join(sql.Placeholder() * len(bet_columns))
                )
                cur.executemany(insert_bet_query, [tuple(b.values()) for b in self.bet_data])

            db_connection.commit()
            print("Data flushed to database successfully.")
            self._clear_buffers()
        except Exception as e:
            db_connection.rollback()
            print(f"Error flushing data to database: {e}")
            raise
        finally:
            cur.close()

    def _clear_buffers(self):
        self.simulation_data = []
        self.session_data = []
        self.roll_data = []
        self.bet_data = []