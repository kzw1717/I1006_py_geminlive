# Gemini Live × 感情分析インタビュー（学生向けサンプル）

Google の **Gemini Live API** を使って、

1. Gemini が**音声**で質問する
2. あなた（被験者）が**マイク**で答える
3. その答えを**文字起こし（STT）**する
4. 答えを**感情分析**する（感情ラベル・強度・根拠・キーワードを構造化して表示）
5. Gemini が答えの中の**キーワードを使って次の質問**を投げかける → 1 に戻る

…というように「会話が続く仕掛け」を体験できるサンプルプログラムです。

音声での対話（STT＋TTS）は Gemini Live API が担当し、感情分析は別途テキストモデルの
**構造化出力（Structured Output）**で行っています。

> 🔰 **はじめて環境を作る人へ**: パソコンの準備から順を追った手順は
> **[docs/開発環境構築手順書_macOS.md](docs/開発環境構築手順書_macOS.md)** にまとめています。

---

## 1. 必要なもの

- **Mac**（mac mini / MacBook Pro で動作確認を想定）
- **[uv](https://docs.astral.sh/uv/)**（Python 環境・パッケージ管理ツール）
- **マイク**と**ヘッドホン**（スピーカーだと音をマイクが拾って会話が乱れやすいので、ヘッドホン推奨）
- **Gemini API キー**（[Google AI Studio](https://aistudio.google.com/apikey) で無料取得）

### uv を入れていない場合

```bash
brew install uv
```

---

## 2. セットアップ

### (1) リポジトリを clone する

```bash
git clone <このリポジトリのURL>
cd I1006_py_geminlive
```

### (2) 依存パッケージをインストールする

```bash
uv sync
```

`uv sync` が Python 3.12 と必要なライブラリ（`google-genai` / `sounddevice` / `python-dotenv`）を
自動でそろえてくれます。

### (3) API キーを設定する

API キーの取得から設定までの詳しい手順は **[docs/API_KEY_SETUP.md](docs/API_KEY_SETUP.md)** を見てください。
環境構築を一から行う場合は **[docs/開発環境構築手順書_macOS.md](docs/開発環境構築手順書_macOS.md)** を参照してください。

かんたんに書くと:

```bash
cp .env.example .env
```

作成された `.env` をエディタで開き、自分の API キーを設定します。

```
GEMINI_API_KEY=ここにあなたのAPIキー
```

> `.env` は `.gitignore` 済みです。**API キーは絶対に GitHub に上げないでください。**

---

## 3. 実行

```bash
uv run python voice/main.py
```

### 使い方

1. 起動すると Gemini が最初の質問を**音声**で話します。
2. 画面に `🎤 Enter で録音開始` と出たら **Enter** を押します。
3. マイクに向かって回答し、話し終えたら **もう一度 Enter**。
4. 回答の文字起こし → 感情分析 → Gemini の次の質問、が順に表示・再生されます。
5. 終了したいときは、録音開始の案内が出たときに **`q` を入力して Enter**。

会話の記録は `logs/session_YYYYMMDD_HHMMSS.jsonl` に1ターン1行で保存されます。

---

## 4. ファイル構成

| ファイル | 役割 |
|----------|------|
| `voice/main.py` | メイン。Live API への接続・録音・再生・会話ループ |
| `voice/emotion.py` | 感情分析（構造化出力で JSON を取得） |
| `voice/config.py` | モデル名・音声・プロンプトなどの設定 |
| `.env.example` | API キー設定のひな形（`.env` にコピーして使う） |
| `pyproject.toml` | uv が読む依存関係の定義 |
| `docs/` | 環境構築手順書・API キー取得マニュアルなどのドキュメント |
| `logs/` | 会話・感情分析の記録（実行時に自動生成） |

---

## 5. 「キーワードで会話が続く仕掛け」について

- Gemini が次の質問を作るときに**直前の回答のキーワードを使う**ように、
  `voice/config.py` の `INTERVIEWER_SYSTEM_PROMPT`（インタビュアーの役割説明）で指示しています。
- 同時に `voice/emotion.py` の感情分析でも**キーワードを抽出して画面に表示**しているので、
  「どのキーワードが拾われて次の質問につながったか」を目で確認できます。

### 発展課題（学生向け）

- 抽出したキーワードを Gemini に明示的に渡して、質問をもっと確実に誘導してみる
- 感情ラベルの種類を増やす／強度のしきい値で会話の分岐を作る
- `logs/` の JSONL を読み込んで、セッション全体の感情の推移をグラフ化する

---

## 6. うまく動かないとき

| 症状 | 対処 |
|------|------|
| `API キーが設定されていません` | `.env` の `GEMINI_API_KEY` を確認 |
| マイクが使えない | macOS の「システム設定 → プライバシーとセキュリティ → マイク」で、使っているターミナル/VSCode に許可を与える |
| 声が二重に聞こえる・会話が乱れる | **ヘッドホンを使う**（スピーカーだと Gemini の声をマイクが拾う） |
| `NOT_FOUND` / `is not found ... bidiGenerateContent` などモデル関連のエラー | モデル名が更新された可能性あり。下の「使えるモデルを調べる」で確認し、`.env` の `GEMINI_LIVE_MODEL` / `GEMINI_ANALYSIS_MODEL` を設定 |
| `PortAudio` 関連のエラー | `uv sync` をやり直す。改善しなければ `brew install portaudio` |

### 使えるモデルを調べる

モデル名は時期によって変わります。`NOT_FOUND` 系のエラーが出たら、
次のコマンドで**今あなたのキーで使えるモデル**を一覧できます。

Live API（音声対話）用のモデル:

```bash
uv run python -c "import sys; sys.path.insert(0,'voice'); import config; from google import genai; c=genai.Client(api_key=config.GEMINI_API_KEY); [print(m.name) for m in c.models.list() if 'bidiGenerateContent' in (m.supported_actions or [])]"
```

感情分析（テキスト）用のモデル:

```bash
uv run python -c "import sys; sys.path.insert(0,'voice'); import config; from google import genai; c=genai.Client(api_key=config.GEMINI_API_KEY); [print(m.name) for m in c.models.list() if 'generateContent' in (m.supported_actions or [])]"
```

表示された名前（`models/` は付けても外してもOK）を `.env` の
`GEMINI_LIVE_MODEL` / `GEMINI_ANALYSIS_MODEL` に設定してください。

---

## 参考リンク

- [Gemini Live API ドキュメント](https://ai.google.dev/gemini-api/docs/live-api)
- [構造化出力（Structured Output）](https://ai.google.dev/gemini-api/docs/structured-output)
- [利用可能なモデル一覧](https://ai.google.dev/gemini-api/docs/models)
