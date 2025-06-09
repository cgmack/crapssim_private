# Product Context

## Why CrapsSim Exists
CrapsSim was created to address the need for a reliable and flexible tool to simulate the game of craps. Users want to develop and test strategies to play at the casino that are fun and maximize returns while limiting downside losses. Existing tools were often limited in their ability to define custom strategies and provide detailed performance analysis. CrapsSim aims to fill this gap by offering a robust, extensible, and analytical platform for craps enthusiasts, strategists, and analysts.

## Problems It Solves
- **Strategy Validation**: Allows users to test and validate their craps betting strategies in a simulated environment without financial risk. When playing craps in a casino, there are unlimited combinations of ways that that players can place their bets. But, with this freedom comes complexity, and players deserve to know how a strategy could perform in each session. 
- **Risk Assessment**: Helps in understanding the inherent risks and rewards associated with different betting patterns. The crampsim package is designed answer these tough questions: What's a fun strategy involving multiple numbers where the house edge doesn't increase too much? How can I best balance risk for and against the 7? Does hedging my bet improve my net winnings? What strategy has the highest upswing where I can capture a win and walk away?
- **Probability Exploration**: Provides a practical way to explore the probabilities and statistical outcomes of various game scenarios. For example, what is the Expected Value of vairous stategies, what is the distribution of outcomes for a given strategy? 
- **Optimization**: Enables strategists to optimize their approaches by analyzing simulation results and refining their betting logic. 
- **Comprehensive Analytics**: Provides detailed metrics and visualizations to answer specific analytical questions about strategy performance, risk, hedging, and comparisons. (Refer to [`memory-bank/analyticsRequirements.md`](memory-bank/analyticsRequirements.md) for full details.)

## How It Should Work
The foundation of CrapsSim is a library that can be integrated into other Python applications. Users will define their strategies using Python code, which will then be executed by the simulation engine. The simulation will track game state, dice rolls, and bet resolutions, accumulating data for post-simulation analysis. Additional application layers (e.g. GUI) will enable other access and workflows in the future.

## User Experience Goals
- **Accurate and Reliablen**: Basic table mechanics and building should be tested extensively. Robust logic should exist to prevent invalid scenarios (invalid bets, incorrect payouts). Strategies should have their own test scenarios (fixed runs) and outcome validation to ensure they are operating correctly under all scenarios. Trust in the game outcomes is of utmost importance. 
- **Clear Simulation Output**: The simulation should provide clear and understandable output, detailing game progression and key events.
- **Actionable Analysis**: The results of simulations should be presented in a way that allows users to easily interpret performance metrics and make informed decisions about their strategies.
- **Documentation**: Clear and concise developer documentation must exists. APIs should be well documents. How to guides should guide users through strategy definition, simulation execution, and results interpretation.

## High-level overview of what you’re building
 - Crapsim is a python package which runs all of the necessary elements of a Craps table. The package follows some natural logic:
   - a Table has Player(s) and Dice on it
   - the Player(s) have Bet(s) on the Table
   - each Player's Strategy can automatically set up Bet(s)
 - With these building blocks, crapssim supports
   - running 1 session with 1 player/strategy to test a realistic day at the craps table,
   - running many sessions with 1 player/strategy to understand how a strategy performs in the long term, or
   - running many sessions with many players/strategies to simulate how they compare to each other
 - Strategies
   - In the crapssim package, a strategy is just a set of rules to describe exactly how a player will bet under any table situation. Put another way, the strategies are the primary way that a Player object (with their bankroll and bets) interacts with the Table object (with the dice, point, and other table features). We can simulate how one or many sessions would play out with the selected strategy, to understand if it fits out playing style, objectives, and compares favorably to other strategies.
 - We have created a number of popular strategies like IronCross and HammerLock as well as innovative custom strategies. We run these strategies 100,000’s of times and analyze the results to find the best strategies to meet our goals. 
 - Simulations 
   - Configuration
      - Table
         - Table settings
              - Players 
              - Starting Bankroll
      - Strategy
        - Strategy Settings 
        - Base bet
        - Etc.
        - Dice roll
        - Finish shooter T/F
   - Summary stats
     - Start time, end time
     - Roll count
     - Player count 
     - Total Sessions 
     - Total Dice rolls
     - Totals start bankroll
     - Total end 
     - Players
     - Sessions
     - Dice rolls
     - Ending balance
   - Logs
