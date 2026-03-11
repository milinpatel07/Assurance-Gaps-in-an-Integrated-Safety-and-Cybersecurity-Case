"""Results generation for publication: LaTeX tables, JSON/CSV export, figures."""

from src.results.latex_tables import generate_all_tables
from src.results.export import export_json, export_csv_tables, export_summary_report

__all__ = [
    "generate_all_tables",
    "export_json",
    "export_csv_tables",
    "export_summary_report",
]
