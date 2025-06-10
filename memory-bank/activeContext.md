# Active Context

## Current Work Focus
The current focus is on implementing a comprehensive analytics system for CrapsSim simulations to support detailed analytical metrics, visualizations, and answering specific analytical questions. This involves capturing raw simulation data, persisting it to a PostgreSQL database, and performing post-simulation analysis, and rendering the analysis in a GUI.

## Requirements
- The requirements for the analytics data logging system is outlined in [`memory-bank/analyticsRequirements.md`](memory-bank/analyticsRequirements.md).

## Next Steps: Implementing Analytics Data Logging
The implementation will proceed in small, incremental, and testable steps.

### Phase 1: Database Setup and Logger Foundation

**1.1. Database Schema Definition & Connection (PostgreSQL)**
*   **Action:** Define the SQL schema for the PostgreSQL database. This will include tables for:
    *   `simulations` (Simulation_ID, Strategy_Name, Starting_Bankroll_For_Simulation, Total_Sessions_To_Run, Simulation_End_Bankroll, Did_Ruin_Occur_In_Simulation, Session_Number_Of_Ruin, etc.)
    *   `sessions` (Session_ID, Simulation_ID (FK), Session_Number, Starting_Bankroll_Session, Ending_Bankroll_Session, Net_Profit_Loss_Session, Session_Outcome, Total_Rolls_In_Session, Total_Dollars_Risked_In_Session, Max_Bankroll_During_Session, Min_Bankroll_During_Session, Did_Target_130_Reach, Did_Target_200_Reach, Total_Hedging_Dollars_Placed_In_Session, Total_Bets_Placed_In_Session, etc.)
    *   `rolls` (Roll_ID, Session_ID (FK), Simulation_ID (FK), Roll_Number_In_Session, Dice_Roll_Value, Current_Bankroll_After_Roll, Cumulative_Net_Profit_Loss_Session_To_Roll, Cumulative_Dollars_Risked_Session_To_Roll, Point_Status_After_Roll, etc.)
    *   `bets` (Bet_Event_ID, Bet_ID, Session_ID (FK), Simulation_ID (FK), Player_ID, Event_Type, Bet_Type, Bet_Amount, Is_Hedging_Bet, Roll_Number_When_Event_Occurred, Profit_Loss_From_Bet_Resolution, etc.)
*   **Action:** Create a new module, e.g., `crapssim/db_utils.py`, to handle PostgreSQL connection and table creation/management. This module will contain functions to:
    *   Connect to the PostgreSQL database.
    *   Create the necessary tables if they don't exist.
    *   Handle database disconnections.
*   **Unit Test:** Write tests for `crapssim/db_utils.py` to ensure:
    *   Successful connection to a test PostgreSQL database.
    *   Correct creation of all defined tables.
    *   Proper handling of connection errors.

**1.2. Create `crapssim/logger.py` and `SimulationLogger` Class**
*   **Action:** Create a new file `crapssim/logger.py`.
*   **Action:** Implement the `SimulationLogger` class within `crapssim/logger.py`.
    *   Initialize internal lists (e.g., `self.simulation_data`, `self.session_data`, `self.roll_data`, `self.bet_data`) to act as in-memory buffers.
    *   Implement `record_simulation_start`, `record_session_start`, `record_roll`, `record_bet_event`, `record_session_end`, `record_simulation_end` methods. These methods will append dictionaries (or dataclass instances) of raw data points to the respective in-memory buffers. Ensure unique IDs (`uuid.uuid4()`) and foreign keys are generated and stored correctly.
    *   Implement a `flush_to_database(db_connection)` method. This method will use `psycopg2` (or similar PostgreSQL adapter) to perform batch `INSERT` operations from the in-memory buffers into the corresponding PostgreSQL tables. It should clear the buffers after a successful flush.
*   **Unit Test:** Write tests for `crapssim/logger.py` to ensure:
    *   Data is correctly added to the in-memory buffers by the `record_` methods.
    *   `flush_to_database` successfully writes data to a mock/test database connection and clears buffers.
    *   Correct handling of unique ID generation and foreign key assignments within the logger.

### Phase 2: Integration into Simulation Flow

**2.1. Integrate Logger into `crapssim/table.py` (`Table` and `TableUpdate`)**
*   **Action:** Modify the `Table.run()` method to accept `logger: SimulationLogger`, `session_id: str`, and `simulation_id: str` as parameters.
*   **Action:** Pass these new parameters from `Table.run()` down to `TableUpdate().run()`.
*   **Action:** Modify the `TableUpdate.run()` method to accept `logger`, `session_id`, `simulation_id`, and `roll_id: str` as parameters.
*   **Action:** Within `TableUpdate.run()`, before and after the dice roll, call `logger.record_roll()` to capture roll-level data, including `Current_Bankroll_After_Roll` and `Dice_Roll_Value`. Generate `roll_id` using `uuid.uuid4()`.
*   **Action:** Pass the logger and IDs from `TableUpdate.run()` to `Player.update_bet()`.
*   **Unit Test:** Write tests to verify that:
    *   `Table.run()` correctly passes logger and IDs to `TableUpdate.run()`.
    *   `TableUpdate.run()` calls `logger.record_roll()` at the appropriate times and passes logger/IDs to `Player.update_bet()`.
    *   The `n_rolls` count is correctly used for `Roll_Number_In_Session`.

**2.2. Integrate Logger into `crapssim/player.py` (`Player` class)**
*   **Action:** Modify `Player.add_bet()` to accept `logger`, `session_id`, `simulation_id`, and `roll_id` as parameters.
*   **Action:** Within `Player.add_bet()`, call `logger.record_bet_event()` for "Place" events, capturing `Bet_Event_ID` (using `uuid.uuid4()`), `Bet_ID` (e.g., `str(id(bet))`), `Bet_Type`, `Bet_Amount`, `Is_Hedging_Bet`, and `Roll_Number_When_Event_Occurred`.
*   **Action:** Modify `Player.update_bet()` to accept `logger`, `session_id`, `simulation_id`, and `roll_id` as parameters.
*   **Action:** Within `Player.update_bet()`, call `logger.record_bet_event()` for "Resolve" events, capturing `Profit_Loss_From_Bet_Resolution` and other relevant bet details.
*   **Unit Test:** Write tests to verify that:
    *   `Player.add_bet()` correctly calls `logger.record_bet_event()` for bet placements.
    *   `Player.update_bet()` correctly calls `logger.record_bet_event()` for bet resolutions.
    *   All required bet-level data points are captured.

### Phase 3: Simulation Orchestration and Data Analysis

**3.1. Create `crapssim/simulation.py`**
*   **Action:** Create a new file `crapssim/simulation.py`.
*   **Action:** Implement the `run_full_simulation` function (or class) within `crapssim/simulation.py`.
    *   This function will be the top-level orchestrator for running multiple sessions.
    *   It will instantiate `SimulationLogger` and `Table` objects.
    *   It will manage the loop for `num_sessions`.
    *   Inside the loop, it will initialize a new `Table` and `Player` for each session to ensure a clean state.
    *   It will call `logger.record_simulation_start()` at the beginning of the entire simulation.
    *   It will call `logger.record_session_start()` at the beginning of each session.
    *   It will call `table.run()` for each session, passing the `logger` and generated `session_id`/`simulation_id`.
    *   It will call `logger.record_session_end()` at the end of each session, capturing session-level summary data.
    *   It will call `logger.record_simulation_end()` at the end of the entire simulation.
    *   Finally, it will call `logger.flush_to_database()` to persist all collected data to PostgreSQL.
*   **Integration Test:** Run a small end-to-end simulation using `run_full_simulation`. Verify that:
    *   Data appears correctly in the PostgreSQL database across all tables (`simulations`, `sessions`, `rolls`, `bets`).
    *   Relationships (foreign keys) are correctly maintained.

**3.2. Data Analysis and Metrics Calculation**
*   **Action:** Create a new module, e.g., `crapssim/analytics.py`.
*   **Action:** Implement functions within `crapssim/analytics.py` to:
    *   Connect to the PostgreSQL database and retrieve raw data.
    *   Use `pandas` (or `polars`) to load data into DataFrames.
    *   Implement functions to compute each of the specified analytical metrics (e.g., `calculate_avg_net_profit_loss_per_session`, `calculate_risk_of_ruin_percentage`, `calculate_empirical_ev`, etc.) by querying and transforming the raw data.
*   **Unit Test:** Write tests for `crapssim/analytics.py` to ensure:
    *   Each metric calculation function produces correct results given sample data.
    *   Data loading from PostgreSQL works as expected.

**3.3. Saving Completed Analysis to Database**
*   **Action:** Extend the PostgreSQL database schema (in `crapssim/db_utils.py`) to include new tables for the aggregated analytical results (e.g., `Strategy_Performance_Summary`, `Strategy_Risk_Profile`, `Hedging_Impact_And_Usage`, `Comprehensive_Strategy_Comparison`).
*   **Action:** Modify `crapssim/analytics.py` to include functions that:
    *   Take the computed analytical metrics.
    *   Persist these aggregated results into the new PostgreSQL summary tables.
*   **Unit Test:** Write tests to verify that:
    *   Aggregated results are correctly inserted into the new summary tables in PostgreSQL.
    *   The data types and constraints are respected.

### Phase 3: Visualization
  **PLACEHOLDER:** TBD

## Active Decisions and Considerations
*   **PostgreSQL Connection Details:** Ensure secure handling of database credentials (e.g., environment variables, configuration file).
*   **Error Handling:** Implement robust error handling for database operations and data collection.
*   **Unique ID Generation:** Use `uuid.uuid4()` for generating unique IDs for simulations, sessions, rolls, and bet events to ensure global uniqueness.
*   **Hedging Bet Identification:** The `Is_Hedging_Bet` flag in `bet` data will need a clear definition within strategies or bet types to be accurately captured.

## Important Patterns and Preferences
*   **Separation of Concerns:** Maintain clear boundaries between game logic, data logging, and data analysis.
*   **Incremental Development:** Build and test each component in isolation before integrating.
*   **Comprehensive Testing:** Unit tests for individual functions/classes and integration tests for end-to-end flows.

## Learnings and Project Insights
This implementation will significantly enhance CrapsSim's analytical capabilities, transforming it from a simulation engine into a powerful tool for strategy validation and optimization. The structured logging to PostgreSQL will provide a solid foundation for future data-driven insights.
