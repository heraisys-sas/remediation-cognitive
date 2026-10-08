from pathlib import Path
import sys

# Les solveurs historiques restent également utilisables comme scripts CLI.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
