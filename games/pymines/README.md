# pymines

A simple Minesweeper game implementation using Python and Matplotlib.

## Features

- Classic Minesweeper gameplay
- Three difficulty levels: Beginner, Intermediate, and Expert
- Custom game settings with adjustable width, height, and mine count
- Mouse controls: Left-click to reveal cells, right-click to place flags
- Keyboard shortcuts: F2 to start a new game

## Installation

Install directly from the source directory:

```bash
pip install .
```

This will install all required dependencies automatically.

### Optional Dependencies

For specific matplotlib backends:

```bash
pip install ".[qt_backend]"    # For PyQt6 backend
pip install ".[webagg_backend]"  # For web-based backend
```

## Usage

After installation, run the game:

```bash
pymines
```

Or run directly from the source:

```bash
python pymines.py
```

Choose a difficulty level:

```bash
pymines -l b  # Beginner: 8x8 grid with 10 mines
pymines -l i  # Intermediate: 16x16 grid with 40 mines
pymines -l e  # Expert: 30x16 grid with 99 mines
```

Create a custom game:

```bash
pymines -c 20 15 50  # 20x15 grid with 50 mines
```

## Controls

- **Left-click**: Reveal a cell
- **Right-click**: Place/remove a flag
- **F2**: Start a new game

## Requirements

- Python 3.11+
- NumPy
- Matplotlib
