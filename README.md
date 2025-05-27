# DeckImg Bot

Magic: The Gatheringのデッキリストから視覚的なデッキ画像を生成するDiscord botです。

## 機能

- **デッキ画像生成**: デッキリストを入力すると、カード画像を組み合わせたデッキ画像を自動生成
- **計算機能**: Discord上で数学計算を実行

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

## API

このbotは[Scryfall API](https://scryfall.com/docs/api)を使用してMagic: The Gatheringのカード情報を取得しています。
