import pandas as pd
import os
import glob
import yaml

# 로그 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

def find_latest_log():
    log_files = glob.glob(f"{LOG_DIR}/log_*_cleaned.csv")
    if not log_files:
        print("❌ 로그 파일을 찾을 수 없습니다.")
        return None
    latest_log = max(log_files, key=os.path.getctime)
    print(f"✅ 가장 최근의 정제 로그 파일: {latest_log}")
    return latest_log

log_file = find_latest_log()

if log_file and os.path.getsize(log_file) > 0:
    try:
        columns = [
            "period_start", "period_end", "job_end", "job_deadline", "deadline_met",
            "job_elapsed", "job_utilization", "job_density",
            "l1_references", "l1_refills", "l2_references", "l2_refills", "inst_retired"
        ]
        df = pd.read_csv(log_file, header=None, names=columns)
        df = df.apply(pd.to_numeric, errors='coerce').dropna()

        avg = df["job_elapsed"].mean()
        maxx = df["job_elapsed"].max()
        miss = 1 - df["deadline_met"].mean()

        print(f"평균 실행 시간: {avg:.0f} µs")
        print(f"최대 실행 시간: {maxx:.0f} µs")
        print(f"데드라인 위반율: {miss:.2%}")

        # 결과 저장
        metrics = {
            "avg_elapsed": float(avg),
            "max_elapsed": float(maxx),
            "deadline_miss": float(miss)
        }
        with open(os.path.join(LOG_DIR, "latest_metrics.yml"), "w") as f:
            yaml.dump(metrics, f)

    except Exception as e:
        print(f"❌ 데이터 처리 중 오류 발생: {e}")
else:
    print("❌ 유효한 로그 파일을 찾을 수 없습니다.")
