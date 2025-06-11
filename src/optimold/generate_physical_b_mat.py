# src/optimold/generate_physical_mat.py

import numpy as np
from scipy.io import savemat
from datetime import datetime
import os

def generate_mat(seed=None, run_id=None):
    """
    분포 기반 이상치가 반영된 사출 성형용 .mat 파일 생성 함수
    run_id: 사용자가 지정하는 고유 ID (예: 001, testA, cycle3 등)
    - inject_data: 정규분포 기반 압력 저하
    - backpr_data: ±0.7 bar 저주파 진동 노이즈
    - retract_data: 지연 offset (지수분포), 시간 순서 보장
    - nozzle_data: 지연 offset + 10% 개방 실패 확률
    - extruder_data: 고정값

    저장 경로: /mnt/c/Users/Admin/MATLAB/Projects/my_project/cycle_results
    """
    if seed is not None:
        np.random.seed(seed)

    win_path = "/mnt/c/Users/Admin/MATLAB/Projects/my_project/cycle_results"
    os.makedirs(win_path, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    id_tag = f"_RID{run_id}" if run_id else ""
    output_path = os.path.join(win_path, f"cycle_{now}{id_tag}.mat")

    timepoints = np.array([0, 0.1, 5.68, 5.84, 7.98, 8.12, 9.0])
    timepoints += np.random.uniform(1e-6, 1e-5, size=timepoints.shape)

    # inject_data: 압력 peak 저하
    inject_peaks = np.clip(
    np.random.normal(loc=17.5, scale=1.5, size=2),
    10.0, 30.0  # 하한 10 bar, 상한 30 bar
    )
    inject_values = [0, inject_peaks[0], inject_peaks[1], -0.5, -0.5, 24, 24]
    inject_data = np.column_stack([timepoints, inject_values])

    # backpr_data: ±0.7bar 진동 노이즈
    base_bp = np.array([26, 26, 0, 0, 25, 25, 25])
    noise_bp = np.random.normal(0, 0.7, size=7)
    backpr_values = np.maximum(base_bp + noise_bp, 0.0)
    backpr_data = np.column_stack([timepoints, backpr_values])

    # retract_data: 지연 offset + 시간 오름차순 보장
    while True:
        delay_offset = np.random.exponential(scale=0.4)
        t4 = 5.84 + delay_offset
        t5_candidate = t4 + np.random.uniform(0.05, 0.5)
        if t5_candidate - t4 >= 0.1:
            break
    t5 = t5_candidate
    
    retract_times = timepoints.copy()
    retract_times[3] = t4
    retract_times[4] = t5
    retract_times = np.sort(retract_times)
    retract_values = np.array([0, 0, 0, 24, 24, 0.5, 0.5])
    sort_idx = np.argsort(retract_times)
    retract_data = np.column_stack([
        retract_times[sort_idx],
        retract_values[sort_idx]
    ])

    # nozzle_data: 개방 지연 + 실패 확률 + 정렬 포함
    nozzle_offset = np.random.exponential(scale=0.3)
    fail_chance = np.random.binomial(1, 0.1)
    nozzle_val = 0 if fail_chance else 24

    nozzle_times = timepoints.copy()
    nozzle_times[3:5] += nozzle_offset
    nozzle_values = np.array([0, 0, 0, nozzle_val, nozzle_val, 0, 0])

    sort_idx = np.argsort(nozzle_times)
    nozzle_data = np.column_stack([
        nozzle_times[sort_idx],
        nozzle_values[sort_idx]
    ])


    # extruder_data: 고정값
    extruder_values = [0, 0, 24.5, 24.5, 0.5, 0.5, 0.5]
    extruder_data = np.column_stack([timepoints, extruder_values])

    mat_data = {
        "inject_data": inject_data,
        "backpr_data": backpr_data,
        "retract_data": retract_data,
        "nozzle_data": nozzle_data,
        "extruder_data": extruder_data
    }

    savemat(output_path, mat_data)
    print(f"[✓] .mat 파일 저장 완료 → {output_path}")
    return output_path
