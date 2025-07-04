import pandas as pd
import numpy as np
import os

# 기존 input_params.csv 경로
csv_dir = "/mnt/c/Users/Admin/MATLAB/Projects/my_project/csv_results"
csv_path = os.path.join(csv_dir, "input_params.csv")

# 로딩
df = pd.read_csv(csv_path)

# 각 변수별 이산화 기준 (20개 구간 기준, right=False로 지정)
inject_bins = np.linspace(10.0, 30.0, 21)
backpr_bins = np.linspace(-2.0, 2.0, 21)
retract_bins = np.linspace(0.0, 0.5, 21)
nozzle_bins = np.linspace(0.0, 1.0, 21)

# bin index 추출 및 클리핑
inject_bin = np.clip(np.digitize(df["Inject"], inject_bins, right=False) - 1, 0, 19)
backpr_bin = np.clip(np.digitize(df["Backpr_amp"], backpr_bins, right=False) - 1, 0, 19)
retract_bin = np.clip(np.digitize(df["Retract_delay"], retract_bins, right=False) - 1, 0, 19)
nozzle_bin = np.clip(np.digitize(df["Nozzle_delay"], nozzle_bins, right=False) - 1, 0, 19)

# bin label 생성
df["bin_label"] = [f"I{i}_B{b}_R{r}_N{n}" for i, b, r, n in zip(inject_bin, backpr_bin, retract_bin, nozzle_bin)]

# 저장
df.to_csv(csv_path, index=False)
print(f"✅ Updated CSV with bin_label saved to: {csv_path}")

