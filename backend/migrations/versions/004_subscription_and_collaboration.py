"""订阅与协作表

Revision ID: 004_subscription
Revises: 003_scene_enhancements
Create Date: 2024-12-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004_subscription'
down_revision = '003_scene_enhancements'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==================== 订阅计划表 ====================
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('type', sa.String(20), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        
        # 价格
        sa.Column('price_monthly', sa.Float, default=0),
        sa.Column('price_yearly', sa.Float, default=0),
        
        # 项目限制
        sa.Column('projects_limit', sa.Integer, default=3),
        sa.Column('scenes_per_project', sa.Integer, default=20),
        sa.Column('storage_gb', sa.Float, default=1),
        
        # AI 配额
        sa.Column('llm_tokens', sa.Integer, default=100000),
        sa.Column('image_count', sa.Integer, default=50),
        sa.Column('video_count', sa.Integer, default=10),
        sa.Column('video_duration', sa.Integer, default=50),
        sa.Column('tts_chars', sa.Integer, default=10000),
        
        # 功能权限
        sa.Column('can_export_hd', sa.Boolean, default=False),
        sa.Column('can_remove_watermark', sa.Boolean, default=False),
        sa.Column('can_use_premium_voices', sa.Boolean, default=False),
        sa.Column('can_collaborate', sa.Boolean, default=False),
        sa.Column('priority_queue', sa.Boolean, default=False),
        sa.Column('api_access', sa.Boolean, default=False),
        
        sa.Column('features', postgresql.JSONB, default={}),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('sort_order', sa.Integer, default=0),
        
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    # ==================== 用户订阅表 ====================
    op.create_table(
        'user_subscriptions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('plan_id', sa.String(36), sa.ForeignKey('subscription_plans.id'), nullable=False),
        
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('billing_cycle', sa.String(20), default='monthly'),
        sa.Column('current_period_start', sa.DateTime),
        sa.Column('current_period_end', sa.DateTime),
        
        sa.Column('payment_method', sa.String(20), nullable=True),
        sa.Column('last_payment_at', sa.DateTime, nullable=True),
        sa.Column('next_payment_at', sa.DateTime, nullable=True),
        
        sa.Column('auto_renew', sa.Boolean, default=True),
        sa.Column('cancelled_at', sa.DateTime, nullable=True),
        sa.Column('cancel_reason', sa.String(255), nullable=True),
        sa.Column('trial_end', sa.DateTime, nullable=True),
        
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    op.create_index('ix_user_subscriptions_user_id', 'user_subscriptions', ['user_id'])
    op.create_index('ix_user_subscriptions_status', 'user_subscriptions', ['status'])
    
    # ==================== 使用记录表 ====================
    op.create_table(
        'usage_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        
        sa.Column('usage_type', sa.String(30), nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('unit', sa.String(20), default='count'),
        
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('task_id', sa.String(36), nullable=True),
        sa.Column('cost', sa.Float, default=0),
        
        sa.Column('extra_data', postgresql.JSONB, default={}),
        sa.Column('recorded_at', sa.DateTime, server_default=sa.func.now()),
        
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    op.create_index('ix_usage_records_user_id', 'usage_records', ['user_id'])
    op.create_index('ix_usage_records_recorded_at', 'usage_records', ['recorded_at'])
    op.create_index('ix_usage_records_type_date', 'usage_records', ['user_id', 'usage_type', 'recorded_at'])
    
    # ==================== 支付订单表 ====================
    op.create_table(
        'payment_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        
        sa.Column('order_no', sa.String(64), unique=True, nullable=False),
        sa.Column('plan_type', sa.String(20), nullable=False),
        sa.Column('billing_cycle', sa.String(20), nullable=False),
        
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(10), default='CNY'),
        
        sa.Column('payment_method', sa.String(20), nullable=True),
        sa.Column('payment_status', sa.String(20), default='pending'),
        sa.Column('paid_at', sa.DateTime, nullable=True),
        
        sa.Column('external_order_id', sa.String(128), nullable=True),
        sa.Column('payment_data', postgresql.JSONB, default={}),
        
        sa.Column('invoice_requested', sa.Boolean, default=False),
        sa.Column('invoice_data', postgresql.JSONB, nullable=True),
        
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    op.create_index('ix_payment_orders_order_no', 'payment_orders', ['order_no'])
    op.create_index('ix_payment_orders_user_id', 'payment_orders', ['user_id'])
    
    # ==================== 项目分享表 ====================
    op.create_table(
        'project_shares',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        
        sa.Column('share_code', sa.String(32), unique=True, nullable=False),
        sa.Column('share_type', sa.String(20), default='view'),
        sa.Column('title', sa.String(100), nullable=True),
        
        sa.Column('password_hash', sa.String(128), nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('max_views', sa.Integer, nullable=True),
        sa.Column('view_count', sa.Integer, default=0),
        sa.Column('allow_download', sa.Boolean, default=False),
        
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id')),
        
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    op.create_index('ix_project_shares_share_code', 'project_shares', ['share_code'])
    op.create_index('ix_project_shares_project_id', 'project_shares', ['project_id'])
    
    # ==================== 项目协作者表 ====================
    op.create_table(
        'project_collaborators',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        
        sa.Column('role', sa.String(20), default='viewer'),
        sa.Column('invited_by', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('invited_at', sa.DateTime, server_default=sa.func.now()),
        
        sa.Column('is_accepted', sa.Boolean, default=False),
        sa.Column('accepted_at', sa.DateTime, nullable=True),
        
        sa.Column('invite_email', sa.String(255), nullable=True),
        sa.Column('invite_code', sa.String(32), unique=True, nullable=True),
        
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    op.create_index('ix_project_collaborators_project_id', 'project_collaborators', ['project_id'])
    op.create_index('ix_project_collaborators_user_id', 'project_collaborators', ['user_id'])
    op.create_unique_constraint('uq_project_collaborator', 'project_collaborators', ['project_id', 'user_id'])
    
    # ==================== 项目评论表 ====================
    op.create_table(
        'project_comments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scene_id', sa.String(36), sa.ForeignKey('scenes.id', ondelete='CASCADE'), nullable=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('project_comments.id', ondelete='CASCADE'), nullable=True),
        
        sa.Column('timestamp', sa.Float, nullable=True),
        sa.Column('position_x', sa.Float, nullable=True),
        sa.Column('position_y', sa.Float, nullable=True),
        
        sa.Column('is_resolved', sa.Boolean, default=False),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('resolved_by', sa.String(36), nullable=True),
        
        sa.Column('is_deleted', sa.Boolean, default=False),
        
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    op.create_index('ix_project_comments_project_id', 'project_comments', ['project_id'])
    op.create_index('ix_project_comments_scene_id', 'project_comments', ['scene_id'])
    
    # ==================== 活动日志表 ====================
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('target_type', sa.String(50), nullable=True),
        sa.Column('target_id', sa.String(36), nullable=True),
        
        sa.Column('details', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_index('ix_activity_logs_project_id', 'activity_logs', ['project_id'])
    op.create_index('ix_activity_logs_created_at', 'activity_logs', ['created_at'])
    
    # ==================== 插入默认订阅计划 ====================
    op.execute("""
        INSERT INTO subscription_plans (id, name, type, price_monthly, price_yearly,
            projects_limit, scenes_per_project, storage_gb, llm_tokens, image_count,
            video_count, video_duration, tts_chars, can_export_hd, can_remove_watermark,
            can_use_premium_voices, can_collaborate, priority_queue, api_access, sort_order)
        VALUES
            (gen_random_uuid()::text, '免费版', 'free', 0, 0, 3, 10, 0.5, 50000, 20, 5, 25, 5000, false, false, false, false, false, false, 0),
            (gen_random_uuid()::text, '基础版', 'basic', 29, 290, 10, 30, 5, 500000, 200, 50, 250, 50000, true, false, false, false, false, false, 1),
            (gen_random_uuid()::text, '专业版', 'pro', 99, 990, 50, 100, 50, 2000000, 1000, 200, 1000, 200000, true, true, true, true, true, false, 2),
            (gen_random_uuid()::text, '企业版', 'enterprise', 0, 0, -1, -1, 500, -1, -1, -1, -1, -1, true, true, true, true, true, true, 3)
    """)


def downgrade() -> None:
    op.drop_table('activity_logs')
    op.drop_table('project_comments')
    op.drop_table('project_collaborators')
    op.drop_table('project_shares')
    op.drop_table('payment_orders')
    op.drop_table('usage_records')
    op.drop_table('user_subscriptions')
    op.drop_table('subscription_plans')

