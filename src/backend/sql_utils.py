import sqlite3
import logging
import string
from pathlib import Path
from backend.log_utils import setup_logger


setup_logger()

logger = logging.getLogger(__name__)

def get_database_version(path):
    try:
        with sqlite3.connect(path) as conn:
            logger.info("Opened sqlite3 database successfully.")
            cursor = conn.cursor()
            query = "SELECT sqlite_version();"
            cursor.execute(query)
            result = cursor.fetchall()
            logger.info("SQLite Version is %f", result[0][0])
    except sqlite3.OperationalError as e:
        logger.info("Failed to open database: %s", e)

def inspect_db(path):
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        logger.info("Database: %s", Path(path).resolve())

        # --- database stats ---
        cur.execute("PRAGMA page_count;")
        pages = cur.fetchone()[0]

        cur.execute("PRAGMA page_size;")
        page_size = cur.fetchone()[0]

        cur.execute("PRAGMA freelist_count;")
        free_pages = cur.fetchone()[0]

        size_mb = pages * page_size / (1024 * 1024)

        logger.info("Database stats")
        logger.info("Pages: %d", pages)
        logger.info("Page size: %d", page_size)
        logger.info("Free pages: %d", free_pages)
        logger.info("Approx size: %f MB", size_mb)

        # --- tables / views ---
        cur.execute("""
            SELECT name, type
            FROM sqlite_master
            WHERE type IN ('table','view')
            AND name NOT LIKE 'sqlite_%'
            ORDER BY type, name;
        """)
        objects = cur.fetchall()

        logger.info("Tables / Views")

        for name, typ in objects:
            logger.info("%s: %s", typ.upper(), name)

            # row count
            cur.execute(f"SELECT COUNT(*) FROM {name};")
            rows = cur.fetchone()[0]
            logger.info("  rows: %s", rows)

            # columns
            cur.execute(f"PRAGMA table_info('{name}');")
            cols = cur.fetchall()

            for c in cols:
                logger.info("  %s (%s)", c[1], c[2])

        # --- indexes ---
        logger.info("Indexes")

        cur.execute("""
            SELECT name, tbl_name
            FROM sqlite_master
            WHERE type = 'index'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY tbl_name;
        """)

        for name, table in cur.fetchall():
            logger.info("%s on %s", name, table)

        # --- foreign key check ---
        logger.info("Foreign key issues")

        cur.execute("PRAGMA foreign_key_check;")
        fk = cur.fetchall()

        if not fk:
            logger.info("None")
        else:
            for row in fk:
                logger.info(row)

def create_tables(path):
    sql_table_gen = [
        """
        CREATE TABLE IF NOT EXISTS food (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            normalized_name TEXT,
            food_group TEXT);
        """,

        """
        CREATE TABLE IF NOT EXISTS nutrients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            unit TEXT,
            category TEXT);
        """,

        """
        CREATE TABLE IF NOT EXISTS food_nutrients (
            food_id INTEGER,
            nutrient_id INTEGER,
            value REAL,
            PRIMARY KEY (food_id, nutrient_id),
            FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE,
            FOREIGN KEY (nutrient_id) REFERENCES nutrients(id) ON DELETE CASCADE);
        """,

        """
        CREATE VIRTUAL TABLE IF NOT EXISTS food_fts USING fts5 (
            normalized_name,
            content='food',
            content_rowid='id',
            tokenize='unicode61',
            prefix='2 3 4');
        """

    ]

    sql_idx_gen = [
        """
        CREATE INDEX IF NOT EXISTS idx_food_nutrients_food
        ON food_nutrients(food_id);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_food_nutrients_nutrient
        ON food_nutrients(nutrient_id);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_food_nutrients_pair
        ON food_nutrients(food_id, nutrient_id);
        """
    ]

    sql_trigger_gen = [
        """
        CREATE TRIGGER IF NOT EXISTS food_ai AFTER INSERT ON food BEGIN
            INSERT INTO food_fts(rowid, normalized_name)
            VALUES (new.id, COALESCE(new.normalized_name, ''));
        END;
        """,

        """
        CREATE TRIGGER IF NOT EXISTS food_ad AFTER DELETE ON food BEGIN
            INSERT INTO food_fts(food_fts, rowid, normalized_name)
            VALUES ('delete', old.id, COALESCE(old.normalized_name, ''));
        END;
        """,

        """
        CREATE TRIGGER IF NOT EXISTS food_au AFTER UPDATE ON food BEGIN
            INSERT INTO food_fts(food_fts, rowid, normalized_name)
            VALUES ('delete', old.id, COALESCE(old.normalized_name, ''));
            INSERT INTO food_fts(rowid, normalized_name)
            VALUES (new.id, COALESCE(new.normalized_name, ''));
        END;
        """
    ]


    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        cur = conn.cursor()

        logger.info("Creating SQL tables...")

        for s in sql_table_gen:
            cur.execute(s)

        logger.info("Creating indexes...")

        for s in sql_idx_gen:
            cur.execute(s)

        logger.info("Creating triggers...")

        for s in sql_trigger_gen:
            cur.execute(s)

        logger.info("Populating fts table...")

        cur.execute("INSERT INTO food_fts(food_fts) VALUES ('rebuild');")

        logger.info("Committing transaction...")

        conn.commit()

        logger.info("Generated database schema successfully.")

def normalize_text(name: str) -> str:
    """
    Remove punctuation and capitalization from input
    """
    trans_table = str.maketrans(dict.fromkeys(string.punctuation, ' '))
    normalized = name.translate(trans_table).lower()
    return ' '.join(normalized.split())


def to_fts_query(query: str) -> str:
    """
    Convert user input into FTS prefix query
    """
    tokens = normalize_text(query).split()
    return " ".join(token + "*" for token in tokens)

def resolve_food_id(conn, id_):
    """
    Return the food id for a given food id or name
    """
    if isinstance(id_, int):
        return id_

    cur = conn.cursor()
    cur.execute("SELECT id FROM food WHERE name = ?;", (id_,))
    row = cur.fetchone()

    if row is None:
        raise ValueError(f"Food not found: {id_}")

    return row[0]

def add_food(conn, name, normalized_name=None, food_group=None):
    """
    Add new food to sql database
    Overrides existing food if name matches
    """
    insert_sql = """
        INSERT OR REPLACE INTO food(name, normalized_name, food_group)
        VALUES (?, ?, ?);
    """

    if normalized_name is None:
        trans_table = str.maketrans(dict.fromkeys(string.punctuation, ' '))
        normalized_name = name.translate(trans_table).lower()
        normalized_name = ' '.join(normalized_name.split())

    cur = conn.cursor()
    cur.execute(insert_sql, (name, normalized_name, food_group))
    conn.commit()

    return resolve_food_id(conn, name)

def delete_food(conn, id_):
    food_id = resolve_food_id(conn, id_)

    cur = conn.cursor()
    cur.execute("DELETE FROM food WHERE id = ?;", (food_id,))
    conn.commit()

    return food_id

def resolve_nutrient_id(conn, id_=None):
    if isinstance(id_, int):
        return id_

    cur = conn.cursor()
    cur.execute("SELECT id FROM nutrients WHERE name = ?;", (id_,))
    row = cur.fetchone()

    if row is None:
        raise ValueError(f"Nutrient not found: {id_}")

    return row[0]

def add_nutrient(conn, name, unit=None, category=None):
    insert_sql = """
        INSERT OR REPLACE INTO nutrients(name, unit, category)
        VALUES (?, ?, ?);
    """
    cur = conn.cursor()
    cur.execute(insert_sql, (name, unit, category))
    conn.commit()

    return resolve_nutrient_id(conn, name)

def delete_nutrient(conn, id_):
    nutrient_id = resolve_nutrient_id(conn, id_)

    cur = conn.cursor()
    cur.execute("DELETE FROM nutrients WHERE id = ?;", (nutrient_id,))
    conn.commit()

    return nutrient_id

def add_food_nutrients(conn, food_id, nutrient_id, value):
    food_id = resolve_food_id(conn, food_id)
    nutrient_id = resolve_nutrient_id(conn, nutrient_id)

    insert_sql = """
        INSERT OR REPLACE INTO food_nutrients (food_id, nutrient_id, value)
        VALUES (?, ?, ?)
    """

    cur = conn.cursor()
    cur.execute(insert_sql, (food_id, nutrient_id, value))
    conn.commit()

    return (food_id, nutrient_id)

def delete_food_nutrients(conn, food_id, nutrient_id):
    food_id = resolve_food_id(conn, food_id)
    nutrient_id = resolve_nutrient_id(conn, nutrient_id)

    cur = conn.cursor()
    cur.execute("""
                DELETE FROM food_nutrients " \
    "           WHERE food_id = ? AND nutried_id = ?;""",
                (food_id, nutrient_id))
    conn.commit()

    return (food_id, nutrient_id)

def query_food_nutrients(conn, food_id, nutrient_id=None):
    food_id = resolve_food_id(conn, food_id)
    cur = conn.cursor()
    if nutrient_id is None:
        cur.execute("""
            SELECT f.name AS food_name, n.name AS nutrient_name, fn.food_id, fn.nutrient_id, fn.value
            FROM food_nutrients fn
            JOIN food f ON fn.food_id = f.id
            JOIN nutrients n ON fn.nutrient_id = n.id
            WHERE fn.food_id = ?;
        """, (food_id,))
    else:
        nutrient_id = resolve_nutrient_id(conn, nutrient_id)
        cur.execute("""
            SELECT f.name AS food_name, n.name AS nutrient_name, fn.food_id, fn.nutrient_id, fn.value
            FROM food_nutrients fn
            JOIN food f ON fn.food_id = f.id
            JOIN nutrients n ON fn.nutrient_id = n.id
            WHERE fn.food_id = ? AND fn.nutrient_id = ?;
        """, (food_id, nutrient_id))

    return cur.fetchall()

def query_nutrient_rich_food_per_100g(conn, nutrient_id, num_foods=20):
    nutrient_id = resolve_nutrient_id(conn, nutrient_id)
    cur = conn.cursor()
    cur.execute("""
        SELECT f.name, n.name, fn.food_id, fn.nutrient_id, fn.value
        FROM food_nutrients fn
        JOIN food f ON fn.food_id = f.id
        JOIN nutrients n ON fn.nutrient_id = n.id
        WHERE fn.nutrient_id = ?
        ORDER BY fn.value DESC LIMIT ?
    """, (nutrient_id, num_foods))

    return cur.fetchall()

def query_nutrient_rich_food_per_kJ(conn, nutrient_id, energy_id="total_energy", num_foods=20):
    nutrient_id = resolve_nutrient_id(conn, nutrient_id)
    energy_id = resolve_nutrient_id(conn, energy_id)
    cur = conn.cursor()
    cur.execute("""
    SELECT f.name, fn1.value AS nutrient_val, fn2.value AS energy_val, fn1.value / fn2.value AS density
    FROM food_nutrients fn1
    JOIN food_nutrients fn2 ON fn1.food_id = fn2.food_id
    JOIN nutrients n1 ON fn1.nutrient_id = n1.id
    JOIN nutrients n2 ON fn2.nutrient_id = n2.id
    JOIN food f ON fn1.food_id = f.id
    WHERE n1.id = ? AND n2.id = ? AND fn2.value > 0
    ORDER BY density DESC LIMIT ?
    """, (nutrient_id, energy_id, num_foods))

    return cur.fetchall()

def search_food_names(conn, query, limit=None):
    """
    FTS-based search with prefix matching,
    giving priority to in order words
    """
    base_query = """
        SELECT f.*
        FROM food_fts
        JOIN food f ON f.id = food_fts.rowid
        WHERE food_fts MATCH ?
        ORDER BY 
            CASE
                WHEN f.normalized_name = ? THEN 0
                WHEN f.normalized_name LIKE ? || ' %' THEN 1
                WHEN f.normalized_name LIKE ? || '%' THEN 2
                ELSE 3
            END,
            f.normalized_name
    """
    normalized = normalize_text(query)
    params = [to_fts_query(query), normalized, normalized, normalized]

    if limit is not None:
        base_query += " LIMIT ?"
        params.append(limit)

    cur = conn.cursor()
    cur.execute(base_query, params)

    return cur.fetchall()

# search:
# fts5 on food name
# nutrient or nutrient / energy range restriction
# sort on nutrient or nutrient / energy
# show selected nutrient values only