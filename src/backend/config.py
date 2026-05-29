RANDOM_SEED = 27

ENERGY_FACTORS = {
    "protein": 17,
    "sugars": 16,
    "other_carbs": 17,
    "fatty_acids": 37,
    "alcohol": 29,
    "sugar_alcohols": 10,
    "organic_acids": 13,
    "fiber": 8,
    "resistant_starch": 12,
}

DEFAULT_ENERGY_COMPONENTS = list(ENERGY_FACTORS.keys())

OTHER_CARBS = [
    "starch",
    "dextrin",
    "glycogen",
    "inulin",
    "maltodextrin",
    "oligosaccharides",
    "polydextrose",
    "raffinose",
    "stachyose"
]

SUGARS = [
    "fructose",
    "glucose",
    "sucrose",
    "maltose",
    "lactose",
    "galactose",
]

SUGAR_ALCOHOLS = [
    "glycerol",
    "erythritol",
    "maltitol",
    "mannitol",
    "xylitol",
    "sorbitol",
]

ORGANIC_ACIDS = [
    "acetic_acid",
    "citric_acid",
    "fumaric_acid",
    "lactic_acid",
    "malic_acid",
    "oxalic_acid",
    "propionic_acid",
    "quinic_acid",
    "shikimic_acid",
    "succinic_acid",
    "tartaric_acid",
]

# awk '{print $(NF-1)}' data/fatty\ acids.txt | grep "^C" | sed 's/^/"/' | sed 's/$/",/'
SFAS = [
    "c4",
    "c6",
    "c8",
    "c10",
    "c11",
    "c12", # lauric acid
    "c13",
    "c14", # myristic acid
    "c15",
    "c16", # palmitic acid
    "c17",
    "c18", # stearic acid
    "c19",
    "c20",
    "c21",
    "c22",
    "c23",
    "c24"
]

MUFAS = [
    "c12:1",
    "c14:1",
    "c15:1",
    "c16:1",
    "c17:1",
    "c18:1", # oleic acid
    "c18:1w7",
    "c20:1",
    "c20:1w11",
    "c22:1",
    "c22:1w11",
    "c24:1"
]

PUFAS = [
    "c12:2",
    "c16:2w4",
    "c16:3",
    "c18:2w6", # linoleic acid
    "c18:3w3", # ALA
    "c18:3w4",
    "c18:3w6",
    "c18:4w1",
    "c18:4w3",
    "c20:2",
    "c20:2w6",
    "c20:3",
    "c20:3w3",
    "c20:3w6",
    "c20:4",
    "c20:4w3",
    "c20:4w6",
    "c20:5w3", # EPA
    "c21:5w3",
    "c22:5w3", # DPA
    "c22:4w6",
    "c22:2",
    "c22:2w6",
    "c22:5w6",
    "c22:6w3" # DHA
]

AMINO_ACIDS = [
    "alanine",
    "arginine",
    "aspartic_acid",
    "cystine_plus_cysteine",
    "glutamic_acid",
    "glycine",
    "histidine",
    "isoleucine",
    "leucine",
    "lysine",
    "methionine",
    "phenylalanine",
    "proline",
    "serine",
    "threonine",
    "tyrosine",
    "tryptophan",
    "valine"
]
