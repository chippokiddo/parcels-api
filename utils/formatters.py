from typing import Tuple, Dict


def format_amount(amount) -> Tuple[str, str]:
    """
    Format amount with proper decimal places
    Returns: (amount_formatted, amount_display)
    """
    if not amount or amount == '':
        return '', ''

    try:
        amount_value = float(amount)
        return f"{amount_value:.2f}", f"{amount_value:,.2f}"
    except (ValueError, TypeError):
        return str(amount), str(amount)


def format_record_dict(record, none_replacement='') -> Dict:
    """
    Format database record dictionary and handle None values
    """
    if not record:
        return {}

    record_dict = dict(record)
    for key in record_dict:
        if record_dict[key] is None:
            record_dict[key] = none_replacement

    return record_dict
