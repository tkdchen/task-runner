from typing import IO, assert_never

from devtool.software_list import Package


def print_packages_table(packages: list[Package], outfile: IO[str]) -> None:
    def install_method(package: Package) -> str:
        match package.type:
            case "go-tool":
                return "`go install`"
            case "go-submodule":
                return "Go submodule"
            case "rpm":
                return "RPM"
            case _:
                assert_never(package.type)

    columns = {
        "Name": [p.name for p in packages],
        "Version": [p.version for p in packages],
        "Install Method": list(map(install_method, packages)),
    }

    # Hardcoded to generate smaller diffs. Increase if any package name is longer than this.
    column_width = 30
    print_markdown_table(columns, outfile, column_widths=column_width)


def print_markdown_table(
    columns: dict[str, list[str]],
    outfile: IO[str],
    *,
    column_widths: int | list[int] | None = None,
) -> None:
    """Print a markdown table to the specified output file.

    Args:
        columns: A dict of {column_name: [column_values]}
        outfile: An object that implements the IO interface
        column_widths:
            None:      Make each column as wide as the longest item in that column
            int:       Make all columns the specified width
            list[int]: Specify the widths of the individual columns
    """
    if column_widths is None:
        column_widths = [max(len(name), max(map(len, values))) for name, values in columns.items()]
    elif isinstance(column_widths, int):
        column_widths = [column_widths] * len(columns)
    elif len(column_widths) != len(columns):
        raise ValueError(f"Need {len(columns)} widths, got {len(column_widths)}")

    column_lists: list[list[str]] = []
    for i, (name, values) in enumerate(columns.items()):
        column = [name, "-" * column_widths[i], *values]
        column_lists.append(column)

    transposed: list[tuple[str, ...]] = list(zip(*column_lists))
    for row in transposed:
        for column_width, value in zip(column_widths, row):
            outfile.write("| ")
            outfile.write(value.ljust(column_width))
            outfile.write(" ")
        outfile.write("|\n")
