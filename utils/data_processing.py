from typing import Dict, Set


def process_record_data(data: Dict, not_null_columns: Set[str],
                        amount_field: str = 'amount') -> Dict:
    """
    Process record data, handling null values and amount formatting

    Args:
        data: Raw data dictionary
        not_null_columns: Set of columns that should not be null
        amount_field: Name of the amount field to format
    """
    from .formatters import format_amount

    processed_data = {}
    for key, value in data.items():
        if key in not_null_columns:
            if key == amount_field and value:
                processed_data[key], _ = format_amount(value)
            else:
                processed_data[key] = value
        else:
            processed_data[key] = None if value == '' else value

    return processed_data
