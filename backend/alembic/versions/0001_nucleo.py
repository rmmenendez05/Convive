"""Núcleo: usuarios, pisos, miembros y avisos

Revision ID: 0001_nucleo
Revises:
Create Date: 2026-11-03
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_nucleo"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("nombre", sa.String(40), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "pisos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(60), nullable=False),
        sa.Column("direccion", sa.String(200), nullable=True),
        sa.Column("codigo_invitacion", sa.String(8), nullable=False, unique=True),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "miembros",
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("piso_id", sa.Integer(), sa.ForeignKey("pisos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rol", sa.String(10), nullable=False),
        sa.Column("unido_en", sa.DateTime(), nullable=False),
        sa.CheckConstraint("rol IN ('admin', 'miembro')", name="ck_miembros_rol"),
    )
    op.create_index("ix_miembros_piso_id", "miembros", ["piso_id"])
    op.create_table(
        "avisos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("piso_id", sa.Integer(), sa.ForeignKey("pisos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("autor_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("texto", sa.String(280), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_avisos_piso_fecha", "avisos", ["piso_id", "creado_en"])


def downgrade() -> None:
    op.drop_index("ix_avisos_piso_fecha", table_name="avisos")
    op.drop_table("avisos")
    op.drop_index("ix_miembros_piso_id", table_name="miembros")
    op.drop_table("miembros")
    op.drop_table("pisos")
    op.drop_table("usuarios")
