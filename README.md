# verytired.net

`../hitori_av` の日別フォルダから作品一覧を作る静的サイト。

- `python3 build.py` … 全部の分で `index.html` と `lab/` を作る
- `ga.py` … GA4 の1週間分を `data/ga/<年>-W<週>.json` に置く（週1作の素材。publish.sh が毎日呼び、未取得の週だけ取る）
- `publish.sh` … ビルドして main に push（`net.verytired.publish.plist` で毎日 0:05 に実行）
