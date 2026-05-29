"""module tests basic docker container setup"""
import os
import logging
import sqlite3 as sql
import numpy as np
import pandas as pd
from log_utils import setup_logger
import config
import parse_afcd
import nutrition
import sql_utils

setup_logger()

logger = logging.getLogger(__name__)

rng = np.random.default_rng(config.RANDOM_SEED)

def food_populate(conn, df):
    conn.execute("PRAGMA foreign_keys = ON;")

    foods = df.index.values.tolist()
    id_map = {}

    for f in foods:
        idx = sql_utils.add_food(conn, f)
        id_map[f] = idx
    
    return id_map

def nutrients_populate(conn, df):
    conn.execute("PRAGMA foreign_keys = ON;")

    nutrients = df.columns.values.tolist()
    id_map = {}

    for n in nutrients:
        idx = sql_utils.add_nutrient(conn, n)
        id_map[n] = idx

    return id_map



def main():
    # usda_key = os.environ['API_KEY']
    # logger.info(usda_key)
    logger.info("Running main script")
    # matrix = rng.random((10, 10))
    # logger.info(matrix)

    # sql_utils.create_tables(db_path)
    # inspect_db(db_path)
    # food_name = "Cake, chocolate, homemade, uniced"
    # filename = "data/AFCD Release 3 - Nutrient profiles.xlsx"
    # df = parse_afcd.load_df(filename, sheet_idx=1)
    # df = parse_afcd.preprocess_afcd(df)
    db_path = "data/food.db"
    with sql.connect(db_path) as conn:
        res = sql_utils.search_food_names(conn, "peanut butter")
        # res = sql_utils.query_food_nutrients(conn, 437)
        logger.info(res)
    #     for food in df.index.values.tolist():
    #         energy = nutrition.compute_energy(df.loc[food])
    #         logger.info("%s has %d kiloJoules per 100g.", food, energy)
    #         sql_utils.add_food_nutrients(conn, food, "total_energy", energy)

        # logger.info(sql_utils.query_nutrient_rich_food_per_100g(conn, 2))
        # rows = sql_utils.query_nutrient_rich_food_per_kJ(conn, 5, num_foods=10000)

        # for row in rows:
        #     row = list(row)
        #     row[-1] *= 8
        #     logger.info(row)
        # logger.info(sql_utils.query_food_nutrients(conn, 1))
    #     food_id_map = food_populate(conn, df)
    #     nutr_id_map = nutrients_populate(conn, df)

    #     rows_to_insert = [
    #         (food_id_map[f], nutr_id_map[n], v)
    #         for f, row in df.iterrows()
    #         for n, v in row.items() if pd.notna(v)
    #     ]

    #     cur = conn.cursor()
    #     cur.executemany("""
    #         INSERT OR REPLACE INTO food_nutrients(food_id, nutrient_id, value)
    #         VALUES (?, ?, ?);
    #     """, rows_to_insert)
    #     conn.commit()


        # idx = add_food(conn, food_name)
        # logger.info("Added or existing record exists for %s with id %d", food_name, idx)

        # idx = delete_food(conn, name=food_name)
        # logger.info("Deleted records for %s with id %d", food_name, idx)

    # inspect_db(db_path)


    # food = "Cake, chocolate, homemade, uniced"
    # cols = df.columns.values.tolist()
    # logger.info("\n".join(cols))
    # logger.info(df.head())
    # nutrients = df.loc[food]
    # logger.info("Data for %s \n%s", food.lower(), nutrients.to_string())
    # logger.info("%s has the following amount of Calories: %d",
    #             food, nutrition.kjoule_to_kcal(nutrition.compute_energy(nutrients)))
    # logger.info("%s has the following amount of protein: %f",
    #             food, nutrition.protein(nutrients))
    # logger.info("%s has the following amount of sugars: %f",
    #             food, nutrition.sugars(nutrients))
    # logger.info("%s has the following amount of other category carbs: %f",
    #             food, nutrition.other_carbs(nutrients))

    # logger.info("Count of non-NaN values\n" + df.count().to_string())

    # # List of indices where free_sugars != added_sugars
    # mismatch_sugars = df.index[df['free_sugars'] != df['added_sugars']].tolist()
    # print("Rows where free_sugars != added_sugars:", mismatch_sugars)
    logger.info("Ending")


# fts5 sql lookup



if __name__ == '__main__':
    main()
