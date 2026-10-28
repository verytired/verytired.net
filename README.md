# verytired.net

`../hitori_av` の日別フォルダから作品一覧を作る静的サイト。

- `python3 build.py` … 今日までの分で `index.html` と `lab/` を作る
- `publish.sh` … ビルドして main に push（`net.verytired.publish.plist` で毎日 0:05 に実行）
