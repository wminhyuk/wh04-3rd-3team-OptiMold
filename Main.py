import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import re
from PIL import Image, ImageDraw
import numpy as np
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="OptiMold 공정 제어 및 분석", layout="wide")

# 해당 카테고리별 탭 구성
tabs = st.tabs(["Main", "Monitoring", "Analysis", "Causality", "Anomaly Detection", "Process Prediction"])

# 해당 페이지


# 1. Main
with tabs[0]:
    st.title(":factory: OptiMold 공정 시뮬레이션 제어")

    st.subheader("Airflow 상태 확인")
    airflow_url = "http://localhost:8080/dags/generate_mat_and_simulate_dag_v14/grid?num_runs=365"
    st.markdown(f"[Airflow Web UI 열기]({airflow_url})")
    st.info("Airflow UI에서는 DAG 상태, 실행 이력, 로그 등을 직접 확인할 수 있습니다.")

    st.markdown("---")
    st.subheader("🧭 공정 HMI 시각화")
    st.markdown("Simulink 기반 사출 성형 공정을 시각적으로 표현합니다.")

    st.subheader("🖱️ 센서 위치 클릭")
    st.markdown("센서가 배치된 영역을 클릭하면 해당 위치의 설명이 표시됩니다.")
    
    st.text("")

    import os
    from PIL import Image, ImageDraw
    from streamlit_image_coordinates import streamlit_image_coordinates

    display_width = 800
    base_path = os.path.join("hmi_base", "fifth_real_model.png")
    base_img = Image.open(base_path).convert("RGB")
    original_width, _ = base_img.size
    scale_ratio = display_width / original_width

    # 센서 좌표 정의 (제어 입력 5 + 공정 출력 5, 각각 2구역씩)
    sensor_boxes = {
        "Extruder": {"coords": [(200, 80, 250, 110), (470, 400, 490, 420)], "color": "purple"},
        "Retract":  {"coords": [(200, 120, 250, 150), (470, 425, 490, 445)], "color": "red"},
        "Inject":   {"coords": [(200, 160, 250, 190), (470, 450, 490, 470)], "color": "green"},
        "Backpr":   {"coords": [(200, 200, 250, 230), (470, 475, 490, 495)], "color": "orange"},
        "Nozzle":   {"coords": [(200, 240, 250, 270), (470, 500, 490, 520)], "color": "blue"},
        "Piston_Position":  {"coords": [(635, 385, 655, 400)], "color": "deeppink"},
        "Piston_Pressure":  {"coords": [(635, 405, 655, 420)], "color": "crimson"},
        "Piston_Velocity":     {"coords": [(635, 425, 655, 440)], "color": "limegreen"},
        "Volume":  {"coords": [(635, 480, 655, 500)], "color": "gold"},
        "Flow_Rate":      {"coords": [(635, 505, 655, 525)], "color": "dodgerblue"},
    }

    # 이미지에 박스 표시
    draw = ImageDraw.Draw(base_img)
    for props in sensor_boxes.values():
        for box in props["coords"]:
            x1, y1, x2, y2 = box
            x1 = int(x1 / scale_ratio)
            y1 = int(y1 / scale_ratio)
            x2 = int(x2 / scale_ratio)
            y2 = int(y2 / scale_ratio)
            draw.rectangle((x1, y1, x2, y2), outline=props["color"], width=3)

    # 좌우 배치
    col_img, col_legend = st.columns([4, 1])
    with col_img:
        coords = streamlit_image_coordinates(base_img, width=display_width, key="main_hmi_img")

    with col_legend:
        st.markdown("#### 🎯 센서 색상 정보")
        for sensor, props in sensor_boxes.items():
            st.markdown(
                f"<span style='color:{props['color']}; font-weight:bold'>■</span> {sensor}",
                unsafe_allow_html=True
            )

    # 클릭된 센서 매핑
    if coords:
        x, y = coords["x"], coords["y"]
        st.markdown(f"**클릭된 좌표**: ({x}, {y})")

        if (200 <= x <= 250 and 80 <= y <= 110) or (470 <= x <= 490 and 400 <= y <= 420):
            st.subheader("🔍 Extruder 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(os.path.join("hmi_base", "Extruder.png"), caption="모델 내 Extruder 센서 상세", width=display_width//2)
            with col2:    
                st.image(os.path.join("hmi_base", "Extruder_Drive.png"), caption="모델 내 Extruder 구동부 상세", width=display_width//2)
            st.image(os.path.join("hmi_base", "System_Extruder.jpg"), caption="시스템 내 Extruder 위치 상세", width=display_width)
            st.info("원료 투입을 제어하는 스크류 구동 영역입니다.")

        elif (200 <= x <= 250 and 120 <= y <= 150) or (470 <= x <= 490 and 425 <= y <= 445):
            st.subheader("🔍 Retract 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(os.path.join("hmi_base", "Retract.png"), caption="모델 내 Retract 센서 상세", width=display_width//2)
            st.image(os.path.join("hmi_base", "System_Retract.jpg"), caption="시스템 내 Retract 위치 상세", width=display_width)     
            st.info("금형 개방 전 이동 위치를 제어하는 센서입니다.")

        elif (200 <= x <= 250 and 160 <= y <= 190) or (470 <= x <= 490 and 450 <= y <= 470):
            st.subheader("🔍 Inject 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(os.path.join("hmi_base", "Inject.png"), caption="모델 내 Inject 센서 상세", width=display_width//2)
            with col2:    
                st.image(os.path.join("hmi_base", "Inject_Drive.png"), caption="모델 내 Inject 구동부 상세", width=display_width//2)
            st.image(os.path.join("hmi_base", "System_Inject.jpg"), caption="시스템 내 Inject 위치 상세", width=display_width)
            st.info("사출 실린더에 유압을 인가하는 제어 밸브 영역입니다.")

        elif (200 <= x <= 250 and 200 <= y <= 230) or (470 <= x <= 490 and 475 <= y <= 495):
            st.subheader("🔍 Backpr 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(os.path.join("hmi_base", "Backpr.png"), caption="모델 내 Backpr 센서 상세", width=display_width//2)
            st.image(os.path.join("hmi_base", "System_Backpr.jpg"), caption="시스템 내 Backpr 위치 상세", width=display_width)
            st.info("백압 조절을 위한 회귀 제어 밸브 위치입니다.")

        elif (200 <= x <= 250 and 240 <= y <= 270) or (470 <= x <= 490 and 500 <= y <= 520):
            st.subheader("🔍 Nozzle 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(os.path.join("hmi_base", "Nozzle.png"), caption="모델 내 Nozzle 센서 상세", width=display_width//2)
            st.image(os.path.join("hmi_base", "System_Nozzle.jpg"), caption="시스템 내 Nozzle 위치 상세", width=display_width)
            st.info("노즐 개방 상태를 감지하는 밸브 제어 센서 위치입니다.")

        elif (635 <= x <= 655 and 385 <= y <= 400):
            st.subheader("🔍 Piston_Position 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1:            
                st.image(os.path.join("hmi_base", "Piston_Position.png"), caption="Piston_Position 센서 상세")
            st.info("Piston_Position 센서는 피스톤의 위치를 감지하여 공정 상태를 모니터링합니다.")

        elif (635 <= x <= 655 and 405 <= y <= 420):
            st.subheader("🔍 Piston_Pressure 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1: 
                st.image(os.path.join("hmi_base", "Piston_Pressure.png"), caption="Piston_Pressure 센서 상세")
            st.info("Piston_Pressure 센서는 피스톤의 압력을 측정하여 공정의 압력 상태를 모니터링합니다.")

        elif (635 <= x <= 655 and 425 <= y <= 440):
            st.subheader("🔍 Piston_Velocity 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1: 
                st.image(os.path.join("hmi_base", "Piston_Velocity.png"), caption="Piston_Velocity 센서 상세")
            st.info("Piston_Velocity 센서는 피스톤의 속도를 측정하여 공정의 속도 상태를 모니터링합니다.")

        elif (635 <= x <= 655 and 480 <= y <= 500):
            st.subheader("🔍 Volume 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(os.path.join("hmi_base", "Volume.png"), caption="Volume 센서 상세")
            st.info("Volume 센서는 금형 내의 물질 부피를 측정하여 공정의 물질 흐름 상태를 모니터링합니다.")

        elif (635 <= x <= 655 and 505 <= y <= 525):
            st.subheader("🔍 Flow_Rate 센서 위치")
            col1, col2, col3 = st.columns(3)
            with col1: 
                st.image(os.path.join("hmi_base", "Flow_Rate.png"), caption="Flow_Rate 센서 상세")
            st.info("Flow_Rate 센서는 금형 내의 유량을 측정하여 공정의 흐름 상태를 모니터링합니다.")

        else:
            st.warning("등록된 센서 좌표가 아닙니다. 필요시 좌표 범위를 확장하세요.")


# 2. Monitoring
with tabs[1]:
    st.header("📊 Simulation Monitoring")
    st.markdown("시뮬레이션 진행 상황 및 최근 실행 결과를 확인할 수 있습니다.")

    st.subheader("📋 최근 실행 통계")
    import re

    log_dir = "/mnt/c/Users/Admin/MATLAB/Projects/my_project/csv_results"
    variables = ["Inject", "Backpr", "Piston_Pressure", "Piston_Position"]
    expected_files = 4
    recent_minutes = 10

    csv_files = glob.glob(os.path.join(log_dir, "*.csv"))

    # 시계열 태그 매핑
    tag_map = {}
    pattern = re.compile(r"_(\d{8})_(\d{6})")

    for f in csv_files:
        fname = os.path.basename(f)
        match = pattern.search(fname)
        if match:
            ymd = match.group(1)
            hms = match.group(2)
            tag = f"{ymd}_{hms[:4]}"  # YYYYMMDD_HHMM
            tag_map.setdefault(tag, []).append(fname)

    # 가장 최근 태그로부터 1분씩 감소
    if tag_map:
        latest_tag = sorted(tag_map.keys(), reverse=True)[0]
        base_dt = datetime.strptime(latest_tag, "%Y%m%d_%H%M")
        recent_tags = [(base_dt - timedelta(minutes=i)).strftime("%Y%m%d_%H%M") for i in range(recent_minutes)]
    else:
        recent_tags = []

    success, fail = 0, 0
    for tag in recent_tags:
        match_count = 0
        files = tag_map.get(tag, [])
        for var in variables:
            if any(fname.startswith(var) for fname in files):
                match_count += 1
        if match_count >= 3:
            st.success(f"✅ [{tag}] 공정이 정상적으로 진행되었습니다.")
            success += 1
        else:
            st.error(f"❌ [{tag}] 공정 실패: 시계열 누락 감지됨")
            fail += 1

    st.metric("최근 10회 기준 성공 횟수", success)
    st.metric("최근 10회 기준 실패 횟수", fail)

    st.markdown("---")
    st.subheader("🧮 전체 사이클 기준 성공/실패 시각화")

    rid_pattern = re.compile(r"_(\d{8})_(\d{6})_RID014")
    variables = ["Inject", "Backpr", "Piston_Pressure", "Piston_Position"]

    # 변수별 성공 tag 수집
    success_tags_by_var = {var: set() for var in variables}
    filtered_files = [f for f in os.listdir(log_dir) if f.endswith(".csv") and "RID014" in f]

    for f in filtered_files:
        match = rid_pattern.search(f)
        if match:
            ymd, hms = match.groups()
            tag = f"{ymd}_{hms[:4]}"  # YYYYMMDD_HHMM
            for var in variables:
                if f.startswith(var):
                    success_tags_by_var[var].add(tag)

    # 각 변수별 성공 개수 출력 (디버깅 목적)
    st.markdown("##### ✅ 변수별 성공 파일 개수:")
    for var in variables:
        st.markdown(f"- `{var}` 성공 파일 개수: {len(success_tags_by_var[var])}")

    # 전체 성공 판단 로직
    tag_sets = list(success_tags_by_var.values())
    common_tags = set.intersection(*tag_sets)
    all_tags = set.union(*tag_sets)

    success_count = len(common_tags)
    ambiguous_tags = []

    for tag in all_tags - common_tags:
        match_count = sum(tag in tag_set for tag_set in tag_sets)
        if match_count >= 3:
            success_count += 1
        elif match_count <= 2:
            ambiguous_tags.append((tag, match_count))

    total_expected = 120
    fail_count = total_expected - success_count

    st.metric("전체 기준 성공", success_count)
    st.metric("전체 기준 실패", fail_count)

    # 경고 메시지
    if ambiguous_tags:
        st.warning("⚠️ 다음 사이클에서 2개 이하의 시계열만 탐지되었습니다 (공정 누락 의심):")
        for tag, cnt in ambiguous_tags:
            st.write(f"- [{tag}] ({cnt}/4)")

    # 반원 그래프 시각화 (크기 작고 정렬 고정)
    fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
    ax.set_title("Success vs Fail")
    wedges, texts, autotexts = ax.pie(
        [success_count, fail_count],
        labels=["Success", "Fail"],
        autopct="%1.1f%%",
        startangle=180,
        counterclock=False,
        textprops=dict(fontsize=8),
    )
    plt.setp(autotexts, size=9, weight="bold")
    st.pyplot(fig, use_container_width=False)
    
# 3. Analysis
with tabs[2]:
    st.title(":mag: 공정 데이터 분석")
    st.markdown("""
    - 시뮬레이션 결과 데이터의 시계열 및 KDE 기반 정밀 분석을 제공합니다.
    - 제어 입력 ↔ 공정 출력 간의 상관성 탐색 및 분포 시각화 포함.
    """)
    st.text("")
    st.text("")
    st.subheader("Extruder 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Extruder_R007.png"), width=display_width)

    st.subheader("Retract 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Retract_R007.png"), width=display_width)

    st.subheader("Inject 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Inject_R007.png"), width=display_width)

    st.subheader("Backpr 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Backpr_R007.png"), width=display_width)

    st.subheader("Nozzle 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Nozzle_R007.png"), width=display_width)

    st.subheader("Piston Position 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Piston_Position_R007.png"), width=display_width)

    st.subheader("Piston Pressure 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Piston_Pressure_R007.png"), width=display_width)

    st.subheader("Piston Velocity 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Piston_Pressure_R007(1).png"), width=display_width)
    st.image(os.path.join("Anal_base", "Piston_Velocity_R007.png"), width=display_width)

    st.subheader("Flow Rate 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Flow_Rate_R007.png"), width=display_width)

    st.subheader("Volume 시계열 데이터 분석")
    st.image(os.path.join("Anal_base", "Volume_R007.png"), width=display_width)
    


# 4. Causality
with tabs[3]:
    st.title(":link: Granger Causality 분석")
    st.markdown("""
    - 제어 입력과 공정 출력 사이의 시계열 인과관계인 Granger Causality를 분석합니다.
    - 네트워크 시각화 및 테이블 형태의 요약 결과를 제공합니다.
    """)
    st.text("")
    st.image(os.path.join("GS_base", "GS_Network.png"), width=display_width)
    st.text("")
    st.image(os.path.join("GS_base", "GS_Total.png"), width=display_width)
    st.image(os.path.join("GS_base", "GS_Piston_Position.png"), width=display_width)
    st.image(os.path.join("GS_base", "GS_Piston_Pressure.png"), width=display_width)
    st.image(os.path.join("GS_base", "GS_Piston_Velocity.png"), width=display_width)
    st.image(os.path.join("GS_base", "GS_Flow_Rate.png"), width=display_width)
    st.image(os.path.join("GS_base", "GS_Volume.png"), width=display_width)



# 5. Anomaly Detection
with tabs[4]:
    st.title(":crystal_ball: 이상 탐지 및 예측")

    st.markdown("### 🔍 이상 시나리오 분포 요약")

    # CSV 로드
    csv_path = "/mnt/c/Users/Admin/MATLAB/Projects/my_project/classified_scenarios_012.csv"
    df = pd.read_csv(csv_path)

    # 정상 / 이상 구분
    df["result"] = df["scenario"].apply(lambda x: "Success" if x == "Normal" else "Fail")
    result_counts = df["result"].value_counts()
    success_count = result_counts.get("Success", 0)
    fail_count = result_counts.get("Fail", 0)

    # 시나리오 비율 계산
    scenario_counts = df["scenario"].value_counts(normalize=True) * 100

    # 📊 그래프 2:1 레이아웃 구성
    col1, col2 = st.columns([2, 1])

    with col1:
        fig2, ax2 = plt.subplots()
        ax2.pie(scenario_counts, labels=scenario_counts.index, autopct="%1.1f%%", textprops={"fontsize": 8})
        ax2.set_title("Anomaly Scenario Distribution")
        st.pyplot(fig2)

    with col2:
        fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
        wedges, texts, autotexts = ax.pie(
            [success_count, fail_count],
            labels=["Normal", "Anomalous"],
            autopct="%1.1f%%",
            startangle=180,
            counterclock=False,
            textprops=dict(fontsize=8),
        )
        plt.setp(autotexts, size=9, weight="bold")
        ax.set_title("Normal vs Anomalous")
        st.pyplot(fig, use_container_width=False)
    
    st.text("")
    st.text("")

    # 📘 시나리오 설명 출력 (설명 + 판정 기준 포함)
    st.text("")
    scenario_desc = {
        "Normal": "공정 출력이 모두 정상 범위 내에 있어 양품으로 판정됨.",
        "Short shot": (
            "충진 부족으로 인해 부품 일부가 비어 있거나 형상이 완성되지 않음.  \n"
            "- **판정 기준**: 최대 충진량(Volume_max) < 45"
        ),
        "Overpacking / Flash": (
            "압력이 과도하거나 피스톤 과이동으로 인해 금형 틈새로 수지가 누출됨.  \n"
            "- **판정 기준**: 최대 충진량(Volume_max) > 55"
        ),
        "Sticking / Slip - Late velocity stall": (
            "보압 시작 이후 피스톤의 속도가 비정상적으로 정지되거나 불안정하게 유지됨.  \n"
            "- **판정 기준**: 피스톤 속도 구간 flat ratio (6초 이후) < 0.9"
        ),
        "Jetting - High flow surge": (
            "충진 초기에 과도한 유량이 짧은 시간 급격히 변화하면서 외관 불량 가능성이 존재함.  \n"
            "- **판정 기준**: Flow Rate 변화 기울기 강도가 0.6초 이상 지속"
        ),
        "Sink mark - Velocity stalled during packing end": (
            "보압 종료 시점 이후 피스톤 속도가 멈추어 냉각 수축에 따른 수축 자국(sink mark)이 발생할 수 있음.  \n"
            "- **판정 기준**: 8초 이후 피스톤 속도 flat 상태 지속시간 > 1.95초"
        )
    }

    st.markdown("### 🧠 이상 시나리오 설명")
    for label, desc in scenario_desc.items():
        st.markdown(f"**🟢 {label}**: {desc}")

# 6. Prediction
from prediction_module import (
    load_input_params_with_binlabel,
    load_selected_files,
    find_closest_bin_match,
    load_time_series
)


def parse_bin_label(label):
    # 예: "I7_B1_R0_N13" → [7, 1, 0, 13]
    return list(map(int, re.findall(r'\d+', label)))

def find_top_k_similar_bins(input_bin, df, k=3):
    input_vec = parse_bin_label(input_bin)
    df["bin_vec"] = df["bin_label"].apply(parse_bin_label)
    df["distance"] = df["bin_vec"].apply(lambda x: sum(abs(a - b) for a, b in zip(x, input_vec)))
    return df.nsmallest(k, "distance")

with tabs[5]:
    st.title(":crystal_ball: 공정 예측")
    st.markdown("""
    - 사용자가 입력한 제어 입력값에 가장 유사한 시뮬레이션 결과를 기반으로 공정 출력 시계열을 시각화합니다.
    - 아래 Test Run에서는 사용자가 제어 입력값을 직접 지정할 수 있습니다.
    """)

    st.text("")
    st.subheader("🧪 Test Run: 단일 공정 입력값 설정")

    with st.form("test_run_input_form"):
        st.markdown("**Inject Pressure Peak (bar)**")
        inject_peak = st.slider("Inject 피크압력", 10.0, 30.0, 17.5, step=1.0)

        st.markdown("**Backpressure Noise Amplitude (σ , ± bar)**")
        backpr_amp = st.slider("표준편차 0.7 기반 백프레셔 노이즈 범위", -2.0, 2.0, 0.0, step=0.2)

        st.markdown("**Retract Delay (초)**")
        retract_delay = st.slider("Retract 지연 시간", 0.00, 0.50, 0.20, step=0.02)

        st.markdown("**Nozzle Open Delay (초)**")
        nozzle_delay = st.slider("노즐 지연 시간", 0.00, 1.00, 0.30, step=0.05)

        run_id = st.text_input("Run ID", value="Test001")

        submitted = st.form_submit_button("입력값 기반 공정 예측")
        if submitted:
            st.cache_data.clear()
            st.success(f"입력값 저장 완료 (Run ID: {run_id})")

            csv_dir = "/mnt/c/Users/Admin/MATLAB/Projects/my_project/csv_results"
            input_path = os.path.join(csv_dir, "input_params.csv")

            selected_files, _ = load_selected_files(csv_dir)
            df = load_input_params_with_binlabel(input_path)

            input_vec = [inject_peak, backpr_amp, retract_delay, nozzle_delay]
            bin_label = find_closest_bin_match(input_vec, df)

            st.markdown("🧩 **입력값 벡터:**")
            st.json(dict(zip(["Inject", "Backpr_amp", "Retract_delay", "Nozzle_delay"], input_vec)))
            st.markdown(f"📌 매칭된 이산화 bin_label: `{bin_label}`")

            matched_rows = df[df["bin_label"] == bin_label]

            if matched_rows.empty:
                st.error("해당 입력값의 bin_label과 정확히 일치하는 공정이 없습니다.")

                st.markdown("🔍 **가장 유사한 공정을 탐색합니다:**")
                similar = find_top_k_similar_bins(bin_label, df, k=3)

                # 유사도 기준 경고
                if similar["distance"].min() > 5:
                    st.warning("⚠️ 매우 유사한 공정이 존재하지 않을 수 있습니다. 입력값을 재조정해보세요.")

                for idx, row in similar.iterrows():
                    st.markdown(f"- `{row['run_id']}` ({row['bin_label']}) → 거리: {row['distance']}")

                if not similar.empty:
                    chosen = similar.iloc[0]
                    run_index = df[df["run_id"] == chosen["run_id"]].index[0]
                    time_series = load_time_series(run_index, selected_files)

                    st.markdown("🧩 **해당 run 입력값:**")
                    for col in ["Inject", "Backpr_amp", "Retract_delay", "Nozzle_delay"]:
                        st.markdown(f"• **{col}**: {chosen[col]:.3f}")

                    for var, df_ts in time_series.items():
                        st.subheader(f"📊 {var}")
                        st.line_chart(df_ts.iloc[:, 1] if df_ts.shape[1] == 2 else df_ts.iloc[:, 0])

            else:
                st.success("정확히 일치하는 공정이 발견되었습니다.")

                for idx, row in matched_rows.iterrows():
                    st.markdown(f"- `{row['run_id']}`")

                run_index = df[df["run_id"] == matched_rows.iloc[0]["run_id"]].index[0]
                time_series = load_time_series(run_index, selected_files)

                st.markdown("🧩 **해당 run 입력값:**")
                for col in ["Inject", "Backpr_amp", "Retract_delay", "Nozzle_delay"]:
                    st.markdown(f"• **{col}**: {matched_rows.iloc[0][col]:.3f}")

                for var, df_ts in time_series.items():
                    st.subheader(f"📊 {var}")
                    st.line_chart(df_ts.iloc[:, 1] if df_ts.shape[1] == 2 else df_ts.iloc[:, 0])


