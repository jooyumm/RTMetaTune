#!/bin/bash

## 메인 실행 스크립트

# 경로 설정
SCRIPT_DIR=$(dirname "$(realpath "$0")")
BASE_DIR=$(realpath "$SCRIPT_DIR/..")
LOG_DIR="$BASE_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d")
LOG_FILE="$LOG_DIR/log_$TIMESTAMP.csv"
RT_BENCH_BASE="$BASE_DIR/rt-bench/rt-tacle-bench/bench/sequential"
RT_BENCH_PATH="$RT_BENCH_BASE/my_statemate"
METADATA_FILE="$BASE_DIR/config/metadata.yml"
INSTALL_DIR="$BASE_DIR/rt-bench"
CLEANED_LOG_FILE="${LOG_FILE%.csv}_cleaned.csv"

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 로그 파일 전처리 함수 (비정상 행 제거)
preprocess_log() {
    local log_file="$1"
    local cleaned_file="$2"
    # 필드 개수가 13개인 행만 남기기
    awk -F',' 'NF==13' "$log_file" > "$cleaned_file"
    echo "✅ 로그 파일 전처리 완료: $cleaned_file"
}

# RT-Bench 설치 함수
install_rtbench() {
    echo "🌱 RT-Bench 설치를 시작합니다..."

    # 필수 패키지 설치
    sudo apt update
    sudo apt install -y git build-essential cmake python3 python3-pip

    # RT-Bench 소스 코드 다운로드 및 컴파일
    if [ ! -d "$INSTALL_DIR" ]; then
        git clone https://gitlab.com/rt-bench/rt-bench.git "$INSTALL_DIR"
    else
        echo "✅ RT-Bench 디렉토리가 이미 존재합니다."
    fi

    cd "$INSTALL_DIR" || exit
    make compile-tacle

    # Python 패키지 설치
    pip3 install pandas matplotlib

    # statemate 디렉토리 복제
    if [ ! -d "$RT_BENCH_PATH" ]; then
        echo "🔧 my_statemate 디렉토리 생성 중..."
        cp -r "$RT_BENCH_BASE/statemate" "$RT_BENCH_PATH"
        echo "✅ my_statemate 디렉토리 생성 완료!"
    fi

    # 설치 경로 확인
    if [ -d "$RT_BENCH_PATH" ]; then
        echo "✅ RT-Bench 설치 완료!"
    else
        echo "❌ RT-Bench 설치 실패!"
        exit 1
    fi
}

# 메타데이터 로드 함수
load_metadata() {
    if [ -f "$METADATA_FILE" ]; then
        PERIOD=$(grep '^period:' "$METADATA_FILE" | awk '{print $2}')
        DEADLINE=$(grep '^deadline:' "$METADATA_FILE" | awk '{print $2}')
        TASK_COUNT=$(grep '^task_count:' "$METADATA_FILE" | awk '{print $2}')
        CORE=$(grep '^core:' "$METADATA_FILE" | awk '{print $2}')
        LOG_LEVEL=$(grep '^log_level:' "$METADATA_FILE" | awk '{print $2}')
        TARGET_DEADLINE_MISS=$(grep '^target_deadline_miss:' "$METADATA_FILE" | awk '{print $2}')

        if [ -z "$PERIOD" ] || [ -z "$DEADLINE" ] || [ -z "$TASK_COUNT" ] || [ -z "$CORE" ] || [ -z "$LOG_LEVEL" ]; then
            echo "❌ 필수 메타데이터가 없습니다. 설정을 확인하세요."
            exit 1
        fi

        echo "✅ 메타데이터 로드 완료:"
        echo "  Period: $PERIOD"
        echo "  Deadline: $DEADLINE"
        echo "  Task Count: $TASK_COUNT"
        echo "  Core: $CORE"
        echo "  Log Level: $LOG_LEVEL"
        echo "  Target Deadline Miss: $TARGET_DEADLINE_MISS"
    else
        echo "❌ 메타데이터 파일($METADATA_FILE)을 찾을 수 없습니다."
        exit 1
    fi
}

# RT-Bench 설치 확인 및 실행
if [ ! -d "$RT_BENCH_PATH" ]; then
    echo "❌ RT-Bench 실행 경로를 찾을 수 없습니다. 설치를 진행합니다."
    install_rtbench
else
    echo "✅ RT-Bench가 이미 설치되어 있습니다."
fi

# 메타데이터 로드
load_metadata

# RT-Bench 실행
echo "🚀 RT-Bench 실행 중..."
cd "$RT_BENCH_PATH" || exit

# 실행 권한 추가
chmod +x ./statemate

./statemate -p "$PERIOD" -d "$DEADLINE" -f "$LOG_LEVEL" -t "$TASK_COUNT" -c "$CORE" > "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ RT-Bench 실행 실패"
    tail -n 10 "$LOG_FILE"
    exit 1
else
    echo "✅ RT-Bench 실행 완료"
fi

# 로그 파일 전처리
preprocess_log "$LOG_FILE" "$CLEANED_LOG_FILE"

# 성능 모니터링 시작
echo "📊 성능 모니터링 시작..."
python3 "$BASE_DIR/monitors/metrics_collector.py" "$CLEANED_LOG_FILE"
echo "✅ 성능 모니터링 완료"

# 메타데이터 조정
echo "🛠️ 메타데이터 조정 시작..."
python3 "$BASE_DIR/tuners/metadata_tuner.py" "$CLEANED_LOG_FILE" || echo "⚠️ 메타데이터 조정 실패"

# 리포트 생성
echo "📑 리포트 생성 시작..."
python3 "$BASE_DIR/reports/report_generator.py" "$CLEANED_LOG_FILE" || echo "⚠️ 리포트 생성 실패"