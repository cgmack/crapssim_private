# We are planning the next phase of work: Analytics. Here you will find: 
 1.0 The types of questions we want to answer with our analytics and the design of tabular summaries and visualizations 
 2.0 The metrics we need to support the analysis and the data we want to record during simulations to compute the metrics

# Here are a few structural aspects of a simulation to keep in mind
 * A simulation can have multiple players, but we usually run it with one player.
 * Each player will have one strategy that remains the same for the entire simulation. 
 * Each player has a starting_bankroll and a current bankroll. The starting_bankroll is the same for each session throughout the simulation. The current bankroll cannot go negative. 
 * A simulation will have multiple sessions. A session consists of a number of dice rolls, set by max_rolls. However, if max_rolls is set to true, the session will continue past max_rolls until player has no more bets on the table.
 * max_rolls is typically set to a number that reflects 1-2 hours of game play in a casino. Assume a typical craps table sees approximately 60-120 rolls per hour.
 * A simulation typically consists of 10000 sessions. This number can be higher or lower to achieve statistical significance.


## 1.0 Analytical Questions and Required Visualizations

### 1.1 Overall Strategy Performance and Profitability:
**Analytical Questions Addressed:**
1.1.1 What is the average net profit/loss per session for a given strategy? In other words, how much do I expect to win/lose per gambling session?
1.1.2 What is the overall expected value (EV) for each strategy? In other words, how much do I expect to win/lose per dollar I risk? (aka empirical EV)
1.1.3 What is the win/loss rate of sessions for a given strategy? In other words, how many time should I expect to win vs. lose? (aka p(win) rate)
1.1.4 What is the relationship between a strategy's EV and its average profit/loss?

** Tabular Summary:**
1.1.5 **Table Name:** `Strategy_Performance_Summary`
*   **Description:** This table provides a concise overview of each strategy's core profitability and win rate metrics.
*   **Columns:**
    *   `Strategy_Name` (e.g., IronCross, HammerLock, CustomStrategy1)
    *   `Avg_Net_Profit_Loss_Per_Session` (Numeric, e.g., $ -5.23)
    *   `Empirical_EV_Per_Dollar_Risked` (Numeric, e.g., -0.014)
    *   `Win_Rate_Percentage` (Numeric, e.g., 45.7%)
    *   `Loss_Rate_Percentage` (Numeric, e.g., 50.1%)
    *   `Push_Rate_Percentage` (Numeric, e.g., 4.2%)
    *   `Total_Sessions_Simulated` (Numeric)
    *   `Total_Dollars_Risked` (Numeric)

**Visualizations:**
**1.1.6 Strategy Performance Dashboard (Combined View):**
    *   **Type:** A dashboard layout featuring multiple small, interconnected charts.
    *   **Description:**
        *   **Bar Chart (Avg. Net Profit/Loss):** Compares `Avg_Net_Profit_Loss_Per_Session` across strategies.
        *   **Bar Chart (Empirical EV):** Compares `Empirical_EV_Per_Dollar_Risked` across strategies.
        *   **Stacked Bar Chart (Win/Loss/Push Rate):** For each strategy, shows the proportion of win, loss, and push sessions.
        *   **Scatter Plot (EV vs. Profit/Loss):** X-axis: `Avg_Net_Profit_Loss_Per_Session`, Y-axis: `Empirical_EV_Per_Dollar_Risked`. Each point represents a strategy, showing their relationship.


### 1.2. Risk and Volatility / Bankroll Management:

**Analytical Questions Addressed:**
1.2.1 How does a strategy's bankroll fluctuate over time (per session and across multiple sessions)?
1.2.2 How does the cumulative EV of a strategy evolve over a long simulation (e.g., 10,000 sessions)?
1.2.3 How does a strategy's EV relate to its bankroll volatility (e.g., standard deviation of outcomes)?
1.2.4 How often does a player's bankroll reach a certain target (e.g., 130% or 200% of the starting bankroll)?
1.2.5 How often does a player's bankroll go to zero (risk of ruin) with a given strategy?
1.2.6 Which strategy offers the best balance between potential returns and risk of ruin (losing the entire bankroll)?
1.2.7 What is the optimal starting bankroll for each strategy to survive a typical session?
1.2.8 Which strategy allows a player to "walk away" with a win more frequently?
**Tabular Summaries:**
1.2.9  **Table Name:** `Strategy_Risk_Profile`
    *   **Description:** Summarizes key risk metrics for each strategy.
    *   **Columns:**
        *   `Strategy_Name`
        *   `Risk_Of_Ruin_Percentage` (e.g., 10.5%)
        *   `Standard_Deviation_Of_Session_ProfitLoss`
        *   `Max_Drawdown_Percentage` (Maximum percentage drop from a peak bankroll)
        *   `Percentage_Sessions_Target_Reached_130%`
        *   `Percentage_Sessions_Target_Reached_200%`
        *   `Percentage_Sessions_Ending_In_Profit` (Walk away win frequency)
        *   `Avg_Sessions_To_Ruin` (for ruined simulations)
        *   `EV_Per_Unit_Risk` (Calculated as `Empirical_EV_Per_Dollar_Risked` / `Standard_Deviation_Of_Session_ProfitLoss`)

1.2.10  **Table Name:** `Bankroll_Trajectory_Data`
    *   **Description:** Detailed data for plotting bankroll and cumulative EV over time. This table would be large and used primarily for visualization.
    *   **Columns:**
        *   `Simulation_ID`
        *   `Strategy_Name`
        *   `Session_Number`
        *   `Roll_Number` (within session)
        *   `Current_Bankroll` (at each roll/point in time)
        *   `Cumulative_Net_Profit_Loss` (up to that session/roll)
        *   `Cumulative_Dollars_Risked` (up to that session/roll)
        *   `Cumulative_Empirical_EV` (Calculated from cumulative profit/loss and dollars risked)

1.2.11  **Table Name:** `Optimal_Starting_Bankroll_Analysis`
    *   **Description:** Results from simulations run with varying starting bankrolls to determine survival rates.
    *   **Columns:**
        *   `Strategy_Name`
        *   `Starting_Bankroll_Tested`
        *   `Survival_Rate_Percentage`
        *   `Recommended_Optimal_Starting_Bankroll` (based on a defined survival threshold)

**Visualizations:**
1.2.12  **Bankroll Fluctuation Over Time:**
    *   **Type:** Line Chart
    *   **Description:** X-axis: `Session_Number` (or `Cumulative_Rolls`), Y-axis: `Current_Bankroll` (or `Cumulative_Net_Profit_Loss`). Multiple lines, each representing a different strategy, showing long-term bankroll trends and volatility. A separate view could show individual session bankroll fluctuations.
1.2.13  **Cumulative EV Evolution:**
    *   **Type:** Line Chart
    *   **Description:** X-axis: `Session_Number` (or `Cumulative_Rolls`), Y-axis: `Cumulative_Empirical_EV`. Each line represents a strategy, showing how its EV converges or fluctuates over the simulation.
1.2.14.  **Risk vs. Return Scatter Plot:**
    *   **Type:** Scatter Plot
    *   **Description:** X-axis: `Risk_Of_Ruin_Percentage`, Y-axis: `Empirical_EV_Per_Dollar_Risked`. Each point is a strategy. Bubble size or color could represent `Standard_Deviation_Of_Session_ProfitLoss` or `Max_Drawdown_Percentage`. This helps identify strategies with the best balance.
1.2.15.  **Target Reach & Ruin Frequency:**
    *   **Type:** Grouped Bar Chart
    *   **Description:** For each strategy, grouped bars showing `Percentage_Sessions_Target_Reached_130%`, `Percentage_Sessions_Target_Reached_200%`, and `Risk_Of_Ruin_Percentage`.
1.2.16.  **Optimal Starting Bankroll:**
    *   **Type:** Line Chart
    *   **Description:** X-axis: `Starting_Bankroll_Tested`, Y-axis: `Survival_Rate_Percentage`. Each line represents a strategy, showing how survival rate changes with starting bankroll.


### 1.3 Hedging Analytics
**Analytical Questions Addressed:**
1.3.1 What amount of hedging is used in each strategy?
1.3.2 How does hedging bets impact overall win rate, profitability, drawdown, expected value, and volatility for a given strategy?
1.3.3 How does the size and timing of placing or removing hedging bets affect overall profitability?
1.3.4 How does  hedging impact the effective house edge for a given strategy?

**Tabular Summary:**
1.3.5   **Table Name:** `Hedging_Impact_And_Usage`
*   **Description:** Compares the performance of strategies with and without hedging (or different hedging levels) and quantifies hedging usage.
*   **Columns:**
    *   `Strategy_Name`
    *   `Hedging_Configuration` (e.g., "No Hedging", "Hedging Level A", "Hedging Level B")
    *   `Total_Hedging_Dollars_Placed`
    *   `Percentage_Of_Total_Bets_As_Hedging`
    *   `Avg_Net_Profit_Loss_Per_Session`
    *   `Empirical_EV_Per_Dollar_Risked`
    *   `Win_Rate_Percentage`
    *   `Max_Drawdown_Percentage`
    *   `Standard_Deviation_Of_Session_ProfitLoss`
    *   `Effective_House_Edge`

**Visualizations:**
1.3.6  **Hedging Impact Comparison:**
    *   **Type:** Grouped Bar Charts or Radar Chart
    *   **Description:** For each strategy, compare key metrics (e.g., `Avg_Net_Profit_Loss_Per_Session`, `Empirical_EV_Per_Dollar_Risked`, `Win_Rate_Percentage`, `Max_Drawdown_Percentage`, `Effective_House_Edge`) across different `Hedging_Configuration` levels. A radar chart could show the overall profile change due to hedging.
1.3.7  **Hedging Usage:**
    *   **Type:** Bar Chart
    *   **Description:** Compares `Percentage_Of_Total_Bets_As_Hedging` across strategies or hedging configurations.
1.3.8  **Hedging Action Profitability (Detailed):**
    *   **Type:** Scatter Plot or Heatmap (if granular data is available)
    *   **Description:** (This visualization might require more detailed simulation logging than the summary table provides). X-axis: `Hedging_Amount`, Y-axis: `Average_Profit_Loss_From_Hedging_Action`, with points colored by `Timing_Condition`. This is for deep-dive analysis into specific hedging mechanics.

### 1.4. Comparison Analytics:
**Analytical Questions Addressed:**
1.4.1 How does a custom strategy perform against a simple baseline strategy (e.g., always betting the pass line)?
1.4.2 How do strategies compare (e.g., IronCross, HammerLock, my custom strategies) compare to each other in terms of profitability and risk?
1.4.3 How do different strategies compare in terms of average p(win), net profit, risk, hourly dollar win/loss rate, expected value, drawdown, and bankroll volatility? 
1.4.4 Which strategy has the highest probability of reaching a specific profit target (e.g., doubling the initial bankroll)?
Which strategy offers the highest Expected Value per unit of risk (e.g., EV per standard deviation of profit/loss)?



**Tabular Summary:**
1.4.5   **Table Name:** `Comprehensive_Strategy_Comparison`
*   **Description:** A single, comprehensive table for comparing all strategies across all key performance and risk metrics. This combines relevant columns from `Strategy_Performance_Summary` and `Strategy_Risk_Profile`, and adds hourly rates.
*   **Columns:**
    *   `Strategy_Name`
    *   `Avg_Net_Profit_Loss_Per_Session`
    *   `Empirical_EV_Per_Dollar_Risked`
    *   `Win_Rate_Percentage`
    *   `Risk_Of_Ruin_Percentage`
    *   `Standard_Deviation_Of_Session_ProfitLoss`
    *   `Max_Drawdown_Percentage`
    *   `Avg_Rolls_Per_Session`
    *   `Hourly_Dollar_Win_Loss_Rate` (Calculated based on `Avg_Net_Profit_Loss_Per_Session` and `Avg_Rolls_Per_Session` assuming 60-120 rolls/hour)
    *   `Percentage_Sessions_Target_Reached_200%` (Example profit target)
    *   `EV_Per_Unit_Risk`

**Visualizations:**
1.4.6  **Multi-Strategy Performance Radar Chart:**
    *   **Type:** Radar Chart
    *   **Description:** Each spoke represents a key metric (e.g., `Avg_Net_Profit_Loss_Per_Session`, `Empirical_EV_Per_Dollar_Risked`, `Win_Rate_Percentage`, `Risk_Of_Ruin_Percentage`, `Max_Drawdown_Percentage`, `Hourly_Dollar_Win_Loss_Rate`, `EV_Per_Unit_Risk`). Each line on the chart represents a strategy, allowing for a quick visual comparison of their overall profiles and trade-offs.
1.4.7  **Parallel Coordinates Plot:**
    *   **Type:** Parallel Coordinates Plot
    *   **Description:** Each vertical axis represents a metric from the `Comprehensive_Strategy_Comparison` table. Each line represents a strategy, connecting its values across all metrics. This is excellent for identifying clusters of similar strategies, outliers, and complex relationships between multiple variables.
1.4.8  **Top Strategies by Specific Metric:**
    *   **Type:** Bar Chart (Ranked)
    *   **Description:** Separate bar charts for specific "best" questions, e.g., a bar chart showing `Percentage_Sessions_Target_Reached_200%` for each strategy (highest probability of reaching profit target), or a bar chart showing `EV_Per_Unit_Risk` (highest EV per unit of risk).




## 2.0 Metrics and Data required to support analytics and visualizations

The metrics are derived from the analytical questions and tabular summaries outlined in your request.

### 2.1 Metrics to Support Analytics

**2.1.1. Overall Strategy Performance and Profitability Metrics:**
*   [`Avg_Net_Profit_Loss_Per_Session`](metrics.md#Avg_Net_Profit_Loss_Per_Session)
*   [`Empirical_EV_Per_Dollar_Risked`](metrics.md#Empirical_EV_Per_Dollar_Risked)
*   [`Win_Rate_Percentage`](metrics.md#Win_Rate_Percentage)
*   [`Loss_Rate_Percentage`](metrics.md#Loss_Rate_Percentage)
*   [`Push_Rate_Percentage`](metrics.md#Push_Rate_Percentage)
*   [`Total_Sessions_Simulated`](metrics.md#Total_Sessions_Simulated)
*   [`Total_Dollars_Risked_Overall`](metrics.md#Total_Dollars_Risked_Overall)

**2.1.2. Risk and Volatility / Bankroll Management Metrics:**
*   [`Risk_Of_Ruin_Percentage`](metrics.md#Risk_Of_Ruin_Percentage)
*   [`Standard_Deviation_Of_Session_ProfitLoss`](metrics.md#Standard_Deviation_Of_Session_ProfitLoss)
*   [`Max_Drawdown_Percentage`](metrics.md#Max_Drawdown_Percentage)
*   [`Percentage_Sessions_Target_Reached_130%`](metrics.md#Percentage_Sessions_Target_Reached_130%)
*   [`Percentage_Sessions_Target_Reached_200%`](metrics.md#Percentage_Sessions_Target_Reached_200%)
*   [`Percentage_Sessions_Ending_In_Profit`](metrics.md#Percentage_Sessions_Ending_In_Profit)
*   [`Avg_Sessions_To_Ruin`](metrics.md#Avg_Sessions_To_Ruin)
*   [`EV_Per_Unit_Risk`](metrics.md#EV_Per_Unit_Risk)
*   [`Cumulative_Net_Profit_Loss`](metrics.md#Cumulative_Net_Profit_Loss) (for trajectory)
*   [`Cumulative_Dollars_Risked`](metrics.md#Cumulative_Dollars_Risked) (for trajectory)
*   [`Cumulative_Empirical_EV`](metrics.md#Cumulative_Empirical_EV) (for trajectory)
*   [`Survival_Rate_Percentage`](metrics.md#Survival_Rate_Percentage) (for optimal bankroll analysis)

**2.1.3. Hedging Analytics Metrics:**
*   [`Total_Hedging_Dollars_Placed`](metrics.md#Total_Hedging_Dollars_Placed)
*   [`Percentage_Of_Total_Bets_As_Hedging`](metrics.md#Percentage_Of_Total_Bets_As_Hedging)
*   [`Effective_House_Edge`](metrics.md#Effective_House_Edge)

**4. Comparison Analytics Metrics:**
*   [`Avg_Rolls_Per_Session`](metrics.md#Avg_Rolls_Per_Session)
*   [`Hourly_Dollar_Win_Loss_Rate`](metrics.md#Hourly_Dollar_Win_Loss_Rate)

### 2.2 Data to Record During Simulations

To compute the above metrics, the simulation logging system should capture the following raw data points at different granularities:

**2.2.1. Simulation-Level Data (recorded once per simulation run):**
*   `Simulation_ID`: A unique identifier for each complete simulation run.
*   `Strategy_Name`: The name of the strategy being simulated.
*   `Player_ID`: Identifier for the player(s) involved in the simulation.
*   `Starting_Bankroll_For_Simulation`: The initial bankroll of the player(s) at the start of the entire simulation.
*   `Total_Sessions_Simulated`: The total number of sessions executed within this simulation.
*   `Total_Rolls_Simulated`: The cumulative number of dice rolls across all sessions in this simulation.
*   `Simulation_End_Bankroll`: The player's final bankroll at the conclusion of the entire simulation.
*   `Did_Ruin_Occur_In_Simulation`: A boolean flag indicating if the player's bankroll reached zero at any point during the simulation.
*   `Session_Number_Of_Ruin`: The specific session number in which the bankroll reached zero, if ruin occurred.

**2.2.2. Session-Level Data (recorded once per session):**
*   `Session_ID`: A unique identifier for each session within a simulation.
*   `Simulation_ID`: A foreign key linking to the parent simulation.
*   `Session_Number`: The sequential number of the session within its parent simulation.
*   `Starting_Bankroll_Session`: The player's bankroll at the beginning of this specific session.
*   `Ending_Bankroll_Session`: The player's bankroll at the end of this specific session.
*   `Net_Profit_Loss_Session`: The difference between `Ending_Bankroll_Session` and `Starting_Bankroll_Session`.
*   `Session_Outcome`: A categorical value (e.g., "Win", "Loss", "Push") based on `Net_Profit_Loss_Session`.
*   `Total_Rolls_In_Session`: The total number of dice rolls that occurred during this session.
*   `Total_Dollars_Risked_In_Session`: The sum of all initial bet amounts placed by the player within this session.
*   `Max_Bankroll_During_Session`: The highest bankroll achieved by the player at any point during this session.
*   `Min_Bankroll_During_Session`: The lowest bankroll reached by the player at any point during this session.
*   `Did_Target_130_Reach`: A boolean indicating if the player's bankroll reached 130% of their `Starting_Bankroll_For_Simulation` at any point during this session.
*   `Did_Target_200_Reach`: A boolean indicating if the player's bankroll reached 200% of their `Starting_Bankroll_For_Simulation` at any point during this session.
*   `Total_Hedging_Dollars_Placed_In_Session`: The cumulative amount of money placed on bets identified as "hedging" within this session.
*   `Total_Bets_Placed_In_Session`: The cumulative amount of money placed on all bets (hedging and non-hedging) within this session.

**2.2.3. Roll-Level Data (recorded after each dice roll within a session):**
*   `Roll_ID`: A unique identifier for each individual dice roll.
*   `Session_ID`: A foreign key linking to the parent session.
*   `Simulation_ID`: A foreign key linking to the parent simulation.
*   `Roll_Number_In_Session`: The sequential number of the roll within its parent session.
*   `Dice_Roll_Value`: The sum of the dice for this specific roll.
*   `Current_Bankroll_After_Roll`: The player's bankroll immediately after all bets are resolved for this roll.
*   `Cumulative_Net_Profit_Loss_Session_To_Roll`: The cumulative net profit/loss from the start of the session up to this roll.
*   `Cumulative_Dollars_Risked_Session_To_Roll`: The cumulative total dollars risked from the start of the session up to this roll.
*   `Point_Status_After_Roll`: The status of the point after this roll (e.g., "Off", "On", "ComeOut").

**2.2.4. Bet-Level Data (recorded for each bet placement and resolution):**
*   `Bet_Event_ID`: A unique identifier for each bet-related event (placement or resolution).
*   `Bet_ID`: A unique identifier for the specific instance of the bet.
*   `Session_ID`: A foreign key linking to the parent session.
*   `Simulation_ID`: A foreign key linking to the parent simulation.
*   `Player_ID`: A foreign key linking to the player who placed the bet.
*   `Event_Type`: Indicates whether the event is "Place" (bet placed) or "Resolve" (bet resolved).
*   `Bet_Type`: The specific type of bet (e.g., "Pass Line", "Come", "Place 6", "Crap Check").
*   `Bet_Amount`: The amount of money placed on the bet.
*   `Is_Hedging_Bet`: A boolean flag indicating if this bet is considered a hedging bet (requires definition within the strategy).
*   `Roll_Number_When_Event_Occurred`: The roll number during which the bet was placed or resolved.
*   `Profit_Loss_From_Bet_Resolution`: (Applicable only for "Resolve" events) The net profit or loss generated by this specific bet.

This detailed specification of metrics and data points will enable the development of a robust simulation logging system capable of supporting all the desired analytical questions, tabular summaries, and visualizations.