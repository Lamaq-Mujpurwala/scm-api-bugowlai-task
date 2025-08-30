"""Initial migration with models (portable JSON)

Revision ID: 95e1a31eab38
Revises: 
Create Date: 2025-08-29
"""
from alembic import op
import sqlalchemy as sa

revision = '95e1a31eab38'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'moderation_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_email', sa.String(), nullable=False, index=True),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('content_hash', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='contentstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'moderation_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('request_id', sa.Integer(), sa.ForeignKey('moderation_requests.id'), nullable=False, index=True),
        sa.Column('classification', sa.Enum('TOXIC', 'SPAM', 'HARASSMENT', 'SAFE', name='classification'), nullable=False),
        sa.Column('confidence', sa.Float()),
        sa.Column('reasoning', sa.String()),
        sa.Column('llm_provider', sa.String()),
        sa.Column('llm_response', sa.JSON()),
    )

    op.create_table(
        'notification_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('request_id', sa.Integer(), sa.ForeignKey('moderation_requests.id'), nullable=False, index=True),
        sa.Column('channel', sa.Enum('SLACK', 'EMAIL', name='notificationchannel'), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('notification_logs')
    op.drop_table('moderation_results')
    op.drop_table('moderation_requests')
