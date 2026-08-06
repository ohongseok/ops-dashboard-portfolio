from __future__ import annotations

import math
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="1P OPS DASHBOARD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    [data-testid="stApp"] { background: #0E1117; }
    [data-testid="stSidebar"] {
        background: #161B22;
        min-width: 300px;
        max-width: 300px;
    }
    [data-testid="stSidebarContent"] { padding-left: 10px; padding-right: 10px; }
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    h1 { color: #FFFFFF !important; font-size: 44px !important; line-height: 1.2 !important; }
    h2 { color: #FFFFFF !important; }
    h3 { color: #FFFFFF !important; }
    [data-testid="stMetricValue"] {
        color: #FFFFFF;
        font-size: 36px;
        font-weight: 800;
    }
    [data-baseweb="tab-list"] { gap: 0.35rem; }
    [data-baseweb="tab"] { font-size: 14px; }
    [data-testid="stPlotlyChart"] { overflow: visible; }
    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] { padding-left: 1.5rem; padding-right: 1.5rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


COLORS = {
    "Member A": "#00FFA3",
    "Member B": "#00D4FF",
    "Member C": "#FFD166",
    "Member D": "#FF5482",
    "Member E": "#B554FF",
}
MEMBERS = ["Member A", "Member B", "Member C", "Member D", "Member E"]
TASK_CRAWL = "크롤링"
TASK_BULK = "벌크"


MONTHLY_MEMBER_COUNTS = {
    TASK_CRAWL: {
        "Member A": 4516,
        "Member B": 1604,
        "Member C": 5159,
        "Member D": 0,
        "Member E": 2358,
    },
    TASK_BULK: {
        "Member A": 18,
        "Member B": 1877,
        "Member C": 1214,
        "Member D": 445,
        "Member E": 1348,
    },
}

JULY_FIRST_COUNTS = {
    TASK_CRAWL: {"Member A": 550, "Member B": 0, "Member C": 0, "Member D": 0, "Member E": 84},
    TASK_BULK: {"Member A": 0, "Member B": 32, "Member C": 0, "Member D": 33, "Member E": 47},
}

W27_MEMBER_COUNTS = {
    TASK_CRAWL: {
        "Member A": 1207,
        "Member B": 109,
        "Member C": 4185,
        "Member D": 0,
        "Member E": 460,
    },
    TASK_BULK: {
        "Member A": 0,
        "Member B": 387,
        "Member C": 190,
        "Member D": 140,
        "Member E": 316,
    },
}


MONTHLY_BRAND_ROWS = [
    # Crawling top brands — exact values observed from the July source chart.
    ("Brand 06", TASK_CRAWL, "Member B", 452),
    ("Brand 04", TASK_CRAWL, "Member B", 507),
    ("Brand 02", TASK_CRAWL, "Member A", 809),
    ("Brand 03", TASK_CRAWL, "Member A", 550),
    ("Brand 05", TASK_CRAWL, "Member A", 458),
    ("Brand 07", TASK_CRAWL, "Member C", 427),
    ("Brand 01", TASK_CRAWL, "Member C", 4185),
    # Bulk top brands — exact values observed from the July source chart.
    ("Brand 08", TASK_BULK, "Member B", 771),
    ("Brand 11", TASK_BULK, "Member B", 227),
    ("Brand 09", TASK_BULK, "Member B", 340),
    ("Brand 10", TASK_BULK, "Member D", 202),
    ("Brand 10", TASK_BULK, "Member E", 44),
    ("Brand 12", TASK_BULK, "Member E", 143),
    ("Brand 13", TASK_BULK, "Member C", 187),
    ("Brand 01", TASK_BULK, "Member C", 160),
    ("Brand 12", TASK_BULK, "Member C", 44),
]


def _distribute(total: int, first_day: int, phase: float) -> list[int]:
    """Deterministically distribute a monthly total across July while keeping day 1 exact."""
    remaining = total - first_day
    if remaining <= 0:
        return [first_day] + [0] * 30

    weights = []
    for day in range(2, 32):
        weekday = date(2026, 7, day).weekday()
        business_weight = 1.0 if weekday < 5 else 0.34
        wave = 1.0 + 0.33 * math.sin(day * 0.71 + phase) + 0.17 * math.cos(day * 0.37 + phase)
        weights.append(max(0.05, business_weight * wave))

    raw = [remaining * weight / sum(weights) for weight in weights]
    values = [math.floor(value) for value in raw]
    residual = remaining - sum(values)
    for index in sorted(range(len(raw)), key=lambda i: raw[i] - values[i], reverse=True)[:residual]:
        values[index] += 1
    return [first_day] + values


def build_daily_data() -> pd.DataFrame:
    rows: list[dict] = []
    for task_index, task in enumerate((TASK_CRAWL, TASK_BULK)):
        for member_index, member in enumerate(MEMBERS):
            values = _distribute(
                MONTHLY_MEMBER_COUNTS[task][member],
                JULY_FIRST_COUNTS[task][member],
                phase=member_index * 0.93 + task_index * 1.77,
            )
            for offset, sku in enumerate(values):
                if sku:
                    rows.append(
                        {
                            "날짜": date(2026, 7, 1) + timedelta(days=offset),
                            "리스트업 담당자": member,
                            "작업 유형": task,
                            "SKU": int(sku),
                        }
                    )
    return pd.DataFrame(rows)


DAILY_DATA = build_daily_data()
BRAND_DATA = pd.DataFrame(MONTHLY_BRAND_ROWS, columns=["브랜드", "작업 유형", "리스트업 담당자", "SKU"])


def aggregate_members(frame: pd.DataFrame) -> dict[str, dict[str, int]]:
    result = {TASK_CRAWL: {member: 0 for member in MEMBERS}, TASK_BULK: {member: 0 for member in MEMBERS}}
    if frame.empty:
        return result
    grouped = frame.groupby(["작업 유형", "리스트업 담당자"], as_index=False)["SKU"].sum()
    for row in grouped.itertuples(index=False):
        result[row[0]][row[1]] = int(row[2])
    return result


def add_counts(counts: dict[str, dict[str, int]]) -> dict[str, int]:
    return {member: counts[TASK_CRAWL].get(member, 0) + counts[TASK_BULK].get(member, 0) for member in MEMBERS}


def total_for(counts: dict[str, dict[str, int]], task: str) -> int:
    return int(sum(counts[task].values()))


def donut_figure(values: dict[str, int], title: str) -> go.Figure:
    cleaned = {name: value for name, value in values.items() if value > 0}
    fig = go.Figure(
        go.Pie(
            labels=list(cleaned),
            values=list(cleaned.values()),
            hole=0.40,
            domain={"x": [0.0, 0.62], "y": [0.03, 0.97]},
            sort=True,
            direction="clockwise",
            textinfo="percent",
            hovertemplate="리스트업 담당자=%{label}<br>SKU=%{value}<extra></extra>",
            marker={"colors": [COLORS[name] for name in cleaned]},
        )
    )
    fig.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left"},
        height=350,
        margin={"l": 10, "r": 10, "t": 52, "b": 10},
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font={"color": "#FAFAFA", "family": "Source Sans, sans-serif"},
        legend={"title": None, "orientation": "v", "x": 0.66, "y": 0.52, "xanchor": "left", "font": {"size": 12}},
        showlegend=True,
    )
    return fig


def brand_bar_figure(frame: pd.DataFrame, title: str) -> go.Figure:
    totals = frame.groupby("브랜드")["SKU"].sum().sort_values(ascending=True)
    order = totals.index.tolist()
    fig = go.Figure()
    for member in MEMBERS:
        member_rows = frame[frame["리스트업 담당자"] == member].groupby("브랜드")["SKU"].sum()
        if member_rows.empty:
            continue
        fig.add_bar(
            name=member,
            x=[int(member_rows.get(brand, 0)) for brand in order],
            y=order,
            orientation="h",
            marker_color=COLORS[member],
            hovertemplate=f"리스트업 담당자={member}<br>SKU=%{{x}}<br>브랜드=%{{y}}<extra></extra>",
        )
    fig.update_layout(
        barmode="stack",
        title={"text": title, "x": 0.02, "xanchor": "left"},
        height=350,
        margin={"l": 8, "r": 8, "t": 52, "b": 8},
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font={"color": "#FAFAFA", "family": "Source Sans, sans-serif"},
        legend={"title": {"text": "리스트업 담당자"}, "orientation": "v", "x": 1.02, "y": 1},
        xaxis={"title": "SKU", "gridcolor": "rgba(250,250,250,0.10)", "zeroline": False},
        yaxis={"title": "브랜드", "categoryorder": "array", "categoryarray": order},
    )
    return fig


def trend_figure(frame: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure()
    series_colors = {
        TASK_CRAWL: "#00D4FF",
        TASK_BULK: "#FFD166",
        "크롤링+벌크 누적 SKU": "#00FFA3",
    }
    for column in frame.columns:
        fig.add_scatter(
            x=[str(value) for value in frame.index],
            y=frame[column].tolist(),
            mode="lines+markers",
            name=str(column),
            line={"color": series_colors.get(str(column), "#B554FF"), "width": 2.5},
            marker={"size": 6},
            hovertemplate=f"{column}<br>%{{x}}<br>SKU=%{{y:,}}<extra></extra>",
        )
    fig.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left"},
        height=350,
        margin={"l": 8, "r": 8, "t": 52, "b": 8},
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font={"color": "#FAFAFA", "family": "Source Sans, sans-serif"},
        legend={"orientation": "h", "y": 1.12, "x": 0},
        xaxis={"gridcolor": "rgba(250,250,250,0.08)", "zeroline": False},
        yaxis={"title": "SKU", "gridcolor": "rgba(250,250,250,0.10)", "zeroline": False},
    )
    return fig


def scaled_brand_data(task: str, target_total: int, seed_shift: int = 0) -> pd.DataFrame:
    base = BRAND_DATA[BRAND_DATA["작업 유형"] == task].copy()
    if base.empty or target_total <= 0:
        return base.iloc[0:0]
    top_budget = max(1, int(target_total * (0.72 if task == TASK_CRAWL else 0.45)))
    ratio = top_budget / base["SKU"].sum()
    base["SKU"] = (base["SKU"] * ratio).round().astype(int).clip(lower=1)
    if seed_shift:
        base["브랜드"] = base["브랜드"].map(
            lambda label: f"Brand {((int(label.split()[-1]) - 1 + seed_shift) % 13) + 1:02d}"
        )
    return base


def detail_table(brand_frame: pd.DataFrame, period_code: str) -> pd.DataFrame:
    if brand_frame.empty:
        return pd.DataFrame(columns=["기간", "브랜드", "작업 유형", "SKU"])
    table = brand_frame.groupby(["브랜드", "작업 유형"], as_index=False)["SKU"].sum()
    table.insert(0, "기간", period_code)
    return table.sort_values("SKU", ascending=False, ignore_index=True)


PLOT_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


def render_period(
    prefix: str,
    counts: dict[str, dict[str, int]],
    crawl_brands: pd.DataFrame,
    bulk_brands: pd.DataFrame,
    period_code: str,
) -> None:
    crawl_total = total_for(counts, TASK_CRAWL)
    bulk_total = total_for(counts, TASK_BULK)
    combined_total = crawl_total + bulk_total

    m1, m2, m3 = st.columns(3)
    m1.metric(f"🔍 {prefix} 크롤링 총합", f"{crawl_total:,} 개")
    m2.metric(f"📦 {prefix} 벌크작업 총합", f"{bulk_total:,} 개")
    m3.metric(f"🔗 {prefix} 크롤링+벌크 총합", f"{combined_total:,} 개")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            donut_figure(counts[TASK_CRAWL], f"{prefix} 크롤링 기여도"),
            use_container_width=True,
            config=PLOT_CONFIG,
            key=f"{prefix}-{period_code}-crawl-pie",
        )
    with right:
        st.plotly_chart(
            donut_figure(counts[TASK_BULK], f"{prefix} 벌크 기여도"),
            use_container_width=True,
            config=PLOT_CONFIG,
            key=f"{prefix}-{period_code}-bulk-pie",
        )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            brand_bar_figure(crawl_brands, f"{prefix} 크롤링 탑 브랜드"),
            use_container_width=True,
            config=PLOT_CONFIG,
            key=f"{prefix}-{period_code}-crawl-brand",
        )
    with right:
        st.plotly_chart(
            brand_bar_figure(bulk_brands, f"{prefix} 벌크 탑 브랜드"),
            use_container_width=True,
            config=PLOT_CONFIG,
            key=f"{prefix}-{period_code}-bulk-brand",
        )

    st.markdown(f"#### 🔗 {prefix} 크롤링+벌크 작업")
    combined_counts = add_counts(counts)
    combined_brands = pd.concat([crawl_brands, bulk_brands], ignore_index=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            donut_figure(combined_counts, f"{prefix} 크롤링+벌크 기여도"),
            use_container_width=True,
            config=PLOT_CONFIG,
            key=f"{prefix}-{period_code}-combined-pie",
        )
    with right:
        st.plotly_chart(
            brand_bar_figure(combined_brands, f"{prefix} 크롤링+벌크 탑 브랜드"),
            use_container_width=True,
            config=PLOT_CONFIG,
            key=f"{prefix}-{period_code}-combined-brand",
        )

    with st.expander(f"📊 {prefix} 크롤링+벌크 주차/브랜드 상세"):
        st.dataframe(
            detail_table(combined_brands, period_code),
            use_container_width=True,
            hide_index=True,
            height=400,
        )


def member_period_counts(frame: pd.DataFrame, member: str) -> dict[str, dict[str, int]]:
    filtered = frame[frame["리스트업 담당자"] == member]
    return aggregate_members(filtered)


def render_member_detail(
    member: str,
    selected_date: date,
    week_counts: dict[str, dict[str, int]],
    month_counts: dict[str, dict[str, int]],
    day_counts: dict[str, dict[str, int]],
    week_label: str,
) -> None:
    st.divider()
    st.subheader(f"👤 {member} 상세 분석")
    st.caption("선택한 익명 담당자의 동일 기간 작업 상세입니다.")

    tabs = st.tabs(
        [
            f"🎯 {week_label} 주차",
            "📅 2026-07 월간",
            f"⚡ {selected_date:%Y-%m-%d} 일간",
            "🏆 2026년 누적",
        ]
    )
    period_counts = [week_counts, month_counts, day_counts, month_counts]
    prefixes = ["주간", "월간", "일간", "2026년"]
    for tab, counts, prefix in zip(tabs, period_counts, prefixes):
        with tab:
            crawl = counts[TASK_CRAWL][member]
            bulk = counts[TASK_BULK][member]
            c1, c2, c3 = st.columns(3)
            c1.metric(f"🔍 {prefix} 크롤링", f"{crawl:,} 개")
            c2.metric(f"📦 {prefix} 벌크작업", f"{bulk:,} 개")
            c3.metric(f"🔗 {prefix} 통합", f"{crawl + bulk:,} 개")

            trend = DAILY_DATA[DAILY_DATA["리스트업 담당자"] == member]
            trend = trend.groupby(["날짜", "작업 유형"], as_index=False)["SKU"].sum()
            pivot = trend.pivot(index="날짜", columns="작업 유형", values="SKU").fillna(0)
            st.plotly_chart(
                trend_figure(pivot, f"{member} 7월 작업 추이"),
                use_container_width=True,
                config=PLOT_CONFIG,
                key=f"member-trend-{member}-{prefix}",
            )


with st.sidebar:
    st.header("인원별 상세 분석")
    st.write("이름을 선택하면 해당 담당자의 작업 상세가 아래에 추가됩니다.")
    selected_members = [member for member in MEMBERS if st.checkbox(member, key=f"member-{member}")]


st.title("📊 1P OPS DASHBOARD")
left, right = st.columns([3, 1])
with right:
    st.markdown(
        "<div style='text-align:right;line-height:1.25'>"
        "Created &amp; Maintained by <b>Member C</b><br>"
        "<span style='font-size:.85rem'>운영 및 유지보완 담당</span></div>",
        unsafe_allow_html=True,
    )

selected_date = st.date_input(
    "📅 조회 기준일 선택",
    value=date(2026, 7, 1),
    min_value=date(2026, 7, 1),
    max_value=date(2026, 7, 31),
    format="YYYY/MM/DD",
)

st.subheader("🏆 팀 통합 성과 (Team Performance)")

week_no = selected_date.isocalendar().week
week_label = f"26W{week_no:02d}"
week_start = selected_date - timedelta(days=selected_date.weekday())
week_end = week_start + timedelta(days=6)
week_frame = DAILY_DATA[(DAILY_DATA["날짜"] >= week_start) & (DAILY_DATA["날짜"] <= week_end)]
day_frame = DAILY_DATA[DAILY_DATA["날짜"] == selected_date]

if week_no == 27:
    weekly_counts = W27_MEMBER_COUNTS
else:
    weekly_counts = aggregate_members(week_frame)

monthly_counts = MONTHLY_MEMBER_COUNTS
daily_counts = aggregate_members(day_frame)
year_counts = MONTHLY_MEMBER_COUNTS

weekly_crawl_brands = scaled_brand_data(TASK_CRAWL, total_for(weekly_counts, TASK_CRAWL), seed_shift=week_no - 27)
weekly_bulk_brands = scaled_brand_data(TASK_BULK, total_for(weekly_counts, TASK_BULK), seed_shift=week_no - 27)
daily_crawl_brands = scaled_brand_data(TASK_CRAWL, total_for(daily_counts, TASK_CRAWL), seed_shift=selected_date.day % 5)
daily_bulk_brands = scaled_brand_data(TASK_BULK, total_for(daily_counts, TASK_BULK), seed_shift=selected_date.day % 5)

team_tabs = st.tabs(
    [
        f"🎯 {week_label} 주차",
        "📅 2026-07 월간",
        f"⚡ {selected_date:%Y-%m-%d} 일간",
        "🏆 2026년 누적",
    ]
)

with team_tabs[0]:
    render_period("주간", weekly_counts, weekly_crawl_brands, weekly_bulk_brands, week_label)

with team_tabs[1]:
    render_period(
        "월간",
        monthly_counts,
        BRAND_DATA[BRAND_DATA["작업 유형"] == TASK_CRAWL],
        BRAND_DATA[BRAND_DATA["작업 유형"] == TASK_BULK],
        "26M07",
    )

with team_tabs[2]:
    render_period("일간", daily_counts, daily_crawl_brands, daily_bulk_brands, selected_date.strftime("%Y-%m-%d"))

with team_tabs[3]:
    render_period(
        "2026년",
        year_counts,
        BRAND_DATA[BRAND_DATA["작업 유형"] == TASK_CRAWL],
        BRAND_DATA[BRAND_DATA["작업 유형"] == TASK_BULK],
        "2026-07 누적",
    )
    st.markdown("#### 팀 전체 2026년 누적 추이")
    final_crawl = total_for(year_counts, TASK_CRAWL)
    final_bulk = total_for(year_counts, TASK_BULK)
    f1, f2, f3 = st.columns(3)
    f1.metric("크롤링 최종 누적 SKU", f"{final_crawl:,}")
    f2.metric("벌크 최종 누적 SKU", f"{final_bulk:,}")
    f3.metric("크롤링+벌크 최종 누적 SKU", f"{final_crawl + final_bulk:,}")

    weekly_trend = DAILY_DATA.copy()
    weekly_trend["주차"] = weekly_trend["날짜"].map(lambda value: f"26W{value.isocalendar().week:02d}")
    weekly_trend = weekly_trend.groupby(["주차", "작업 유형"], as_index=False)["SKU"].sum()
    weekly_pivot = weekly_trend.pivot(index="주차", columns="작업 유형", values="SKU").fillna(0)
    weekly_pivot["크롤링+벌크 누적 SKU"] = weekly_pivot.sum(axis=1).cumsum()

    month_trend = pd.DataFrame(
        {TASK_CRAWL: [final_crawl], TASK_BULK: [final_bulk], "크롤링+벌크 누적 SKU": [final_crawl + final_bulk]},
        index=["26M07"],
    )
    trend_tabs = st.tabs(["주차별 SKU", "월별 SKU"])
    with trend_tabs[0]:
        st.plotly_chart(
            trend_figure(weekly_pivot, "팀 전체 주차별 SKU 및 크롤링+벌크 누적"),
            use_container_width=True,
            config=PLOT_CONFIG,
            key="year-weekly-trend",
        )
        st.dataframe(weekly_pivot.reset_index(), use_container_width=True, hide_index=True)
    with trend_tabs[1]:
        st.plotly_chart(
            trend_figure(month_trend, "팀 전체 월별 SKU 및 크롤링+벌크 누적"),
            use_container_width=True,
            config=PLOT_CONFIG,
            key="year-monthly-trend",
        )
        st.dataframe(month_trend.reset_index(names="월"), use_container_width=True, hide_index=True)


for selected_member in selected_members:
    render_member_detail(
        selected_member,
        selected_date,
        weekly_counts,
        monthly_counts,
        daily_counts,
        week_label,
    )
