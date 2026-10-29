#!/usr/bin/env python3
"""hitori_av の日別フォルダから lab/ と index.html を作る。

使い方: python3 build.py [../hitori_av]
- lab/<名前>/piece.html  … 作品の HTML をそのままコピー（自己完結しているので書き換えない）
- lab/<名前>/index.html  … player.html で piece.html を包む（英語の操作バー）
- lab/<名前>/loop.mp4     … 1:1 版の mp4 から作る無音・480px・8秒のループ（元の mp4 はサイトに入れない）
- index.html                  … template.html の {{ITEMS}} を埋める
"""
import html, re, shutil, subprocess, sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "../hitori_av").resolve()
OUT = Path(__file__).parent
LAB = OUT / "lab"
# 説明は英語（タブ区切り: フォルダ名\t英文）。書き忘れた日は README の日本語を出す
EN = dict(l.split("\t", 1) for l in (OUT / "en.tsv").read_text().splitlines() if "\t" in l) if (OUT / "en.tsv").exists() else {}


def first_sentence(readme):
    for line in readme.read_text().splitlines()[1:]:
        if line.strip():
            line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)  # リンクは文字だけ残す
            return line.split("。")[0] + "。"
    return ""


def build_item(d):
    name = d.name.split("_", 1)[1]
    piece, mp4 = d / f"{name}.html", d / f"{name}.mp4"
    dst = LAB / name  # URL に日付は出さない
    dst.mkdir(parents=True, exist_ok=True)
    if piece.exists():
        shutil.copy(piece, dst / "piece.html")
        for src in re.findall(r'src="([^"/]+\.mp4)"', piece.read_text(errors="ignore")):
            if (d / src).exists():
                shutil.copy(d / src, dst / src)  # 作品が素材として読む動画（slowdive の dive.mp4 など）はそのまま置く
    loop = dst / "loop.mp4"
    if mp4.exists() and (not loop.exists() or loop.stat().st_mtime < mp4.stat().st_mtime):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", mp4, "-t", "8", "-an", "-vf", "scale=480:-2",
                        "-c:v", "libx264", "-crf", "32", "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", loop], check=True)
    return {
        "name": name,
        "desc": first_sentence(d / "README.md") if (d / "README.md").exists() else "",
        "en": EN.get(d.name, "").strip(),
        "live": piece.exists(),
    }


def player(i, n):
    page = (OUT / "player.html").read_text()
    for k, v in {"NUM": f"{n:03d}", "NAME": i["name"], "DESC": i["en"] or i["desc"]}.items():
        page = page.replace("{{%s}}" % k, html.escape(v))
    (LAB / i["name"] / "index.html").write_text(page)


def tile(i, n):
    href = f"lab/{i['name']}/" if i["live"] else f"lab/{i['name']}/loop.mp4"
    return (f'<a class="tile" href="{href}">'
            f'<video src="lab/{i["name"]}/loop.mp4" muted loop playsinline preload="none"></video>'
            f'<span class="cap"><b>#{n:03d}</b> <i>{html.escape(i["name"])}</i>'
            f'<em>{html.escape(i["en"] or i["desc"])}</em></span></a>')


def main():
    dirs = sorted(d for d in SRC.iterdir() if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}_", d.name))  # 並び順にだけ日付を使う
    for old in LAB.glob("*") if LAB.exists() else []:
        if old.name not in {d.name.split("_", 1)[1] for d in dirs}:
            shutil.rmtree(old)  # 名前を変えた・フォルダを消した場合の残骸
    items = [build_item(d) for d in dirs]
    numbered = list(enumerate(items, 1))[::-1]  # 新しい順、番号は古い順に振る
    for n, i in numbered:
        if i["live"]:
            player(i, n)
    page = (OUT / "template.html").read_text()
    page = page.replace("{{ITEMS}}", "\n".join(tile(i, n) for n, i in numbered))
    page = page.replace("{{COUNT}}", str(len(items)))
    (OUT / "index.html").write_text(page)
    print(f"{len(items)} items -> index.html")


if __name__ == "__main__":
    main()
