import uuid
from crapssim.table import Table, Player
from crapssim.strategy import Strategy, BetPassLine
from crapssim.logger import SimulationLogger
from crapssim.db_utils import get_db_connection, create_tables

def run_full_simulation(
    num_sessions: int,
    player_bankroll: float,
    player_strategy: Strategy = BetPassLine(5),
    player_name: str = "Player",
    max_rolls_per_session: int = 100,
    verbose: bool = False
):
    """
    Orchestrates a full simulation run, including multiple sessions,
    data logging, and persistence to the database.

    Parameters
    ----------
    num_sessions : int
        The total number of sessions to run in this simulation.
    player_bankroll : float
        The starting bankroll for the player in each session.
    player_strategy : Strategy
        The betting strategy for the player.
    player_name : str
        The name of the player.
    max_rolls_per_session : int
        The maximum number of rolls per session.
    verbose : bool
        If true, print results from table during each roll.
    """

    # Ensure tables exist
    create_tables()

    simulation_id = str(uuid.uuid4())
    logger = SimulationLogger()

    # Record simulation start
    logger.record_simulation_start(
        simulation_id=simulation_id,
        strategy_name=player_strategy.__class__.__name__,
        player_id=str(uuid.uuid4()), # A unique ID for the player across the simulation
        starting_bankroll=player_bankroll
    )

    total_rolls_simulated = 0
    simulation_end_bankroll = player_bankroll
    did_ruin_occur_in_simulation = False
    session_number_of_ruin = None

    for session_number in range(1, num_sessions + 1):
        session_id = str(uuid.uuid4())
        table = Table()
        player = Player(table=table, bankroll=player_bankroll, bet_strategy=player_strategy, name=player_name)
        table.add_player(player.bankroll, player.strategy, player.name)
        table.players[0].player_id = player.player_id # Ensure the player_id is consistent

        # Record session start
        logger.record_session_start(
            session_id=session_id,
            simulation_id=simulation_id,
            session_number=session_number,
            starting_bankroll_session=player_bankroll
        )

        # Run the session
        table.run(
            max_rolls=max_rolls_per_session,
            verbose=verbose,
            logger=logger,
            session_id=session_id,
            simulation_id=simulation_id
        )

        # Update session end data
        ending_bankroll_session = table.players[0].bankroll
        net_profit_loss_session = ending_bankroll_session - player_bankroll
        session_outcome = "Win" if net_profit_loss_session > 0 else ("Loss" if net_profit_loss_session < 0 else "Push")
        total_rolls_in_session = table.dice.n_rolls
        total_dollars_risked_in_session = table.players[0].total_dollars_risked_session # From player object
        max_bankroll_during_session = max(r["current_bankroll_after_roll"] for r in logger.roll_data if r["session_id"] == session_id)
        min_bankroll_during_session = min(r["current_bankroll_after_roll"] for r in logger.roll_data if r["session_id"] == session_id)

        # Placeholder for target reach and hedging (needs actual logic in strategy/player)
        did_target_130_reach = False
        did_target_200_reach = False
        total_hedging_dollars_placed_in_session = 0.0
        total_bets_placed_in_session = table.players[0].total_dollars_risked_session # For now, same as risked

        logger.record_session_end(
            session_id=session_id,
            ending_bankroll_session=ending_bankroll_session,
            net_profit_loss_session=net_profit_loss_session,
            session_outcome=session_outcome,
            total_rolls_in_session=total_rolls_in_session,
            total_dollars_risked_in_session=total_dollars_risked_in_session,
            max_bankroll_during_session=max_bankroll_during_session,
            min_bankroll_during_session=min_bankroll_during_session,
            did_target_130_reach=did_target_130_reach,
            did_target_200_reach=did_target_200_reach,
            total_hedging_dollars_placed_in_session=total_hedging_dollars_placed_in_session,
            total_bets_placed_in_session=total_bets_placed_in_session
        )

        total_rolls_simulated += total_rolls_in_session
        simulation_end_bankroll = ending_bankroll_session # This should be cumulative across sessions, not just last session
        if ending_bankroll_session <= 0 and not did_ruin_occur_in_simulation:
            did_ruin_occur_in_simulation = True
            session_number_of_ruin = session_number

    # Record simulation end
    logger.record_simulation_end(
        simulation_id=simulation_id,
        total_sessions_simulated=num_sessions,
        total_rolls_simulated=total_rolls_simulated,
        simulation_end_bankroll=simulation_end_bankroll,
        did_ruin_occur_in_simulation=did_ruin_occur_in_simulation,
        session_number_of_ruin=session_number_of_ruin
    )

    # Flush all data to database
    conn = None
    try:
        conn = get_db_connection()
        logger.flush_to_database(conn)
    except Exception as e:
        print(f"Error during database flush: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Example usage:
    # Run a simulation of 5 sessions with a starting bankroll of 1000
    # python crapssim/simulation.py
    print("Running a sample simulation...")
    run_full_simulation(num_sessions=5, player_bankroll=1000.0, verbose=True)
    print("Simulation finished. Check your PostgreSQL database.")