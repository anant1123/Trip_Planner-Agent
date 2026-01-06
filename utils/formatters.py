"""
Formatting utilities for TripGenie
"""
from datetime import datetime, timedelta
from typing import Optional


def format_currency(amount: float, currency: str = "USD", show_symbol: bool = True) -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, INR, etc.)
        show_symbol: Whether to show currency symbol
        
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "INR": "₹",
        "JPY": "¥",
        "AUD": "A$",
        "CAD": "C$"
    }
    
    if show_symbol and currency in symbols:
        return f"{symbols[currency]}{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_date(date: datetime, format_str: str = "%B %d, %Y") -> str:
    """
    Format date for display
    
    Args:
        date: Date to format
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    return date.strftime(format_str)


def format_duration(days: int) -> str:
    """
    Format trip duration
    
    Args:
        days: Number of days
        
    Returns:
        Formatted duration string
    """
    if days == 1:
        return "1 day"
    elif days < 7:
        return f"{days} days"
    elif days == 7:
        return "1 week"
    elif days < 30:
        weeks = days // 7
        remaining_days = days % 7
        if remaining_days == 0:
            return f"{weeks} weeks"
        else:
            return f"{weeks} weeks and {remaining_days} days"
    else:
        months = days // 30
        remaining_days = days % 30
        if remaining_days == 0:
            return f"{months} months"
        else:
            return f"{months} months and {remaining_days} days"


def format_budget_range(min_budget: float, max_budget: float, currency: str = "USD") -> str:
    """
    Format budget range
    
    Args:
        min_budget: Minimum budget
        max_budget: Maximum budget
        currency: Currency code
        
    Returns:
        Formatted budget range string
    """
    if max_budget == float('inf'):
        return f"{format_currency(min_budget, currency)}+"
    else:
        return f"{format_currency(min_budget, currency)} - {format_currency(max_budget, currency)}"


def format_list_items(items: list, separator: str = ", ", last_separator: str = " and ") -> str:
    """
    Format list items into a readable string
    
    Args:
        items: List of items
        separator: Separator between items
        last_separator: Separator before last item
        
    Returns:
        Formatted string
    """
    if not items:
        return ""
    elif len(items) == 1:
        return str(items[0])
    elif len(items) == 2:
        return f"{items[0]}{last_separator}{items[1]}"
    else:
        return separator.join(items[:-1]) + last_separator + str(items[-1])


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length - len(suffix)] + suffix


def format_markdown_section(title: str, content: str, level: int = 2) -> str:
    """
    Format a markdown section
    
    Args:
        title: Section title
        content: Section content
        level: Header level (1-6)
        
    Returns:
        Formatted markdown string
    """
    header = "#" * level
    return f"{header} {title}\n\n{content}\n\n"


def format_bullet_list(items: list, indent: int = 0) -> str:
    """
    Format items as markdown bullet list
    
    Args:
        items: List of items
        indent: Indentation level
        
    Returns:
        Formatted bullet list
    """
    indent_str = "  " * indent
    return "\n".join([f"{indent_str}- {item}" for item in items])
