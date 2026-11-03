# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""lab/ の作品が、再生を押す前に見えたり動いたり鳴ったりしないかを確かめる（python3 build.py のあとに）。

  uv run check_player.py              # 全作品
  uv run check_player.py fold coil    # 名前を指定

ブラウザは自動再生を許して開く（押す前に音を作る作品があれば、そのまま鳴って見つかる）。
押す前：作品が隠れている・描画ループ（rAF）が進まない・AudioContext が鳴っていない・動画が流れていない。
押した後：見えて、rAF が進み、音と動画が流れる。一時停止：音・動画・rAF が止まる。
"""
import functools, http.server, sys, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent

# どのフレームでも作品より先に走る：rAF が実際に呼ばれた回数、作られた AudioContext、play() された動画を数える
SPY = r"""(() => {
const orig = window.requestAnimationFrame.bind(window);
window.__rafRuns = 0;
window.__rafWrap = window.requestAnimationFrame = cb => orig(t => { window.__rafRuns++; cb(t); });
window.__acs = [];
const AC = window.AudioContext;
if (AC) window.AudioContext = class extends AC { constructor(...a) { super(...a); window.__acs.push(this); } };
window.__vids = new Set();
const play = HTMLMediaElement.prototype.play;
HTMLMediaElement.prototype.play = function () { window.__vids.add(this); return play.call(this); };
})();"""

STATE = r"""() => {
const s = document.getElementById('stage'), W = s.contentWindow, b = document.getElementById('play');
if (!W || !W.piece || W.requestAnimationFrame === W.__rafWrap) return null;   // プレイヤーがまだ作品をつかんでいない
const vids = [...new Set([...W.__vids, ...W.document.querySelectorAll('video'), ...(W.piece.media?.() || [])])];
return { raf: W.__rafRuns, visible: getComputedStyle(s).visibility !== 'hidden',
  audio: W.__acs.filter(a => a.state === 'running').length, videos: vids.filter(v => !v.paused).length, media: (W.piece.media?.() || []).length,
  canPlay: !b.disabled && !b.hidden, files: !!W.document.getElementById('files'), output: !!W.piece.output?.() };
}"""


def check(page, url, name):
    errs = []
    page.goto(url)
    s = None
    for _ in range(400):   # プレイヤーが作品をつかむまで
        s = page.evaluate(STATE)
        if s: break
        time.sleep(.1)
    if not s: return ['プレイヤーが作品をつかめない（window.piece がない？）']
    time.sleep(.2); raf0 = page.evaluate(STATE)['raf']   # つかむ前に予約済みだった1コマは走ってよい（作品は隠れている）
    # 押す前：Play が押せるようになってから 2 秒後までずっと見張る（coil は前計算で 20 秒ほど待つ）
    until = None
    for _ in range(1200):
        s = page.evaluate(STATE)
        if s['visible']: errs.append('押す前に見えている')
        if s['raf'] != raf0: errs.append(f"押す前に描画ループが進んでいる（{s['raf'] - raf0} コマ）")
        if s['audio']: errs.append('押す前に音が鳴っている')
        if s['videos']: errs.append('押す前に動画が流れている')
        if errs: return sorted(set(errs))
        if until is None and (s['canPlay'] or s['files']): until = time.time() + 2
        if until and time.time() > until: break
        time.sleep(.1)
    else: return ['Play が押せるようにならない']
    if s['files']: return []   # strobe は写真を選ぶまで始まらないので、押す前だけ見る

    page.click('#play')   # 本物のクリック
    for _ in range(600):
        s = page.evaluate(STATE)
        if s['visible']: break
        time.sleep(.1)
    else: return ['押しても見えない']
    raf1 = s['raf']; time.sleep(1.5); s = page.evaluate(STATE)
    if s['raf'] == raf1: errs.append('押しても描画ループが進まない')
    if s['output'] and not s['audio']: errs.append('押しても音が鳴らない')
    if s['media'] and not s['videos']: errs.append('押しても動画が流れない')

    page.click('#play')   # 一時停止
    time.sleep(.5); s = page.evaluate(STATE); raf2 = s['raf']; time.sleep(1); s = page.evaluate(STATE)
    if s['audio']: errs.append('一時停止しても音が止まらない')
    if s['videos']: errs.append('一時停止しても動画が止まらない')
    if s['raf'] != raf2: errs.append('一時停止しても描画ループが止まらない')
    return errs


def main():
    names = sys.argv[1:] or sorted(p.parent.name for p in (ROOT / 'lab').glob('*/piece.html'))
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=ROOT))
    srv.handle_error = lambda *a: None   # ページを移るときに切れた動画の転送は無視する
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    bad = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', args=['--autoplay-policy=no-user-gesture-required'])
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.add_init_script(SPY)
        for n in names:
            errs = check(page, f'http://127.0.0.1:{srv.server_port}/lab/{n}/', n)
            bad += bool(errs)
            print(f"{'NG' if errs else 'ok'}  {n}" + ''.join(f'\n      - {e}' for e in errs), flush=True)
        browser.close()
    print(f'{len(names) - bad}/{len(names)} ok')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
