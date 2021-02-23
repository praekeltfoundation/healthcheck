These scripts help implement the anonymisation protocol for tbconnect.

First, we need to extract the data from the database, the following SQL queries will
give you the data in a CSV:

```sql
COPY tbconnect_tbcheck TO STDOUT DELIMITER ',' CSV HEADER;
```
```sql
COPY tbconnect_tbtest TO STDOUT DELIMITER ',' CSV HEADER;
```

We can then import those CSVs into our sqlite database:
```bash
~ sqlite3 tb.db
sqlite> .mode csv
sqlite> .import tbcheck.csv tbcheck
sqlite> .import tbtest.csv tbtest
```

Then we can run `anonymise.py` to hash the msisdns, and randomise the timestamps
```bash
~ python anonymise.py
```

Then we can check which fields we should include in our final export:
```bash
~ python check_redaction.py
```

Now we can edit `extract_tbcheck.py` and `extract_tbtest.py` to include the fields from
the result of the previous script, and then we can run them to get our data extract
```bash
~ python extract_tbcheck.py > tbcheck.csv
~ python extract_tbtest.py > tbtest.csv
```
