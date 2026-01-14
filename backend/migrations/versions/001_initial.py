"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-10

创建所有基础表
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建所有基础表"""
    
    # ==================== 用户表 ====================
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('nickname', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('role', sa.String(20), server_default='user', nullable=False),
        sa.Column('status', sa.String(20), server_default='active', nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_status', 'users', ['status'])
    
    # ==================== 用户配额表 ====================
    op.create_table(
        'user_quotas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_type', sa.String(20), server_default='free', nullable=False),
        sa.Column('total_credits', sa.Integer, server_default='100', nullable=False),
        sa.Column('used_credits', sa.Integer, server_default='0', nullable=False),
        sa.Column('reset_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_quotas_user_id', 'user_quotas', ['user_id'], unique=True)
    
    # ==================== 项目表 ====================
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('story_text', sa.Text, nullable=True),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('final_video_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(20), server_default='draft', nullable=False),
        sa.Column('config', postgresql.JSONB, nullable=True),
        sa.Column('scene_count', sa.Integer, server_default='0', nullable=False),
        sa.Column('total_duration', sa.Numeric(10, 2), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])
    op.create_index('ix_projects_status', 'projects', ['status'])
    op.create_index('ix_projects_deleted_at', 'projects', ['deleted_at'])
    
    # ==================== 角色表 ====================
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('appearance', sa.Text, nullable=True),
        sa.Column('prompt_template', sa.Text, nullable=True),
        sa.Column('reference_image_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_characters_project_id', 'characters', ['project_id'])
    
    # ==================== 分镜表 ====================
    op.create_table(
        'scenes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scene_index', sa.Integer, nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('scene_description', sa.Text, nullable=True),
        sa.Column('characters', postgresql.JSONB, server_default='[]', nullable=False),
        sa.Column('props', postgresql.JSONB, server_default='[]', nullable=False),
        sa.Column('camera_type', sa.String(50), nullable=True),
        sa.Column('mood', sa.String(50), nullable=True),
        sa.Column('image_prompt', sa.Text, nullable=True),
        sa.Column('negative_prompt', sa.Text, nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('duration', sa.Numeric(6, 2), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'scene_index', name='uq_scene_project_index')
    )
    op.create_index('ix_scenes_project_id', 'scenes', ['project_id'])
    op.create_index('ix_scenes_status', 'scenes', ['status'])
    
    # ==================== 任务表 ====================
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scene_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('progress', sa.Integer, server_default='0', nullable=False),
        sa.Column('message', sa.String(500), nullable=True),
        sa.Column('result', postgresql.JSONB, nullable=True),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('celery_task_id', sa.String(100), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_project_id', 'tasks', ['project_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_type', 'tasks', ['type'])
    
    # ==================== 资产表 ====================
    op.create_table(
        'assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scene_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('size', sa.BigInteger, nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_assets_project_id', 'assets', ['project_id'])
    op.create_index('ix_assets_type', 'assets', ['type'])


def downgrade() -> None:
    """删除所有表"""
    op.drop_table('assets')
    op.drop_table('tasks')
    op.drop_table('scenes')
    op.drop_table('characters')
    op.drop_table('projects')
    op.drop_table('user_quotas')
    op.drop_table('users')

