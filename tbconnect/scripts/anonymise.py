"""
Anonymises the MSISDN and timestamp fields
"""
import random
import sqlite3
from datetime import datetime, timedelta
from hashlib import sha256
from uuid import uuid4

conn = sqlite3.connect("tb.db")
c = conn.cursor()
c2 = conn.cursor()

c.execute(
    """
CREATE TABLE IF NOT EXISTS msisdn_salt
(msisdn text, salt text)
"""
)

msisdns = c.execute(
    """
SELECT DISTINCT tb.msisdn FROM (
    SELECT msisdn FROM tbcheck
    UNION
    SELECT msisdn FROM tbtest
) as tb
LEFT JOIN msisdn_salt ON tb.msisdn = msisdn_salt.msisdn
WHERE msisdn_salt.salt IS NULL
"""
)

for (msisdn,) in msisdns:
    c2.execute(
        "INSERT INTO msisdn_salt (msisdn, salt) VALUES (?,?)", (msisdn, uuid4().hex)
    )

for table in ("tbcheck", "tbtest"):
    rows = c.execute(
        f"""
    SELECT {table}.id, {table}.msisdn, msisdn_salt.salt
    FROM {table}
    JOIN msisdn_salt on {table}.msisdn = msisdn_salt.msisdn
    """
    )
    for (id, msisdn, salt) in rows:
        if len(msisdn) < 20:
            hash = sha256(f"{msisdn}:{salt}".encode()).hexdigest()
            c2.execute(f"UPDATE {table} SET msisdn=? WHERE id=?", (hash, id))


for table in ("tbcheck", "tbtest"):
    try:
        c.execute(f"ALTER TABLE {table} ADD COLUMN timestamp_randomised INT DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    rows = c.execute(f"SELECT id, timestamp FROM {table} WHERE timestamp_randomised=0")
    for (id, timestamp) in rows:
        timestamp += "00"
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
        timestamp += timedelta(seconds=random.uniform(-60 * 60, 60 * 60))
        c2.execute(
            f"UPDATE {table} SET timestamp=?, timestamp_randomised=1 WHERE id=?",
            (timestamp.isoformat(), id),
        )


conn.commit()
conn.close()
