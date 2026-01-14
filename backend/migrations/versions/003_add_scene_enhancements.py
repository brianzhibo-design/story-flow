"""add scene enhancement fields

Revision ID: 003
Revises: 002
Create Date: 2024-01-15

为 Scene 表添加专业级镜头控制和画质增强字段
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '003_scene_enhancements'
down_revision: Union[str, None] = '002_visual_elements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 Scene 表的新字段"""
    
    # ==================== 镜头控制字段 ====================
    
    # 镜头类型
    op.add_column('scenes', sa.Column(
        'shot_type',
        sa.String(50),
        nullable=True,
        comment='镜头类型: extreme_close_up/close_up/medium_shot/wide_shot'
    ))
    
    # 机位角度
    op.add_column('scenes', sa.Column(
        'camera_angle',
        sa.String(50),
        nullable=True,
        comment='机位角度: eye_level/low_angle/high_angle/dutch_angle'
    ))
    
    # 镜头运动
    op.add_column('scenes', sa.Column(
        'camera_movement',
        sa.String(50),
        nullable=True,
        comment='镜头运动: static/zoom_in/zoom_out/pan_left/pan_right'
    ))
    
    # 运动强度
    op.add_column('scenes', sa.Column(
        'movement_intensity',
        sa.Float,
        nullable=True,
        comment='运动强度: 0-1，特写镜头自动降低'
    ))
    
    # Motion Bucket ID
    op.add_column('scenes', sa.Column(
        'motion_bucket_id',
        sa.Integer,
        nullable=True,
        comment='Motion Bucket ID: 0-255，127为中等运动'
    ))
    
    # ==================== 角色状态字段 ====================
    
    op.add_column('scenes', sa.Column(
        'character_states',
        postgresql.JSONB,
        nullable=True,
        comment='角色状态: {char_id: {position, action, expression, costume_id}}'
    ))
    
    # ==================== 光照信息字段 ====================
    
    op.add_column('scenes', sa.Column(
        'lighting_info',
        postgresql.JSONB,
        nullable=True,
        comment='光照信息: {primary, direction, color}'
    ))
    
    # ==================== 画质增强字段 ====================
    
    op.add_column('scenes', sa.Column(
        'is_face_enhanced',
        sa.Boolean,
        server_default='false',
        nullable=False,
        comment='是否已进行面部增强'
    ))
    
    op.add_column('scenes', sa.Column(
        'is_hand_enhanced',
        sa.Boolean,
        server_default='false',
        nullable=False,
        comment='是否已进行手部增强'
    ))
    
    op.add_column('scenes', sa.Column(
        'is_upscaled',
        sa.Boolean,
        server_default='false',
        nullable=False,
        comment='是否已超分'
    ))
    
    op.add_column('scenes', sa.Column(
        'original_image_url',
        sa.String(500),
        nullable=True,
        comment='增强前原图URL'
    ))
    
    # ==================== 修改历史字段 ====================
    
    op.add_column('scenes', sa.Column(
        'edit_history',
        postgresql.JSONB,
        nullable=True,
        comment='修改历史: [{type, region, prompt, timestamp}]'
    ))
    
    # ==================== 创建索引 ====================
    
    # 镜头类型索引（常用于筛选）
    op.create_index(
        'ix_scenes_shot_type',
        'scenes',
        ['shot_type'],
        unique=False
    )
    
    # 增强状态索引（用于批量处理）
    op.create_index(
        'ix_scenes_enhance_status',
        'scenes',
        ['is_face_enhanced', 'is_hand_enhanced', 'is_upscaled'],
        unique=False
    )


def downgrade() -> None:
    """移除 Scene 表的新字段"""
    
    # 删除索引
    op.drop_index('ix_scenes_enhance_status', table_name='scenes')
    op.drop_index('ix_scenes_shot_type', table_name='scenes')
    
    # 删除字段
    op.drop_column('scenes', 'edit_history')
    op.drop_column('scenes', 'original_image_url')
    op.drop_column('scenes', 'is_upscaled')
    op.drop_column('scenes', 'is_hand_enhanced')
    op.drop_column('scenes', 'is_face_enhanced')
    op.drop_column('scenes', 'lighting_info')
    op.drop_column('scenes', 'character_states')
    op.drop_column('scenes', 'motion_bucket_id')
    op.drop_column('scenes', 'movement_intensity')
    op.drop_column('scenes', 'camera_movement')
    op.drop_column('scenes', 'camera_angle')
    op.drop_column('scenes', 'shot_type')

