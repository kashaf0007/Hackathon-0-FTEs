"""Entry point for Bronze Tier Constitutional FTE.

Starts the orchestrator that monitors tasks, enforces approval boundaries,
and logs all operations.
"""

from src.orchestrator.main import main

if __name__ == "__main__":
    main()
