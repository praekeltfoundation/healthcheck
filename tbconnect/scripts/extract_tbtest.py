import sqlite3
import csv
import sys

conn = sqlite3.connect("tb.db")
c = conn.cursor()

TBTEST_FIELDS = ("result",)

writer = csv.writer(sys.stdout)
writer.writerow(
    list(TBTEST_FIELDS) + ["hashed_msisdn", "source", "timestamp_randomised"]
)

rows = c.execute(
    f"""
SELECT
{",".join(TBTEST_FIELDS)},
msisdn,source,timestamp
FROM tbtest
"""
)
for row in rows:
    writer.writerow(row)

conn.close()
