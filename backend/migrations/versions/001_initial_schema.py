"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-02-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('subscription_tier', sa.Enum('FREE', 'PREMIUM', 'ENTERPRISE', name='subscriptiontier'), nullable=True),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True),
        sa.Column('subscription_end_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create projects table
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='analysisstatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)

    # Create analyses table
    op.create_table('analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('reddit_data', sa.JSON(), nullable=True),
        sa.Column('twitter_data', sa.JSON(), nullable=True),
        sa.Column('linkedin_data', sa.JSON(), nullable=True),
        sa.Column('overall_score', sa.Integer(), nullable=True),
        sa.Column('verdict', sa.String(), nullable=True),
        sa.Column('key_insights', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analyses_id'), 'analyses', ['id'], unique=False)

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('plan', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('current_period_end', sa.Integer(), nullable=True),
        sa.Column('validations_used', sa.Integer(), nullable=True),
        sa.Column('validations_limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_analyses_id'), table_name='analyses')
    op.drop_table('analyses')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
