# Repomix チートシート（Gemini Live 音声・感情分析アプリ開発向け）

Repomix は、指定したディレクトリ内のコードベースを AI（Gemini など）に読み込ませやすい
1 つのテキストファイルにまとめるツールです。このプロジェクト（Gemini Live × 感情分析）での
使い方に合わせてまとめました。

> ⚠️ **最重要：`.env`（API キー）は絶対に AI に渡さないこと。**
> このプロジェクトの `.env` には Gemini の API キーが入っています。
> 後述の `.repomixignore` で `.env` を必ず除外してください（初期設定で除外例を載せています）。

---

## 1. 基本的な使い方

デフォルトでは、コマンドを実行した階層のファイルをまとめ、`repomix-output.txt` を生成します。

```bash
npx repomix
```

---

## 2. 出力フォーマットの変更

XML 形式や Markdown 形式など、AI が理解しやすい形式を指定できます。
プロンプトとして渡す場合は構造化された XML 形式がおすすめです。

```bash
npx repomix --style xml
```

---

## 3. `--init` を使った初期設定とファイル除外の自動化（おすすめ）

毎回オプション（`--ignore` や `--style` など）を指定する手間を省くため、プロジェクトルートで
初期化コマンドを実行し、設定ファイルを作成するのがおすすめです。

```bash
npx repomix --init
```

**【実行画面のサンプル】**
```text
watan@macbookpro2025 I1006_py_geminlive % npx repomix --init

📦 Repomix v1.18.1

┌  Welcome to Repomix Configuration!
│
◇  Do you want to create a repomix.config.json file?
│  Yes
│
◇  Output style:
│  XML
│
◇  Output file path:
│  repomix-output.xml
│
◆  Config file created!
│  Path: repomix.config.json
│
◇  Do you want to create a .repomixignore file?
│  Yes
│
◆  Created .repomixignore file!
│  Path: .repomixignore
│
└  Initialization complete! You can now use Repomix with your specified settings.
```

**【解説】**
このコマンドを実行し、対話形式の質問に「Yes」や「XML」と答えていくと、以下の 2 つのファイルが
プロジェクトルートに自動作成されます。

*   **`repomix.config.json`**: 出力形式（XML）や出力ファイル名などの**全体設定**を保存します。
*   **`.repomixignore`**: Git の `.gitignore` と全く同じように、AI に読み込ませたくない不要な
    ファイルやフォルダを箇条書きで指定するための**除外設定専用ファイル**です。

### `.repomixignore` の設定方法（このプロジェクト向け）

作成された `.repomixignore` ファイルをエディタで開き、不要なファイルを以下のように追記します。
特に **`.env`（API キー）**、環境ファイル、巨大なロックファイルを除外することで、
**情報漏えいの防止**・トークンの節約・AI の回答精度の向上が見込めます。

```text
# ========================
# 最重要：秘密情報（絶対に AI に渡さない）
# ========================
# Gemini の API キーが入っているため必ず除外
.env

# ========================
# Python環境・キャッシュ
# ========================
.venv/
__pycache__/
*.pyc

# ========================
# 実行時に生成されるデータ
# ========================
# 会話・感情分析のログ（設計には不要／個人の発話を含む）
logs/

# ========================
# 関連ドキュメント（設計に関係しない）
# ========================
docs/

# ========================
# 環境・OS・エディタ関連
# ========================
# Macのシステムファイル
.DS_Store

# Git関連
.git/
.gitignore

# VS Code の設定
.vscode/

# ========================
# パッケージ管理
# ========================
# 依存関係のロックファイル（pyproject.tomlがあれば十分なため除外）
uv.lock

# ========================
# Repomix自身の出力ファイル
# ========================
repomix-output.*
```

> 💡 これで AI に渡るのは、主に `voice/`（音声対話プログラム）や `pyproject.toml`、
> （将来作る）`app.py`・`templates/` など、**設計・実装に本当に必要なファイルだけ**になります。

---

## 4. クリップボードへ直接コピー

ファイルを出力せずに直接クリップボードにコピーします。すぐに Gemini のチャット画面に
貼り付けたい場合に一番便利なオプションです。
（上記 3 の設定を行っていれば、これだけでファイル除外や XML 化も自動で適用されます）

```bash
npx repomix --copy
```

---

## 5. AI（Gemini 等）との開発サイクル

**⚠️ 注意: `npx repomix` コマンドは、必ず開発ディレクトリのプロジェクトルート
（`pyproject.toml` や `repomix.config.json` が置かれている一番上の階層＝`I1006_py_geminlive/`）で
実行してください。** 別の階層で実行すると、必要なファイルが読み込まれなかったり、
想定外のファイルが含まれたりする原因になります。

以下のサイクルを回すことで、AI を活用した「バイブコーディング」をスムーズに行えます。

1. **コードをまとめる:** 必ずプロジェクトルートに移動し、以下のコマンドで最新のコード全体を
   クリップボードにコピーします。
   ```bash
   npx repomix --copy
   ```
2. **AI にプロンプトを送信:** Gemini などのチャット欄にペーストし、「このエラーを直して」
   「感情の推移をグラフにする管理画面を Flask で作りたい」などの具体的な指示を添えて送信します。
3. **コードの反映:** AI が提案した修正内容を VS Code 上の各ファイルに反映させます。
4. **動作確認:**
   - 音声対話プログラム → `uv run python voice/main.py`
   - （将来の Flask 管理画面）→ `uv run python app.py` し、ブラウザで <http://127.0.0.1:5001> を確認
5. **繰り返す:** 新しい変更を加えた後や、エラーが発生した場合は、再度 1. に戻って最新状態を
   コピーし、AI に渡します。

---

## 参考

- このプロジェクトの環境構築：[開発環境構築手順書_macOS.md](開発環境構築手順書_macOS.md)
- Repomix 公式：<https://github.com/yamadashy/repomix>
