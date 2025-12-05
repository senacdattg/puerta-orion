"""
Helper functions for safe table modifications in migrations.

This module provides shared functions to safely modify tables
by handling errors gracefully when constraints or columns don't exist.
"""

from alembic import op
from typing import List, Set, Dict, Any


def drop_constraint_safe(
    constraint_name: str,
    table_name: str,
    constraint_type: str = 'foreignkey'
) -> None:
    """
    Safely drop a constraint, ignoring if it doesn't exist.
    
    Args:
        constraint_name: Name of the constraint to drop
        table_name: Name of the table
        constraint_type: Type of constraint (default: 'foreignkey')
    """
    try:
        op.drop_constraint(constraint_name, table_name, type_=constraint_type)
    except Exception:
        pass  # Ignore if constraint doesn't exist


def drop_column_safe(table_name: str, column_name: str) -> None:
    """
    Safely drop a column, ignoring if it doesn't exist.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column to drop
    """
    try:
        op.drop_column(table_name, column_name)
    except Exception:
        pass  # Ignore if column doesn't exist


def drop_foreign_keys_for_columns(
    table_name: str,
    foreign_keys: List[Dict[str, Any]],
    target_columns: Set[str]
) -> None:
    """
    Drop foreign key constraints for specific columns.
    
    Args:
        table_name: Name of the table
        foreign_keys: List of foreign key dictionaries from inspector
        target_columns: Set of column names to drop FKs for
    """
    for fk in foreign_keys:
        constrained_column = fk.get('constrained_columns', [])
        if constrained_column and constrained_column[0] in target_columns:
            constraint_name = fk.get('name')
            if constraint_name:
                drop_constraint_safe(constraint_name, table_name, 'foreignkey')


def drop_columns_safe(
    table_name: str,
    column_names: List[str],
    existing_columns: Set[str]
) -> None:
    """
    Drop multiple columns safely, only if they exist.
    
    Args:
        table_name: Name of the table
        column_names: List of column names to drop
        existing_columns: Set of existing column names
    """
    for column_name in column_names:
        if column_name in existing_columns:
            drop_column_safe(table_name, column_name)

