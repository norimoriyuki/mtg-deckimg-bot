# DeckImg Bot

Magic: The Gatheringのデッキリストから視覚的なデッキ画像を生成するDiscord botです。

## 機能

- **デッキ画像生成**: デッキリストを入力すると、カード画像を組み合わせたデッキ画像を自動生成
- **計算機能**: Discord上で数学計算を実行
- **Scryfall API連携**: 最新のカード情報と画像を取得

## コマンド

### `!deckimg [デッキリスト]`
デッキリストから画像を生成します。

**使用例:**
```
!deckimg 4 Lightning Bolt
3 Counterspell
2 Brainstorm
```

### `!c [計算式]`
数学計算を実行します。

**使用例:**
```
!c 2 + 3 * 4
!c comb(52, 7)
```

### メンション計算
botをメンションして計算式を送信することでも計算できます。

## セットアップ

### Discord Developer Portal設定

1. [Discord Developer Portal](https://discord.com/developers/applications/)にアクセス
2. アプリケーションを作成またはを選択
3. 「Bot」セクションに移動
4. 「Privileged Gateway Intents」で以下を有効化：
   - **Message Content Intent** ✅ （必須）
   - Server Members Intent は無効のまま
   - Presence Intent は無効のまま

### 必要な環境変数

以下の環境変数を設定してください：

- `DISCORD_BOT_TOKEN`: Discord botのトークン
- `DATABASE_URL`: データベースのURL（現在未使用）

### ローカル実行

1. リポジトリをクローン:
```bash
git clone <repository-url>
cd deckimg-bot
```

2. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

3. 環境変数を設定:
```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
export DATABASE_URL="your_database_url_here"
```

4. botを実行:
```bash
python bot.py
```

### Herokuデプロイ

このプロジェクトはHerokuでの実行に対応しています。

1. Heroku CLIをインストール
2. Herokuアプリを作成:
```bash
heroku create your-app-name
```

3. 環境変数を設定:
```bash
heroku config:set DISCORD_BOT_TOKEN="your_bot_token_here"
heroku config:set DATABASE_URL="your_database_url_here"
```

4. デプロイ:
```bash
git push heroku main
```

## 依存関係

- `discord.py`: Discord API wrapper
- `requests`: HTTP リクエスト処理
- `python-dotenv`: 環境変数管理
- `Pillow`: 画像処理

## ファイル構成

- `bot.py`: メインのbot実行ファイル
- `deckviewer.py`: デッキ画像生成のロジック
- `myutils.py`: ユーティリティ関数
- `requirements.txt`: Python依存関係
- `Procfile`: Herokuデプロイ設定
- `Roboto-Black.ttf`: フォントファイル

## API

このbotは[Scryfall API](https://scryfall.com/docs/api)を使用してMagic: The Gatheringのカード情報を取得しています。

## トラブルシューティング

### PrivilegedIntentsRequired エラー
```
discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents...
```

**解決方法:**
1. [Discord Developer Portal](https://discord.com/developers/applications/)でアプリケーションを開く
2. 「Bot」セクションに移動
3. 「Privileged Gateway Intents」で「Message Content Intent」を有効化
4. 変更を保存してbotを再起動

### 計算エラー
- `eval()`を使用しているため、安全でない入力は避けてください
- 数学関数（`comb`, `sin`, `cos`など）が利用可能です

## 注意事項

- カード名は正確に入力してください（英語名推奨）
- 大量のカードを含むデッキの場合、画像生成に時間がかかる場合があります
- Scryfall APIの利用制限に注意してください
- `eval()`関数を使用しているため、信頼できるユーザーのみが使用することを推奨

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能要望は、GitHubのIssuesでお知らせください。プルリクエストも歓迎します。
