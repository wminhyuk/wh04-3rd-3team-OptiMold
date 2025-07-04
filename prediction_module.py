import numpy as np
import pandas as pd
import os
import glob
import re

# [1] 시뮬레이션 결과 파일 로딩
def load_selected_files(base_dir, max_per_var=200):
    variables = [
        "Backpr", "Extruder", "Flow_Rate", "Inject", "Nozzle",
        "Piston_Position", "Piston_Pressure", "Piston_Velocity", "Retract", "Volume"
    ]
    pattern = re.compile(r"_(\d{8})_(\d{6})_RID014")
    selected_files = {var: [] for var in variables}
    all_csvs = glob.glob(os.path.join(base_dir, "*.csv"))

    for var in variables:
        var_files = [f for f in all_csvs if var.lower() in os.path.basename(f).lower() and "RID014" in f]
        var_files_sorted = sorted(var_files)
        selected_files[var] = var_files_sorted[:max_per_var]

    run_ids = []
    for f in selected_files["Inject"]:
        fname = os.path.basename(f)
        match = pattern.search(fname)
        if match:
            date, time = match.groups()
            run_id = f"{date}_{time[:4]}_RID014"
            run_ids.append(run_id)
    return selected_files, run_ids

# [2] 이산화된 입력 매개변수 로딩
def load_input_params_with_binlabel(csv_path):
    df = pd.read_csv(csv_path)
    return df  # bin_label 포함되어 있어야 함

# [3] 입력값과 가장 유사한 bin_label 매칭
def find_closest_bin_match(input_vec, df):
    # 각 변수별 bin 기준 정의
    inject_bins = np.linspace(10.0, 30.0, 21)
    backpr_bins = np.linspace(-2.0, 2.0, 21)
    retract_bins = np.linspace(0.0, 0.5, 21)
    nozzle_bins = np.linspace(0.0, 1.0, 21)

    inject_bin = np.digitize(input_vec[0], inject_bins, right=False) - 1
    backpr_bin = np.digitize(input_vec[1], backpr_bins, right=False) - 1
    retract_bin = np.digitize(input_vec[2], retract_bins, right=False) - 1
    nozzle_bin = np.digitize(input_vec[3], nozzle_bins, right=False) - 1

    # 클리핑 (경계 바깥일 경우)
    inject_bin = np.clip(inject_bin, 0, 19)
    backpr_bin = np.clip(backpr_bin, 0, 19)
    retract_bin = np.clip(retract_bin, 0, 19)
    nozzle_bin = np.clip(nozzle_bin, 0, 19)

    bin_label = f"I{inject_bin}_B{backpr_bin}_R{retract_bin}_N{nozzle_bin}"
    return bin_label

# [4] 시계열 데이터 로딩
def load_time_series(run_index, selected_files):
    data = {}
    for var, file_list in selected_files.items():
        if run_index < len(file_list):
            df = pd.read_csv(file_list[run_index])
            data[var] = df
    return data
