"""
元素提取服务

使用 LLM 从故事文本中提取视觉元素
"""

import json

from app.ai_gateway.providers.deepseek import DeepSeekProvider


class ElementExtractor:
    """元素提取器"""
    
    def __init__(self):
        self.llm = DeepSeekProvider()
    
    async def extract_all(self, story_text: str) -> dict[str, list[dict]]:
        """
        从故事中提取所有视觉元素
        
        Returns:
            {
                "characters": [...],
                "locations": [...],
                "props": [...],
                "costumes": [...]
            }
        """
        prompt = self._build_extraction_prompt(story_text)
        
        response = await self.llm.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=8000
        )
        
        return self._parse_response(response)
    
    def _build_extraction_prompt(self, story_text: str) -> str:
        """构建提取提示词"""
        return f'''分析以下故事文本，提取所有视觉元素。

## 故事文本
{story_text}

## 输出要求
请以 JSON 格式输出：

{{
    "characters": [
        {{
            "name": "角色名",
            "name_en": "English Name",
            "role_type": "protagonist/antagonist/supporting",
            "gender": "male/female",
            "age_range": "child/teen/adult/elderly",
            "body_type": "slim/average/athletic",
            "skin_tone": "肤色",
            "face_shape": "脸型",
            "eye_color": "眼睛颜色",
            "hair_color": "头发颜色",
            "hair_style": "发型",
            "hair_length": "short/medium/long",
            "scars": "疤痕（如有）",
            "accessories": ["配饰"],
            "description": "角色简介"
        }}
    ],
    "locations": [
        {{
            "name": "地点名称",
            "name_en": "Location Name",
            "location_type": "interior/exterior",
            "environment": "urban/rural/nature/fantasy",
            "architecture_style": "建筑风格",
            "time_of_day": "时间",
            "lighting_mood": "光照氛围",
            "mood": "整体氛围",
            "key_elements": ["关键元素"],
            "description": "场景描述"
        }}
    ],
    "props": [
        {{
            "name": "道具名称",
            "name_en": "Prop Name",
            "category": "weapon/tool/furniture/other",
            "material": "材质",
            "primary_color": "主色",
            "size": "尺寸",
            "style_era": "时代风格",
            "owner": "所属角色名",
            "description": "道具描述"
        }}
    ],
    "costumes": [
        {{
            "name": "服装名称",
            "name_en": "Costume Name",
            "garment_type": "服装类型",
            "style": "风格",
            "era": "时代",
            "culture": "文化",
            "primary_color": "主色",
            "fabric": "面料",
            "decorations": ["装饰"],
            "worn_by": "穿戴角色名",
            "description": "服装描述"
        }}
    ]
}}

## 注意事项
1. 角色描述要详细，便于 AI 绘图保持一致性
2. 主角描述比配角更详细
3. name_en 用于 AI 绘图提示词
4. 如果文中没有明确描述，可以合理推断

请开始提取：'''
    
    def _parse_response(self, response: str) -> dict:
        """解析响应"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                return json.loads(match.group())
            return {"characters": [], "locations": [], "props": [], "costumes": []}

