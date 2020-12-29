# SEKit (science experiment kit, エスイーキット)
科学計算実験のために、作者が自分で使うように作成したPythonツール郡です。
それぞれ独立して使用することができますが、親和性が高いので連携して使うことがおすすめです。

現在は以下のツールを提供しています。
各ツールの使い方は、それぞれのツールが保存されているディレクトリのREADMEを参照してください。
- Spartan
  - クラスタマシン用分散実行ツール。ローカルマシンだけでも使えます。
- EIO
  - 実験用関数をいい感じに保存するためのデコレータ
- Search
  - 実験結果が保存されたJSONファイルを集約して、CSV形式に変換するツール
  - Stats
    - Searchの拡張ツール. Searchの結果から統計値を算出するツール

## 必要なパッケージ
Python3で動きます。
標準で含まれていない必要なライブラリはNumpy, Pandas, PyYAMLです。
以下のコマンドでインストールできます。
```
pip install numpy
```
```
pip install pandas
```
```
pip install pyyaml
```

少なくとも、作者の以下の環境では動作します。
```
$ python --version
Python 3.8.5
```
```
$ pip freeze
certifi==2020.12.5
numpy==1.19.4
pandas==1.1.5
python-dateutil==2.8.1
pytz==2020.5
PyYAML==5.3.1
six==1.15.0
```


## 作者情報
- 名前: 川口英俊(Hidetoshi KAWAGUCHI)
- 所属1: NTT
- 所属2: JAIST(学生)
- 専門: 機械学習の応用
- Twitter: Hidetoshi_RM
