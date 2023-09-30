import utils


def get_unitlist():
    row_units = [utils.cross(r, utils.cols) for r in utils.rows]
    column_units = [utils.cross(utils.rows, c) for c in utils.cols]
    square_units = [
        utils.cross(rs, cs)
        for rs in ("ABC", "DEF", "GHI")
        for cs in ("123", "456", "789")
    ]

    unitlist = row_units + column_units + square_units

    return unitlist


def get_unitlist_with_diagonal():
    unitlist = get_unitlist()

    diagonal_1 = [[c1 + c2 for c1, c2 in zip("ABCDEFGHI", "123456789")]]
    diagonal_2 = [[c1 + c2 for c1, c2 in zip("ABCDEFGHI", "987654321")]]

    unitlist += diagonal_1 + diagonal_2

    return unitlist


def get_units_and_peers(unitlist):
    units = utils.extract_units(unitlist, utils.boxes)
    peers = utils.extract_peers(units, utils.boxes)

    return units, peers


def eliminate(values: dict, units, peers) -> dict:
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}
    units(dict)
        a dictionary with a key for each box (string) whose value is a list
        containing the units that the box belongs to (i.e., the "member units")
    peers(dict)
        a dictionary with a key for each box (string) whose value is a set
        containing all boxes that are peers of the key box (boxes that are in a unit
        together with the key box)

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


def only_choice(values: dict, unitlist) -> dict:
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}
    unitlist(list)
        a list of dictionaries containing all of the units in puzzle

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


def reduce_puzzle(values: dict, unitlist, units, peers) -> dict | bool:
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}
    unitlist(list)
        a list of dictionaries containing all of the units in puzzle
    units(dict)
        a dictionary with a key for each box (string) whose value is a list
        containing the units that the box belongs to (i.e., the "member units")
    peers(dict)
        a dictionary with a key for each box (string) whose value is a set
        containing all boxes that are peers of the key box (boxes that are in a unit
        together with the key box)

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
        values = eliminate(values, units, peers)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values, unitlist)

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


def search(values: dict, unitlist, units, peers) -> dict | bool:
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}
    unitlist(list)
        a list of dictionaries containing all of the units in puzzle
    units(dict)
        a dictionary with a key for each box (string) whose value is a list
        containing the units that the box belongs to (i.e., the "member units")
    peers(dict)
        a dictionary with a key for each box (string) whose value is a set
        containing all boxes that are peers of the key box (boxes that are in a unit
        together with the key box)

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
    reduced_values = reduce_puzzle(values, unitlist, units, peers)

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
        attempt = search(new_sudoku, unitlist, units, peers)
        if attempt:
            return attempt


def naked_twins(values, peers):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}
    peers(dict)
        a dictionary with a key for each box (string) whose value is a set
        containing all boxes that are peers of the key box (boxes that are in a unit
        together with the key box)

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


def solve(grid, unitlist, units, peers):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    unitlist(list)
        a list of dictionaries containing all of the units in puzzle
    units(dict)
        a dictionary with a key for each box (string) whose value is a list
        containing the units that the box belongs to (i.e., the "member units")
    peers(dict)
        a dictionary with a key for each box (string) whose value is a set
        containing all boxes that are peers of the key box (boxes that are in a unit
        together with the key box)

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = utils.grid2values(grid)
    values = search(values, unitlist, units, peers)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = "2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3"
    utils.display(utils.grid2values(diag_sudoku_grid))

    unitlist = get_unitlist_with_diagonal()
    units, peers = get_units_and_peers(unitlist)
    result = solve(diag_sudoku_grid, unitlist, units, peers)
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
