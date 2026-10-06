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

API キーの取得から設定までの詳しい手順は **[API_KEY_SETUP.md](API_KEY_SETUP.md)** を見てください。

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
uv run python main.py
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
| `main.py` | メイン。Live API への接続・録音・再生・会話ループ |
| `emotion.py` | 感情分析（構造化出力で JSON を取得） |
| `config.py` | モデル名・音声・プロンプトなどの設定 |
| `.env.example` | API キー設定のひな形（`.env` にコピーして使う） |
| `pyproject.toml` | uv が読む依存関係の定義 |

---

## 5. 「キーワードで会話が続く仕掛け」について

- Gemini が次の質問を作るときに**直前の回答のキーワードを使う**ように、
  `config.py` の `INTERVIEWER_SYSTEM_PROMPT`（インタビュアーの役割説明）で指示しています。
- 同時に `emotion.py` の感情分析でも**キーワードを抽出して画面に表示**しているので、
  「どのキーワードが拾われて次の質問につながったか」を目で確認できます。

### 発展課題（学生向け）

- 抽出したキーワードを Gemini に明示的に渡して、質問をもっと確実に誘導してみる
- 感情ラベルの種類を増やす／強度のしきい値で会話の分岐を作る
- `logs/` の JSONL を読み込んで、セッション全体の感情の推移をグラフ化する

---

## 6. 音声再生の工夫（なぜこの処理があるのか）

あとでコードを読んだときに「なぜこんな処理をしているの?」と迷わないよう、
音声再生まわりの工夫とその理由をまとめます。関連コードはすべて `main.py` にあります。

### 背景にある問題：Mac 内蔵スピーカーの「音量補正」

Mac の内蔵スピーカーには、音を保護・最適化するための**音量補正（ラウドネス補正／リミッター）**が
働いています。これには次のクセがあります。

1. **音の立ち上がりは一瞬大きく鳴り、その後すぐ補正が効いて音量が落ち着く。**
   → そのままだと「発話の最初の1〜2秒だけ音が大きい」ように聞こえる。
2. **音が完全に途切れる（無音になる）と、補正がリセットされる。**
   → 次に音が鳴るとき、また最初から大きく鳴ってしまう。
   このプログラムは「Gemini が話す → ユーザーが録音する（この間スピーカーは無音）」を
   繰り返すため、**ターンごとに無音の時間ができ、毎回リセット**されてしまう。

この 1. と 2. に対して、それぞれ対策を入れています。

### 対策1：冒頭フェードイン（`shape_audio` 関数）

`main.py` の `shape_audio()` で、**各発話の冒頭を `PLAYBACK_FADE_IN_SECONDS` 秒かけて
音量 0 → 通常音量へ徐々に上げて**います（音量カーブ＝ランプをかける）。

- ねらい：立ち上がりの「一瞬の大音量」をなだらかにして、耳障りな出だしを消す。
- 実装：受信した 16bit PCM を numpy で数値配列に変換し、冒頭部分に 0.0→1.0 の
  係数（ランプ）を掛け算 → 再び 16bit に戻す。
- ついでに `OUTPUT_GAIN`（全体音量の倍率）も同じ場所で掛けています。
- フェードの位置は**発話（ターン）ごとに 0 から数え直す**ので、毎回の質問の冒頭に効きます。

> 関連設定（`config.py`）: `PLAYBACK_FADE_IN_SECONDS`, `OUTPUT_GAIN`

### 対策2：無音のキープアライブ再生（`Speaker` クラス）

対策1だけだと「最初の発話」は良くなりますが、**ターンを繰り返すと再び出だしが大きく**なります。
これは上記 2.（無音でリセットされる）が原因です。

そこで `Speaker` クラスでは、**再生していない間も 20 ミリ秒ごとに「無音データ」を書き込み続け**、
スピーカー（CoreAudio デバイス）を止めずに動かし続けます（キープアライブ）。

- ねらい：デバイスを“無音状態”にさせないことで、**音量補正がリセットされるのを防ぐ**。
  これにより、2 回目以降のターンでも出だしの音量が一定になる。
- 実装：
  - 再生は専用の非同期タスク（`Speaker._run`）＋キュー（`asyncio.Queue`）で行う。
  - キューに音声があれば再生、なければ無音（`self._silence`）を書き込む、を繰り返す。
  - 録音中もこのタスクは動き続けるので、録音の無音区間でもリセットされない。
- 実音声と無音を**1 本のタスクで順番に書き込む**ため、両者がぶつからない。

### 対策3：録音前に再生を待つ（`Speaker.wait_idle`）

録音を始める前に `wait_idle()` を呼び、**直前の質問音声を最後まで再生し終えてから**
マイクを開きます。

- ねらい：質問の音声がまだ鳴っている最中に録音が始まると、スピーカーの音をマイクが拾って
  しまう（回り込み・エコー）。それを防ぐ。
- 実装：再生キューが空になるまで待ち、さらにデバイスの出力バッファ分だけ少し待つ。

### それでも気になるときは

内蔵スピーカー特有の挙動なので、**ヘッドホンや外部スピーカーを使うと補正自体が働かず、
いちばん確実に解消**します。ソフト側で粘るなら `config.py` の
`PLAYBACK_FADE_IN_SECONDS` を長く、または `OUTPUT_GAIN` を下げて調整してください。

---

## 7. うまく動かないとき

| 症状 | 対処 |
|------|------|
| `API キーが設定されていません` | `.env` の `GEMINI_API_KEY` を確認 |
| マイクが使えない | macOS の「システム設定 → プライバシーとセキュリティ → マイク」で、使っているターミナル/VSCode に許可を与える |
| 声が二重に聞こえる・会話が乱れる | **ヘッドホンを使う**（スピーカーだと Gemini の声をマイクが拾う） |
| 発話の出だしだけ音が大きい | Mac 内蔵スピーカーの音量補正でよく起きます。冒頭フェードインで緩和済み。さらに調整したいときは `config.py` の `PLAYBACK_FADE_IN_SECONDS`（冒頭を大きくする秒数）や `OUTPUT_GAIN`（全体音量。例: 0.6）を変更 |
| `NOT_FOUND` / `is not found ... bidiGenerateContent` などモデル関連のエラー | モデル名が更新された可能性あり。下の「使えるモデルを調べる」で確認し、`.env` の `GEMINI_LIVE_MODEL` / `GEMINI_ANALYSIS_MODEL` を設定 |
| `PortAudio` 関連のエラー | `uv sync` をやり直す。改善しなければ `brew install portaudio` |

### 使えるモデルを調べる

モデル名は時期によって変わります。`NOT_FOUND` 系のエラーが出たら、
次のコマンドで**今あなたのキーで使えるモデル**を一覧できます。

Live API（音声対話）用のモデル:

```bash
uv run python -c "import config; from google import genai; c=genai.Client(api_key=config.GEMINI_API_KEY); [print(m.name) for m in c.models.list() if 'bidiGenerateContent' in (m.supported_actions or [])]"
```

感情分析（テキスト）用のモデル:

```bash
uv run python -c "import config; from google import genai; c=genai.Client(api_key=config.GEMINI_API_KEY); [print(m.name) for m in c.models.list() if 'generateContent' in (m.supported_actions or [])]"
```

表示された名前（`models/` は付けても外してもOK）を `.env` の
`GEMINI_LIVE_MODEL` / `GEMINI_ANALYSIS_MODEL` に設定してください。

---

## 参考リンク

- [Gemini Live API ドキュメント](https://ai.google.dev/gemini-api/docs/live-api)
- [構造化出力（Structured Output）](https://ai.google.dev/gemini-api/docs/structured-output)
- [利用可能なモデル一覧](https://ai.google.dev/gemini-api/docs/models)
