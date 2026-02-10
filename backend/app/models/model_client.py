import httpx
import json
import logging
from typing import Optional, Dict, Any, List
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


class ModelConfig(BaseModel):
    model_type: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: str


class ModelClient:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate(self, prompt: str, **kwargs) -> str:
        logger.info(f"开始调用模型: {self.config.model_type} - {self.config.model_name}")
        logger.debug(f"调用参数: {json.dumps(kwargs, ensure_ascii=False)}")
        
        try:
            if self.config.model_type == "ollama":
                result = await self._generate_ollama(prompt, **kwargs)
            elif self.config.model_type == "deepseek":
                result = await self._generate_deepseek(prompt, **kwargs)
            else:
                raise ValueError(f"Unsupported model type: {self.config.model_type}")
            
            logger.info(f"模型调用成功，响应长度: {len(result)}")
            logger.debug(f"模型响应内容: {result[:500]}...")
            return result
        except Exception as e:
            logger.error(f"模型调用失败: {str(e)}", exc_info=True)
            raise

    async def _generate_ollama(self, prompt: str, **kwargs) -> str:
        url = f"{self.config.base_url}/api/generate"
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")

    async def _generate_deepseek(self, prompt: str, **kwargs) -> str:
        url = f"{self.config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }
        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    async def close(self):
        await self.client.aclose()
