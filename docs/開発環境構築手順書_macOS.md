# 開発環境構築手順書（macOS）

**教材「Gemini Live × 感情分析インタビュー」**

このプロジェクトは、Google の **Gemini Live API** を使って、

- Gemini が**音声**で質問する
- あなた（被験者）が**マイク**で答える
- 答えを**文字起こし（STT）**して**感情分析**する
- 答えの**キーワードを使って次の質問**につなげる

というように「音声で会話が続く」サンプルプログラムです。
この手順書では、macOS で開発・実行できる環境を一から用意します。

> **これから作るもの（今後の予定）**
> このサンプルは、まず**コマンドライン（ターミナル）で動く音声対話プログラム**です。
> 次以降の課題では、**Flask** を使って感情分析の結果を見る**管理画面（Web 画面）**を
> 作っていく予定です。そのため、この手順書の最後に Flask を使い始めるステップも載せています。

---

## 目次

1. [VS Code のインストール](#1-vs-code-のインストール)
2. [Python（uv）のインストール](#2-pythonuvのインストール)
3. [Git のインストール](#3-git-のインストール)
4. [Node.js と repomix のインストール](#4-nodejs-と-repomix-のインストール)
5. [プロジェクトの取得とセットアップ](#5-プロジェクトの取得とセットアップ)
6. [API キーの設定](#6-api-キーの設定)
7. [実行と動作確認](#7-実行と動作確認)
8. [次のステップ：Flask で管理画面を作る](#8-次のステップflask-で管理画面を作る)
9. [よくあるトラブルと対処法](#9-よくあるトラブルと対処法)
10. [付録A：uv の仕組み（clone と uv sync）](#付録auv-の仕組みclone-と-uv-sync)

---

## 1. VS Code のインストール

### 1-1. ダウンロード・インストール

1. <https://code.visualstudio.com/> を開く
2. **「Download for Mac」** をクリックして `.zip` を取得
3. ダウンロードした `.zip` を展開し、`Visual Studio Code.app` を **アプリケーションフォルダ** へドラッグ
4. アプリケーションフォルダから VS Code を起動する

### 1-2. `code` コマンドを PATH に追加

ターミナルから VS Code を開けるようにします。

1. VS Code を起動する
2. `Cmd + Shift + P` でコマンドパレットを開く
3. `Shell Command: Install 'code' command in PATH` を検索して実行する

確認：

```bash
code --version
```

### 1-3. 拡張機能のインストール

左サイドバーの拡張機能アイコン（四角が4つ）をクリックして以下を検索・インストールします。

| 拡張機能名 | 用途 |
|-----------|------|
| `Python`（Microsoft） | Python のシンタックスハイライト・補完 |
| `Japanese Language Pack for VS Code` | 日本語化（任意） |

> このプロジェクトには `.vscode/extensions.json` が入っているので、
> VS Code でフォルダを開くと「推奨拡張機能」としても案内されます。

### 1-4. ターミナルの確認

VS Code のメニュー **「ターミナル → 新しいターミナル」** を開き、zsh が起動することを確認します。

---

## 2. Python（uv）のインストール

Python のパッケージ管理に **uv** を使います。

### 2-1. uv のインストール

**アプリケーション → ユーティリティ → ターミナル** を開き、次のコマンドを実行します。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストール完了後、ターミナルを **一度閉じて開き直します**（PATH を反映するため）。

### 2-2. インストール確認

```bash
uv --version
```

バージョン番号（例：`uv 0.12.3`）が表示されれば成功です。

### 2-3. Python のインストール

```bash
uv python install 3.12
```

確認：

```bash
uv python list
```

`cpython-3.12` が表示されれば成功です。

> このプロジェクトには `.python-version`（中身は `3.12`）が入っているので、
> `uv` が自動的に Python 3.12 を使います。

---

## 3. Git のインストール

macOS には Git が最初から使える場合がありますが、次の手順で確認・インストールします。

### 3-1. インストール確認

```bash
git --version
```

バージョン番号が表示された場合はインストール済みです。
「コマンドが見つかりません」と出た場合は次の手順へ進みます。

### 3-2. Xcode コマンドラインツールのインストール

macOS の Git は Xcode コマンドラインツールに含まれています。

```bash
xcode-select --install
```

ポップアップが表示されたら「インストール」をクリックします（数分かかります）。

### 3-3. ユーザー情報の設定（初回のみ）

```bash
git config --global user.name "あなたの名前"
git config --global user.email "your@email.com"
```

---

## 4. Node.js と repomix のインストール

**repomix** は、プロジェクトのコードを 1 つのファイルにまとめて AI（Gemini など）に渡すためのツールです。
Gemini とのバイブコーディング（AI とのペアプログラミング）で使います。repomix の動作に Node.js が必要です。

> この章は、AI にコードを読ませて相談しながら開発する場合に使います。
> 実行するだけなら必須ではありませんが、授業ではインストールしておくことをおすすめします。

### 4-1. Node.js のインストール

#### 方法A: 公式インストーラーを使う（推奨）

1. <https://nodejs.org/> を開く
2. **「LTS」版**（推奨版）の macOS インストーラー（`.pkg`）をダウンロード
3. `.pkg` を実行してインストール

#### 方法B: Homebrew を使う（Homebrew が既にある場合）

```bash
brew install node
```

#### インストール確認

ターミナルを開き直してから確認します。

```bash
node --version
npm --version
```

### 4-2. repomix のインストール

```bash
npm install -g repomix
```

確認：

```bash
repomix --version
```

### 4-3. 基本的な使い方（参考）

プロジェクトフォルダで実行すると `repomix-output.xml` が生成されます。
このファイルを Gemini に貼り付けてバイブコーディングを行います。

```bash
repomix
```

---

## 5. プロジェクトの取得とセットアップ

このプロジェクトは **GitHub から clone（ダウンロード）して使います**。

### 5-1. リポジトリを clone する

作業用フォルダ（例：`~/dev`）に移動してから clone します。

```bash
cd ~/dev
git clone https://github.com/kzw1717/I1006_py_geminlive.git
cd I1006_py_geminlive
```

### 5-2. VS Code で開く

```bash
code .
```

### 5-3. 依存パッケージをインストールする

```bash
uv sync
```

`uv sync` は、`pyproject.toml` と `uv.lock` を見て、
**必要な Python（3.12）とライブラリをまとめて自動でそろえます。**
初回は少し時間がかかります。

> 主なライブラリ：
> `google-genai`（Gemini API）/ `sounddevice`（マイク・スピーカー）/ `python-dotenv`（.env 読み込み）
> ※ `sounddevice` には音声処理に必要な PortAudio が同梱されているので、別途インストールは不要です。

---

## 6. API キーの設定

Gemini API を使うには **API キー**（無料で取得可能）が必要です。

### 6-1. API キーを取得する

取得手順の詳細は **[API キー取得マニュアル](API_KEY_SETUP.md)** を参照してください。
（Google AI Studio <https://aistudio.google.com/apikey> から無料で取得できます）

### 6-2. `.env` ファイルを作る

```bash
cp .env.example .env
```

### 6-3. `.env` にキーを貼り付ける

作成された `.env` を VS Code で開き、`GEMINI_API_KEY=` の右側にキーを貼り付けます。

```
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ **API キーはパスワードと同じです。他人に教えない・GitHub に上げないこと。**
> `.env` は `.gitignore` 済みなので、Git には含まれません（安全）。
> 無料枠・課金についての注意は [API キー取得マニュアル](API_KEY_SETUP.md) を読んでください。

---

## 7. 実行と動作確認

### 7-1. マイクとヘッドホンの準備

- **マイク**が使えること（内蔵マイクで OK）
- **ヘッドホンの使用を強くおすすめします。**
  スピーカーだと Gemini の声をマイクが拾って会話が乱れることがあります。

### 7-2. プログラムの起動

```bash
uv run python main.py
```

`uv run` は仮想環境を自動で使うため、手動での有効化（`source .venv/bin/activate`）は不要です。

### 7-3. マイクの許可（初回のみ）

初めて実行すると、macOS がマイクの使用許可を求めることがあります。
**「システム設定 → プライバシーとセキュリティ → マイク」** で、
使っているターミナル（または VS Code）に許可を与えてください。

### 7-4. 使い方

1. 起動すると Gemini が最初の質問を**音声**で話します。
2. 画面に `🎤 Enter で録音開始` と出たら **Enter** を押します。
3. マイクに向かって回答し、話し終えたら **もう一度 Enter**。
4. 回答の文字起こし → 感情分析 → Gemini の次の質問、が順に表示・再生されます。
5. 終了したいときは、録音開始の案内が出たときに **`q` を入力して Enter**。

会話の記録は `logs/session_YYYYMMDD_HHMMSS.jsonl` に 1 ターン 1 行で保存されます。
この**ログが、次のステップで作る Flask 管理画面の表示データ**になります。

---

## 8. 次のステップ：Flask で管理画面を作る

次以降の課題では、**Flask**（Python の Web フレームワーク）を使って、
感情分析の結果（`logs/` に保存された JSONL）を**ブラウザで見る管理画面**を作っていきます。

ここでは、Flask を使い始めるための準備だけ紹介します（実際の実装は授業で進めます）。

### 8-1. Flask を追加する

```bash
uv add flask
```

`pyproject.toml` に `flask` が追記され、`uv.lock` も更新されます。

### 8-2. これから増えるファイルの置き場所（予定）

このプロジェクトは、コードをフォルダのルート（いちばん上）に置く構成です。
Flask の管理画面は、次のような形で足していく予定です。

```
I1006_py_geminlive/
├── main.py           ← 音声対話プログラム（今あるもの）
├── config.py         ← 設定（モデル名・音声など）
├── emotion.py        ← 感情分析（Web 画面からも再利用できる）
├── app.py            ← ★ これから作る Flask アプリ（管理画面）
├── templates/        ← ★ HTML テンプレート（Flask が使う）
├── static/           ← ★ CSS や画像
├── logs/             ← 会話・感情分析のログ（管理画面の表示データ）
└── docs/             ← ドキュメント（この手順書など）
```

### 8-3. Flask アプリの起動（将来）

```bash
uv run python app.py
```

> **ポートについての注意**
> macOS 12 以降は AirPlay レシーバーが **5000 番ポート**を使うことがあります。
> Flask を作るときは競合を避けるため、`app.py` で **5001 番**を使う設定にします。
>
> ```python
> app.run(debug=True, port=5001)
> ```
>
> ブラウザで <http://127.0.0.1:5001> を開いて確認します。
> 5001 番も使用中の場合は、別の空きポート（例：5002）に変更してください。

---

## 9. よくあるトラブルと対処法

### `uv` コマンドが見つからない

**原因：** PATH が反映されていない
**対処：** ターミナルを開き直す。それでも解決しない場合は次を実行する

```bash
source ~/.zshrc
```

---

### `API キーが設定されていません` と表示される

**対処：** `.env` が作られているか、`GEMINI_API_KEY` にキーが入っているかを確認する。
手順は [6. API キーの設定](#6-api-キーの設定) を参照。

---

### マイクが使えない・音声が認識されない

**対処：** **「システム設定 → プライバシーとセキュリティ → マイク」** で、
使っているターミナル（または VS Code）にマイクの許可を与える。
許可を変えたあとはプログラムを一度終了して起動し直す。

---

### 声が二重に聞こえる・会話が乱れる

**対処：** **ヘッドホンを使う。**
スピーカーだと Gemini の声をマイクが拾ってしまうのが原因です。

---

### `NOT_FOUND` / `is not found ... bidiGenerateContent` などモデル関連のエラー

**原因：** モデル名が更新された可能性がある
**対処：** 次のコマンドで、今使えるモデルを確認して `.env` に設定する。

Live API（音声対話）用：

```bash
uv run python -c "import config; from google import genai; c=genai.Client(api_key=config.GEMINI_API_KEY); [print(m.name) for m in c.models.list() if 'bidiGenerateContent' in (m.supported_actions or [])]"
```

感情分析（テキスト）用：

```bash
uv run python -c "import config; from google import genai; c=genai.Client(api_key=config.GEMINI_API_KEY); [print(m.name) for m in c.models.list() if 'generateContent' in (m.supported_actions or [])]"
```

表示された名前を `.env` の `GEMINI_LIVE_MODEL` / `GEMINI_ANALYSIS_MODEL` に設定します。

---

### `503 UNAVAILABLE`（高負荷）と出る

**原因：** サーバーが一時的に混雑している
**対処：** 時間をおいて再実行する。感情分析は数回リトライするようになっているので、会話は続けられます。

---

### `PortAudio` 関連のエラーが出る

**対処：** `uv sync` をやり直す。改善しなければ `brew install portaudio` を試す。

---

### VS Code で Python のインタープリタが選択されていない

**対処：**
1. VS Code の右下に表示されている Python バージョンをクリック
2. 「インタープリタの選択」→ `.venv` 内の Python を選択（`.venv/bin/python`）

---

## 付録A：uv の仕組み（clone と uv sync）

### A-1. このプロジェクトは「clone して uv sync」

localmydiary のように自分で `uv init --bare` からプロジェクトを作る場合と違い、
**このプロジェクトは完成した状態を GitHub から clone して使います。**
そのため、環境づくりは次の 1 コマンドだけです。

```bash
uv sync
```

`uv sync` は `uv.lock`（ライブラリの正確なバージョンを記録したファイル）に従って
環境を**全員同じ状態に**そろえます。だれがいつ clone しても同じ環境になるのが利点です。

| コマンド | いつ使う | 役割 |
|---------|---------|------|
| `uv sync` | clone した直後 | `pyproject.toml` / `uv.lock` 通りに環境を用意する |
| `uv add <パッケージ>` | 新しいライブラリを足したいとき | 依存に追加し、`pyproject.toml` / `uv.lock` を更新 |
| `uv run python <ファイル>` | プログラムを動かすとき | 仮想環境を自動で使って実行（有効化は不要） |

### A-2. 将来 Flask を足すときも uv add

管理画面を作るときは、次のように Flask を追加します（[8 章](#8-次のステップflask-で管理画面を作る)参照）。

```bash
uv add flask
```

これで `pyproject.toml` に `flask` が加わり、`uv.lock` も更新されます。
他の人は `uv sync` を実行し直せば、同じ環境（Flask 入り）に追いつけます。
