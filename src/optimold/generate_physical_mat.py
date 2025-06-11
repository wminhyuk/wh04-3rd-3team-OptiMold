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
    - extruder_data: 고정된 정상 시나리오 기반

    저장 경로: /mnt/c/Users/Admin/MATLAB/Projects/my_project/cycle_results
    """

    def enforce_min_interval(t_array, min_dt=0.05):
        for i in range(1, len(t_array)):
            if t_array[i] - t_array[i - 1] < min_dt:
                t_array[i] = t_array[i - 1] + min_dt
        return t_array

    if seed is not None:
        np.random.seed(seed)

    win_path = "/mnt/c/Users/Admin/MATLAB/Projects/my_project/cycle_results"
    os.makedirs(win_path, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    id_tag = f"_RID{run_id}" if run_id else ""
    output_path = os.path.join(win_path, f"cycle_{now}{id_tag}.mat")

    # 정상 기준 타임포인트
    inject_time = np.array([0, 0.1, 5.68, 5.84, 7.98, 8.12, 9.0])
    backpr_time = np.array([0, 2.02, 2.1, 2.34, 2.46, 9, 10])
    retract_time = np.array([0, 1.96, 2.06, 2.3, 2.4, 8, 9, 10])
    nozzle_time = np.array([0, 5.46, 5.64, 8.34, 8.42, 9, 10])
    extruder_time = np.array([0, 0.46, 0.58, 1.64, 1.7, 8, 9, 10])

    # inject_data: 압력 피크 저하
    inject_peaks = np.clip(np.random.normal(loc=17.5, scale=1.5, size=2), 10.0, 30.0)
    inject_values = [0, inject_peaks[0], inject_peaks[1], -0.5, -0.5, 24, 24]
    inject_data = np.column_stack([inject_time, inject_values])

    # backpr_data: ±0.7bar 노이즈
    base_bp = np.array([26, 26, 0, 0, 25, 25, 26])
    noise_bp = np.random.normal(0, 0.7, size=7)
    backpr_values = np.maximum(base_bp + noise_bp, 0.0)
    backpr_data = np.column_stack([backpr_time, backpr_values])

    # retract_data: 지연 + 시간 간격 보장
    delay_offset = np.random.exponential(scale=0.1)
    t3 = 2.06 + delay_offset
    t4 = t3 + np.random.uniform(0.1, 0.5)
    retract_mod_time = np.array([0, 1.96, t3, t4, 8, 9, 10])
    retract_mod_time = enforce_min_interval(np.sort(retract_mod_time))
    retract_values = [0, 0, 24, 24, 0.5, -0.23684, -0.23684]
    retract_data = np.column_stack([retract_mod_time, retract_values])

    # nozzle_data: 지연 + 실패 확률 + 시간 간격 보장
    nozzle_offset = np.random.exponential(scale=0.3)
    fail_chance = np.random.binomial(1, 0.1)
    nozzle_val = 0 if fail_chance else 24
    nozzle_mod_time = nozzle_time.copy()
    nozzle_mod_time[2:4] += nozzle_offset
    nozzle_mod_time = enforce_min_interval(np.sort(nozzle_mod_time))
    nozzle_values = [0, 0, nozzle_val, nozzle_val, 0, -0.36709, -1]
    nozzle_data = np.column_stack([nozzle_mod_time, nozzle_values])

    # extruder_data: 고정값 + 시간 간격 보장
    extruder_time = enforce_min_interval(extruder_time.copy())
    extruder_values = [0, 0, 24.5, 24.5456, 0.5, 0.12048, 0.12048, 0]
    extruder_data = np.column_stack([extruder_time, extruder_values])

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
