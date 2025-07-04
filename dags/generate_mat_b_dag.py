# dags/generate_mat_and_simulate_dag.py

"""
Airflow DAG: .mat 파일 생성 및 MATLAB Simulink 시뮬레이션 자동 실행

[기능 요약]
1. generate_mat 태스크:
   - 분포 기반 공정 이상치가 반영된 .mat 파일을 생성
   - 저장 경로는 WSL 환경에서 마운트된 Windows 경로 (/mnt/c/...)
   - 생성된 파일 경로를 XCom으로 전달

2. simulate_matlab 태스크:
   - 전달받은 .mat 파일 경로를 MATLAB에서 load
   - 지정된 Simulink 모델(.slx)을 실행

[환경 전제]
- pdm 또는 .venv 환경에서 airflow를 실행
- MATLAB CLI 실행 가능 환경 (예: Windows + Simulink 설치)
"""

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import get_current_context
from airflow.models import Variable
from airflow.exceptions import AirflowSkipException
from datetime import datetime, timedelta
import subprocess
import sys
import os

# 사용자 정의 모듈 import 경로 등록
sys.path.append('/home/seominhyuk/code/wh04-3rd-3team-OptiMold/src')
from optimold.generate_physical_mat import generate_mat  # 실제 .mat 생성 함수


# 🔁 실행 횟수 제한 로직.
# 터미널에서 airflow variables set cycle_count 0,  airflow variables get cycle_count 실행 필요
def check_cycle_count():
    count = int(Variable.get("cycle_count", default_var=0))
    if count >= 120:
        raise AirflowSkipException("Cycle count reached. Skipping execution.")
    Variable.set("cycle_count", count + 1)

def simulate_matlab():
    """
    MATLAB 명령줄에서 .mat 파일 로드 및 Simulink 모델 실행
    - MATLAB CLI 가용 환경이어야 함
    - 모델 경로 및 이름은 고정값으로 가정
    """
    context = get_current_context()
    mat_path = context['ti'].xcom_pull(task_ids='generate_mat')

    if not mat_path or not mat_path.endswith('.mat'):
        raise ValueError("유효한 .mat 파일 경로가 전달되지 않았습니다.")
    

    # Simulink 모델 절대 경로 (윈도우 기준)
    slx_path = "C:/Users/Admin/MATLAB/Projects/my_project/src/wh04_3rd_3team_optimold/fifth_real_model.slx"

    # Postprocess 스크립트 경로
    postprocess_script = "C:/Users/Admin/MATLAB/Projects/my_project/scripts/save_results_to_csv.m"
        
    # MATLAB CLI 실행 경로 (WSL용)
    matlab_exe = '"/mnt/c/Program Files/MATLAB/R2024b/bin/matlab.exe"'
    
    # Windows 경로로 변환한 .mat 파일 경로
    win_mat_path = mat_path.replace("/mnt/c", "C:").replace("/", "\\")
    
    # 🔁 변수명 매핑: {Simulink에서 필요한 이름: .mat 내부 변수명}
    var_map = {
        "Backpr": "backpr_data",
        "Extruder": "extruder_data",
        "Flow_Rate": "flow_rate_data",
        "Inject": "inject_data",
        "Nozzle": "nozzle_data",
        "Piston_Position": "piston_position_data",
        "Piston_Pressure": "piston_pressure_data",
        "Piston_Velocity": "piston_velocity_data",
        "Retract": "retract_data",
        "Volume": "volume_data",
    }

    # 🔧 assignin('base', 'Simulink용 이름', .mat 내부 변수명) 생성
    assign_lines = "; ".join([
        f"assignin('base','{k}',{v})" for k, v in var_map.items()
    ])

    # 명령어 구성
    matlab_cmd = (
        f'{matlab_exe} -batch '
        '"diary(\'C:/Users/Admin/MATLAB/Projects/my_project/log.txt\'); '
        'clearvars -except run_id; '
        f"load('{win_mat_path}'); "
        f"assignin('base','Backpr',backpr_data); "
        f"assignin('base','Extruder',extruder_data); "
        f"assignin('base','Inject',inject_data); "
        f"assignin('base','Nozzle',nozzle_data); "
        f"assignin('base','Retract',retract_data); "
        f"sim('{slx_path}'); "
        f"run('{postprocess_script}'); "
        'diary off;"'
    )

    print(f"실행할 MATLAB 명령: {matlab_cmd}")
    subprocess.run(matlab_cmd, shell=True, check=True)


# DAG 기본 설정
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 6, 5),
    'retries': 0,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id='generate_mat_and_simulate_dag_v14',
    default_args=default_args,
    description='Generate .mat file and run Simulink simulation via MATLAB CLI, convert results to CSV',
    schedule_interval='*/1 * * * *',  # 1분 간격
    catchup=False,
    tags=['optimold', 'matlab', 'simulation']
) as dag:

    start = DummyOperator(task_id='start')

    check_cycle = PythonOperator(
        task_id='check_cycle_count',
        python_callable=check_cycle_count
    )

    generate_mat_file = PythonOperator(
        task_id='generate_mat',
        python_callable=generate_mat,
        op_kwargs={'seed': int(datetime.now().timestamp()) % (2**32 - 1),
                   'run_id': "014"}, # 여기에 직접 run_id 부여
    )

    simulate_matlab_task = PythonOperator(
        task_id='simulate_matlab',
        python_callable=simulate_matlab
    )

    end = DummyOperator(task_id='end')

    # DAG 흐름 정의
    start >> check_cycle >> generate_mat_file >> simulate_matlab_task >> end