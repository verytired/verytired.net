# verytired.net

Static site for [verytired.net](https://verytired.net). It is built from the audiovisual pieces in `../hitori_av` (one folder per piece, `NNN_name/`).

## Usage

```sh
python3 build.py [../hitori_av]   # build the site
uv run check_player.py [name…]    # check every piece in lab/ in a browser
./publish.sh                      # build, check, push to main (run by hand only)
```

## Output

| Path | Contents |
| --- | --- |
| `index.html` | Top page: the latest piece only |
| `audiovisual/index.html` | List of all pieces |
| `lab/<name>/` | Each piece: `piece.html` (copied as is), `index.html` (wrapped in `player.html`), media in `src/`, light `.sp.mp4` for phones, `loop.mp4` preview |
| `music/index.html` | Built from `music.tsv` |
| `tools/index.html` | Built from `tools.tsv` |

Pages use `template.html`; the piece player is `player.html`.

## Input files

| File | Format |
| --- | --- |
| `en.tsv` | `folder<TAB>English description` |
| `youtube.tsv` | `folder<TAB>YouTube URL` — adds a YouTube link to that piece's player |
| `music.tsv` | `title<TAB>URL` — YouTube URL, or the `src` of a Bandcamp embed |
| `tools.tsv` | `name<TAB>description<TAB>play URL<TAB>GitHub URL<TAB>video URL (optional)`; image at `tools/<name>.jpg` |
| `hold.txt` | Folder names to keep off the site for now |

## Scripts

- `check_player.py` — opens each piece with Playwright and checks that nothing is shown, moves or plays before Play is pressed, that it runs after Play, and that Pause stops it. `publish.sh` runs it after the build and does not push if anything fails.
- `ga.py` — saves one week of GA4 data to `data/ga/<year>-W<week>.json`. Called by `publish.sh`; fetches only missing weeks.
- `net.verytired.publish.plist` — launchd job from when `publish.sh` ran daily at 0:05. Not loaded now.
