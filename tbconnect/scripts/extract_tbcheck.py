import sqlite3
import csv
import sys

conn = sqlite3.connect("tb.db")
c = conn.cursor()

TBCHECK_FIELDS = ("risk", "province", "exposure")

writer = csv.writer(sys.stdout)
writer.writerow(
    list(TBCHECK_FIELDS)
    + ["symptom_count", "hashed_msisdn", "source", "timestamp_randomised"]
)

rows = c.execute(
    f"""
SELECT
{",".join(TBCHECK_FIELDS)},
CASE WHEN cough='t' THEN 1 ELSE 0 END +
CASE WHEN fever='t' THEN 1 ELSE 0 END +
CASE WHEN sweat='t' THEN 1 ELSE 0 END +
CASE WHEN weight='t' THEN 1 ELSE 0 END AS symptom_count,
msisdn,source,timestamp
FROM tbcheck
"""
)
for row in rows:
    writer.writerow(row)

conn.close()
