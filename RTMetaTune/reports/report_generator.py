import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def generate_report(log_file):
    try:
        # 열 이름 명시적으로 지정
        columns = [
        "period_start", "period_end", "job_end", "job_deadline", "job_elapsed",
        "job_utilization", "job_density",
        "job_release", "job_finish",
        "execution_time", "deadline_met",
        "l1_references", "l1_refills"
        ]
        df = pd.read_csv(log_file, header=None, names=columns)

        # 숫자형 변환 및 정제
        df = df.apply(pd.to_numeric, errors='coerce').dropna()

        if "job_elapsed" not in df.columns:
            print("❌ 로그 파일에 'job_elapsed' 필드가 없습니다.")
            return

        avg_elapsed = df["job_elapsed"].mean()
        max_elapsed = df["job_elapsed"].max()

        plt.figure(figsize=(10, 4))
        df["job_elapsed"].plot(title="Job Elapsed Time", label="Elapsed", color='blue')
        plt.axhline(y=avg_elapsed, color='red', linestyle='--', label=f"Average: {avg_elapsed:.0f} µs")
        plt.axhline(y=max_elapsed, color='green', linestyle='--', label=f"Max: {max_elapsed:.0f} µs")
        plt.xlabel("Job Index")
        plt.ylabel("Elapsed Time (µs)")
        plt.legend()
        plt.tight_layout()

        report_path = log_file.replace(".csv", "_report.png")
        plt.savefig(report_path)
        print(f"✅ 리포트 생성 완료: {report_path}")

    except Exception as e:
        print(f"❌ 리포트 생성 오류: {e}")

if len(sys.argv) > 1:
    generate_report(sys.argv[1])
else:
    print("❌ 로그 파일 경로가 지정되지 않았습니다.")
