"""
Helper functions for table creation in migrations.

This module provides shared functions to reduce duplication
in migration files that create similar table structures.
"""

from alembic import op
import sqlalchemy as sa
from typing import List, Tuple, Optional


def create_simple_table(
    table_name: str,
    id_column_name: str,
    name_column_name: str,
    name_column_length: int = 150,
    autoincrement: bool = True,
    unique_name: bool = True,
    additional_columns: Optional[List[sa.Column]] = None,
    foreign_keys: Optional[List[sa.ForeignKeyConstraint]] = None
):
    """
    Creates a simple table with id, name, created_at, updated_at columns.
    
    Args:
        table_name: Name of the table
        id_column_name: Name of the ID column
        name_column_name: Name of the name column
        name_column_length: Length of the name column
        autoincrement: Whether ID column should autoincrement
        unique_name: Whether name column should be unique
        additional_columns: List of additional columns to add
        foreign_keys: List of foreign key constraints
    """
    columns = [
        sa.Column(id_column_name, sa.Integer(), autoincrement=autoincrement, nullable=False),
        sa.Column(name_column_name, sa.String(length=name_column_length), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    ]
    
    if additional_columns:
        columns.extend(additional_columns)
    
    constraints = [
        sa.PrimaryKeyConstraint(id_column_name),
    ]
    
    if unique_name:
        constraints.append(sa.UniqueConstraint(name_column_name))
    
    if foreign_keys:
        constraints.extend(foreign_keys)
    
    op.create_table(table_name, *columns, *constraints)


def create_table_with_columns(
    table_name: str,
    columns: List[sa.Column],
    primary_key: str,
    unique_constraints: Optional[List[str]] = None,
    foreign_keys: Optional[List[sa.ForeignKeyConstraint]] = None
):
    """
    Creates a table with custom columns and constraints.
    
    Args:
        table_name: Name of the table
        columns: List of columns
        primary_key: Name of the primary key column
        unique_constraints: List of column names for unique constraints
        foreign_keys: List of foreign key constraints
    """
    constraints = [
        sa.PrimaryKeyConstraint(primary_key),
    ]
    
    if unique_constraints:
        for col_name in unique_constraints:
            constraints.append(sa.UniqueConstraint(col_name))
    
    if foreign_keys:
        constraints.extend(foreign_keys)
    
    op.create_table(table_name, *columns, *constraints)


def create_table_if_missing(
    table_name: str,
    existing_tables: set,
    existing_tables_lower: set,
    columns: List[sa.Column],
    constraints: List
):
    """
    Creates a table only if it doesn't already exist.
    
    Args:
        table_name: Name of the table
        existing_tables: Set of existing table names
        existing_tables_lower: Set of existing table names in lowercase
        columns: List of columns
        constraints: List of constraints
    """
    if table_name in existing_tables or table_name.lower() in existing_tables_lower:
        return
    
    op.create_table(table_name, *columns, *constraints)
    existing_tables.add(table_name)
    existing_tables_lower.add(table_name.lower())


def get_standard_timestamp_columns() -> List[sa.Column]:
    """
    Returns standard created_at and updated_at columns.
    
    Returns:
        List with created_at and updated_at columns
    """
    return [
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    ]





