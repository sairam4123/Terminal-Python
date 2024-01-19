from io import StringIO

from typing import Generator, Sequence, SupportsInt
from itertools import zip_longest

import keyboard

from terminal import Font, terminal_cursor


def replace_none_with[
    T
](*vals: Sequence[T | None], fillvalue: T = "") -> Generator[tuple[T, ...], None, None]:
    for val in vals:
        yield tuple((fillvalue if col is None else col) for col in val)


def replace_none[
    T
](*vals: T | None | Sequence[T | None], fillvalue: T = "") -> Generator[T, None, None]:
    if isinstance(vals[0], Sequence):
        for val in vals:
            yield type(val)((fillvalue if col is None else col) for col in val)
    else:
        yield from ((fillvalue if col is None else col) for col in vals)


string = "─│┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬"


class Table:
    def __init__(self, *values) -> None:
        self.values = values
        self.headings = None
        self.padding = 2
        self.empty_default = " "
        self.empty_heading = "Untitled"

    def with_headings(self, *headings):
        self.headings = headings
        return self

    def with_padding(self, padding: int = 2):
        self.padding = padding or self.padding
        return self

    def with_default(self, empty_default=""):
        self.empty_default = empty_default or self.empty_default
        return self

    def with_default_heading(self, empty_heading: str = ""):
        self.empty_heading = empty_heading
        return self

    def __str__(self) -> str:
        return tabulates(
            *self.values,
            padding=self.padding,
            headings=self.headings,
            empty_default=self.empty_default,
            empty_heading=self.empty_heading,
        ).strip()


def tabulate(*values: Sequence[str | None]):
    return Table(*values)


def _tabulate(
    *_values: Sequence[str | None],
    selected_cell: tuple[int, int] | None = (0, 0),
    highlight_cell: tuple[int, int] | None = (0, 0),
    padding: SupportsInt = 2,
    headings: Sequence[str | None] | None = None,
    empty_default: str = " ",
    empty_heading: str = "Untitled",
    file=None,
):
    # from t import print
    headings = headings or []
    vals: Sequence[Sequence[str]] = list(
        zip_longest(
            *zip_longest(
                *replace_none(*_values, fillvalue=empty_default),
                fillvalue=empty_default,
            ),
            fillvalue=empty_default,
        )
    )
    if headings:
        vals: Sequence[Sequence[str]] = list(
            zip_longest(
                replace_none(*headings, fillvalue=empty_heading),
                *vals,
                fillvalue=empty_default,
            )
        )
    t_values: Sequence[Sequence[str]] = list(zip(*vals))

    sizes = _calculate_sizes(*vals, padding=padding)
    print("╔" + "╤".join(["═" * size for size in sizes]) + "╗", file=file)
    for row_idx, row in enumerate(t_values):
        print("║", end="", file=file)
        for col_idx, (size, col) in enumerate(zip(sizes, row)):
            if row_idx < 1 and headings:
                print("\033[1m" + col.center(size), end="\033[0m", file=file)
            elif (col_idx, row_idx) == selected_cell:
                print(
                    "\033[45m"
                    + Font.bold_font
                    + Font.underline_font
                    + col.center(size, " ")
                    + "​",
                    end="\033[0m",
                    file=file,
                )
            elif (col_idx, row_idx) == highlight_cell:
                print(
                    "\033[41m" + Font.bold_font + col.center(size),
                    end="\033[0m",
                    file=file,
                )
            else:
                print(col.center(size), end="", file=file)

            if col_idx < (len(t_values[row_idx]) - 1):
                print("│", end="", file=file)
        print("║", file=file)
        if row_idx < 1 and headings:
            print("╠" + "╪".join(["═" * size for size in sizes]), end="╣\n", file=file)
        elif row_idx < len(vals[0]) - 1:
            print("╟" + "┼".join(["─" * size for size in sizes]), end="╢\n", file=file)

    print("╚" + "╧".join(["═" * size for size in sizes]) + "╝", file=file)
    return file


def tabulates(
    *values: Sequence[str | None],
    padding: SupportsInt = 2,
    headings: Sequence[str | None] | None = None,
    empty_default: str = " ",
    **kwargs,
) -> str:
    print(values)
    highlight_cell: tuple[int, int] | None = (0, 0)
    selected_cell: tuple[int, int] | None = None
    key_pressed = False
    selected = False
    value_entered = False

    closed = False

    max_lens = len(values), max(len(value) for value in values)

    values: Sequence[Sequence[str]] = list(
        zip_longest(
            *zip_longest(
                *replace_none(*values, fillvalue=None),
                fillvalue=None,
            ),
            fillvalue=None,
        )
    )
    if headings:
        values: Sequence[Sequence[str]] = list(
            zip_longest(
                replace_none(*headings, fillvalue=None),
                *values,
                fillvalue=None,
            )
        )

    list_values = []
    for val in values:
        list_value = []
        for col in val:
            list_value.append(col)
        list_values.append(list_value)

    values = list_values

    def up_arrow_event():
        nonlocal key_pressed, highlight_cell
        if not highlight_cell:
            return
        highlight_cell = (highlight_cell[0], (highlight_cell[1] - 1) % max_lens[1])
        key_pressed = True

    def down_arrow_event():
        nonlocal key_pressed, highlight_cell
        if not highlight_cell:
            return
        highlight_cell = (highlight_cell[0], (highlight_cell[1] + 1) % max_lens[1])
        key_pressed = True

    def left_arrow_event():
        nonlocal key_pressed, highlight_cell
        if not highlight_cell:
            return
        highlight_cell = ((highlight_cell[0] - 1) % max_lens[0], highlight_cell[1])
        key_pressed = True

    def right_arrow_event():
        nonlocal key_pressed, highlight_cell
        if not highlight_cell:
            return
        highlight_cell = ((highlight_cell[0] + 1) % max_lens[0], highlight_cell[1])
        key_pressed = True

    def enter_event():
        nonlocal values, key_pressed, selected_cell, highlight_cell, selected, value_entered
        if selected and selected_cell and not value_entered:
            value_entered = True
            key_pressed = True
            value: str = ""
            ch = ""
            print(keyboard.read_key(True))
            values[selected_cell[0]][selected_cell[1]] = value + "col"
            value_entered = False
            return

        elif not selected or selected_cell:
            selected_cell = highlight_cell
            highlight_cell = None
            selected = True
            key_pressed = True

        print("Test")

    def escape_event():
        nonlocal key_pressed, selected_cell, highlight_cell, selected, closed
        if not selected:
            closed = True
        highlight_cell = selected_cell
        selected_cell = None
        selected = False
        key_pressed = True

    keyboard.add_hotkey("up", up_arrow_event, suppress=True)
    keyboard.add_hotkey("down", down_arrow_event, suppress=True)
    keyboard.add_hotkey("left", left_arrow_event, suppress=True)
    keyboard.add_hotkey("right", right_arrow_event, suppress=True)
    keyboard.add_hotkey("enter", enter_event, suppress=True)
    keyboard.add_hotkey("escape", escape_event, suppress=True)

    with StringIO() as buf, terminal_cursor() as crsr:
        while not closed:
            for _ in range(max_lens[1] * 2 + 2):
                print(" " * 100)
            crsr.move_up(max_lens[1] * 2 + 3)
            _tabulate(
                *values,
                selected_cell=selected_cell,
                highlight_cell=highlight_cell,
                padding=padding,
                headings=headings,
                empty_default=empty_default,
                # file=buf,
                **kwargs,
            )
            buf.seek(0)
            # print(buf.getvalue().strip())
            key_pressed = False
            while not key_pressed:
                pass
            crsr.move_up(max_lens[1] * 2 + 2 + (2 if headings else 0))

        _tabulate(
            *values,
            selected_cell=None,
            highlight_cell=None,
            padding=padding,
            headings=headings,
            empty_default=empty_default,
            # file=buf,
            **kwargs,
        )
        return ""
        # return buf.getvalue()


def _calculate_sizes(*values: Sequence[str], padding: SupportsInt = 2) -> Sequence[int]:
    sizes = []
    for value in values:
        longest = len(max(value, key=len))
        cell_size = int(padding) + longest + int(padding)
        sizes.append(cell_size)
    return sizes


if __name__ == "__main__":
    # from t import print as p
    # print(
    str(
        tabulate(
            ["Hello", "This is a test.", "Cool"],
            ["This is cool stuff", "Test Cool"],
            [None, None, "Cool stuff"],
        )
        # .with_headings("Systems", "Invitations", None)
        .with_padding(5)
        .with_default("N/A")
        .with_default_heading("Untitled")
    )
# )
