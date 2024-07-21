# jymatplot
jymatplotは、グラフ描画Pythonライブラリの matplotlib のラッパーです。グラフの情報を、指定の様式のJSONかYAMLとして受け取り、画像として保存する機能を有します。matplotlibで描画するときは、描画用の Pythonスクリプトを記述する必要がありますが、JSONかYAMLで記述することが可能になります。別の言い方をすれば、グラフ内のデータと処理を分離することが可能となります。

## まず動かしてみる
1. 本リポジトリの`examples`内にある`jymatplot_input_1.yaml`を任意の場所に保存する。
2. 1.で保存したファイルのあるフォルダに移動する。
3. 以下のコマンドを実行する。
```
cat jymatplot_input_1.yaml | sekit-jymatplot --output jymatplot_output_1.png
```
3. カレントディレクトリに`jymatplot_output_1.png`というグラフ画像ファイルが保存されているので、確認します。
![sample1](https://raw.githubusercontent.com/HidetoshiKawaguchi/sekit/main/examples/jymatplot_output_1.png)

## 入力の形式
3.のコマンドは、`jymatplot_input_1.yaml`というグラフ描画の情報を入力として、`jymatplot_output_1.png` に保存をしています。`jymatplot_input_1.yaml`の中身は以下の通りになっています。
```yaml
__init__:
  title: The Graph
  xlabel: XXX
  ylabel: YYY
  xlim: [0, 6]
  ylim: [0, 6]
  aspect: equal
plots:
  - {x: [1, 2, 3], y: [1, 3, 5], label: hoge, method: scatter}
  - {x: [0.5, 2.0, 4.0], y: [0.5, 0.4, 0.35], label: goro, method: scatter}
  - {x: [2, 3, 4], y: [1, 2, 5], label: piyo, method: plot, linewidth: 10.0}

grid:
  color: "#DDDDDD"
set_axisbelow: True
legend:
  bbox_to_anchor: [1.05, 1.0]
  loc: "upper left"
```
キーは主に以下の３種類に分類できます。
- `__init__`: 図の初期化パラメータを指定します。Figureクラスの`add_subplot`メソッドでAxesインスタンスを設定する際に反映されます。
- `plots`: 点や線の描画について指定します。詳細は後述します。
- それ以外: Axesインスタンスのメソッド名をキーとして、値はパラメータとなります。オブジェクト・リスト・数値・文字列と何でも指定出来ます。

各キーの説明は以下の通りです。基本的には、`plots`以外はmatplotlibのAxesクラスの設定項目と同じです。`plots` 以外は省略することが可能です。
- `__init__`:
  - `title`: グラフ上部に設定してあるグラフの題名です。
  - `xlabel`: X軸の名前
  - `ylabel`: Y軸の名前
  - `xlim`: X軸の最小値と最大値を指定している。(`[最小値, 最大値]`)
  - `ylim`: Y軸の最小値と最大値を指定している。(`[最小値, 最大値]`)
  - `aspect`: グラフのアスペクト比を指定している。サンプルでは`equal`として、縦と横の比率が同じに設定してある。
- `plots`: (詳細は後述)
- `grid`: グリッド線に関する情報を指定している。
  - `color`: サンプルでは、グリッド線の色をRGB値で指定している。
- `set_axisbelow`: グリッド線を背景側に持っていくかどうか。True か Falseで指定。
- `legend`: 凡例を表示することに関する情報を指定している。
  - bbox_to_anchor: 凡例の位置を示します。図全体の左下を(0,0)、右上を(1,1)とした時の相対値で指定します。
  - loc: 凡例の基準位置を指定します。`upper left`の場合は、凡例の枠線の左上の点が基準点となります。

### 点や線の描画(Plots)
点や線の情報は、`Plots`をキーとして、リスト形式で指定します。リストの一要素が、凡例一つに対応します。上述した、`jymatplot_input_1.yaml`から抜き出した以下の部分です。
```yaml
plots:
  - {x: [1, 2, 3], y: [1, 3, 5], label: hoge, method: scatter}
  - {x: [0.5, 2.0, 4.0], y: [0.5, 0.4, 0.35], label: goro, method: scatter}
  - {x: [2, 3, 4], y: [1, 2, 5], label: piyo, method: plot, linewidth: 10.0}
```
各要素は、キー・バリュー形式で指定します。
サンプルは、`x`と`y`は、点のX値とY値を指定しています。リストの位置は対応しています。そのため、`x`と`y`のリストの長さは同じにする必要があります。

`label`は、凡例名を指定しています。

`method`は、matplotlibで対応している描画方法(点なのか、線なのか等)を指定します。matplotlibにそのまま設定するため、サンプルにある`scatter`や`plot`以外にも設定はできます。`linewidth`では線の太さを指定しています。

基本的には、matplotlib にそのまま設定値を流しているだけなので、作者が知らない描画方法でも使えるとは思います。

## JSONを入力とする場合
上述したサンプルでは、YAML形式のファイルを入力としましたが、JSONでも実行可能です。例えば、`jymatplot_input_1.yaml`をJSON形式で記述したものは以下の通りとなります。
```json
{
    "__init__": {
        "title": "The Graph",
        "xlabel": "XXX",
        "ylabel": "YYY",
        "xlim": [0, 6],
        "ylim": [0, 6],
        "aspect": "equal"
    },
    "plots": [
        {
            "x": [1, 2, 3],
            "y": [1, 3, 5],
            "label": "hoge",
            "method": "scatter"
        },
        {
            "x": [0.5, 2, 4],
            "y": [0.5, 0.4, 0.35],
            "label": "goro",
            "method": "scatter"
        },
        {
            "x": [2, 3, 4],
            "y": [1, 2, 5],
            "label": "piyo",
            "method": "plot",
            "linewidth": 10
        }
    ],
    "grid": {
        "color": "#DDDDDD"
    },
    "set_axisbelow": true,
    "legend": {
        "bbox_to_anchor": [1.05, 1],
        "loc": "upper left"
    }
}
```

## オプション
- `-i` or `--input`: 入力となるYAMLかJSONファイルのパス。省略した場合は標準入力からYAML形式もしくはJSON形式のテキストを受け取る。上述したサンプルでは、指定していない。
- `-o` or `--output`: 画像の保存先。設定しなかった場合は、カレントディレクトリに自動で名前つけされて保存される。その場合、現在時刻を基に、`Plot<年>-<月>-<日>-<時>-<分>-<秒>-<ミリ秒>.png`という形式で命名される。例えば、2021年8月15日16時4分32秒に保存した場合は、`Plot2021-08-15-16-04-32-592742.png`というようになる。
- `--dpi`: png画像のdpi値(インチあたりのピクセル数)を指定する。基本的に大きな数を設定すると画像も大きくなる。デフォルトでは、`None` が入り、matplotlibにパラメータ設定が委ねられる。 ~作者はよくわからない~
- `-d` または `--display` とコマンドにつけると、実行時に保存先を表示する。

すべてのオプションを使った場合の、動作例は以下の通りです。
```
./jymatplot --display --input examples/jymatplot_input_1.yaml --output ./full_options.png
saved a plot file, ./full_options.png
```

# 注意
- 作者自身がmatplotlibの把握しきれていないので、シンプルな機能しか実装されていません。込み入った画像描画はおそらく出来ないことにご注意ください。
- ある程度、matplotlib の使い方に慣れている向けです。
- アップデートは、**後方互換は考慮せずに**不定期に実施されます。(masterのドキュメントは更新します)
