# Material Decisions

## AI Code Generation
* This project will use LLMs to generate code. 
* A structured Memory Bank with specific core files was made to ensure comprehensive and consistent project documentation from the outset. This will serve as a reliable source of truth for all future development and analysis tasks.

## Upstream Dependency on the original Crapssim
* This project will use the upstream repository is the open source project [crapssim](https://github.com/skent259/crapssim).
* We will ocasionally pull new updates from this project. 
* We expect to diverge significantly from this baseline over time. To avoid conflicts, we should extend code instead of rewriting code when possible.
* We don't plan to contribute our changes back to the upstream project at this time.

## GUI Technology Stack
*   **Frontend Framework:** React
*   **Backend API Framework:** Python Flask/FastAPI
*   **API Design:** Multiple specialized endpoints for each report/visualization (e.g., `/api/strategy-performance`, `/api/risk-profile`)
*   **Data Visualization Library:** Plotly.js for its strong interactive and scientific charting capabilities

## GUI Requirements Definition
*   **Date:** 6/10/2025
*   **Decision:** Proceeding with detailed GUI requirements definition based on `analyticsRequirements.md`.
*   **Context:** The existing `analyticsRequirements.md` provides high-level analytical needs. More granular GUI specifications are required for phased development.
*   **Outcome:** Detailed GUI components, layouts, and interactions have been proposed for the "Strategy Report Card," "Central Dashboard," "Deep Dive Comparisons," and "Dice Roll/Hedge Analysis" views. High-level backend API requirements for data serving have also been outlined.
*   **Technology Notes:** Frontend will utilize React (existing setup). Backend API will be built with Flask/Python.

## Strategy and Simulation Relationship
*   **Date:** 6/10/2025
*   **Decision:** To accurately represent the relationship between strategies and simulations, and to accommodate strategy-specific input parameters, a new `strategy_configurations` table will be introduced in the database schema. The `simulations` table will now link to this new table via a foreign key.
*   **Context:** The GUI design necessitates a clear understanding of which specific strategy (including its parameters) was used for each simulation run. The previous schema only stored `Strategy_Name` in the `simulations` table, which is insufficient for distinguishing between simulations of the same strategy with different parameters.
*   **Outcome:** The database schema will be updated to include `strategy_configurations` table, and the `simulations` table will be modified to reference `Strategy_Config_ID`. This will allow for more precise tracking and analysis of simulation results based on specific strategy configurations.
