def legend_class_from_size(size: str) -> str:
    size_class = f"govuk-fieldset__legend--{size[0:1]}"

    return f"govuk-fieldset__legend {size_class}"

def label_class_from_size(size: str) -> str:
    size_class = f"govuk-label--{size[0:1]}"

    return f"govuk-label {size_class}"