# verytired.net

`../hitori_av` の作品フォルダ（`NNN_名前/`）から作品一覧を作る静的サイト。

- `python3 build.py` … 全部の分で `index.html` と `lab/` を作る。`music.tsv`（曲名<TAB>URL）から `music/index.html` も作る（YouTube はそのまま、Bandcamp は埋め込みコードの `src` の URL を書く）。`tools.tsv` から `tools/index.html` も作る（画像は `tools/<名前>.jpg`）
- `ga.py` … GA4 の1週間分を `data/ga/<年>-W<週>.json` に置く（週1作の素材。publish.sh が毎日呼び、未取得の週だけ取る）
- `publish.sh` … ビルドして main に push（`net.verytired.publish.plist` で毎日 0:05 に実行）
