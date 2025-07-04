import os
import glob
import pandas as pd
import numpy as np

# 경로 설정
csv_dir = "/mnt/c/Users/Admin/MATLAB/Projects/my_project/csv_results"
csv_path = os.path.join(csv_dir, "input_params.csv")
os.makedirs(csv_dir, exist_ok=True)

def find_closest_file(base_dir, variable, run_id):
    prefix = run_id[:13]  # 'YYYYMMDD_HHMM'
    pattern = os.path.join(base_dir, f"{variable}_{prefix}??_RID014.csv")
    candidates = glob.glob(pattern)
    if not candidates:
        return None
    return sorted(candidates)[0]

def extract_param_from_csv(path, valid_time, method="mean"):
    df = pd.read_csv(path, skiprows=1)
    t = df.iloc[:, 0].astype(float).values
    v = df.iloc[:, 1].astype(float).values
    idx = (t >= valid_time[0]) & (t <= valid_time[1])
    if not np.any(idx):
        return np.nan
    if method == "mean":
        return float(np.mean(v[idx]))
    elif method == "max":
        return float(np.max(v[idx]))
    elif method == "std":
        return float(np.std(v[idx]))
    return np.nan

# ✅ Backpressure 노이즈 추정값 계산 (정규화된 평균 편차)
def extract_backpr_noise(path, base_pressure=26.0, noise_std=0.7):
    df = pd.read_csv(path, skiprows=1)
    t = df.iloc[:, 0].astype(float).values
    v = df.iloc[:, 1].astype(float).values
    idx = (t >= backpr_noise_time[0]) & (t <= backpr_noise_time[1])
    if not np.any(idx):
        return np.nan
    mean_val = np.mean(v[idx])
    return float((mean_val - base_pressure) / noise_std)

def find_24bar_time(path, valid_time):
    df = pd.read_csv(path, skiprows=1)
    t = df.iloc[:, 0].astype(float).values
    v = df.iloc[:, 1].astype(float).values
    idx = (t >= valid_time[0]) & (t <= valid_time[1])
    t_window, v_window = t[idx], v[idx]
    if len(t_window) < 2 or max(v_window) < 24:
        return np.nan
    for i in range(1, len(v_window)):
        if v_window[i - 1] < 24 <= v_window[i]:
            t1, t2 = t_window[i - 1], t_window[i]
            v1, v2 = v_window[i - 1], v_window[i]
            return t1 + (24 - v1) * (t2 - t1) / (v2 - v1)
    return np.nan

# 유효 시간대 설정
inject_valid_time = (5.6, 5.8)
backpr_noise_time = (0.0, 2.02)  # Backpr_amp 기준 시간대
retract_valid_time = (2.0, 2.6)
nozzle_valid_time = (5.6, 8.5)

# run_id 추출
input_list = sorted(glob.glob(os.path.join(csv_dir, "Inject_*_RID014.csv")))
run_ids = [os.path.basename(f).split("_", 1)[1].replace(".csv", "") for f in input_list]

inject_list, backpr_list, retract_list, nozzle_list = [], [], [], []
valid_ids = []

for run_id in run_ids:
    inject_path = find_closest_file(csv_dir, "Inject", run_id)
    backpr_path = find_closest_file(csv_dir, "Backpr", run_id)
    retract_path = find_closest_file(csv_dir, "Retract", run_id)
    nozzle_path = find_closest_file(csv_dir, "Nozzle", run_id)

    if not all([inject_path, backpr_path, retract_path, nozzle_path]):
        print(f"⚠️ 누락된 파일로 인해 제외됨: {run_id}")
        continue

    inject_val = extract_param_from_csv(inject_path, inject_valid_time, method="mean")
    backpr_val = extract_backpr_noise(backpr_path)

    # Retract_delay (보간 → 실패 시 fallback to max)
    retract_24 = find_24bar_time(retract_path, retract_valid_time)
    if not np.isnan(retract_24):
        retract_val = retract_24 - 2.06
    else:
        retract_val = extract_param_from_csv(retract_path, retract_valid_time, method="max")

    # Nozzle_delay (보간 → 실패 시 fallback to max)
    nozzle_24 = find_24bar_time(nozzle_path, nozzle_valid_time)
    if not np.isnan(nozzle_24):
        nozzle_val = nozzle_24 - 5.64
    else:
        nozzle_val = extract_param_from_csv(nozzle_path, nozzle_valid_time, method="max")

    if any(pd.isna([inject_val, backpr_val, retract_val, nozzle_val])):
        print(f"⚠️ NaN 발생으로 제외됨: {run_id}")
        continue

    inject_list.append(inject_val)
    backpr_list.append(backpr_val)
    retract_list.append(retract_val)
    nozzle_list.append(nozzle_val)
    valid_ids.append(run_id)

df_new = pd.DataFrame({
    "run_id": valid_ids,
    "Inject": inject_list,
    "Backpr_amp": backpr_list,
    "Retract_delay": retract_list,
    "Nozzle_delay": nozzle_list
})

def compute_bin_label(row):
    inject_bins = np.linspace(10.0, 30.0, 21)
    backpr_bins = np.linspace(-2.0, 2.0, 21)
    retract_bins = np.linspace(0.0, 0.5, 21)
    nozzle_bins = np.linspace(0.0, 1.0, 21)

    inject_bin = np.digitize(row["Inject"], inject_bins) - 1
    backpr_bin = np.digitize(row["Backpr_amp"], backpr_bins) - 1
    retract_bin = np.digitize(row["Retract_delay"], retract_bins) - 1
    nozzle_bin = np.digitize(row["Nozzle_delay"], nozzle_bins) - 1

    inject_bin = np.clip(inject_bin, 0, 19)
    backpr_bin = np.clip(backpr_bin, 0, 19)
    retract_bin = np.clip(retract_bin, 0, 19)
    nozzle_bin = np.clip(nozzle_bin, 0, 19)

    return f"I{inject_bin}_B{backpr_bin}_R{retract_bin}_N{nozzle_bin}"

df_new["bin_label"] = df_new.apply(compute_bin_label, axis=1)
df_new.to_csv(csv_path, index=False)
print("✅ input_params.csv 라벨링 포함 완료.")
