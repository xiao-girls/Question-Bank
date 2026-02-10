import json
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 设置控制台输出编码
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
logger = logging.getLogger(__name__)


class Question(BaseModel):
    id: str
    type: str
    difficulty: str
    question: str
    options: Optional[List[str]] = None
    answer: str
    explanation: Optional[str] = None


class QuestionGenerator:
    def __init__(self, model_client):
        self.model_client = model_client

    async def generate_questions(
        self,
        knowledge_content: str,
        keyword: str,
        question_type: str,
        difficulty: str,
        count: int = 5
    ) -> List[Question]:
        try:
            logger.info(f"开始生成题目: 关键词={keyword}, 类型={question_type}, 难度={difficulty}, 数量={count}")
            logger.debug(f"知识库内容长度: {len(knowledge_content)}")
            
            prompt = self._build_prompt(
                knowledge_content, keyword, question_type, difficulty, count
            )
            logger.info(f"生成的提示词长度: {len(prompt)}")
            # 创建不包含知识库内容的提示词副本用于日志打印
            prompt_for_log = prompt.replace(knowledge_content[:3000], "[知识库内容已省略]")
            logger.info(f"提示词内容:\n{prompt_for_log}")

            response = await self.model_client.generate(prompt)
            logger.debug(f"模型响应长度: {len(response)}")
            
            questions = self._parse_questions(response, question_type)
            logger.info(f"成功生成题目数量: {len(questions)}")
            
            return questions
        except Exception as e:
            logger.error(f"生成题目失败: {str(e)}", exc_info=True)
            return []

    def _build_prompt(
        self,
        knowledge_content: str,
        keyword: str,
        question_type: str,
        difficulty: str,
        count: int
    ) -> str:
        type_mapping = {
            "single_choice": "单选题",
            "multiple_choice": "多选题",
            "fill": "填空题",
            "essay": "问答题",
            "true_false": "判断题"
        }

        difficulty_mapping = {
            "easy": "简单",
            "medium": "中等",
            "hard": "困难"
        }

        # 根据题目类型构建特定的提示词
        if question_type == "single_choice":
            prompt = f"""你是一个专业的题目生成助手。请根据以下知识库内容，生成{count}道单选题。

关键词：{keyword}
难度：{difficulty_mapping.get(difficulty, difficulty)}

知识库内容：
{knowledge_content[:3000]}

请严格按照以下JSON格式返回题目（不要包含其他文字）：
{{
    "questions": [
        {{
            "type": "single_choice",
            "difficulty": "{difficulty}",
            "question": "题目内容",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "answer": "正确答案（单个选项，如\"A\"、\"B\"、\"C\"或\"D\"）",
            "explanation": "解析"
        }}
    ]
}}

注意：
1. 对于单选题，options字段必须包含4个选项
2. answer字段只能是一个选项，如\"A\"、\"B\"、\"C\"或\"D\"\n3. 确保题目基于知识库内容生成
"""
        elif question_type == "multiple_choice":
            prompt = f"""你是一个专业的题目生成助手。请根据以下知识库内容，生成{count}道多选题。

关键词：{keyword}
难度：{difficulty_mapping.get(difficulty, difficulty)}

知识库内容：
{knowledge_content[:3000]}

请严格按照以下JSON格式返回题目（不要包含其他文字）：
{{
    "questions": [
        {{
            "type": "multiple_choice",
            "difficulty": "{difficulty}",
            "question": "题目内容",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "answer": "正确答案（多个选项，如\"AB\"、\"ACD\"等）",
            "explanation": "解析"
        }}
    ]
}}

注意：
1. 对于多选题，options字段必须包含4个选项
2. answer字段可以是多个选项，如\"AB\"、\"ACD\"等
3. 确保题目基于知识库内容生成
"""
        elif question_type == "true_false":
            prompt = f"""你是一个专业的题目生成助手。请根据以下知识库内容，生成{count}道判断题。

关键词：{keyword}
难度：{difficulty_mapping.get(difficulty, difficulty)}

知识库内容：
{knowledge_content[:3000]}

请严格按照以下JSON格式返回题目（不要包含其他文字）：
{{
    "questions": [
        {{
            "type": "true_false",
            "difficulty": "{difficulty}",
            "question": "题目内容",
            "options": ["是", "否"],
            "answer": "正确答案（\"是\"或\"否\"）",
            "explanation": "解析"
        }}
    ]
}}

注意：
1. 对于判断题，options字段只能是["是", "否"]两种
2. answer字段只能是\"是\"或\"否\"\n3. 确保题目基于知识库内容生成
"""
        else:
            prompt = f"""你是一个专业的题目生成助手。请根据以下知识库内容，生成{count}道{type_mapping.get(question_type, question_type)}。

关键词：{keyword}
难度：{difficulty_mapping.get(difficulty, difficulty)}

知识库内容：
{knowledge_content[:3000]}

请严格按照以下JSON格式返回题目（不要包含其他文字）：
{{
    "questions": [
        {{
            "type": "{question_type}",
            "difficulty": "{difficulty}",
            "question": "题目内容",
            "answer": "正确答案",
            "explanation": "解析"
        }}
    ]
}}

注意：
1. 对于填空题和问答题，不需要options字段
2. answer字段要简洁明确
3. 确保题目基于知识库内容生成
"""
        return prompt

    def _parse_questions(self, response: str, question_type: str) -> List[Question]:
        try:
            data = json.loads(response)
            questions = []

            for idx, q in enumerate(data.get("questions", [])):
                question = Question(
                    id=f"q_{idx + 1}",
                    type=q.get("type", question_type),
                    difficulty=q.get("difficulty", "medium"),
                    question=q.get("question", ""),
                    options=q.get("options"),
                    answer=q.get("answer", ""),
                    explanation=q.get("explanation")
                )
                questions.append(question)

            return questions
        except json.JSONDecodeError as e:
            logger.error(f"解析题目失败: {str(e)}")
            logger.error(f"模型响应内容: {response[:500]}...")
            return []
        except Exception as e:
            logger.error(f"解析题目时发生错误: {str(e)}", exc_info=True)
            return []
