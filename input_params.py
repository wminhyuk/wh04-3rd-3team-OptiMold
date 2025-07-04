# generate_input_params.py

import pandas as pd
import os
import glob
import re
import numpy as np

# [1] 경로 설정
csv_dir = "/mnt/c/Users/Admin/MATLAB/Projects/my_project/csv_results"
save_path = os.path.join(csv_dir, "input_params.csv")
os.makedirs(csv_dir, exist_ok=True)

# [2] run_id 그룹핑 (분 단위로 식별)
pattern = re.compile(r"_(\d{8})_(\d{6})_RID014")
run_id_map = {}
all_files = glob.glob(os.path.join(csv_dir, "*.csv"))
for f in all_files:
    match = pattern.search(os.path.basename(f))
    if match:
        date, time = match.groups()
        run_id = f"{date}_{time[:4]}_RID014"
        run_id_map.setdefault(run_id, []).append(f)

# [3] 입력값 추출
records = []
for run_id, files in run_id_map.items():
    entry = {"run_id": run_id}
    try:
        # Inject
        inject_file = next((f for f in files if "inject" in f.lower()), None)
        if inject_file:
            inject_df = pd.read_csv(inject_file)
            entry["Inject"] = inject_df.iloc[:, 1].max()

        # Backpr_amp
        backpr_file = next((f for f in files if "backpr" in f.lower()), None)
        if backpr_file:
            backpr_df = pd.read_csv(backpr_file)
            amp = backpr_df.iloc[:, 1].max() - backpr_df.iloc[:, 1].min()
            entry["Backpr_amp"] = min(amp, 2.0)  # clip

        # Retract_delay
        retract_file = next((f for f in files if "retract" in f.lower()), None)
        if retract_file:
            retract_df = pd.read_csv(retract_file)
            signal = retract_df.iloc[:, 1]
            delay_index = signal[signal > 0].index.min()
            delay_time = retract_df.iloc[delay_index, 0]
            entry["Retract_delay"] = max(delay_time - 2.06, 0)

        # Nozzle_delay
        nozzle_file = next((f for f in files if "nozzle" in f.lower()), None)
        if nozzle_file:
            nozzle_df = pd.read_csv(nozzle_file)
            signal = nozzle_df.iloc[:, 1]
            delay_index = signal[signal > 0].index.min()
            delay_time = nozzle_df.iloc[delay_index, 0]
            entry["Nozzle_delay"] = np.clip(delay_time - 2.0, 0, 1.5)

        # 조건 충족 시 추가
        if len(entry) == 5:
            records.append(entry)
    except Exception:
        continue

# [4] CSV 저장
df = pd.DataFrame(records)
df.to_csv(save_path, index=False)
print(f"[✓] Saved {len(df)} entries to {save_path}")
