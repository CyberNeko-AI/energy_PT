"""绿城能源数据仪表盘。

运行：streamlit run app.py
数据目录保持为当前项目下的「电表数据」和「光伏数据」。
"""

from __future__ import annotations

import json
from pathlib import Path
import re

import openpyxl
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="绿城能源数据仪表盘", page_icon="🌿", layout="wide")

ROOT = Path(__file__).resolve().parent
ELECTRIC_DIR = ROOT / "电表数据"
PV_DIR = ROOT / "光伏数据"
LOCAL_CACHE = ROOT / ".energy_dashboard_cache.pkl"
LOCAL_CACHE_META = ROOT / ".energy_dashboard_cache.json"
EMISSION_FACTOR_TON_PER_KWH = 0.000581


def to_number(series: pd.Series) -> pd.Series:
    """安全转换 Excel 内可能被存为文字的数字。"""
    return pd.to_numeric(series, errors="coerce")


def classify_meter(filename: str) -> str:
    """按文件名归集主要用电场景。"""
    name = filename.lower()
    rules = [
        ("空调", "空调系统"),
        ("照明", "照明系统"),
        ("水泵", "给排水系统"),
        ("电梯", "电梯系统"),
        ("花房", "花房"),
        ("儿童", "儿童空间"),
        ("宠物", "宠物用房"),
        ("学习", "学习盒子"),
        ("日咖", "日咖夜酒"),
    ]
    for keyword, category in rules:
        if keyword in name:
            return category
    return "其他负荷"


def read_excel_columns(file: Path, columns: list[str]) -> pd.DataFrame:
    """以只读模式提取指定列，减少大量历史台账的首次加载时间。"""
    workbook = openpyxl.load_workbook(file, read_only=True, data_only=True)
    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        header = next(rows, None)
        if not header:
            return pd.DataFrame(columns=columns)
        positions = {str(value).strip(): idx for idx, value in enumerate(header) if value is not None}
        missing = [column for column in columns if column not in positions]
        if missing:
            return pd.DataFrame(columns=columns)
        records = [tuple(row[positions[column]] for column in columns) for row in rows]
        return pd.DataFrame(records, columns=columns)
    finally:
        workbook.close()


def source_signature() -> dict[str, list[int]]:
    """用文件大小和修改时间判断本地汇总缓存是否仍可用。"""
    files = list(ELECTRIC_DIR.glob("*.xlsx")) if ELECTRIC_DIR.exists() else []
    files += list(PV_DIR.rglob("*.xlsx")) if PV_DIR.exists() else []
    return {
        str(file.relative_to(ROOT)): [file.stat().st_size, file.stat().st_mtime_ns]
        for file in sorted(files)
    }


@st.cache_data(show_spinner="正在读取电表与光伏数据…")
def load_energy_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    """读取所有台账并返回日用电量、日光伏发电量、用电分类及异常文件。"""
    current_signature = source_signature()
    if LOCAL_CACHE.exists() and LOCAL_CACHE_META.exists():
        try:
            if json.loads(LOCAL_CACHE_META.read_text(encoding="utf-8")) == current_signature:
                cached = pd.read_pickle(LOCAL_CACHE)
                return cached["usage_daily"], cached["pv_daily"], cached["category_daily"], cached["problems"]
        except (OSError, ValueError, KeyError):
            pass

    usage_parts: list[pd.DataFrame] = []
    pv_parts: list[pd.DataFrame] = []
    problems: list[str] = []

    for file in sorted(ELECTRIC_DIR.glob("*.xlsx")) if ELECTRIC_DIR.exists() else []:
        try:
            raw = read_excel_columns(file, ["数据时间", "总电量(kWh)"])
            if raw.empty:
                problems.append(f"{file.name}：缺少数据时间或总电量列")
                continue
            raw["日期"] = pd.to_datetime(raw["数据时间"], errors="coerce")
            raw["累计电量"] = to_number(raw["总电量(kWh)"])
            raw = raw.dropna(subset=["日期", "累计电量"]).sort_values("日期")
            if raw.empty:
                continue
            # 同一时刻出现重复上报时取末条，累计表读数仅取正向增量。
            raw = raw.drop_duplicates("日期", keep="last")
            raw["用电量(kWh)"] = raw["累计电量"].diff().clip(lower=0).fillna(0)
            raw["日期"] = raw["日期"].dt.normalize()
            daily = raw.groupby("日期", as_index=False)["用电量(kWh)"].sum()
            daily["分类"] = classify_meter(file.name)
            daily["设备"] = re.sub(r"_0702-0804合并\.xlsx$", "", file.stem)
            usage_parts.append(daily)
        except Exception as exc:  # 单个文件异常不阻断整个仪表盘
            problems.append(f"{file.name}：{type(exc).__name__}")

    for file in sorted(PV_DIR.rglob("*.xlsx")) if PV_DIR.exists() else []:
        try:
            raw = read_excel_columns(file, ["数据更新时间", "日发电量(度)", "总发电量(度)"])
            if raw.empty:
                # 少数型号没有“日发电量”列，改用总发电量的相邻正向增量。
                raw = read_excel_columns(file, ["数据更新时间", "总发电量(度)"])
                if raw.empty:
                    problems.append(f"{file.name}：缺少发电量列")
                    continue
                raw["日期"] = pd.to_datetime(raw["数据更新时间"], errors="coerce")
                raw["累计发电量"] = to_number(raw["总发电量(度)"])
                raw = raw.dropna(subset=["日期", "累计发电量"]).sort_values("日期")
                raw = raw.drop_duplicates("日期", keep="last")
                raw["日发电量(kWh)"] = raw["累计发电量"].diff().clip(lower=0).fillna(0)
                raw["日期"] = raw["日期"].dt.normalize()
                daily = raw.groupby("日期", as_index=False)["日发电量(kWh)"].sum()
                daily["逆变器"] = file.stem
                pv_parts.append(daily)
                continue
            raw["日期"] = pd.to_datetime(raw["数据更新时间"], errors="coerce")
            raw["日发电量(kWh)"] = to_number(raw["日发电量(度)"])
            raw = raw.dropna(subset=["日期", "日发电量(kWh)"])
            # 日发电量为逆变器内的当日累计值，因此每台设备每天取最大读数。
            raw["日期"] = raw["日期"].dt.normalize()
            daily = raw.groupby("日期", as_index=False)["日发电量(kWh)"].max()
            daily["逆变器"] = file.stem
            pv_parts.append(daily)
        except Exception as exc:
            problems.append(f"{file.name}：{type(exc).__name__}")

    usage_detail = (
        pd.concat(usage_parts, ignore_index=True)
        if usage_parts
        else pd.DataFrame(columns=["日期", "用电量(kWh)", "分类", "设备"])
    )
    pv_detail = (
        pd.concat(pv_parts, ignore_index=True)
        if pv_parts
        else pd.DataFrame(columns=["日期", "日发电量(kWh)", "逆变器"])
    )
    usage_daily = usage_detail.groupby("日期", as_index=False)["用电量(kWh)"].sum()
    pv_daily = pv_detail.groupby("日期", as_index=False)["日发电量(kWh)"].sum()
    category_daily = usage_detail.groupby(["日期", "分类"], as_index=False)["用电量(kWh)"].sum()
    try:
        pd.to_pickle(
            {
                "usage_daily": usage_daily,
                "pv_daily": pv_daily,
                "category_daily": category_daily,
                "problems": problems,
            },
            LOCAL_CACHE,
        )
        LOCAL_CACHE_META.write_text(json.dumps(current_signature, ensure_ascii=False), encoding="utf-8")
    except OSError:
        # 缓存不可写时仍以本次计算结果渲染页面。
        pass
    return usage_daily, pv_daily, category_daily, problems


def recent_window(frame: pd.DataFrame, value_col: str, days: int | None) -> pd.DataFrame:
    if frame.empty or days is None:
        return frame.copy()
    endpoint = frame["日期"].max()
    start = endpoint - pd.Timedelta(days=days - 1)
    return frame.loc[frame["日期"] >= start].copy()


def chinese_date(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return "暂无数据"
    return pd.Timestamp(value).strftime("%Y年%m月%d日")


def make_line_chart(frame: pd.DataFrame, value_col: str, title: str, color: str, unit: str = "kWh") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame["日期"],
            y=frame[value_col],
            mode="lines+markers",
            line={"color": color, "width": 3},
            marker={"size": 6, "color": color},
            fill="tozeroy",
            fillcolor="rgba(22, 163, 74, 0.08)" if color == "#168a55" else "rgba(245, 130, 32, 0.09)",
            hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.1f} " + unit + "<extra></extra>",
        )
    )
    fig.update_layout(
        title={"text": title, "font": {"size": 16, "color": "#173d32"}, "x": 0.02, "xanchor": "left"},
        height=310,
        margin={"l": 12, "r": 12, "t": 54, "b": 12},
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",
        showlegend=False,
        xaxis={"showgrid": False, "tickformat": "%m-%d", "fixedrange": True},
        yaxis={"title": unit, "gridcolor": "#edf2ef", "zeroline": False, "fixedrange": True},
    )
    return fig


def metric_card(title: str, value: str, detail: str, accent: str) -> str:
    return f"""
    <div class='metric-card'>
      <div class='metric-label'>{title}</div>
      <div class='metric-value' style='color:{accent}'>{value}</div>
      <div class='metric-detail'>{detail}</div>
      <div class='metric-line' style='background:{accent}'></div>
    </div>
    """


st.markdown(
    """
    <style>
      .stApp { background: #f5f8f6; color: #173d32; }
      /* 隐藏 Streamlit 固定顶部栏，避免其覆盖仪表盘标题。 */
      header[data-testid='stHeader'] { display: none; }
      [data-testid='stAppViewContainer'] > .main { top: 0; }
      .block-container { max-width: 1600px; padding-top: 1.6rem; padding-bottom: 2rem; }
      [data-testid='stSidebar'] { background: linear-gradient(180deg, #0c6341 0%, #0a4933 100%); }
      [data-testid='stSidebar'] * { color: #f3fff9 !important; }
      [data-testid='stSidebar'] .stRadio label { padding: .16rem 0; }
      h1, h2, h3 { color: #143d30; }
      .dashboard-title { font-size: 29px; font-weight: 750; letter-spacing: .5px; color: #0c573a; margin: 0; }
      .dashboard-subtitle { color: #789187; margin-top: 4px; font-size: 14px; }
      .status-pill { display: inline-block; border: 1px solid #d7e9de; background: #f0faf4; color: #137349; padding: 8px 12px; border-radius: 9px; font-size: 13px; }
      .metric-card { background: #fff; border: 1px solid #e7efea; border-radius: 15px; padding: 18px 19px 13px; min-height: 128px; box-shadow: 0 3px 13px rgba(20, 64, 45, .055); position: relative; overflow: hidden; }
      .metric-label { color: #456257; font-size: 14px; font-weight: 600; }
      .metric-value { font-size: 28px; font-weight: 750; margin-top: 8px; letter-spacing: .2px; }
      .metric-detail { color: #82958b; font-size: 12px; margin-top: 7px; }
      .metric-line { height: 3px; width: 42px; border-radius: 8px; position: absolute; left: 19px; bottom: 13px; opacity: .85; }
      .section-card { background:#fff; border:1px solid #e7efea; border-radius:15px; padding:10px 12px; box-shadow: 0 3px 13px rgba(20, 64, 45, .04); height:100%; }
      .section-heading { color:#16583d; font-size:18px; font-weight:750; margin: 2px 5px 2px; }
      .section-note { color:#82958b; font-size:12px; margin: 0 5px 10px; }
      .insight-card { background:#fff; border:1px solid #e7efea; border-radius:15px; padding:19px; margin-bottom:14px; }
      .insight-title { color:#16583d; font-weight:750; font-size:17px; margin-bottom:12px; }
      .insight-row { display:flex; justify-content:space-between; gap:12px; border-bottom:1px solid #eef3ef; padding:9px 0; color:#496258; font-size:13px; }
      .insight-row:last-child { border-bottom:0; }
      .insight-value { color:#126940; font-weight:700; white-space:nowrap; }
      .stSelectbox div[data-baseweb='select'] > div { border-color:#dbe8df; background-color:#fff; }
      div[data-testid='stDataFrame'] { border:0; }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("## 🌿 绿城能源平台")
    st.caption("园区能源运营中心")
    st.divider()
    page = st.radio("导航", ["能源总览", "数据说明"], label_visibility="collapsed")
    st.divider()
    st.caption("数据源：项目目录中的电表数据与光伏数据")
    if st.button("刷新本地数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

usage_daily, pv_daily, category_daily, problems = load_energy_data()

if page == "数据说明":
    st.markdown("# 数据说明")
    st.info("仪表盘自动扫描项目下的 Excel 数据。点击侧边栏“刷新本地数据”可重新读取新增文件。")
    st.markdown("""
    - 用电量：每个电表的累计电量相邻读数差值，按天和设备分类汇总；负增量按 0 处理，以避免电表清零造成虚高。
    - 光伏发电量：各逆变器的“日发电量(度)”按天取最大值后汇总。
    - 两类源数据的采集周期不同，因此仪表盘分别展示用电与光伏曲线，不将不同日期的值直接相减。
    """)
    if problems:
        st.warning("部分文件未能读取：" + "；".join(problems[:8]))
    st.stop()

period_map = {"近 7 天": 7, "近 30 天": 30, "全部数据": None}

header_left, header_right = st.columns([4, 1])
with header_left:
    st.markdown("<p class='dashboard-title'>🌿 能源数据仪表台</p>", unsafe_allow_html=True)
    st.markdown("<p class='dashboard-subtitle'>示范区能源运行概览 · 电表与光伏逆变器实时台账</p>", unsafe_allow_html=True)
with header_right:
    selected_period = st.selectbox("统计周期", list(period_map), index=1, label_visibility="collapsed")
    newest = max(
        [frame["日期"].max() for frame in [usage_daily, pv_daily] if not frame.empty],
        default=None,
    )
    st.markdown(f"<div class='status-pill'>数据更新至 {chinese_date(newest)}</div>", unsafe_allow_html=True)

days = period_map[selected_period]
usage_view = recent_window(usage_daily, "用电量(kWh)", days)
pv_view = recent_window(pv_daily, "日发电量(kWh)", days)

usage_total = usage_view["用电量(kWh)"].sum() if not usage_view.empty else 0.0
pv_total = pv_view["日发电量(kWh)"].sum() if not pv_view.empty else 0.0
emission = pv_total * EMISSION_FACTOR_TON_PER_KWH

cards = st.columns(5)
for col, title, value, detail, accent in zip(
    cards,
    ["总用电量", "光伏发电量", "光伏自用率", "节约电费", "累计减排量"],
    [f"{usage_total:,.1f} kWh", f"{pv_total:,.1f} kWh", "—", "—", f"{emission:,.2f} 吨"],
    [f"{len(usage_view)} 个统计日", f"{len(pv_view)} 个统计日", "待接入上网电量数据", "待接入电价或结算数据", "按 0.581 kg/kWh 折算"],
    ["#137c4c", "#ef7e19", "#1768ba", "#c86b11", "#0b806e"],
):
    with col:
        st.markdown(metric_card(title, value, detail, accent), unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
main, right = st.columns([4.1, 1.25], gap="large")
with main:
    st.markdown("<div class='section-card'><div class='section-heading'>能源趋势</div><div class='section-note'>分别按各自最新数据日期倒推统计，单位：kWh</div>", unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2)
    with chart_left:
        if usage_view.empty:
            st.info("未发现可用的电表数据。")
        else:
            st.plotly_chart(make_line_chart(usage_view, "用电量(kWh)", "用电曲线", "#168a55"), use_container_width=True, config={"displayModeBar": False})
    with chart_right:
        if pv_view.empty:
            st.info("未发现可用的光伏数据。")
        else:
            st.plotly_chart(make_line_chart(pv_view, "日发电量(kWh)", "光伏发电曲线", "#ef7e19"), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='insight-card'><div class='insight-title'>运行摘要</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='insight-row'><span>接入电表</span><span class='insight-value'>{category_daily.shape[0] and len(list(ELECTRIC_DIR.glob('*.xlsx'))) or 0} 台</span></div>
        <div class='insight-row'><span>接入逆变器</span><span class='insight-value'>{len(list(PV_DIR.rglob('*.xlsx'))) if PV_DIR.exists() else 0} 台</span></div>
        <div class='insight-row'><span>用电数据周期</span><span class='insight-value'>{chinese_date(usage_daily['日期'].min() if not usage_daily.empty else None)} 起</span></div>
        <div class='insight-row'><span>光伏数据周期</span><span class='insight-value'>{chinese_date(pv_daily['日期'].min() if not pv_daily.empty else None)} 起</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='insight-card'><div class='insight-title'>节能建议</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#60756b;font-size:13px;line-height:1.8'>关注日用电峰值较高的设备分类；可将可转移负荷安排至光伏发电时段，提升清洁能源消纳。</div></div>", unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-card'><div class='section-heading'>分类用电概览</div><div class='section-note'>按电表文件名称自动归集；点击表头可排序</div>", unsafe_allow_html=True)
if category_daily.empty:
    st.info("暂无分类用电数据。")
else:
    category_view = category_daily.copy()
    if days is not None:
        cutoff = category_view["日期"].max() - pd.Timedelta(days=days - 1)
        category_view = category_view[category_view["日期"] >= cutoff]
    summary = category_view.groupby("分类", as_index=False)["用电量(kWh)"].sum().sort_values("用电量(kWh)", ascending=False)
    summary["占比"] = (
        summary["用电量(kWh)"] / summary["用电量(kWh)"].sum() * 100
        if summary["用电量(kWh)"].sum()
        else 0
    )
    summary["用电量(kWh)"] = summary["用电量(kWh)"].round(1)
    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
        column_config={"占比": st.column_config.ProgressColumn("占比", min_value=0, max_value=100, format="%.1f%%")},
    )
st.markdown("</div>", unsafe_allow_html=True)

if problems:
    st.caption("提示：部分数据文件未能解析，已跳过。可在“数据说明”查看详情。")
