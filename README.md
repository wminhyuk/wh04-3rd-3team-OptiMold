# wh04-3rd-3team-OptiMold

---

# 🚀 옵티몰드(OptiMold) - 사출 성형 공정 데이터 파이프라인

## 📌 프로젝트 개요
옵티몰드는 자동차 산업에서 사용되는 범퍼의 사출 성형 공정 데이터를 시뮬레이션하여, 이상 탐지 및 품질 분석을 자동화하는 데이터 파이프라인 구축 프로젝트입니다. Matlab Simulink를 활용하여 실제 공정 환경과 유사한 금형 온도 및 사출 압력 데이터를 생성하고, Airflow, Apache Spark, Zeppelin, Streamlit 등을 통해 데이터 분석 및 시각화를 수행합니다.

## 🎯 주요 목표
- **데이터 시뮬레이션:** Matlab Simulink를 통해 사출 성형 공정에서의 금형 온도 및 사출 압력 데이터를 시계열 형태로 생성
- **데이터 파이프라인 구축:** Airflow or Spark Streaming 활용하여 시뮬레이션 데이터를 자동 수집 및 전처리
- **데이터 분석 및 이상 탐지:** Apache Spark를 이용한 데이터 기반의 이상 탐지와 품질 분석
- **데이터 시각화:** Zeppelin을 통해 데이터 분석 결과와 공정 변수 간의 상관관계를 시각화
- **대시보드 제공:** Streamlit을 이용한 시계열 데이터 및 분석 결과를 웹 기반 대시보드 형태로 제공

## 🌟 기대효과
- 스마트 제조와 공정 자동화에 대한 실제적 이해 향상
- 사출 성형 공정에서의 이상 사전 탐지 및 품질 안정화 기여
- 엔드-투-엔드 제조 데이터 파이프라인의 설계와 실행 경험
- 실제 자동차 부품 제조 공정에 적용 가능한 실질적 인사이트 제공

## 🛠️ MVP (최소 기능 제품)
자동차 범퍼의 사출 성형 공정에서 발생하는 금형 온도 및 사출 압력 데이터를 Simulink로 시계열로 생성하고, 데이터 수집 및 전처리, 이상 탐지 및 시각화까지의 과정을 통합한 MVP 시스템을 구현합니다.

## 🧰 사용 기술
| 단계 | 기술 스택 |
|------|-----------|
| 시뮬레이션 | Matlab Simulink, Simscape |
| 데이터 수집 및 스케줄링 | Apache Airflow, Spark Streaming |
| 데이터 전처리 및 분석 | Python, pandas, NumPy |
| 대규모 데이터 분석 | Apache Spark (PySpark) |
| 분석 환경 및 시각화 | Apache Zeppelin |
| 웹 시각화 및 리포팅 | Streamlit |
| 데이터베이스 탐색 | DBeaver |
| 클라우드 인프라 | AWS EC2 또는 GCP Compute Engine (선택) |

## ⚙️ 설치 및 실행 방법
*(추가 예정)*



# Airflow DAG: .mat File Generation and Simulink Execution


---

## ✅ 개요
이 DAG는 다음 단계를 자동으로 수행합니다:

1. 시뮬레이션 입력을 위한 현실 기반 노이즈가 포함된 `.mat` 파일 생성
2. 생성된 파일 경로를 MATLAB CLI로 전달하여 Simulink 모델 실행
3. 시작부터 종료까지 워크플로우 관리

---

## 📂 파일 구조
```
dags/
  generate_mat_and_simulate_dag.py     # Airflow DAG 정의 파일
src/optimold/
  generate_physical_mat.py             # .mat 파일 생성 로직
```

---

## ⚙ 요구 사항
- PDM 또는 venv로 구성된 Python 환경의 Airflow 2.x
- CLI(`matlab -batch`) 실행이 가능한 MATLAB 설치
- Simulink 모델 파일: `third_real_model.slx`
- `/mnt/c/...` 형태로 접근 가능한 WSL 또는 Windows 경로

---

## 🔄 워크플로우 단계

### `start`
DAG 시작 지점을 나타내는 Dummy 태스크입니다.

### `generate_mat`
`generate_physical_mat.py`의 `generate_mat(seed=42)` 함수를 호출하여:
- 압력/밸브/후진 관련 이상치가 반영된 `.mat` 파일 생성
- 저장 위치: `/mnt/c/Users/Admin/MATLAB/Projects/my_project/cycle_YYYYMMDD_HHMMSS.mat`
- 전체 파일 경로를 XCom으로 반환

### `simulate_matlab`
- XCom을 통해 전달받은 `.mat` 파일 경로 사용
- Windows 스타일 경로(`C:\Users\Admin\...`)로 변환
- 다음 MATLAB 명령 실행:
```matlab
load('path_to_file.mat');
sim('third_real_model.slx');
```

### `end`
DAG 종료를 나타내는 Dummy 태스크입니다.

---

## 🛠 실행 예시
```bash
pdm run airflow webserver &
pdm run airflow scheduler &
```
DAG 파일 위치:
```bash
/home/seominhyuk/airflow/dags/generate_mat_and_simulate_dag.py
```

---

## 🧩 확장 가능 항목
- Simulink 실행 결과 로깅 및 외부 DB 연동
- 이상 탐지를 위한 Spark 파이프라인 구성
- Simulink 결과를 CSV, Excel, 이미지 등으로 자동 내보내기
