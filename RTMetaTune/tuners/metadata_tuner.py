# from config_updater import update_metadata
# import os

# performance_goal_value = float(os.getenv("TARGET_DEADLINE_MISS", "0.01"))

# def tune_metadata():
#     try:
#         if performance_goal_value < 0.01:
#             update_metadata("period", 0.08)
#         else:
#             update_metadata("period", 0.12)
#         print("✅ 메타데이터가 성능 목표에 맞게 조정되었습니다")
#     except Exception as e:
#         print(f"❌ 메타데이터 조정 실패: {e}")

# tune_metadata()

from config_updater import update_metadata
import yaml
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
METADATA_FILE = os.path.join(BASE_DIR, "config", "metadata.yml")
METRICS_FILE = os.path.join(BASE_DIR, "logs", "latest_metrics.yml")  # metrics_collector가 저장

def tune_metadata():
    try:
        # 1. 메트릭 정보 로드
        with open(METRICS_FILE, "r") as f:
            metrics = yaml.safe_load(f)
        actual_miss = metrics.get("deadline_miss", 0.0)

        # 2. 메타데이터에서 목표 deadline_miss 불러오기
        with open(METADATA_FILE, "r") as f:
            meta = yaml.safe_load(f)
        goal_miss = meta.get("target_deadline_miss", 0.01)
        current_period = meta.get("period", 0.1)

        # 3. 비교 후 조정
        if actual_miss > goal_miss:
            new_period = round(current_period + 0.02, 3)
            print(f"🔧 성능 미달 → 주기 증가: {current_period} → {new_period}")
        else:
            new_period = current_period  # 유지
            print(f"✅ 성능 만족: 주기 유지 ({current_period})")

        update_metadata("period", new_period)
        print(f"✅ 메타데이터가 성능 목표에 맞게 조정되었습니다: period={new_period}")

    except Exception as e:
        print(f"❌ 메타데이터 조정 실패: {e}")

tune_metadata()
