import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sqlite3
import json
import time
import random
import re
import os

# ==========================================
# 1. 설정 및 상수
# ==========================================
TARGET_URL_PATTERN = "https://api.card-gorilla.com:8080/v1/cards/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://www.card-gorilla.com",
    "Referer": "https://www.card-gorilla.com/"
}
DB_NAME = "card_gorilla_master.db"
IMAGE_DIR = "card_images"  # 이미지를 저장할 폴더명

# ==========================================
# 2. 헬퍼 함수
# ==========================================
def create_session():
    """네트워크 불안정 시 재시도하는 세션 생성"""
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update(HEADERS)
    return session

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '\n', raw_html)
    cleantext = cleantext.replace('&amp;', '&').replace('&nbsp;', ' ')
    return re.sub(r'\n+', '\n', cleantext).strip()

def download_image(url, gorilla_id):
    """
    이미지 다운로드 함수
    [기능 추가]: 이미 파일이 존재하면 다운로드를 생략합니다.
    """
    if not url: return "", "없음"
    
    try:
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
            
        # URL에서 확장자 추출 (예: .png) - 쿼리스트링 제거
        clean_url = url.split('?')[0]
        ext = clean_url.split('.')[-1]
        if len(ext) > 4: ext = 'png' # 확장자가 이상하면 png로 고정
        
        filename = f"{gorilla_id}.{ext}"
        filepath = os.path.join(IMAGE_DIR, filename)
        
        # ---------------------------------------------------------
        # [핵심] 파일이 이미 있고, 용량이 0보다 크면 다운로드 스킵
        # ---------------------------------------------------------
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath, "건너뜀(중복)"

        # 파일이 없으면 다운로드 진행
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath, "다운로드됨"
        
        return "", "실패"
    except Exception as e:
        print(f"    ⚠️ 이미지 다운로드 에러: {e}")
        return "", "에러"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL;")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY,
            gorilla_id INTEGER UNIQUE,
            name TEXT,
            company TEXT,
            card_type TEXT,
            annual_fee TEXT,
            min_spending INTEGER,
            image_url TEXT,
            local_image_path TEXT,
            benefits_summary TEXT,
            benefits_json TEXT,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_name_company ON cards (name, company)')
    conn.commit()
    return conn

def get_last_crawled_id():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(gorilla_id) FROM cards")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0

# ==========================================
# 3. 메인 크롤링 로직
# ==========================================
def crawl_master(target_end_id):
    # 이어하기 확인
    last_id = get_last_crawled_id()
    start_id = last_id + 1
    
    print(f"🔄 시작 ID: {start_id} ~ 목표 ID: {target_end_id}")
    
    conn = init_db()
    cursor = conn.cursor()
    
    # [핵심 1] 안전 모드(WAL) 켜기 - 파일 깨짐 방지 필수
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;") 
    
    session = create_session()
    
    # 통계용 변수
    success_cnt = 0
    skipped_cnt = 0
    error_cnt = 0
    
    # 배치 저장을 위한 변수
    BATCH_SIZE = 10  # 10개씩 모아서 저장
    unsaved_count = 0 

    try:
        for card_id in range(start_id, target_end_id + 1):
            url = TARGET_URL_PATTERN.format(card_id)
            
            try:
                response = session.get(url, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()

                if not data or 'idx' not in data or 'name' not in data:
                    continue
                
                if 'key_benefit' not in data or not isinstance(data['key_benefit'], list):
                    continue

                g_id = data.get('idx')
                name = data.get('name').strip()
                corp_data = data.get('corp') or {}
                company = corp_data.get('name', '').strip()
                
                if not company: continue

                # 중복 확인
                cursor.execute("SELECT 1 FROM cards WHERE name = ? AND company = ?", (name, company))
                if cursor.fetchone():
                    print(f"⏭️  [{card_id}] DB 중복 생략: {name}")
                    continue

                # 이미지 다운로드
                img_data = data.get('card_img') or {}
                origin_img_url = img_data.get('url', '')
                local_img_path = ""
                img_status = "없음"
                
                if origin_img_url:
                    local_img_path, img_status = download_image(origin_img_url, g_id)

                # 데이터 파싱
                c_type = data.get('cate', '')
                annual_fee = data.get('annual_fee_basic', '')
                min_spending = data.get('pre_month_money', 0)
                
                benefit_list = data.get('key_benefit', [])
                parsed_benefits = []
                summary_parts = []

                for ben in benefit_list:
                    title = ben.get('title', '')
                    comment = ben.get('comment', '')
                    clean_info = clean_html(ben.get('info', ''))
                    
                    parsed_benefits.append({'title': title, 'summary': comment, 'detail': clean_info})
                    if title: summary_parts.append(f"[{title}] {comment}")

                benefits_json = json.dumps(parsed_benefits, ensure_ascii=False)
                benefits_summary = " / ".join(summary_parts)

                # INSERT (아직 커밋 안 함!)
                cursor.execute('''
                    INSERT INTO cards 
                    (gorilla_id, name, company, card_type, annual_fee, min_spending, image_url, local_image_path, benefits_summary, benefits_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (g_id, name, company, c_type, annual_fee, min_spending, origin_img_url, local_img_path, benefits_summary, benefits_json))
                
                success_cnt += 1
                unsaved_count += 1
                print(f"✅ [{card_id}] {name} (대기중..)")

                # [핵심 2] 10개가 모였을 때만 저장 (Commit)
                if unsaved_count >= BATCH_SIZE:
                    conn.commit()
                    unsaved_count = 0
                    print(f"💾 --- {BATCH_SIZE}개 데이터 저장 완료 (Safety Commit) ---")
                
                time.sleep(random.uniform(0.3, 0.7))

            except Exception as e:
                print(f"❌ [{card_id}] 에러: {e}")
                error_cnt += 1
                time.sleep(1)

        # 반복문이 끝나고 남은 데이터 저장
        if unsaved_count > 0:
            conn.commit()
            print(f"💾 --- 남은 {unsaved_count}개 데이터 최종 저장 완료 ---")

    except KeyboardInterrupt:
        # 사용자가 Ctrl+C를 눌렀을 때
        print("\n🛑 사용자 중단! 현재까지 진행된 내용을 저장하고 종료합니다.")
        conn.commit() # 지금까지 작업한 건 살리기
    except Exception as e:
        print(f"\n❌ 치명적 오류 발생: {e}")
    finally:
        # [핵심 3] 무조건 연결 닫기
        conn.close()
        print(f"\n🎉 크롤링 종료. (성공: {success_cnt}, 에러: {error_cnt})")

# ==========================================
# 4. 실행
# ==========================================
if __name__ == "__main__":
    # 3000번까지 크롤링
    crawl_master(2931)