# Spartan
Spartanは、実験を並列実行するためのツールです。
主にクラスタマシンで使用することを想定していますが、コンピュータ1台で使用することもできます。

以降では、コンピュータ1台での使い方、クラスタマシンでの使い方の順に説明します。

## コンピュータ1台での使い方
1. このREADME.mdがあるディレクトリに移動する
2. 以下のコマンドを実行する。
```
$ ./spartan sample/input.yaml
```
もしくは
```
$ python spartan sample/input.yaml
```

以上の手順を実行すると、以下のような表示時がされるかと思います。
```
hoge-999999.9998389754 (a=0.1, b=hoge, _seed=3705792)
goro-2000000.000713748 (a=0.1, b=goro, _seed=2599545)
hoge-75000000.0 (a=0.5, b=hoge, _seed=5658655)
goro-75000000.0 (a=0.5, b=goro, _seed=1910151)
hoge-127999999.67022167 (a=0.8, b=hoge, _seed=4419740)
hoge-999999.9998389754 (a=0.1, b=hoge, _seed=2216445)
goro-127999999.67022167 (a=0.8, b=goro, _seed=7591866)
goro-2000000.000713748 (a=0.1, b=goro, _seed=8931611)
piyo-31999999.95432012 (a=0.4, b=piyo, _seed=3524648)
piyo-27000000.04254542 (a=0.3, b=piyo, _seed=7386266)
hoge-50000000.0 (a=0.5, b=hoge, _seed=6772151)
hoge-63999999.90864024 (a=0.8, b=hoge, _seed=8641143)
piyo-8999999.997841937 (a=0.3, b=piyo, _seed=8328011)
goro-75000000.0 (a=0.5, b=goro, _seed=1837357)
piyo-31999999.95432012 (a=0.4, b=piyo, _seed=5196403)
goro-127999999.67022167 (a=0.8, b=goro, _seed=2397773)
```

完全に同じものにはならないと思います。似たようなモノが表示されればOKです。

何が実行されたかというと、`sample/command.py`が様々なパラメータで並列実行されました。
`sample/command.py`の中身は以下のとおりです。
```python
# -*- coding: utf-8 -*-
import sys, json, random
from argparse import ArgumentParser

def exe(a: float, b: str, _seed: int) -> str:
    random.seed(_seed)
    s = 0
    c = random.randint(1, 3)
    for _ in range(int(a * (c * 10**8))):
        s += a
    out = '{}-{} (a={}, b={}, _seed={})'.format(b, s, a, b, _seed)
    return out

if __name__ == '__main__':
    parser = ArgumentParser(description='')
    parser.add_argument('json', nargs='*')
    parser.add_argument('--a', type=float, default=0.1)
    parser.add_argument('--b', type=str, default='hoge')
    parser.add_argument('--_seed', type=int, default=3939)
    args = parser.parse_args()
    if len(args.json) > 0:
        param = json.loads(args.json[0])
    else:
        param = args.__dict__
        del param['json']
    print(exe(**param))
```

実験で実行したい処理（例えばシミュレーション）が書かれているものだと見立ててください。
本体は`exe`メソッドで、引数は`a`,`b`,`_seed`です。
`a`, `b`は実験用のパラメータで、`_seed`は疑似乱数生成のための乱数シードです。

パラメータは、コマンドの引数にargparser形式で受け渡されます。
以下のように内部では実行されています。
```
python sample/command.py --a 0.1 --b hoge --_seed 5702596
```
Spartanは、このように自動で生成されたを引数に受け渡す形で、コマンドを並列で実行していきます。


このようなコマンドが、以下の2つのパラメータの総当りが２回ずつ実行されました。

- a: [0.1, 0.5, 0.8], b:["hoge", "goro"]
- a: [0.3, 0.4], b:["piyo"]

すべてのパラメータの総当りを列挙すると
- a=0.1, b="hoge"
- a=0.1, b="goro"
- a=0.5, b="hoge"
- a=0.5, b="goro"
- a=0.8, b="hoge"
- a=0.8, b="goro"

と

- a=0.3, b="piyo"
- a=0.4, b="piyo"

となります。これらが２回ずつ実行、合計16回実行されました。上述した実行結果も16行あるはずです。

このように実行するのを設定しているのは`sample/input.yaml`です。
内容は以下の通りです。

```yaml
command: python sample/command.py
param_grid:
  - {a: [0.1, 0.5, 0.8], b: [hoge, goro]}
  - {a: [0.3, 0.4], b: [piyo]}
hosts:
  - {hostname: localhost, n_jobs: 4}
option:
  n_seeds: 2
#  mode: json
#  maxsize: 7
#  interval: 1
#  config_filepath: .spartan_config.yaml
#  display: true
```

Spartanの実行時に引数に設定したファイルです。
パラメータの組み合わせや並列実行数やその他オプションを、yaml形式で設定します。
キーが設定項目と対応します。

必須の設定項目は以下の3つです。
- `command`: Spartanで並列実行するコマンド。
- `param_grid`: パラメータの総当りの組み合わせ
- `hosts`: コマンドを実行するホストとその並列数

`hosts`の詳細は後のクラスタマシンでの使い方で説明します。
ここでは、`{hostname: localhost, n_jobs: 4}`がローカルホストで並列実行数4と設定されているということがわかればOKです。

続いてオプションについてです。
オプションはいろいろな項目を設定できますが、ここでは`n_seeds`についてだけ解説します。
`n_seeds`はパラメータ総当りでの実行回数です。
それぞれ異なる乱数シードが自動生成されます。

## クラスタマシンでの使い方
クラスタマシンで計算を分散させるためには、以下の前提を満たす必要があります。

- Spartanを実行するホストから計算ノードにパスワードなしでSSH接続ができる
- すべての計算ノードでコマンドを実行できる

1つ目の前提は、例えば計算ノードのホスト名を`cassia`だとすると、以下のコマンドだけで接続できることです。
```
$ ssh cassia
```
また、接続確認方法として
```
$ ssh cassia ls
```
としてパスワードを聞かれることなく接続先でlsコマンドの結果(おそらくホームディレクトリのファイルやディレクトリ一覧)が表示されればOKです。

2つ目の前提は、ホストと計算ノードですべてライブラリ等の実験環境を同一にしておくということです。
例えば、ホストで
```
$ python command.py
```
と実行できるとします。他の計算ノードでも同じコマンドを実行できるようにしておきます。
つまり、ホストから以下のように実行できるようにする必要があります。
```
$ ssh cassia "python command.py"
```

続いて設定ファイルの書き方を説明します。
ホストから`cassia-1`と`cassia-2`という２つの計算ノードにSSH接続できるものとします。
そして、ローカルホスト、とこれら2つの計算ノードで分散しながら並列実行する例を示します。
設定ファイルは以下のようになります。
```yaml
command: python sample/command.py
param_grid:
  - {a: [0.1, 0.5, 0.8], b: [hoge, goro]}
  - {a: [0.3, 0.4], b: [piyo]}
hosts:
  - {hostname: localhost, n_jobs: 2}
  - {hostname: cassia-1, n_jobs: 4}
  - {hostname: cassia-2, n_jobs: 8}
option:
  n_seeds: 2
#  maxsize: 7
#  interval: 1
#  config_filepath: .spartan_config.yaml
#  display: true
```
このファイルは`sample/cluster_input.yaml`としてリポジトリ内に保存されています。
このファイルは、ローカルで2並列、`cassia-1`で4並列、`cassia-2`で8並列で実行されます。
また、`hostname`への設定で`localhost`だけは特別で、SSHを使わずにローカルで並列実行数ということになります。

実行結果は、コンピュータ1台での使い方、の例と同じようなものが表示されるはずです。

## その他機能
### GPUの利用
実験にGPUを使いたい場合があります。コンピュータ1台にGPUが2台以上ある場合、それらの割り振りも管理しながら実行する場合の機能も搭載しています。
例えば、以下のようにhosts内のホスト毎に`device`をキーとして、GPUの識別名のリストを値として設定します。
```yaml
command: python sample/command_cuda.py
param_grid:
  - {a: [0.1, 0.5, 0.8], b: [hoge, goro]}
  - {a: [0.3, 0.4], b: [piyo]}
hosts:
  - {hostname: localhost, n_jobs: 5, device: [cuda:0, cuda:1]}
option:
  n_seeds: 5
```
ここでは、CUDAに対応したGPUが2台搭載されたコンピュータをlocalhostとして実行する場合を想定しています。
2代のGPUそれぞれの識別子を`cuda:0`と`cuda:1`とします。
このように実行することで、以下の5つのコマンドが最初に同時実行されます。

- `python sample/command_cuda.py --a 0.1 --b hoge --_seed 3705792 --_device cuda:0`
- `python sample/command_cuda.py --a 0.1 --b goro --_seed 2599545 --_device cuda:1`
- `python sample/command_cuda.py --a 0.5 --b hoge --_seed 5658655 --_device cuda:0`
- `python sample/command_cuda.py --a 0.5 --b goro --_seed 1910151 --_device cuda:1`
- `python sample/command_cuda.py --a 0.8 --b hoge --_seed 1910151 --_device cuda:1`

`cuda:0`と`cuda:1`が割り振られます。この時、1台のGPUに割り振りが集中せず、分散されるように割り振られます。例えば、`cuda:0`が2つのジョブに割り振られている状態で、`cuda:0`が割り振られることはなく、`cuda:1`が割り振られます。`n_jobs`の数がGPUの識別子の数で割り切れない場合、リストの先頭にあるものに優先的に割り当てられます。


### 実行中の設定変更
Spartanは実行中に、並列実行数を変更することが可能です。
そのためには、設定ファイルの`option`に`config_filepath`を設定してください。
例えば以下のとおりです。
```yaml
command: python sample/command.py
param_grid:
  - {a: [0.1, 0.5, 0.8], b: [hoge, goro]}
  - {a: [0.3, 0.4], b: [piyo]}
hosts:
  - {hostname: localhost, n_jobs: 2}
  - {hostname: cassia-1, n_jobs: 4}
  - {hostname: cassia-2, n_jobs: 8}
option:
  n_seeds: 2
  config_filepath: .spartan_config.yaml
```
末尾で`config_filepath`に`.spartan_config.yaml`というファイル名が設定されていますね。

Spartanを実行すると、最初に`.spartan_config.yaml`というファイルが保存されます。
その中には`hosts`の情報が記載されています。
Spartan実行中にこのファイルの中身を書き換えることで、Spartanで計算ノード毎の並列実行数を制御できます。

例えば、上記の設定ファイルを実行すると、`.spartan_config.yaml`は以下のnような内容で保存されます。

```yaml
hosts:
- hostname: localhost
  interval: 1
  n_jobs: 2
- hostname: cassia-1
  interval: 1
  n_jobs: 4
- hostname: cassia-2
  interval: 1
  n_jobs: 8
```

これを、`cassia-1`での並列実行数を4から8に増やしたい時は、以下のように書き直して上書き保存します。
```yaml
hosts:
- hostname: localhost
  interval: 1
  n_jobs: 2
- hostname: cassia-1
  interval: 1
  n_jobs: 8
- hostname: cassia-2
  interval: 1
  n_jobs: 8
```
こうすると、即座に並列実行数が増えます。
また、ここからすべての計算ノードですべての並列実行数を1にしたいときは以下のように書きます。
```yaml
hosts:
- hostname: localhost
  interval: 1
  n_jobs: 1
- hostname: cassia-1
  interval: 1
  n_jobs: 1
- hostname: cassia-2
  interval: 1
  n_jobs: 1
```

並列実行数(`n_jobs`)を減らした場合は、即座にコマンドは停止しません。
現在実行中のコマンドが実行完了するのを待つことで並列実行数を段階的に減らしていきます。


## オプション一覧
### よく使うオプション
- `n_seeds`: 乱数シードの個数。パラメータの組み合わせ毎の実行数
- `config_filepath`: Spartan実行中に、ホスト毎の並列実行数を変更するためのファイルのパス

### あまり設定しないと思われるオプション
- `mode`: `argparse`か`json`のどちらかを設定します。デフォルトは`argparse`です。`json`と設定すると、コマンド実行時の引数をjson形式で生成します。例えば以下のとおりです。
  - `python sample/command.py "{\"a\": 0.1, \"b\": \"hoge\", \"_seed\": 5702596}"`
- `maxsize`: 内部でパラメータの組み合わせを保持する個数。あまりにもパラメータの組み合わせ数が多いときに100,1000などの数を設定してください。デフォルトだと、すべてのパラメータの組み合わせをメモリ上に保持します。
- `interval`: Spartan実行時、各種処理の間隔。単位は秒。デフォルトは1秒
- `display`: Spartanの実行中の状態を表示するかどうかを設定する。デフォルトは`true`で、表示される。


## 【開発者向け】注意
### テストについて
テストファイルは実行環境に依存します。作者の環境にあわせて作成されており、実行してもテストは通らないと思います。
サンプルは動くと思います。
