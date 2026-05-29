import pandas as pd
import config

def kcal_to_kjoule(a):
    return 4.184 * a

def kjoule_to_kcal(a):
    return a / 4.184

def get_val(n, key):
    return 0 if pd.isna(n.get(key, 0)) else n.get(key, 0)

def total_group(nutrients, name, keys):
    """
    Return the total for a nutrient group.

    If the total already exists in nutrients, use it.
    Otherwise compute from component nutrients.
    """
    if name in nutrients:
        return nutrients[name]

    return nutrients[keys].sum()

def protein(n):
    return max(total_group(n, "protein", config.AMINO_ACIDS), get_val(n, "total_protein"))

def sugars(n):
    return max(total_group(n, "sugars", config.SUGARS), get_val(n, "total_sugars"))

def sugar_alcohols(n):
    return total_group(n, "sugar_alcohols", config.SUGAR_ALCOHOLS)

def organic_acids(n):
    return total_group(n, "organic_acids", config.ORGANIC_ACIDS)

def fatty_acids(n):
    return max(SFAs(n) + MUFAs(n) + PUFAs(n), get_val(n, "total_fat"))

def SFAs(n):
    return max(total_group(n, "SFAs", config.SFAS), get_val(n, "total_saturated_fatty_acids"))

def MUFAs(n):
    return max(total_group(n, "MUFAs", config.MUFAS), get_val(n, "total_monounsaturated_fatty_acids"))

def PUFAs(n):
    return max(total_group(n, "PUFAs", config.PUFAS), get_val(n, "total_polyunsaturated_fatty_acids"))

def other_carbs(n):
    """
    Compute the carbs that are not sugar, fiber, or resistant starch
    """
    if "other_carbs" in n:
        return n["other_carbs"]

    total = n[config.OTHER_CARBS].sum()
    return total - get_val(n, "resistant_starch")

ENERGY_COMPONENT_FUNCS = {
    "protein": protein,
    "sugars": sugars,
    "other_carbs": other_carbs,
    "fatty_acids": fatty_acids,
    "alcohol": lambda n: get_val(n, "alcohol"),
    "sugar_alcohols": sugar_alcohols,
    "organic_acids": organic_acids,
    "fiber": lambda n: get_val(n, "fiber"),
    "resistant_starch": lambda n: get_val(n, "resistant_starch"),
}

def compute_energy(nutrients, keys=None):
    """
    Compute the energy content of food from nutrient dictionary.

    Args:
        nutrients (dict): Keys can include:
            protein, fat, alcohol, sugars,
            organic acids, sugar alcohols, 
            other available carbohydrates,
            dietary fiber, resistant starch
    

    Returns:
        float: Energy in kJ
    """
    if keys == None:
        keys = config.DEFAULT_ENERGY_COMPONENTS

    return sum(
        ENERGY_COMPONENT_FUNCS[k](nutrients) * config.ENERGY_FACTORS[k]
        for k in keys
    )

def total_provitamin_A(n):
    beta_carotene = get_val(n, "beta-carotene")
    alpha_carotene = get_val(n, "alpha-carotene")
    cryptoxanthin = get_val(n, "cryptoxanthin")

    return beta_carotene + alpha_carotene / 2 + cryptoxanthin / 2

def total_RAE(n):
    retinol = get_val(n, "retinol")

    return total_provitamin_A(n) / 12 + retinol

def total_niacin_equivalent(n):
    niacin = get_val(n, "niacin")
    tryptophan = get_val(n, "tryptophan")

    return .017 * tryptophan + niacin

def total_folate_equivalent(n):
    folate = get_val(n, "folate")
    folic_acid = get_val(n, "folic_acid")

    return 1.67 * folic_acid + folate
