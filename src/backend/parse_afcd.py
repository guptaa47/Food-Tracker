"""module tests basic docker container setup"""
import logging
from log_utils import setup_logger
import pandas as pd
import re

setup_logger()

logger = logging.getLogger(__name__)

def load_df(filename, sheet_idx=0):
    df = pd.read_excel(filename, sheet_name=sheet_idx)
    return df

def preprocess_afcd(df):
    df = df.iloc[:, 3:]

    df.columns = df.iloc[1].values
    df = df.iloc[2:, :]
    
    df = df.set_index("Food Name")

    # remove amino acids as percent of fat
    df = df.loc[:, ~df.columns.str.endswith('(%T)')]

    # remove amino acids per gram nitrogen
    df = df.loc[:, ~df.columns.str.endswith('/gN)')]

    mg_cols = df.columns[df.columns.str.endswith("(mg)")]
    df[mg_cols] /= 1000

    ug_cols = df.columns[df.columns.str.endswith("(ug)")]
    df[ug_cols] /= 1000000

    df.columns = [clean_column(c) for c in df.columns]

    df = df.rename(columns={'sucrose(g)': 'sucrose',
                            'protein': 'total_protein',
                            'fat_total': 'total_fat',
                            'total_dietary_fibre': 'fiber',
                            'total_saturated_fatty_acids_equated': 'total_saturated_fatty_acids',
                            'total_monounsaturated_fatty_acids_equated': 'total_monounsaturated_fatty_acids',
                            'total_polyunsaturated_fatty_acids_equated': 'total_polyunsaturated_fatty_acids'})

    df = remove_computed_cols(df)

    return df

def remove_computed_cols(df):
    cols_to_remove = [
        'energy_with_dietary_fibre_equated',
        'energy_without_dietary_fibre_equated',
        'available_carbohydrate_without_sugar_alcohols',
        'available_carbohydrate_with_sugar_alcohols',
        'beta-carotene_equivalents',
        'vitamin_a_retinol_equivalents',
        'niacin_derived_from_tryptophan',
        'niacin_derived_equivalents',
        'total_folates',
        'dietary_folate_equivalents',
        'vitamin_d3_equivalents',
        'vitamin_e',
        'total_long_chain_omega_3_fatty_acids_equated',
        'total_undifferentiated_fatty_acids_mass',
        'total_trans_fatty_acids_imputed',
        'nitrogen'
    ]
    df = df.drop(columns=cols_to_remove)

    return df

def clean_column(name):
    name = name.replace("\n", "").replace(",", "")
    name = name.strip().lower()
    name = name.rsplit(" ", 1)[0]
    name = name.strip().replace(" ", "_")
    name = re.sub(r'_\(.*', '', name)

    return name

def main():
    logger.info("Running parse_afcd script")

    filename = "data/AFCD Release 3 - Nutrient profiles.xlsx"
    df = load_df(filename, sheet_idx=1)
    df = preprocess_afcd(df)

    # logger.info(df.iloc[1].to_string())
    # logger.info(df.loc[:, df.count() / len(df.index) > .99].iloc[1].to_string())
    # logger.info(df.iloc[0:, 0].to_string())
    # logger.info(df.iloc[0].to_string())
    # logger.info(df.columns)
    logger.info("\n" + df.loc["Cardamom seed, dried, ground"].to_string())

    logger.info("Ending")


if __name__ == '__main__':
    main()
