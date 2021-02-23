import sqlite3

conn = sqlite3.connect("tb.db")
c = conn.cursor()

print("Checking tbcheck")
TBCHECK_FIELDS = ("gender", "age", "risk", "province", "exposure")

for i in range(len(TBCHECK_FIELDS)):
    rows = c.execute(
        f"""
    SELECT * FROM (
        SELECT count(*) as total, {",".join(TBCHECK_FIELDS[i:])},
        CASE WHEN cough='t' THEN 1 ELSE 0 END +
        CASE WHEN fever='t' THEN 1 ELSE 0 END +
        CASE WHEN sweat='t' THEN 1 ELSE 0 END +
        CASE WHEN weight='t' THEN 1 ELSE 0 END AS symptom_count
        FROM tbcheck
        GROUP BY {",".join(TBCHECK_FIELDS[i:])}
    )
    WHERE total < 5
    """
    )
    if rows.fetchone() is None:
        print(f"Rows: {TBCHECK_FIELDS[i:]}")
        break

print("Checking tbcheck")
TBTEST_FIELDS = ("result",)

for i in range(len(TBTEST_FIELDS)):
    rows = c.execute(
        f"""
    SELECT * FROM (
        SELECT count(*) as total, {",".join(TBTEST_FIELDS[i:])}
        FROM tbtest
        GROUP BY {",".join(TBTEST_FIELDS[i:])}
    )
    WHERE total < 5
    """
    )
    if rows.fetchone() is None:
        print(f"Rows: {TBTEST_FIELDS[i:]}")
        break
conn.close()
