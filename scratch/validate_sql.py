import sqlparse

with open('supabase_schema_and_data.sql', 'r') as f:
    sql = f.read()

# Let's find any \' in the SQL
print("Occurrences of backslash-quote:", sql.count("\\'"))

# Replace \' with '' which is standard PostgreSQL
# Also check for words like you're, Don't, etc.
import re

fixed_sql = sql.replace("\\'", "''")

# Specifically check for any unescaped English contractions like you're, don't, it's, doesn't, wasn't, shouldn't, could've, etc.
# But wait! In sql, string is 'hello', if inside it has you're without doubling, it breaks.
# Let's inspect where "you're" or "you\'re" appeared:
for m in re.finditer(r"[a-zA-Z]'[a-zA-Z]", fixed_sql):
    start = max(0, m.start() - 30)
    end = min(len(fixed_sql), m.end() + 30)
    print("Found single quote in word:", fixed_sql[start:end])

