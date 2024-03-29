# Search
実験結果が保存されたJSONファイルを集約して、CSV形式に変換するツールです。

## まず動かしてみる。
1. このREADME.mdがあるディレクトリに移動する
2. 以下のコマンドを実行する。
```
$ ./search sample/result/*.json > sample/sample_search.csv
```
3. `sample/sample_search.csv`に実行結果が保存されているので確認します。
```
$ cat sample/sample_search.csv
,_header,_seed,activation,hidden_layer_sizes,validation_fraction,|,goro,hoge,piyo,_process_time,_filename
0,sample,1310594.0,relu,"[100, 200]",0.1,|,___relu___,600.43511624812,0.9403189928133333,2.5510787963867188e-05,"sample,a=relu,hls=100_200,vf=0.1,_s=1310594.json"
1,sample,8464620.0,relu,"[100, 200]",0.1,|,___relu___,600.0944444683364,1.2068970555777847,2.3365020751953125e-05,"sample,a=relu,hls=100_200,vf=0.1,_s=8464620.json"
2,sample,6400996.0,relu,[300],0.1,|,___relu___,600.2177963090445,0.3982820513584382,2.288818359375e-05,"sample,a=relu,hls=300,vf=0.1,_s=6400996.json"
3,sample,9667937.0,relu,[300],0.1,|,___relu___,600.7429092878614,0.41764986261200676,2.193450927734375e-05,"sample,a=relu,hls=300,vf=0.1,_s=9667937.json"
4,sample,3246075.0,relu,"[500, 500, 500]",0.4,|,___relu___,3001.4014718764633,1.5745036227868974,2.1457672119140625e-05,"sample,a=relu,hls=500_500_500,vf=0.4,_s=3246075.json"
5,sample,7901026.0,relu,"[500, 500, 500]",0.4,|,___relu___,3001.2393623552925,1.2297033417783192,2.5987625122070312e-05,"sample,a=relu,hls=500_500_500,vf=0.4,_s=7901026.json"
6,sample,5168185.0,relu,"[500, 500, 500]",0.5,|,___relu___,3001.0257777747875,2.27902365301889,2.5033950805664062e-05,"sample,a=relu,hls=500_500_500,vf=0.5,_s=5168185.json"
7,sample,7587603.0,relu,"[500, 500, 500]",0.5,|,___relu___,3001.217828590123,2.3094741094577635,2.1219253540039062e-05,"sample,a=relu,hls=500_500_500,vf=0.5,_s=7587603.json"
8,sample,1881864.0,tanh,"[100, 200]",0.1,|,___tanh___,600.995475021502,0.9392883331993762,2.9802322387695312e-05,"sample,a=tanh,hls=100_200,vf=0.1,_s=1881864.json"
9,sample,2971965.0,tanh,"[100, 200]",0.1,|,___tanh___,601.4229930136728,0.5645295203575379,2.574920654296875e-05,"sample,a=tanh,hls=100_200,vf=0.1,_s=2971965.json"
10,sample,2715881.0,tanh,[300],0.1,|,___tanh___,600.4125244895451,1.1058198220772304,2.5272369384765625e-05,"sample,a=tanh,hls=300,vf=0.1,_s=2715881.json"
11,sample,8256549.0,tanh,[300],0.1,|,___tanh___,600.373664527264,0.30975114085611066,2.1696090698242188e-05,"sample,a=tanh,hls=300,vf=0.1,_s=8256549.json"
```

12件の実験結果がひとつのCSVファイルに集約されました。
各列の説明は以下の通りです。


実験結果は`sample/result/`ディレクトリに保存されています。
これらの実験結果は、本リポジトリの別ツールのSpartanとEIOを使うことで生成しています。
以下のコマンドで実験結果を追加することができます。

```
../spartan/spartan sample/input.yaml
```

入力となった実験結果の一例配下のとおりです。
```json
{
    "_header": "sample",
    "_param": {
        "_seed": 1310594,
        "activation": "relu",
        "hidden_layer_sizes": [
            100,
            200
        ],
        "validation_fraction": 0.1
    },
    "_process_time": 2.5510787963867188e-05,
    "giro": [
        300.9559435305069,
        600.0159616691503
    ],
    "goro": "___relu___",
    "hoge": 600.43511624812,
    "piyo": 0.9403189928133333
}
```
このうち、実験のパラメータに当たる部分は以下の2つです
- `_header`: 実験名
- `_param`: 実験パラメータの組み合わせ

実験結果は
- `giro`
- `goro`
- `hoge`
- `piyo`
- `_process_time`

です。これらのうち、アンダーバー`_`のついたものはEIOにより自動で組み込まれた値で、searchの処理では特別な扱いを受けています。
- `_header`: 出力の先頭列に来ます
- `_param`: この中のキーと値がパラメータ名とその値として、`_header`列の右の列にキーでソートされて組み込まれます
- `_process_time`: 実験結果の一番右の列として組み込まれます。


また、CSVの最右列に`_filename`という列があります。
これは、その実験結果JSONのファイル名を表しています。

## キャッシュ機能
ツールのオプションで`--cache <CSV Filename>`とすると、すでにあるCSVファイルに追加することができます。
このとき、実験結果JSONファイルのファイル名(`_filename`)がかぶるものは読み込まれません。

## コマンドのオプション
- `--display`: 処理中の表示をONにします
- `-o` or `--output`: 標準出力せずにファイルを保存する際のファイル名
- `--dir`: 引数でファイル名を渡さずにディレクトリ名で指定するためのオプション。対象としたディレクトリ内のjsonファイルを読み込むようになる。ファイル数が多すぎて引数にできない場合に用いる。
- `--param_key`: 実験結果JSONファイル内のパラメータのキー。デフォルトは`_param`
- `--filename_key`: 実験結果JSONファイル名を記載する列名。 デフォルトは`_filename`
- `--head_columns`: 列を並び替えCSVの左側に持ってくる列名を指定する。デフォルトは`_header`のみ。
- `--tail_columns`: 列を並び替えCSVの右側に持ってくる列名を指定する。デフォルトは`_process_time`と`_filename`のみ。
- `--separator`: 実験パラメータと実験結果を区切る列に入れる文字列. デフォルトは `|`
- `--cache`: キャッシュもとになるCSVのパス

# Stats
Searchで得たCSVに統計処理を行うツールです。
同じパラメータの組み合わせで実行された実験結果のサンプルから平均値・標準偏差の値等を算出してCSV形式で出力します。

## 動かしかた
1. このREADME.mdがあるディレクトリに移動する
2. 以下のコマンドを実行する。
```
$ ./search sample/result/*.json | ./stats > sample/sample_stats.csv
```
3. `sample/sample_stats.csv`に実行結果が保存されているので確認します。
```
$ cat sample/sample_stats.csv 
,_header,activation,hidden_layer_sizes,validation_fraction,_n,|,hoge(ave),hoge(std),hoge(min),hoge(max),piyo(ave),piyo(std),piyo(min),piyo(max),_process_time(ave),_process_time(std),_process_time(min),_process_time(max)
0,sample,relu,"[100, 200]",0.1,2,|,600.2647803582282,0.1703358898918168,600.0944444683364,600.43511624812,1.073608024195559,0.13328903138222575,0.9403189928133332,1.2068970555777847,2.4437904357910156e-05,1.072883605957033e-06,2.3365020751953125e-05,2.551078796386719e-05
1,sample,relu,[300],0.1,2,|,600.4803527984529,0.2625564894084391,600.2177963090445,600.7429092878614,0.40796595698522253,0.009683905626784312,0.3982820513584382,0.4176498626120068,2.2411346435546875e-05,4.76837158203125e-07,2.193450927734375e-05,2.288818359375e-05
2,sample,relu,"[500, 500, 500]",0.4,2,|,3001.320417115878,0.08105476058562999,3001.2393623552925,3001.401471876464,1.4021034822826084,0.1724001405042891,1.2297033417783192,1.5745036227868974,2.372264862060547e-05,2.264976501464842e-06,2.1457672119140625e-05,2.598762512207031e-05
3,sample,relu,"[500, 500, 500]",0.5,2,|,3001.1218031824556,0.0960254076678666,3001.0257777747875,3001.217828590123,2.294248881238327,0.015225228219436726,2.27902365301889,2.3094741094577635,2.3126602172851566e-05,1.9073486328125e-06,2.1219253540039066e-05,2.5033950805664066e-05
4,sample,tanh,"[100, 200]",0.1,2,|,601.2092340175873,0.2137589960853461,600.995475021502,601.4229930136727,0.7519089267784571,0.18737940642091916,0.5645295203575379,0.9392883331993762,2.777576446533203e-05,2.0265579223632812e-06,2.574920654296875e-05,2.9802322387695312e-05
5,sample,tanh,[300],0.1,2,|,600.3930945084046,0.01942998114054717,600.373664527264,600.4125244895451,0.7077854814666705,0.39803434061055987,0.30975114085611066,1.1058198220772304,2.3484230041503906e-05,1.7881393432617188e-06,2.1696090698242188e-05,2.5272369384765625e-05
```

Searchで集計した実験結果の統計値をとっています。
例えば、`hoge(ave)`, `hoge(std)`, `hoge(min)`, `hoge(max)`は、順にhoge値の平均、標準偏差、最小値、最大値を表しています。
`_n`列は、サンプリング数を表しています。

## オプション
- `-i` or `--input`: 入力となるCSVファイルのパス. 省略した場合は標準入力からうけとる
- `-o` or `--output`: 標準出力せずにファイルを保存する際のファイル名
- `--separator`: 実験パラメータと実験結果を区切る列に入れる文字列. デフォルトは `|`
- `--funcs`: 計算する統計値。以下の中から複数選択する。デフォルトは`ave std min max`
  - `ave`: 平均
  - `std`: 標準偏差
  - `min`: 最小値
  - `max`: 最大値
- `ignore`: 実験パラメータとみなさない列を指定する。デフォルトは`_seed, _filename`
- `count_key`: パラメータの組み合わせ毎のサンプリング数を保存するカラム名を指定する。デフォルトは`_n`
- `n_samples`: サンプリング数の最大値を設定する. デフォルトではすべてのサンプルから統計値を得る。


# Scatter(試作版)
※この機能はmasterブランチに入れるべきか悩みましたが、一度作った手前消すのがもったいなかったのでいれています。使い勝手もあまり良くないしそのうち消すかもしれない。必要になったときにまた改良します。

SearchでまとめられたCSVファイルの、全評価軸(セパレーター`|`の右側)を総当りで散布図を作成するツールです。

## 最低限の動かし方(たくさんPNGファイルがカレントディレクトリに出来るので注意)
```
$ cat sample/sample_search.csv | ./scatter --figure_keys activation --input_keys hidden_layer_sizes validation_fraction
```
これで、カレントディレクトリに、`figure_keys`で指定したパラメータと評価値2つの散布図が複数個できている。各画像の凡例は、`hidden_layer_sizes`と`validation_fraction`の総当りとなっている。

## 必須のパラメータ
- `--figure_keys`: 画像にまとめるパラメータ複数個
- `--input_keys`: 凡例で組み合わせるパラメータ複数個

## オプション
- `-i` or `--input`: 入力となるCSVファイルのパス. 省略した場合は標準入力からうけとる
- `-o` or `--output`: 散布図を保存するフォルダへのパス。ファイル名は自動で付与される。デフォルトではカレントディレクトリ(`./`)
- `--separator`: 実験パラメータと実験結果を区切る列に入れる文字列. デフォルトは `|`
- `-d` または `--display` とコマンドにつけると、実行時に保存先を表示する。
- `--dpi`: png画像のdpi値(インチあたりのピクセル数)を指定する。基本的に大きな数を設定すると画像も大きくなる。デフォルトでは、`None` が入り、matplotlibにパラメータ設定が委ねられる。
