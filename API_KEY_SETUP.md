# Gemini API キー 取得マニュアル

このプログラムを動かすには、Google の **Gemini API キー**が必要です。
API キーは [Google AI Studio](https://aistudio.google.com/) から**無料**で取得できます。

所要時間は 3〜5 分程度です。

---

## 事前に必要なもの

- **Google アカウント**（Gmail アカウントなど。持っていない場合は先に作成してください）
- インターネットにつながった PC（ブラウザ）

---

## 手順

### 1. Google AI Studio を開く

ブラウザで次の URL を開きます。

👉 **https://aistudio.google.com/apikey**

> ログインを求められたら、自分の Google アカウントでログインしてください。

### 2. 利用規約に同意する（初回のみ）

初めて使う場合、利用規約（Terms of Service）への同意画面が表示されます。
内容を確認し、チェックを入れて同意します。

### 3. 「API キーを作成」をクリック

画面の **「Create API key」（API キーを作成）** ボタンをクリックします。

### 4. プロジェクトを選ぶ／作る

- Google Cloud のプロジェクトを選ぶ画面が出たら、
  **「Create API key in new project」（新しいプロジェクトで作成）** を選べば OK です。
- すでにプロジェクトがある人は、それを選んでも構いません。

### 5. API キーが表示される

`AIza...` で始まる文字列が **あなたの API キー**です。

> 🔑 **この文字列をコピーしておきます。**（次の「設定方法」で使います）

---

## API キーをプログラムに設定する

### 1. `.env` ファイルを作る

プロジェクトのフォルダで、次のコマンドを実行します。

```bash
cp .env.example .env
```

### 2. `.env` にキーを貼り付ける

作成された `.env` をエディタ（VSCode など）で開き、
`GEMINI_API_KEY=` の右側にコピーした API キーを貼り付けます。

```
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> `=` の前後にスペースを入れない／キーを引用符で囲まない、のがポイントです。

### 3. 保存する

ファイルを保存すれば設定完了です。これでプログラムが API キーを読み込めます。

---

## ⚠️ とても大事な注意

- **API キーは「パスワード」と同じです。他人に教えない・公開しないでください。**
- **GitHub に絶対にアップロードしないこと。**
  このプロジェクトでは `.env` が `.gitignore` に登録済みなので、
  `.env` に書いたキーは Git には含まれません（安全）。
- キーをうっかり公開してしまったら、
  [Google AI Studio の API キー画面](https://aistudio.google.com/apikey) から
  そのキーを **削除（Delete）** し、新しいキーを作り直してください。
- 友だちや SNS、課題の提出物などにキーを貼り付けないよう注意してください。

---

## 困ったときは

| 症状 | 原因・対処 |
|------|-----------|
| プログラムが `API キーが設定されていません` と出る | `.env` が作られていない／`GEMINI_API_KEY` が空。手順をもう一度確認 |
| `401` や `API key not valid` と出る | キーの貼り付けミス（スペースや改行が混入）。コピーし直す |
| `429`／`quota` と出る | 無料枠の上限に達した可能性。時間をおくか、使用量を確認する |
| キー画面が英語で分からない | ブラウザの翻訳機能を使うと読みやすくなります |

---

## 参考リンク

- [Google AI Studio（API キー画面）](https://aistudio.google.com/apikey)
- [Gemini API 公式ドキュメント](https://ai.google.dev/gemini-api/docs)
- [料金・無料枠について](https://ai.google.dev/pricing)
