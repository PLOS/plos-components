def legend_class_from_size(size: str) -> str:
    size_class = f"govuk-fieldset__legend--{size[0:1]}"

    return f"govuk-fieldset__legend {size_class}"


def label_class_from_size(size: str) -> str:
    size_class = f"govuk-label--{size[0:1]}"

    return f"govuk-label {size_class}"


# GOV.UK fixed character-width scale (max-width sized to roughly N characters).
FIXED_INPUT_WIDTHS = {2, 3, 4, 5, 10, 20, 30}
# Custom PLOS fluid, fraction-of-container widths
# Currently shared by inputs and textareas
FLUID_WIDTHS = {"one-quarter", "one-third", "one-half", "two-thirds", "three-quarters"}


def fluid_width_class(width: str | None) -> str:
    """
    Maps a fluid, fraction-of-container width to its ``plos-width--{fraction}`` class.

    - A fraction keyword (one-quarter, one-third, one-half, two-thirds,
      three-quarters) -> ``plos-width--{fraction}``.
    - ``None`` or "full" -> no class; the field stays full width.
    """
    if width is None or width == "full":
        return ""
    if width in FLUID_WIDTHS:
        return f"plos-width--{width}"
    valid = ", ".join(sorted(FLUID_WIDTHS) + ["full"])
    raise ValueError(f"Invalid width {width!r}: must be one of {valid}")


def input_width_class(width: int | str | None) -> str:
    """
    Maps a text-input width to its CSS class.

    - An integer (or digit string) from the GOV.UK character-width scale
      (2, 3, 4, 5, 10, 20, 30) -> ``govuk-input--width-N``, a fixed ~N-character width.
    - A fraction keyword -> ``plos-width--{fraction}`` (see :func:`fluid_width_class`).
    - ``None`` or "full" -> no class; the input stays full width.
    """
    if isinstance(width, str) and width.isdigit():
        width = int(width)
    if isinstance(width, int):
        if width not in FIXED_INPUT_WIDTHS:
            valid = ", ".join(str(w) for w in sorted(FIXED_INPUT_WIDTHS))
            raise ValueError(f"Invalid input character width {width}: must be one of {valid}")
        return f"govuk-input--width-{width}"
    return fluid_width_class(width)
