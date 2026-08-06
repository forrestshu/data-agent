"""大模型 Adapter：以 OpenAI 兼容协议调用 DeepSeek。"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol

import httpx


class LLMUnavailable(RuntimeError):
    """AI 边界异常：配置缺失、网络失败或模型输出不可解析时显式降级。"""


class LLMClient(Protocol):
    """模型接口：业务层只依赖 JSON 与文本完成能力，便于测试替换真实网络。"""

    provider: str
    model: str

    def complete_json(self, system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> dict[str, Any]:
        """返回可校验 JSON 对象。"""

    def complete_text(self, system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> str:
        """返回最终自然语言文本。"""


@dataclass(frozen=True)
class DeepSeekConfig:
    """配置模型：Key 只来自后端环境，不进入接口响应、日志或前端构建。"""

    api_key: str
    model: str = "deepseek-v4-flash"
    base_url: str = "https://api.deepseek.com"
    timeout_seconds: float = 45.0

    @classmethod
    def from_environment(cls) -> "DeepSeekConfig | None":
        """配置入口：没有 Key 时返回 None，查询运行时会明确拒绝自然语言查询。"""

        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            return None
        return cls(
            api_key=api_key,
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash").strip(),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/"),
            timeout_seconds=float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "45")),
        )


class DeepSeekClient:
    """DeepSeek 实现：调用 Chat Completions，并关闭思考模式以降低交互查询延迟。"""

    provider = "deepseek"

    def __init__(self, config: DeepSeekConfig) -> None:
        self.config = config
        self.model = config.model

    @classmethod
    def from_environment(cls) -> "DeepSeekClient | None":
        """应用装配入口：只有后端环境配置完整时才创建真实模型客户端。"""

        config = DeepSeekConfig.from_environment()
        return cls(config) if config else None

    def _complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        json_output: bool,
    ) -> str:
        """网络边界：发送最小必要上下文，并把远端错误转换成不含 Key 的本地异常。"""

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "thinking": {"type": "disabled"},
            "stream": False,
            "max_tokens": max_tokens,
        }
        if json_output:
            payload["response_format"] = {"type": "json_object"}
        try:
            # DeepSeek 是国内直连服务：该专用客户端不继承系统的海外代理环境变量，
            # 避免本地代理未启动或线路异常时阻断 ERP 查询；其他程序的代理配置不受影响。
            with httpx.Client(
                timeout=self.config.timeout_seconds,
                trust_env=False,
            ) as client:
                response = client.post(
                    f"{self.config.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            response.raise_for_status()
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise LLMUnavailable("DeepSeek 返回了空内容。")
            return content.strip()
        except LLMUnavailable:
            raise
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            raise LLMUnavailable(f"DeepSeek 请求失败：{type(error).__name__}") from error

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> dict[str, Any]:
        """结构化输出：启用 JSON Output，并再次在本地执行 JSON 解析校验。"""

        content = self._complete(system_prompt, user_prompt, max_tokens, json_output=True)
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as error:
            raise LLMUnavailable("DeepSeek 返回内容不是合法 JSON。") from error
        if not isinstance(parsed, dict):
            raise LLMUnavailable("DeepSeek JSON 顶层必须是对象。")
        return parsed

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> str:
        """自然语言输出：用于查询完成后的中文业务回答。"""

        return self._complete(system_prompt, user_prompt, max_tokens, json_output=False)
