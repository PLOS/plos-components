# Date Input Component

The Date Input component provides a standardized way to collect date information from users, following the GOV.UK Design System patterns. It supports partial dates and provides utility methods for date comparison and conversion.

## Features

- **Flexible Date Input**: Supports day, month, and year inputs with configurable visibility
- **Partial Date Support**: Handles incomplete dates with sensible defaults
- **Date Conversion Utilities**: Convert between DateValue dictionaries and Python date objects
- **Date Comparison**: Compare dates with support for partial dates
- **Customizable Labels**: Customize labels and field IDs for each date component
- **Error Handling**: Display validation errors for date inputs
- **Accessibility**: Follows GOV.UK accessibility guidelines

## Usage

### Basic Usage

```django
{% load component_tags %}

<!-- Basic date input -->
{% component "plos_date_input" legend="When was your passport issued?" %}{% endcomponent %}

<!-- Date input with hint -->
{% component "plos_date_input"
    legend="When was your passport issued?"
    hint="For example, 27 3 2007" %}
{% endcomponent %}
```

### With Pre-filled Values

```django
<!-- Date input with existing values -->
{% component "plos_date_input"
    legend="When was your passport issued?"
    value={"day": 27, "month": 3, "year": 2007} %}
{% endcomponent %}
```

### Customizing Date Components

```django
<!-- Hide day input -->
{% component "plos_date_input"
    legend="Expiry month and year"
    day=False %}
{% endcomponent %}

<!-- Custom labels -->
{% component "plos_date_input"
    legend="When was your passport issued?"
    date_settings={"day": {"label": "D"}, "month": {"label": "M"}, "year": {"label": "Y"}} %}
{% endcomponent %}
```

### With Error Messages

```django
<!-- Date input with errors -->
{% component "plos_date_input"
    legend="When was your passport issued?"
    errors=["Please enter a valid date"] %}
{% endcomponent %}
```

## Component Parameters

### Required Parameters

- `legend` (str): The label for the date input fieldset

### Optional Parameters

- `field_id` (str, optional): Unique identifier for the fieldset. Auto-generated if not provided.
- `legend_size` ("large"|"medium"|"small", default: "small"): Size of the legend text
- `hint` (str, optional): Hint text to help users fill in the date
- `errors` (list[str], optional): List of error messages to display
- `day` (bool, default: True): Whether to show the day input
- `month` (bool, default: True): Whether to show the month input
- `year` (bool, default: True): Whether to show the year input
- `value` (DateValue|str|dict, optional): Pre-filled values for the date inputs
- `use_field_value_names` (bool, default: False): Whether to use custom field value names
- `field_value_names` (dict, optional): Custom field value names mapping
- `date_settings` (DateSettings, optional): Custom settings for individual date components

## DateValue Type

The DateValue type is a TypedDict that represents a date with optional components:

```python
class DateValue(TypedDict):
    day: NotRequired[int | None]
    month: NotRequired[int | None]
    year: NotRequired[int | None]
```

Examples:
- `DateValue(year=2023, month=6, day=15)` - Complete date
- `DateValue(year=2023, month=6)` - Missing day
- `DateValue(month=6, day=15)` - Missing year
- `DateValue(day=15)` - Missing year and month

## DateSettings Type

The DateSettings type allows customization of individual date components:

```python
class DateSettings(TypedDict):
    day: NotRequired[DateSettingOption | None]
    month: NotRequired[DateSettingOption | None]
    year: NotRequired[DateSettingOption | None]
```

## DateSettingOption Type

The DateSettingOption type defines options for individual date components:

```python
class DateSettingOption(TypedDict):
    label: NotRequired[str | None]
    field_id: NotRequired[str | None]
    field_name: NotRequired[str | None]
    display: NotRequired[bool | None]
```

## Utility Methods

The DateInput component provides several static utility methods for working with dates:

### convert_to_date(date_value: DateValue | None) -> date

Convert a DateValue to a Python date object, using default values for missing components:
- Default year: 1900
- Default month: 1 (January)
- Default day: 1

```python
from plos_django_components.components.components.date_input.date_input import DateInput, DateValue

# Convert partial date
partial_date = DateValue(year=2023, month=6)  # Missing day
date_obj = DateInput.convert_to_date(partial_date)  # Returns date(2023, 6, 1)
```

### convert_from_date(date_obj: date) -> DateValue

Convert a Python date object to a DateValue dictionary.

```python
from datetime import date
from plos_django_components.components.components.date_input.date_input import DateInput

# Convert date object
date_obj = date(2023, 6, 15)
date_value = DateInput.convert_from_date(date_obj)  # Returns DateValue(year=2023, month=6, day=15)
```

### is_date_before_or_equal(first_date: date | DateValue, second_date: date | DateValue) -> bool

Check if the first date is before or equal to the second date, with special handling for partial dates.

For partial dates, the comparison follows these rules:
- Only compare incomplete objects to incomplete objects
- The second_date may be more complete than the first object
- Wherever the first_date has a None DateValue, the second_date is converted to match
- The inverse is not true - any None value for the second_date is assumed to be the default value

```python
from plos_django_components.components.components.date_input.date_input import DateInput, DateValue

# Compare partial dates
jan_2001 = DateValue(year=2001, month=1)  # Missing day
dec_2001 = DateValue(year=2001, month=12)  # Missing day
result = DateInput.is_date_before_or_equal(jan_2001, dec_2001)  # Returns True

# Compare dates with different missing components
mar_30 = DateValue(month=3, day=30)  # Missing year
may_1 = DateValue(month=5, day=1)  # Missing year
result = DateInput.is_date_before_or_equal(mar_30, may_1)  # Returns True (1900-03-30 <= 1900-05-01)
```

### convert_any_date_value_to_date(date_value: DateValue | date | None, blank_out_day: bool = False, blank_out_month: bool = False, blank_out_year: bool = False) -> date

Convert any date representation (DateValue, date object, or None) to a date object, with options to blank out specific components.

## Accessibility

The Date Input component follows GOV.UK accessibility guidelines:
- Uses semantic HTML fieldset and legend elements
- Properly associated labels for each input
- Error messages are linked to their respective inputs
- Inputs are properly labeled for screen readers

## Technical Details

### Component Class

The component is implemented in `date_input.py` and uses the template `date_input.html`.

### CSS Classes

- `.govuk-date-input` - Base date input wrapper class
- `.govuk-date-input__item` - Wrapper for individual date inputs
- `.govuk-date-input__input` - Individual date input fields
- `.govuk-input--width-2` - CSS class for day/month inputs (2 character width)
- `.govuk-input--width-4` - CSS class for year inputs (4 character width)

### Default Values

When date components are missing, the following defaults are used:
- Default year: 1900
- Default month: 1 (January)
- Default day: 1

### Error Handling

The component validates:
- Date values are properly formatted
- Required date components are provided when specified
- Error messages are properly associated with inputs
