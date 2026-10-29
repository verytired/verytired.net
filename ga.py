#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = ["google-auth", "requests"]
# ///
"""GA4 から1週間（月〜日）の数字を取って data/ga/<年>-W<週>.json に置く。

使い方: ./ga.py [2026-W43]
- 週を省くと、日曜から2日以上たった直近の週（GA の集計が固まるのを待つ）
- もうファイルがある週は取り直さない（publish.sh から毎日呼んでも1週1回だけ取る）
- 鍵: サービスアカウントの JSON（GA_KEY、既定 ~/.config/verytired/ga-key.json）
"""
import datetime as dt, json, os, sys
from pathlib import Path
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

PROPERTY = "561091078"
KEY = Path(os.environ.get("GA_KEY", "~/.config/verytired/ga-key.json")).expanduser()
OUT = Path(__file__).parent / "data" / "ga"

# 名前: (ディメンション, 指標)。作品側はこの名前で読む
REPORTS = {
    "total": ([], ["activeUsers", "screenPageViews", "sessions", "eventCount", "userEngagementDuration"]),
    "days": (["date"], ["activeUsers", "screenPageViews", "sessions"]),
    "hours": (["dayOfWeek", "hour"], ["screenPageViews"]),
    "pages": (["pageTitle"], ["screenPageViews", "userEngagementDuration"]),
    "places": (["country", "city"], ["activeUsers"]),
    "sources": (["sessionSource", "sessionMedium"], ["sessions"]),
    "devices": (["deviceCategory", "browser"], ["activeUsers"]),
}
ORDERED = {"days", "hours"}  # 時間順に並べる。ほかは多い順


def week(arg=None):
    if arg:
        y, w = arg.split("-W")
        mon = dt.date.fromisocalendar(int(y), int(w), 1)
    else:
        d = dt.date.today() - dt.timedelta(days=2)
        mon = d - dt.timedelta(days=(d.weekday() + 1) % 7 + 6)  # d 以前で直近の日曜の、6日前
    y, w, _ = mon.isocalendar()
    return f"{y}-W{w:02d}", mon, mon + dt.timedelta(days=6)


def num(v):
    return float(v) if "." in v else int(v)


def report(session, start, end, dims, metrics):
    r = session.post(f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY}:runReport", json={
        "dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
        "dimensions": [{"name": d} for d in dims],
        "metrics": [{"name": m} for m in metrics],
        "limit": 250,
    })
    r.raise_for_status()
    return [dict(zip(dims, (v["value"] for v in row.get("dimensionValues", []))),
                 **dict(zip(metrics, (num(v["value"]) for v in row["metricValues"]))))
            for row in r.json().get("rows", [])]


def main():
    name, start, end = week(sys.argv[1] if len(sys.argv) > 1 else None)
    path = OUT / f"{name}.json"
    if path.exists():
        return
    if not KEY.exists():
        sys.exit(f"ga.py: 鍵がない（{KEY}）")
    creds = service_account.Credentials.from_service_account_file(
        KEY, scopes=["https://www.googleapis.com/auth/analytics.readonly"])
    session = AuthorizedSession(creds)
    data = {"week": name, "start": start.isoformat(), "end": end.isoformat()}
    for k, (dims, metrics) in REPORTS.items():
        rows = report(session, start, end, dims, metrics)
        rows.sort(key=lambda r: [r[d] for d in dims] if k in ORDERED else -r[metrics[0]])
        data[k] = rows[0] if k == "total" and rows else rows
    OUT.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"{name} -> {path}")


if __name__ == "__main__":
    main()
