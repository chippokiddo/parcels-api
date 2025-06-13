import csv
import io
from typing import List

from flask import make_response


def create_csv_response(data: List, headers: List[str], filename: str):
    """
    Create a CSV response from data
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow(headers)

    # Write data
    for row in data:
        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"

    return response


def build_export_filename(base_name: str, **filters) -> str:
    """
    Build export filename with applied filters
    """
    filename = base_name

    for key, value in filters.items():
        if value:
            filename += f"_{value}"

    return f"{filename}.csv"
