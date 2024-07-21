# SEKit (science experiment kit, エスイーキット)
科学計算実験のために、作者が自分で使うように作成したPythonツール郡です。
それぞれ独立して使用することができますが、親和性が高いので連携して使うことがおすすめです。

現在は以下のツールを提供しています。
各ツールの使い方は、それぞれのツールが保存されているディレクトリのREADMEを参照してください。
- Spartan
  - クラスタマシン用分散実行ツール。ローカルマシンだけでも使えます。
  - ドキュメント: [docs/spartan.md](docs/spartan.md)
- EIO
  - 実験用関数をいい感じに保存するためのデコレータ
  - ドキュメント: [docs/eio.md](docs/eio.md)
- Search
  - 実験結果が保存されたJSONファイルを集約して、CSV形式に変換するツール
  - ドキュメント: [docs/search.md](docs/search.md)
- Stats
  - Searchの拡張ツール. Searchの結果から統計値を算出するツール
  - ドキュメント: [docs/stats.md](docs/stats.md)
- jymatplot
  - JSONかYAMLからグラフ画像を描画するmatplotlibのラッパー
  - ドキュメント [docs/jymatplot.md](docs/jymatplot.md)

## インストール方法
以下の pip install でインストールできます。
```
pip install sekit
```

## 【開発者向け】注意
### テストのセットアップ
テストを実行するためには、以下の手順を実行する必要があります。
以下の手順のコマンドはすべて本リポジトリのルートディレクトリで実行されるものとします。

1. 例えば以下のコマンドで、SSH接続用の秘密鍵と公開鍵を作る
```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```
この時、`~/.ssh/にid_rsaとid_rsa.pub`ができる。

2. 以下のコマンドを実行して、このファイルがあるディレクトリにid_rsa.pubを保存する。
```
cp ~/.ssh/id_rsa.pub ./tests/spartan/
```

3. 以下のコマンドを実行して、Dockerイメージをビルドする
```
docker build -t test_ssh_server ./tests/spartan/
```

4. 以下のコマンドを実行して、テスト用Dockerコンテナを起動する。
```
docker run -d -p 2222:22 --name test_ssh_container test_ssh_server
```

5. /etc/hostsを設定してtest-ssh-serverというホスト名で127.0.0.1につながるようにする。
```
127.0.0.1       test-ssh-server
```

6. ~/.ssh/configに以下の設定を追加する。
```
Host test-ssh-server
  HostName test-ssh-server
  User root
  Port 2222
```

確認方法
```
ssh test-ssh-server
```

### テストの実行方法
テストコードはpytestで実装されています。以下のコマンドでテスト可能です。
```
pytest
```


## 作者情報
- 名前: 川口英俊(Hidetoshi KAWAGUCHI)
- 職業: データサイエンティスト
- 学位: 博士（情報科学）
- Twitter: Hidetoshi_RM
- Zenn: https://zenn.dev/hidetoshi
- Qiita: https://qiita.com/Hidetoshi_Kawaguchi

