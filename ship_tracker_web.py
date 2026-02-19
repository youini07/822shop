"""
ship_tracker_web.py
---------------------
기존 pygame 기반 ship_tracker.py의 해상 운송 노선 트래커를
Streamlit 웹 환경에 임베드 가능한 HTML5+CSS+JS 버전으로 재구현한 모듈.

[사용법]
    from shipping.ship_tracker_web import get_ship_tracker_html
    html_code = get_ship_tracker_html(arrival_dates=["2024-04-05", "2024-04-20"])
    st.components.v1.html(html_code, height=320, scrolling=False)
"""

import datetime
from dateutil import parser as date_parser


# ===========================================
# [설정] 항로 기항지 정보
# 실제 해운 소요일 기준 x 비율: INCHEON(0일) -> BANGKOK(21일)
# ===========================================
STATIONS = [
    {"name": "INCHEON",     "x_pct": 93, "days": 0},
    {"name": "BUSAN",       "x_pct": 80, "days": 2},
    {"name": "SHANGHAI",    "x_pct": 65, "days": 5},
    {"name": "HONG KONG",   "x_pct": 48, "days": 9},
    {"name": "HO CHI MINH","x_pct": 28, "days": 15},
    {"name": "BANGKOK",     "x_pct": 7,  "days": 21},
]

# 서로 다른 선박에 부여할 색상 목록 (hex)
SHIP_COLORS = ["#e84040", "#3a7bd5", "#f5a623", "#27ae60"]


def _parse_arrivals(arrival_dates: list) -> list:
    """
    도착 예정일 문자열 리스트를 파싱하여 운항 스케줄 dict 리스트로 변환.
    반환값: [{"start": datetime, "end": datetime, "label": str, "color": str}, ...]
    """
    schedules = []
    seen = set()

    for raw in arrival_dates:
        if not raw or not str(raw).strip():
            continue
        try:
            arrival = date_parser.parse(str(raw).strip())
            # 중복 제거
            key = arrival.date().isoformat()
            if key in seen:
                continue
            seen.add(key)

            # 출발일 = 도착일 - 21일 (총 항해 기간)
            departure = arrival - datetime.timedelta(days=21)
            idx = len(schedules)
            schedules.append({
                "start": departure,
                "end": arrival,
                "label": f"{arrival.month}/{arrival.day} 도착",
                "color": SHIP_COLORS[idx % len(SHIP_COLORS)],
            })
        except Exception:
            continue

    return sorted(schedules, key=lambda s: s["end"])


def _calc_progress(schedule: dict, now: datetime.datetime) -> float:
    """
    현재 시각 기준으로 해당 스케줄의 운항 진행률(0.0 ~ 1.0)을 계산.
    0.0 = 출발 전, 1.0 = 도착 완료.
    """
    total_sec = (schedule["end"] - schedule["start"]).total_seconds()
    elapsed_sec = (now - schedule["start"]).total_seconds()
    if total_sec <= 0:
        return 1.0
    return max(0.0, min(1.0, elapsed_sec / total_sec))


def get_ship_tracker_html(
    arrival_dates: list = None,
    now: datetime.datetime = None,
    height: int = 300,
) -> str:
    """
    해상 운송 노선 트래커 HTML 문자열을 반환합니다.

    Args:
        arrival_dates: 도착 예정일 문자열 리스트 (e.g. ["2024-04-05"])
                       None이면 내부 TEST_DATA 사용
        now:           현재 시각 (None이면 실제 현재 시각 사용)
        height:        HTML 컨테이너 높이 (px)

    Returns:
        st.components.v1.html()에 직접 전달 가능한 HTML 문자열
    """
    # 기본 테스트 데이터 (실제 데이터 없을 때)
    if not arrival_dates:
        today = datetime.datetime.now()
        arrival_dates = [
            (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
            (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"),
        ]

    if now is None:
        now = datetime.datetime.now()

    schedules = _parse_arrivals(arrival_dates)

    # -------------------------------------------------------------------
    # 선박 위치 데이터를 Python에서 계산 → JS로 전달 (정적 렌더링)
    # -------------------------------------------------------------------
    ships_js_data = []
    for sched in schedules:
        prog = _calc_progress(sched, now)
        # 화면상 X 좌표 % = 출발(93%) → 도착(7%) 사이 선형 보간
        start_x = STATIONS[0]["x_pct"]   # 93
        end_x   = STATIONS[-1]["x_pct"]  # 7
        x_pct = start_x + (end_x - start_x) * prog

        status = "운항중" if 0 < prog < 1 else ("도착완료" if prog >= 1 else "출발전")

        ships_js_data.append({
            "label":  sched["label"],
            "color":  sched["color"],
            "x_pct":  round(x_pct, 2),
            "prog":   round(prog * 100, 1),
            "status": status,
        })

    # Python → JS JSON 직렬화
    import json
    ships_json   = json.dumps(ships_js_data, ensure_ascii=False)
    stations_json = json.dumps(STATIONS, ensure_ascii=False)
    now_str = now.strftime("%Y-%m-%d")

    # -------------------------------------------------------------------
    # HTML 생성
    # 캔버스 대신 순수 CSS+div 로 렌더링 → 폰트/스케일 이슈 없음
    # -------------------------------------------------------------------
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 16px 20px 10px;
    min-height: {height}px;
    color: #fff;
  }}

  /* ── 제목 ── */
  .tracker-title {{
    text-align: center;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #a8d8ea;
    margin-bottom: 4px;
    text-transform: uppercase;
  }}
  .tracker-date {{
    text-align: center;
    font-size: 11px;
    color: #7fb3c8;
    margin-bottom: 14px;
  }}

  /* ── 노선도 컨테이너 ── */
  .route-wrap {{
    position: relative;
    width: 100%;
    height: 110px;
    margin-bottom: 12px;
  }}

  /* 메인 라인 */
  .route-line {{
    position: absolute;
    top: 52px;
    left: 4%;
    right: 4%;
    height: 4px;
    background: linear-gradient(90deg, #4fc3f7, #81d4fa, #4fc3f7);
    border-radius: 2px;
    box-shadow: 0 0 12px rgba(79,195,247,0.6);
  }}

  /* 기항지 노드 */
  .station {{
    position: absolute;
    top: 38px;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }}
  .station-dot {{
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #fff;
    border: 2px solid #4fc3f7;
    box-shadow: 0 0 8px rgba(79,195,247,0.8);
  }}
  .station-dot.main {{
    width: 18px;
    height: 18px;
    background: #4fc3f7;
    border-color: #fff;
  }}
  .station-name {{
    font-size: 9px;
    font-weight: 600;
    color: #cde;
    text-align: center;
    white-space: nowrap;
    margin-top: 6px;
    letter-spacing: 0.5px;
  }}

  /* ── 선박 아이콘 ── */
  .ship {{
    position: absolute;
    top: 20px;          /* 노선 위로 배치 */
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    animation: bob 2.5s ease-in-out infinite;
    cursor: default;
  }}
  .ship-icon {{
    font-size: 22px;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.6));
    /* 배가 왼쪽(방콕)을 향하도록 수평 반전 */
    transform: scaleX(-1);
  }}
  .ship-bubble {{
    background: rgba(255,255,255,0.95);
    color: #1a2a3a;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 10px;
    white-space: nowrap;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    margin-top: 2px;
  }}

  @keyframes bob {{
    0%, 100% {{ transform: translateX(-50%) translateY(0); }}
    50%        {{ transform: translateX(-50%) translateY(-4px); }}
  }}

  /* ── 선박 상태 카드 ── */
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
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 11px;
  }}
  .status-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
  }}
  .status-badge {{
    background: rgba(79,195,247,0.25);
    color: #4fc3f7;
    border-radius: 8px;
    padding: 1px 6px;
    font-size: 10px;
    font-weight: 700;
  }}
  .status-badge.arrived {{
    background: rgba(39,174,96,0.25);
    color: #2ecc71;
  }}
  .status-badge.before {{
    background: rgba(200,200,200,0.15);
    color: #aaa;
  }}
</style>
</head>
<body>

<div class="tracker-title">⚓ INCHEON → BANGKOK  Shipping Route</div>
<div class="tracker-date">📅 기준일: {now_str}</div>

<!-- 노선도 -->
<div class="route-wrap" id="routeWrap">
  <div class="route-line"></div>
  <!-- 기항지 & 선박을 JS로 동적 삽입 -->
</div>

<!-- 선박 상태 카드 -->
<div class="status-row" id="statusRow"></div>

<script>
const STATIONS = {stations_json};
const SHIPS    = {ships_json};

const wrap      = document.getElementById('routeWrap');
const statusRow = document.getElementById('statusRow');

// ── 기항지 노드 렌더링 ──
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

// ── 선박 렌더링 ──
SHIPS.forEach((ship, i) => {{
  // 운항중인 선박만 지도 위에 표시
  if (ship.status === '운항중') {{
    const el = document.createElement('div');
    el.className = 'ship';
    // 여러 배가 겹치지 않게 조금씩 위치 조정
    el.style.left  = ship.x_pct + '%';
    el.style.top   = (14 - i * 8) + 'px';
    el.style.animationDelay = (i * 0.7) + 's';

    el.innerHTML = `
      <div class="ship-icon">🚢</div>
      <div class="ship-bubble" style="border:1.5px solid ${{ship.color}}">${{ship.label}}</div>
    `;
    wrap.appendChild(el);
  }}

  // 상태 카드
  const card = document.createElement('div');
  card.className = 'status-card';

  const badgeClass = ship.status === '도착완료' ? 'arrived' : (ship.status === '출발전' ? 'before' : '');
  card.innerHTML = `
    <div class="status-dot" style="background:${{ship.color}}"></div>
    <span>🚢 ${{ship.label}}</span>
    <span class="status-badge ${{badgeClass}}">${{ship.status}} ${{ship.status === '운항중' ? ship.prog + '%' : ''}}</span>
  `;
  statusRow.appendChild(card);
}});
</script>
</body>
</html>"""

    return html
