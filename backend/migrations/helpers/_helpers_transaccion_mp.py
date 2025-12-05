"""
Helper functions for TransaccionMercadoPago migrations.

This module provides shared functions to reduce duplication
in migration files that create the transaccion_mercadopago table.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def create_transaccion_mercadopago_table(created_at_nullable: bool = True, updated_at_nullable: bool = True):
    """
    Creates the puerta_orion_transaccion_mercadopago table.
    
    Args:
        created_at_nullable: Whether created_at column should be nullable
        updated_at_nullable: Whether updated_at column should be nullable
    """
    op.create_table('puerta_orion_transaccion_mercadopago',
        sa.Column('id_transaccion', sa.Integer(), nullable=False),
        sa.Column('id_pago_mercadopago', sa.String(length=255), nullable=False),
        sa.Column('preference_id', sa.String(length=255), nullable=True),
        sa.Column('estado', sa.String(length=50), nullable=False),
        sa.Column('monto', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('moneda', sa.String(length=3), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False),
        sa.Column('datos_pago', mysql.JSON(), nullable=True),
        sa.Column('id_cuota', sa.Integer(), nullable=True),
        sa.Column('id_mensualidad', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=created_at_nullable),
        sa.Column('updated_at', sa.DateTime(), nullable=updated_at_nullable),
        sa.ForeignKeyConstraint(['id_cuota'], ['puerta_orion_cuota.id_cuota'], ),
        sa.ForeignKeyConstraint(['id_mensualidad'], ['puerta_orion_mensualidad.id_mensualidad'], ),
        sa.PrimaryKeyConstraint('id_transaccion'),
        sa.UniqueConstraint('id_pago_mercadopago')
    )


def drop_transaccion_mercadopago_table():
    """Drops the puerta_orion_transaccion_mercadopago table."""
    op.drop_table('puerta_orion_transaccion_mercadopago')

