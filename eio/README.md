# EIO
実験用関数をいい感じに保存するためのデコレータです。

## まず動かしてみる。
例えば、以下のような実験用関数を例に説明します。
なお、このファイルはsample/sample1.pyです。
```python
# -*- coding:utf-8 -*-
import os.path as op
_base = op.join(op.dirname(op.abspath(__file__)), '..', '..')
import sys
sys.path.append(_base)
import pandas as pd

from eio import eio

@eio()
def sample1(hidden_layer_sizes: tuple,
            activation: str,
            validation_fraction:float) -> dict:
    dict_out = {
        'a': [a * 2 for a in hidden_layer_sizes],
        'b': '___' + activation + '___',
        'c': validation_fraction * 3
    }
    return dict_out

if __name__ == '__main__':
    sample1(hidden_layer_sizes=[100, 200],
            activation='relu',
            validation_fraction=0.1)
```
`sample1`メソッドが、`eio`メソッドでデコレートされています。
`sample`ディレクトリに移動して、実行してみましょう。
```
$ cd sample
$ python sample.py
[0.0m] finished: a=relu,hls=100,vf=0.1
```
そうすると、以上のようになります。
実験結果を確認してみましょう。
```json
$ cat sample1,a=relu,hls=100,vf=0.1.json
{
    "_param": {
        "activation": "relu",
        "hidden_layer_sizes": [
            100,
            200
        ],
        "validation_fraction": 0.1
    },
    "_process_time": 3.0994415283203125e-06,
    "a": [
        200,
        400
    ],
    "b": "___relu___",
    "c": 0.30000000000000004
}
```

以上がEIOの基本動作です。
EIOデコレータは、実験用関数(この例では`sample1`関数)の出力を、いい感じに保存してくれる機能を有します。
具体的には、実験用関数に以下の機能を付与します。

- 引数(実験パラメータ)を加味した自動ファイル名生成による保存
- 実験結果のJSONに以下の情報を自動付与
  - `_param`: 実験パラメータ
  - `_process_time`: 実行時間(単位:秒)


## 実験用関数のインタフェース
実験用関数の出力は以下のいずれかに対応しています。

- Dict型
- PandasのDataframe型

実験用関数の出力を以上のいずれかもしくは複数の組み合わせに設定することで、Dict型をJSONとして、Dataframe型はCSVとして保存します。
`sample2.py`のようにすることで、両方で保存することもできます。
```python
# -*- coding:utf-8 -*-
import os.path as op
_base = op.join(op.dirname(op.abspath(__file__)), '..', '..')
import sys
sys.path.append(_base)
import pandas as pd

from eio import eio

@eio()
def sample2(hidden_layer_sizes: tuple,
            activation: str,
            validation_fraction:float) -> dict:
    dict_out = {
        'a': [a * 2 for a in hidden_layer_sizes],
        'b': '___' + activation + '___',
        'c': validation_fraction * 3
    }
    df_out = pd.DataFrame(
        {
            'a': [hidden_layer_sizes[0]],
            'b': ['___' + activation + '___'],
            'c': [validation_fraction * 3]
        }
    )
    return dict_out, df_out

if __name__ == '__main__':
    sample2(hidden_layer_sizes=[100, 200],
            activation='relu',
            validation_fraction=0.1)
```

## 出力ファイル名に記載されているパラメータ名短縮の規則
出力されるファイル名は実験関数名と実験パラメータ名とその値で構成されます。
`sample1.py`の場合は`sample1,a=relu,hls=100_200,vf=0.1.json`ですね。
このうち、`,`で区切られている要素を個別に意味を説明します。

- `sample1`: 実験関数名
- `a=relu`: `activation`引数に`relu`が設定されている
- `hls=100_200`: `hidden_layer_sizes`に`[100,200]`が設定されている
- `vf=0.1`: `validation_fraction`に`0.1`が設定されている

実験パラメータ名の短縮規則は、以下の通りです。
- `_`区切りでそれぞれの単語の頭文字が結合される
- 短縮後の名前に被りがある場合は、２個目以降の末尾に数値が追加される。
  - 例えば、`activation`と`alpha`というパラメータがあった場合、前者は`a`に、後者や`a1`となる。


## EIOデコレータの引数
- `out_dir`:
  - 出力先フォルダ
  - str型
  - デフォルトは`./`
- `header`
  - 出力ファイル名の頭につける文字列
  - str型
  - デフォルトは`None`. `None`の場合、デコレートされた実験関数名が自動で割り当てられる
- `param`
  - `_param`（実験パラメータを表したDict)を結果のJSONに入れるか否か
  - Boolean型
  - デフォルトはTrue
- `process_time`:
  - `_process_time`を結果のJSONに入れるか否か
  - Boolean型
  - デフォルトは`True`
- `trace_back`:
  - 実験関数内で例外発生時に、例外をそのまま上に上げるか否か。Falseの場合はキャッチして実験結果JSONにいれる
  - Boolean型
  - デフォルトは`False`
- `display`:
  - 実行完了時に表示をするか否か
  - Boolean型
  - デフォルトは`True`
- `error_display`
  - エラー発生時に表示をするか否か
  - Boolean型
  - デフォルトは`False`
- `sort_keys`:
  - 実験結果JSON内をキーでソートするか否か
  - Boolean型
  - デフォルトは`True`
- `ensure_ascii`
  - 実験結果のJSONを生成するときの引数. 日本語をエスケープするか否か
  - Boolean型
  - デフォルトは`False`
- `mkdir`: 出力先フォルダの作り方. `off`, `on`, `shallow`, `deep`のいずれかを指定
  - `off`: 出力先フォルダを作成しない
  - `on`: 出力先フォルダを自動作成する
  - `shallow`:出力先フォルダの更に下に、パラメータ名に応じたフォルダを作成
  - `deep`:出力先フォルダの更に下に、パラメータ名に応じたフォルダを作成.パラメータ毎に階層を１つ深くする
- `indent`:
  - 実験結果JSONのインデントに使う半角スペースの数
  - int型
  - デフォルトは`4`
- `default`:
  - 実験結果をJSONにエンコードする際の`json.dumps`メソッドの引数設定値.
  - 関数型
  - デフォルトはnumpy配列をlistに変換するオリジナルの関数(`supportnumpy`)
- `tail_param`:
  - 実験パラメータのうち、出力ファイルのパラメータの並びで末尾に持ってくるパラメータ
  - str型
  - デフォルトは`_seed`. これはSpartanで自動で生成される乱数シードのため

