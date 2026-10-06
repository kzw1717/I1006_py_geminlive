"""Gemini Live API で音声対話しながら感情分析を行うサンプル。

流れ（1ターン）:
  1. Gemini が音声で質問する（スピーカーから聞こえる）
  2. あなた（被験者）が Enter を押してマイクで回答する
  3. 回答を文字起こし（STT）して画面に表示する
  4. 回答を感情分析して、感情ラベル・強度・根拠・キーワードを表示する
  5. Gemini が回答のキーワードを使って「次の質問」を音声で投げかける → 1 に戻る

終了するには、録音開始の案内が出たときに「q」を入力して Enter。

※ スピーカーの音をマイクが拾うと会話が乱れるので、ヘッドホンの使用を強くおすすめします。
"""

import asyncio
import datetime
import json
import os
import sys

import sounddevice as sd
from google import genai
from google.genai import types

import config
from emotion import EmotionResult, analyze_emotion


# ---------------------------------------------------------------------------
# 画面表示のための小さなヘルパー
# ---------------------------------------------------------------------------
def print_question(text: str) -> None:
    print(f"\n🤖 Gemini（質問）: {text}")


def print_answer(text: str) -> None:
    print(f"🗣  被験者（回答）: {text}")


def print_emotion(emo: EmotionResult) -> None:
    """感情分析の結果を見やすく表示する。"""
    # 強度を 0〜10 個の ● で棒グラフ風に表示
    filled = round(max(0.0, min(1.0, emo.intensity)) * 10)
    bar = "●" * filled + "○" * (10 - filled)
    print("┌─ 感情分析 ─────────────────────────────")
    print(f"│ 感情    : {emo.primary_emotion}")
    print(f"│ 強度    : {bar} {emo.intensity:.2f}")
    print(f"│ キーワード: {', '.join(emo.keywords) if emo.keywords else '(なし)'}")
    print(f"│ 根拠    : {emo.rationale}")
    print("└────────────────────────────────────────")


# ---------------------------------------------------------------------------
# Live API とのやりとり
# ---------------------------------------------------------------------------
async def collect_response(session, out_stream) -> tuple[str, str]:
    """Gemini からの1ターン分の応答を受け取る。

    - 届いた音声はスピーカーで再生する
    - 文字起こし（被験者の発話 / Gemini の発話）を集める
    戻り値: (被験者の回答テキスト, Gemini の質問テキスト)
    """
    answer_text = ""
    question_text = ""

    async for response in session.receive():
        # response.data は音声データ（あれば）
        if response.data:
            await asyncio.to_thread(out_stream.write, response.data)

        server_content = response.server_content
        if server_content is None:
            continue

        # 被験者の発話の文字起こし（STT の結果）
        if server_content.input_transcription and server_content.input_transcription.text:
            answer_text += server_content.input_transcription.text

        # Gemini の発話（質問）の文字起こし
        if server_content.output_transcription and server_content.output_transcription.text:
            question_text += server_content.output_transcription.text

        # このターンが終わったら受信ループを抜ける
        if server_content.turn_complete:
            break

    return answer_text.strip(), question_text.strip()


async def record_subject_turn(session, out_stream) -> tuple[str, str]:
    """被験者の回答をマイクで録音して Gemini に送り、応答を受け取る。

    Enter を押すと録音が止まる（プッシュ・トゥ・トーク方式）。
    戻り値: (被験者の回答テキスト, Gemini の次の質問テキスト)
    """
    # 「もう一度 Enter が押されたら録音終了」を待つタスク
    stop_waiter = asyncio.create_task(asyncio.to_thread(sys.stdin.readline))

    # 手動で「発話の開始」を Gemini に伝える
    await session.send_realtime_input(activity_start=types.ActivityStart())

    in_stream = sd.RawInputStream(
        samplerate=config.SEND_SAMPLE_RATE,
        channels=config.CHANNELS,
        dtype="int16",
    )
    in_stream.start()
    print("   ● 録音中… 話し終えたら Enter を押してください")

    try:
        # Enter が押される（stop_waiter が完了する）までマイク音声を送り続ける
        while not stop_waiter.done():
            data, _overflowed = await asyncio.to_thread(in_stream.read, config.CHUNK_FRAMES)
            await session.send_realtime_input(
                audio=types.Blob(
                    data=bytes(data),
                    mime_type=f"audio/pcm;rate={config.SEND_SAMPLE_RATE}",
                )
            )
    finally:
        in_stream.stop()
        in_stream.close()

    # 「発話の終了」を Gemini に伝える → ここで Gemini が応答（次の質問）を作り始める
    await session.send_realtime_input(activity_end=types.ActivityEnd())
    await stop_waiter  # 念のため終了待ちを回収

    return await collect_response(session, out_stream)


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------
def build_live_config() -> dict:
    """Live API の接続設定を作る。"""
    return {
        "response_modalities": ["AUDIO"],          # Gemini は音声で返す
        "input_audio_transcription": {},            # 被験者の音声を文字起こし（STT）
        "output_audio_transcription": {},           # Gemini の音声も文字起こし（質問テキスト取得用）
        "system_instruction": config.INTERVIEWER_SYSTEM_PROMPT,
        "speech_config": {
            "language_code": config.LANGUAGE_CODE,
            "voice_config": {
                "prebuilt_voice_config": {"voice_name": config.VOICE_NAME}
            },
        },
        # 録音の開始／終了を自分で制御する（プッシュ・トゥ・トーク）
        "realtime_input_config": {
            "automatic_activity_detection": {"disabled": True}
        },
    }


def open_log_file():
    """会話ログを保存する JSONL ファイルを開く。"""
    os.makedirs("logs", exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("logs", f"session_{stamp}.jsonl")
    return open(path, "w", encoding="utf-8"), path


async def main() -> None:
    if not config.GEMINI_API_KEY:
        print("エラー: API キーが設定されていません。")
        print("  1) .env.example を .env にコピー:  cp .env.example .env")
        print("  2) .env を開いて GEMINI_API_KEY にキーを設定してください。")
        print("  API キーの取得: https://aistudio.google.com/apikey")
        return

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    # Gemini の音声を再生するスピーカー用ストリーム
    out_stream = sd.RawOutputStream(
        samplerate=config.RECV_SAMPLE_RATE,
        channels=config.CHANNELS,
        dtype="int16",
    )
    out_stream.start()

    log_file, log_path = open_log_file()

    print("=" * 60)
    print(" Gemini Live × 感情分析インタビュー サンプル")
    print("=" * 60)
    print(f" Live モデル     : {config.LIVE_MODEL}")
    print(f" 感情分析モデル  : {config.ANALYSIS_MODEL}")
    print(f" ログの保存先    : {log_path}")
    print(" ヘッドホンの使用を推奨します。")
    print("=" * 60)

    try:
        async with client.aio.live.connect(
            model=config.LIVE_MODEL, config=build_live_config()
        ) as session:
            # --- 最初の質問を作らせる ---
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": config.KICKOFF_PROMPT}]},
                turn_complete=True,
            )
            _, question = await collect_response(session, out_stream)
            print_question(question)

            # --- 会話ループ ---
            turn = 1
            while True:
                cmd = await asyncio.to_thread(
                    input, f"\n[{turn}ターン目] 🎤 Enter で録音開始（終了は q → Enter）: "
                )
                if cmd.strip().lower() == "q":
                    break

                answer, next_question = await record_subject_turn(session, out_stream)

                if not answer:
                    print("   （音声を認識できませんでした。もう一度お試しください）")
                    continue

                print_answer(answer)

                # 感情分析（構造化出力）
                emotion = await analyze_emotion(client, answer)
                print_emotion(emotion)

                # Gemini がキーワードを使って作った「次の質問」
                print_question(next_question)

                # ログを1行（JSON）で保存
                log_file.write(
                    json.dumps(
                        {
                            "turn": turn,
                            "answer": answer,
                            "emotion": emotion.model_dump(),
                            "next_question": next_question,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                log_file.flush()
                turn += 1

    except KeyboardInterrupt:
        pass
    finally:
        out_stream.stop()
        out_stream.close()
        log_file.close()
        print("\nインタビューを終了しました。お疲れさまでした。")
        print(f"会話ログ: {log_path}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n中断しました。")
