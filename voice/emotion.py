"""感情分析モジュール。

被験者の発話（文字起こしテキスト）を受け取り、
Gemini の「構造化出力（Structured Output）」機能を使って
感情ラベル・強度・根拠・キーワードを JSON で取り出します。
"""

from pydantic import BaseModel

import config


class EmotionResult(BaseModel):
    """感情分析の結果。この形（スキーマ）で JSON を返すよう Gemini に指示する。"""

    primary_emotion: str  # 主要な感情ラベル（喜び・悲しみ など）
    intensity: float      # 感情の強さ（0.0〜1.0）
    rationale: str        # なぜそう判断したかの根拠
    keywords: list[str]   # 発話から抽出した印象的なキーワード


async def analyze_emotion(client, text: str) -> EmotionResult:
    """発話テキストを感情分析して EmotionResult を返す。

    client: genai.Client（呼び出し側で作ったもの）
    text:   被験者の発話（文字起こし済みテキスト）
    """
    response = await client.aio.models.generate_content(
        model=config.ANALYSIS_MODEL,
        contents=f"次の被験者の発話を感情分析してください。\n\n発話:「{text}」",
        config={
            "system_instruction": config.ANALYZER_SYSTEM_PROMPT,
            # JSON で返すよう指定し、スキーマに EmotionResult を渡す
            "response_mime_type": "application/json",
            "response_schema": EmotionResult,
            "temperature": 0.2,  # 分析はぶれないよう低めに
            # このサンプルでは関数呼び出し(AFC)を使わないので無効化（警告抑制）
            "automatic_function_calling": {"disable": True},
        },
    )
    # response.parsed はスキーマに沿ってパース済みの EmotionResult インスタンス
    return response.parsed
