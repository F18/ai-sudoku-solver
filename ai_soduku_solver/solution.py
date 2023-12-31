import utils

row_units = [utils.cross(r, utils.cols) for r in utils.rows]
column_units = [utils.cross(utils.rows, c) for c in utils.cols]
square_units = [
    utils.cross(rs, cs) for rs in ("ABC", "DEF", "GHI") for cs in ("123", "456", "789")
]
unitlist = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
unitlist = unitlist


# Must be called after all units (including diagonals) are added to the unitlist
units = utils.extract_units(unitlist, utils.boxes)
peers = utils.extract_peers(units, utils.boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    This solution processes all pairs of naked twins from the input once.

    Pseudocode for this algorithm on github:

    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """

    v_out = values.copy()
    for box_a in values:
        for box_b in peers[box_a]:
            if values[box_a] == values[box_b] and len(values[box_a]) == 2:
                intersection = [x for x in peers[box_a] if x in peers[box_b]]
                for peer in intersection:
                    for digit in values[box_a]:
                        v_out[peer] = v_out[peer].replace(digit, "")

    return v_out


def eliminate(values: dict) -> dict:
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """

    solved_boxes: list = [box for box in units if len(values[box]) == 1]

    for box in solved_boxes:
        solved_value: int = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(solved_value, "")

    return values


def only_choice(values: dict) -> dict:
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """

    for unit in unitlist:
        for digit in "123456789":
            # For the given digit, find all boxes that contain the digit in their values
            dplaces: list = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                # If the digit appears in only one location, then it is the only choice
                values[dplaces[0]] = digit

    return values


def reduce_puzzle(values: dict) -> dict | bool:
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable
    """
    stalled: bool = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before: int = len(
            [box for box in values.keys() if len(values[box]) == 1]
        )

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after: int = len(
            [box for box in values.keys() if len(values[box]) == 1]
        )
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values: dict) -> dict | bool:
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """

    # First, reduce the puzzle using the previous function
    reduced_values = reduce_puzzle(values)

    # Return Statements
    # -----------------
    # Check if reduce_puzzle was unsuccessful
    if reduced_values is False:
        return False

    values = reduced_values
    # Check is all lengths are 1, then puzzle is solved!
    if all(len(values[s]) == 1 for s in utils.boxes):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    unsolved_values = {key: value for key, value in values.items() if len(value) != 1}
    sorted_values = sorted(
        unsolved_values.keys(), key=lambda key: len(unsolved_values[key])
    )
    s = sorted_values[0]

    # Recursively solve for each character in unfilled square's string representation
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        # Recursive call:
        # --------------
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = utils.grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = "2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3"
    utils.display(utils.grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    utils.display(result)

    try:
        import PySudoku

        PySudoku.play(utils.grid2values(diag_sudoku_grid), result, utils.history)

    except Exception as e:
        if type(e).__name__ == "SystemExit":
            pass
        else:
            print(
                "We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement."
            )
