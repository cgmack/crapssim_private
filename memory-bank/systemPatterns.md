# System Patterns

## System Architecture
CrapsSim follows a modular architecture, primarily composed of the following key components:

- **Table Module**: Manages the state of the craps table, including the point, active bets, and player bankrolls. It orchestrates the game flow.
- **Dice Module**: Handles dice rolling mechanics, including generating random numbers and summing dice.
- **Bet Module**: Defines various types of craps bets, their rules, payouts, and resolution logic. Each bet type is an independent entity.
- **Player/Strategy Module**: Encapsulates player behavior and betting strategies. Strategies interact with the table to place and remove bets based on game state.
- **Simulation Engine**: The core orchestrator that runs multiple game iterations, collects data, and manages the overall simulation process.

## Key Technical Decisions
- **Object-Oriented Design**: Core entities like `Dice`, `Bet`, `Table`, and `Player` are implemented as classes to promote encapsulation, reusability, and maintainability.
- **Strategy Pattern**: Betting strategies are designed as interchangeable components, allowing users to easily plug in new strategies without modifying the core simulation logic.
- **Event-Driven Simulation (Implicit)**: While not a formal event bus, the interaction between components (e.g., dice roll triggering bet resolution) can be thought of as an implicit event-driven system.
- **Data Collection**: Simulation data is collected incrementally during runtime and aggregated for post-simulation analysis.

## Design Patterns in Use
- **Strategy Pattern**: Evident in the `crapssim/strategy` module, where different betting strategies can be implemented and swapped.
- **Singleton Pattern (Potential)**: The `Table` or `Dice` might implicitly act as singletons if only one instance is ever needed globally, though explicit enforcement might not be necessary in Python. (Note: This is a potential pattern, not necessarily explicitly implemented as a strict singleton).
- **Observer Pattern (Potential)**: Could be used for bets to "observe" table state changes (e.g., point being set/off) and react accordingly. Currently, this is handled by direct calls from the `Table` module.

## Component Relationships
- `Table` interacts with `Dice` to get roll outcomes.
- `Table` manages `Bet` objects, resolving them based on dice rolls and point state.
- `Player`/`Strategy` interacts with `Table` to place and remove `Bet`s.
- The `Simulation Engine` orchestrates `Table` and `Player` interactions over multiple iterations.

## Critical Implementation Paths
- **Dice Roll to Bet Resolution**: The sequence from a dice roll, updating the table state, and then resolving all active bets is a critical path that must be robust and accurate.
- **Strategy Execution**: The logic within strategies for deciding when and what to bet is central to the simulation's purpose.
- **Data Aggregation**: Ensuring that simulation results are correctly collected and stored for analysis.
- **Unit Tests**: Thorough test coverage of each and every component and bet type. 
- **Integration Tests**: Thorough test coverage of Component Relationships
- **Strategy Tests**: Test data and test drivers (fixed runs) to test all scenarios for standard and custom strategies.