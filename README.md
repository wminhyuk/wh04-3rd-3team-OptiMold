# 🛠 wh04-3rd-3team-OptiMold

## 🚀 OptiMold: 자동차 범퍼 사출 성형 공정의 스마트 모니터링 및 이상 탐지 시스템

---

## 📌 프로젝트 개요
**OptiMold**는 자동차 부품(범퍼)의 사출 성형 공정을 Simulink로 시뮬레이션하고, 실제 공정 환경을 모사한 데이터를 기반으로 이상 탐지 및 공정 예측을 수행하는 **스마트 제조 분석 파이프라인**입니다.  

Matlab Simulink 기반의 정밀 모델링, Airflow 자동화, Streamlit 인터페이스를 통해 **공정 모니터링 → 이상 공정 자동 식별 → 품질 분류 → 공정 시계열 예측**까지 이어지는 통합 시스템을 구축하였습니다.

---

## 🎯 주요 기능
- 💾 **Simulink 기반 사출 공정 시뮬레이션**
  - 실제 범퍼 제조 환경을 반영한 Matlab 모델 구현 및 `.mat` 기반 반복 시뮬레이션 수행

- 🔄 **Airflow 자동화 파이프라인**
  - `.mat` 생성 → 시뮬레이션 실행 → 결과 저장까지 자동화된 DAG 구성

- 📊 **시계열 기반 이상 탐지 및 분류**
  - 사출 압력/위치/속도 등 주요 출력 변수 분석을 통해 총 6가지 시나리오로 공정 분류

- 🧠 **Granger Causality 분석**
  - 제어 ↔ 출력 변수 간 인과성 시각화 네트워크 구축 및 해석 제공

- 📈 **Streamlit 기반 HMI 시각화 및 공정 예측**
  - 클릭 기반 센서 위치 정보, 실시간 분석 결과 요약, 입력값 기반 공정 예측 기능 탑재

---

## 🌟 기대효과
- 스마트 제조와 공정 자동화에 대한 실제적 이해 향상
- 사출 성형 공정에서의 이상 사전 탐지 및 품질 안정화 기여
- 엔드-투-엔드 제조 데이터 파이프라인의 설계와 실행 경험
- 실제 자동차 부품 제조 공정에 적용 가능한 실질적 인사이트 제공

---

## 🧪 이상 시나리오 정의 및 분류 예시

| 분류 | 설명 | 판정 기준 |
|------|------|------------|
| Short shot | 충진 부족으로 형상이 미완성됨 | `Volume_max < 45` |
| Overpacking / Flash | 과충진에 따른 수지 누출 발생 | `Volume_max > 55` |
| Jetting | 고속 유량 서지로 인한 외관 이상 | `Flow Rate 기울기 변화 지속시간 > 0.6초` |
| Sink mark | 보압 종료 후 속도 정지로 수축 자국 | `8초 이후 flat duration > 1.95초` |
| Sticking / Slip | 보압 중 피스톤 불안정 정지 | `flat ratio (6초 이후) < 0.9` |

---

## 🧰 사용 기술
| 단계 | 기술 스택 |
|------|-----------|
| 공정 시뮬레이션 | Matlab Simulink (Simscape) |
| 데이터 수집 및 공정 스케줄링 | Apache Airflow |
| 데이터 전처리 및 분석 | Python (Jupyter lab) |
| 분석 시각화 및 리포팅 | Streamlit |


## 🌐 시스템 구성도

[Matlab Simulink] → [Airflow 자동 반복] → [CSV 저장] → [Python 분석] → [Streamlit 대시보드]
→ 이상 탐지 + 공정 예측      

---


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
- Simulink 모델 파일: `fifth_real_model.slx`
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
sim('fifth_real_model.slx');
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
