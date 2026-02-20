"""
ship_tracker_web.py  (v2 - 흰 배경, 다국어, 말풍선 위치 수정)
-------------------------------------------------------------
pygame 기반 ship_tracker.py를 Streamlit 임베드용 HTML5로 재구현한 모듈.

변경사항 (v2):
  - 배경 흰색으로 변경 + 전체 색상 라이트모드로 전환
  - 말풍선 위치: 배 아래 → 배 위
  - 다국어 지원: lang 파라미터로 KR / EN / TH 전환
  - 출발일 계산: 도착일 - 28일 (기존 21일에서 변경)
"""

import datetime
from dateutil import parser as date_parser


# ──────────────────────────────────────────────────────
# [설정] 항로 기항지  (좌=방콕, 우=인천)
# ──────────────────────────────────────────────────────
STATIONS = [
    {"name": "INCHEON",       "x_pct": 93, "days": 0},
    {"name": "BUSAN",         "x_pct": 80, "days": 4},
    {"name": "SHANGHAI",      "x_pct": 65, "days": 9},
    {"name": "HONG KONG",     "x_pct": 48, "days": 14},
    {"name": "HO CHI MINH",   "x_pct": 28, "days": 21},
    {"name": "BANGKOK",       "x_pct": 7,  "days": 28},
]

SHIP_COLORS = ["#e84040", "#3a7bd5", "#f5a623", "#27ae60"]

# ──────────────────────────────────────────────────────
# [다국어] 문자열 테이블
# ──────────────────────────────────────────────────────
I18N = {
    "KR": {
        "title":       "⚓ 인천 → 방콕  해상 운송 노선",
        "date_label":  "기준일",
        "in_transit":  "운항중",
        "arrived":     "도착완료",
        "pending":     "출발전",
        "arrives":     "도착",   # "3/15 도착"
    },
    "EN": {
        "title":       "⚓ INCHEON → BANGKOK  Shipping Route",
        "date_label":  "As of",
        "in_transit":  "In Transit",
        "arrived":     "Arrived",
        "pending":     "Pending",
        "arrives":     "Arrives",
    },
    "TH": {
        "title":       "⚓ อินชอน → กรุงเทพฯ  เส้นทางเดินเรือ",
        "date_label":  "ณ วันที่",
        "in_transit":  "กำลังเดินทาง",
        "arrived":     "มาถึงแล้ว",
        "pending":     "ยังไม่ออกเดินทาง",
        "arrives":     "ถึง",
    },
}


def _parse_arrivals(arrival_dates: list, lang: str = "KR") -> list:
    """도착 예정일 문자열 리스트 → 운항 스케줄 dict 리스트."""
    t = I18N.get(lang, I18N["KR"])
    schedules = []
    seen = set()

    for raw in arrival_dates:
        if not raw or not str(raw).strip():
            continue
        try:
            arrival = date_parser.parse(str(raw).strip())
            key = arrival.date().isoformat()
            if key in seen:
                continue
            seen.add(key)

            # ★ 출발일 = 도착일 - 28일 (변경: 기존 21일)
            departure = arrival - datetime.timedelta(days=28)
            idx = len(schedules)

            # 언어에 맞는 말풍선 라벨 생성
            month = arrival.month
            day   = arrival.day
            if lang == "KR":
                label = f"{month}/{day} {t['arrives']}"
            elif lang == "EN":
                label = f"{t['arrives']} {month}/{day}"
            else:  # TH
                label = f"{t['arrives']} {month}/{day}"

            schedules.append({
                "start":  departure,
                "end":    arrival,
                "label":  label,
                "color":  SHIP_COLORS[idx % len(SHIP_COLORS)],
            })
        except Exception:
            continue

    return sorted(schedules, key=lambda s: s["end"])


def _calc_progress(schedule: dict, now: datetime.datetime) -> float:
    """현재 시각 기준 운항 진행률 (0.0 ~ 1.0)."""
    total_sec   = (schedule["end"] - schedule["start"]).total_seconds()
    elapsed_sec = (now - schedule["start"]).total_seconds()
    if total_sec <= 0:
        return 1.0
    return max(0.0, min(1.0, elapsed_sec / total_sec))


def get_ship_tracker_html(
    arrival_dates: list = None,
    now: datetime.datetime = None,
    height: int = 280,
    lang: str = "KR",
) -> str:
    """
    해상 운송 노선 트래커 HTML 문자열 반환.

    Args:
        arrival_dates : 도착 예정일 문자열 리스트
        now           : 기준 시각 (None → 실제 현재 시각)
        height        : 컨테이너 높이(px)
        lang          : 'KR' | 'EN' | 'TH'
    """
    t = I18N.get(lang, I18N["KR"])

    # 기본 테스트 데이터
    if not arrival_dates:
        today = datetime.datetime.now()
        arrival_dates = [
            (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
            (today + datetime.timedelta(days=18)).strftime("%Y-%m-%d"),
        ]

    if now is None:
        now = datetime.datetime.now()

    schedules = _parse_arrivals(arrival_dates, lang=lang)

    # ── 선박 위치 계산 (Python → JS 전달) ──
    ships_js = []
    for sched in schedules:
        prog  = _calc_progress(sched, now)
        start_x = STATIONS[0]["x_pct"]   # 93
        end_x   = STATIONS[-1]["x_pct"]  # 7
        x_pct   = start_x + (end_x - start_x) * prog

        if prog >= 1:
            status = t["arrived"]
        elif prog <= 0:
            status = t["pending"]
        else:
            status = t["in_transit"]

        ships_js.append({
            "label":   sched["label"],
            "color":   sched["color"],
            "x_pct":   round(x_pct, 2),
            "prog":    round(prog * 100, 1),
            "status":  status,
            "moving":  0 < prog < 1,
        })

    import json
    ships_json    = json.dumps(ships_js,   ensure_ascii=False)
    stations_json = json.dumps(STATIONS,   ensure_ascii=False)
    now_str       = now.strftime("%Y-%m-%d")

    # ── HTML 생성 (흰 배경 라이트모드) ──
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: #ffffff;
    padding: 14px 20px 10px;
    min-height: {height}px;
    color: #1a1a2e;
  }}

  /* ── 제목 ── */
  .tracker-title {{
    text-align: center;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #1a3a5c;
    margin-bottom: 3px;
    text-transform: uppercase;
  }}
  .tracker-date {{
    text-align: center;
    font-size: 11px;
    color: #5a7a9a;
    margin-bottom: 14px;
  }}

  /* ── 노선도 컨테이너 ── */
  .route-wrap {{
    position: relative;
    width: 100%;
    height: 120px;
    margin-bottom: 14px;
  }}

  /* 메인 라인 */
  .route-line {{
    position: absolute;
    top: 70px;
    left: 4%;
    right: 4%;
    height: 4px;
    background: linear-gradient(90deg, #1a6fa8, #4fc3f7, #1a6fa8);
    border-radius: 2px;
    box-shadow: 0 1px 6px rgba(26,111,168,0.25);
  }}

  /* 기항지 노드 */
  .station {{
    position: absolute;
    top: 56px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .station-dot {{
    width: 12px; height: 12px;
    border-radius: 50%;
    background: #fff;
    border: 2.5px solid #1a6fa8;
    box-shadow: 0 0 5px rgba(26,111,168,0.35);
  }}
  .station-dot.main {{
    width: 16px; height: 16px;
    background: #1a6fa8;
    border-color: #fff;
    box-shadow: 0 0 8px rgba(26,111,168,0.5);
  }}
  .station-name {{
    font-size: 8.5px;
    font-weight: 700;
    color: #2c4a6a;
    text-align: center;
    white-space: nowrap;
    margin-top: 8px;
    letter-spacing: 0.4px;
  }}

  /* ── 선박 ── */
  .ship {{
    position: absolute;
    /* 말풍선이 위에 있으므로 선박 아이콘은 노선선 바로 위쪽 */
    top: 28px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    animation: bob 2.5s ease-in-out infinite;
    cursor: default;
  }}
  /* 말풍선: 선박 아이콘 위 */
  .ship-bubble {{
    background: #fff;
    color: #1a2a3a;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 10px;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(0,0,0,0.18);
    border: 1.5px solid #cde;
    margin-bottom: 3px;  /* 말풍선 아래에 선박 아이콘이 오도록 */
    order: -1;           /* Flexbox 순서: 버블 먼저(위), 아이콘 나중(아래) */
  }}
  .ship-icon {{
    font-size: 22px;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    transform: scaleX(-1); /* 왼쪽(방콕) 방향 */
  }}

  @keyframes bob {{
    0%, 100% {{ transform: translateX(-50%) translateY(0); }}
    50%        {{ transform: translateX(-50%) translateY(-5px); }}
  }}

  /* ── 상태 카드 ── */
  .status-row {{
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
  }}
  .status-card {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: #f0f6ff;
    border: 1px solid #c8ddf4;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 11px;
    color: #1a2a3a;
  }}
  .status-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
  }}
  .status-badge {{
    background: #dceeff;
    color: #1a6fa8;
    border-radius: 8px;
    padding: 1px 7px;
    font-size: 10px;
    font-weight: 700;
  }}
  .status-badge.arrived {{
    background: #d4f7e7;
    color: #1a8a50;
  }}
  .status-badge.pending {{
    background: #e8e8e8;
    color: #666;
  }}
</style>
</head>
<body>

<div class="tracker-title">{t['title']}</div>
<div class="tracker-date">📅 {t['date_label']}: {now_str}</div>

<div class="route-wrap" id="routeWrap">
  <div class="route-line"></div>
</div>

<div class="status-row" id="statusRow"></div>

<script>
const STATIONS = {stations_json};
const SHIPS    = {ships_json};

const wrap      = document.getElementById('routeWrap');
const statusRow = document.getElementById('statusRow');

// 기항지 노드
STATIONS.forEach(st => {{
  const el = document.createElement('div');
  el.className = 'station';
  el.style.left = st.x_pct + '%';
  const isMain = (st.name === 'INCHEON' || st.name === 'BANGKOK');
  el.innerHTML = `
    <div class="station-dot ${{isMain ? 'main' : ''}}"></div>
    <div class="station-name">${{st.name}}</div>
  `;
  wrap.appendChild(el);
}});

// 선박 렌더링
SHIPS.forEach((ship, i) => {{
  if (ship.moving) {{
    const el = document.createElement('div');
    el.className = 'ship';
    el.style.left = ship.x_pct + '%';
    // 여러 선박 겹침 방지: 위아래 오프셋
    el.style.top  = (28 - i * 10) + 'px';
    el.style.animationDelay = (i * 0.8) + 's';
    // 말풍선(위) + 아이콘(아래) 순서는 CSS order:-1로 처리됨
    el.innerHTML = `
      <div class="ship-bubble" style="border-color:${{ship.color}}">${{ship.label}}</div>
      <div class="ship-icon">🚢</div>
    `;
    wrap.appendChild(el);
  }}

  // 상태 카드
  const badgeClass = ship.status.includes('도착') || ship.status === 'Arrived' || ship.status.includes('มาถึง') ? 'arrived'
                   : (!ship.moving && ship.prog === 0) ? 'pending' : '';
  const card = document.createElement('div');
  card.className = 'status-card';
  card.innerHTML = `
    <div class="status-dot" style="background:${{ship.color}}"></div>
    <span>🚢 ${{ship.label}}</span>
    <span class="status-badge ${{badgeClass}}">
      ${{ship.status}} ${{ship.moving ? ship.prog + '%' : ''}}
    </span>
  `;
  statusRow.appendChild(card);
}});
</script>
</body>
</html>"""

    return html
