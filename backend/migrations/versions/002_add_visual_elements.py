"""add visual elements

Revision ID: 002_visual_elements
Revises: 001_initial
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_visual_elements'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 visual_elements 表
    op.create_table(
        'visual_elements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('prompt_cn', sa.Text(), nullable=True),
        sa.Column('prompt_en', sa.Text(), nullable=True),
        sa.Column('negative_prompt', sa.Text(), nullable=True),
        sa.Column('reference_images', postgresql.JSONB(), default=list),
        sa.Column('primary_reference_url', sa.String(500), nullable=True),
        sa.Column('consistency_config', postgresql.JSONB(), default=dict),
        sa.Column('attributes', postgresql.JSONB(), default=dict),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('tags', postgresql.JSONB(), default=list),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_visual_elements_project_id', 'visual_elements', ['project_id'])
    op.create_index('ix_visual_elements_type', 'visual_elements', ['type'])
    op.create_index('ix_visual_elements_project_type', 'visual_elements', ['project_id', 'type', 'is_active'])
    
    # 创建 element_appearances 表
    op.create_table(
        'element_appearances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('element_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scene_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scene_state', postgresql.JSONB(), default=dict),
        sa.Column('generated_image_url', sa.String(500), nullable=True),
        sa.Column('cropped_region', postgresql.JSONB(), nullable=True),
        sa.Column('generation_params', postgresql.JSONB(), default=dict),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('consistency_score', sa.Float(), nullable=True),
        sa.Column('is_reference_candidate', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['element_id'], ['visual_elements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_element_appearances_element_id', 'element_appearances', ['element_id'])
    op.create_index('ix_element_appearances_scene_id', 'element_appearances', ['scene_id'])
    op.create_index('ix_element_appearances_element_scene', 'element_appearances', ['element_id', 'scene_id'])
    
    # 添加 scenes 表新索引
    op.create_index('ix_scenes_project_index', 'scenes', ['project_id', 'scene_index'])
    
    # 添加 tasks 表新索引
    op.create_index('ix_tasks_project_status', 'tasks', ['project_id', 'status', 'type'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_tasks_project_status', table_name='tasks')
    op.drop_index('ix_scenes_project_index', table_name='scenes')
    op.drop_index('ix_element_appearances_element_scene', table_name='element_appearances')
    op.drop_index('ix_element_appearances_scene_id', table_name='element_appearances')
    op.drop_index('ix_element_appearances_element_id', table_name='element_appearances')
    
    # 删除表
    op.drop_table('element_appearances')
    
    op.drop_index('ix_visual_elements_project_type', table_name='visual_elements')
    op.drop_index('ix_visual_elements_type', table_name='visual_elements')
    op.drop_index('ix_visual_elements_project_id', table_name='visual_elements')
    op.drop_table('visual_elements')

