import sqlite3

DB_NAME = "card_gorilla_master.db"

def clear_structured_benefit_all():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("UPDATE cards SET structured_benefit = NULL")
    cur.execute("UPDATE cards SET structured_benefit_raw = NULL")

    conn.commit()
    print(f"✅ 초기화 완료 (전체): {cur.rowcount} rows updated")
    conn.close()

if __name__ == "__main__":
    clear_structured_benefit_all()
