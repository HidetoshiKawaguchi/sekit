# SEKit (science experiment kit, エスイーキット)
科学計算実験のために、作者が自分で使うように作成したPythonツール郡です。
それぞれ独立して使用することができますが、親和性が高いので連携して使うことがおすすめです。

現在は以下のツールを提供しています。
各ツールの使い方は、それぞれのツールが保存されているディレクトリのREADMEを参照してください。
- Spartan
  - クラスタマシン用分散実行ツール。ローカルマシンだけでも使えます。

## 必要なパッケージ
Python3で動きます。
標準で含まれていない必要なライブラリはPyYAMLだけです。
以下のコマンドでPyYAMLはインストールできます。
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
PyYAML==5.3.1
```


## 作者情報
- 名前: 川口英俊(Hidetoshi KAWAGUCHI)
- 所属1: NTT
- 所属2: JAIST(学生)
- 専門: 機械学習の応用
- Twitter: Hidetoshi_RM
