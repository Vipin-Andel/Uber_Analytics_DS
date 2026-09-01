import pandas as pd

def format_currency_inr(value: float) -> str:
    """Formats numeric value into Indian Lakhs/Crores or Currency string."""
    if value >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"
    elif value >= 100_000:
        return f"₹{value / 100_000:.2f} L"
    else:
        return f"₹{value:,.2f}"

def format_metrics(value: float, metric_type: str = "number") -> str:
    """Helper for executive KPI presentation."""
    if metric_type == "percent":
        return f"{value:.1f}%"
    elif metric_type == "distance":
        return f"{value:.2f} km"
    return f"{value:,.0f}"