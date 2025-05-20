import yaml
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
METADATA_FILE = os.path.join(BASE_DIR, 'config', 'metadata.yml')

def update_metadata(key, value):
    try:
        with open(METADATA_FILE, 'r') as file:
            metadata = yaml.safe_load(file) or {}

        metadata[key] = round(value, 2)
        with open(METADATA_FILE, 'w') as file:
            yaml.dump(metadata, file)
        print(f"✅ 메타데이터 업데이트 완료: {key}={value}")
    except Exception as e:
        print(f"❌ 메타데이터 업데이트 실패: {e}")
