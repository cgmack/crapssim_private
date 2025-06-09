# Material Decisions

## AI Code Generation
* This project will use LLMs to generate code. 
* A structured Memory Bank with specific core files was made to ensure comprehensive and consistent project documentation from the outset. This will serve as a reliable source of truth for all future development and analysis tasks.

## Upstream Dependency on the original Crapssim
* This project will use the upstream repository is the open source project [crapssim](https://github.com/skent259/crapssim).
* We will ocasionally pull new updates from this project. 
* We expect to diverge significantly from this baseline over time. To avoid conflicts, we should extend code instead of rewriting code when possible.
* We don't plan to contribute our changes back to the upstream project at this time.
