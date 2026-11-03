# verytired.net

`../hitori_av` の作品フォルダ（`NNN_名前/`）から作品一覧を作る静的サイト。

- `python3 build.py` … 全部の分で `index.html`（最新作だけ）と `audiovisual/index.html`（全作品の一覧）と `lab/` を作る。`music.tsv`（曲名<TAB>URL）から `music/index.html` も作る（YouTube はそのまま、Bandcamp は埋め込みコードの `src` の URL を書く）。`tools.tsv` から `tools/index.html` も作る（画像は `tools/<名前>.jpg`）
- `ga.py` … GA4 の1週間分を `data/ga/<年>-W<週>.json` に置く（週1作の素材。publish.sh が呼び、未取得の週だけ取る）
- `check_player.py` … `uv run check_player.py [名前…]`。lab/ の全作品をブラウザ（Playwright）で開き、再生を押す前に見えない・動かない・鳴らないこと、押すと動き、一時停止で止まることを確かめる。publish.sh がビルドのあとに回し、NG があれば push しない
- `publish.sh` … ビルドして main に push（指示したときだけ手で実行する。`net.verytired.publish.plist` は毎日 0:05 に回していたときのもので、今は登録していない）
