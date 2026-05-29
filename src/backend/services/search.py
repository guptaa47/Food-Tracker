import sqlite3 as sql
from backend import sql_utils

DB_PATH = "data/food.db"

def search_food(query: str):
    with sql.connect(DB_PATH) as conn:
        conn.row_factory = sql.Row
        results = sql_utils.search_food_names(conn, query)
    return [dict(r) for r in results]

def get_nutrients(food: str):
    with sql.connect(DB_PATH) as conn:
        conn.row_factory = sql.Row
        results = sql_utils.query_food_nutrients(conn, food)
    return [dict(r) for r in results]