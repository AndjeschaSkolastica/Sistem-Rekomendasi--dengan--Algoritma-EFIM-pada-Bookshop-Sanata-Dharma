# =========================================
# FILE : evaluasi.py
# =========================================

from itertools import combinations
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# =========================================
# PRINT HELPER
# =========================================

def print_judul(judul):

    print("\n")
    print("=" * 80)
    print(judul)
    print("=" * 80)


def print_df(
        judul,
        df,
        jumlah=5):

    print_judul(judul)

    print(df.head(jumlah))

    print(
        "\nJumlah Data :",
        len(df)
    )

# =========================================
# TRANSACTION MAPPING
# =========================================

def get_items_dict(t):

    return {

        item: util

        for item, util in t['pairs']
    }


# =========================================
# U(X)
# total utility itemset X
# di semua transaksi
# =========================================

def U(transactions, X):

    X = set(X)

    total = 0

    for t in transactions:

        items = get_items_dict(t)

        for i in X:

            if i in items:

                total += items[i]

    return total


# =========================================
# LU(X | XY)
# utility X hanya pada transaksi
# yang mengandung XY
# =========================================

def LU(transactions, X, XY):

    X = set(X)

    XY = set(XY)

    total = 0

    for t in transactions:

        items = get_items_dict(t)

        # transaksi mengandung XY
        if XY.issubset(items.keys()):

            for i in X:

                if i in items:

                    total += items[i]

    return total


# =========================================
# GENERATE RULES
# =========================================

def generate_rules(itemset):

    rules = []

    items = list(itemset)

    for i in range(1, len(items)):

        for X in combinations(items, i):

            Y = tuple(

                sorted(

                    set(items) - set(X)
                )
            )

            rules.append(

                (
                    tuple(X),
                    tuple(Y)
                )
            )

    return rules


# =========================================
# EVALUASI HUI
# =========================================

def evaluasi_hui(

        hasil_hui,
        transactions,
        total_utility_database):

    # =====================================
    # JIKA HUI KOSONG
    # =====================================

    if len(hasil_hui) == 0:

        return hasil_hui, pd.DataFrame(), {}

    # =====================================
    # LANGKAH 1
    # U-SUPPORT
    # =====================================

    hasil_hui['u-support'] = (

        hasil_hui['Utility']

        / total_utility_database

    ).round(6)

    print_df(

        "LANGKAH 1 - U-SUPPORT",

        hasil_hui[
            [
                'Itemset',
                'Utility',
                'u-support'
            ]
        ]
    )

    # =====================================
    # LANGKAH 2
    # U-CONFIDENCE
    # =====================================

    uconf_results = []

    for _, row in hasil_hui.iterrows():

        R = tuple(
            row['Itemset']
        )

        rules = generate_rules(
            R
        )

        for X, Y in rules:

            XY = tuple(

                sorted(
                    set(X) | set(Y)
                )
            )

            numerator = LU(

                transactions,

                X,

                XY
            )

            denominator = U(

                transactions,

                X
            )

            uconf = (

                numerator / denominator

                if denominator > 0

                else 0
            )

            uconf = min(
                uconf,
                1
            )

            uconf_results.append({

                "Rule":
                    f"{X} -> {Y}",

                "Antecedent":
                    X,

                "Consequent":
                    Y,

                "uconf":
                    round(
                        uconf,
                        6
                    )
            })

    uconf_df = pd.DataFrame(
        uconf_results
    )

    if len(uconf_df) > 0:

        uconf_df = (

            uconf_df

            .sort_values(
                by='uconf',
                ascending=False
            )

            .reset_index(
                drop=True
            )
        )

    print_df(

        "LANGKAH 2 - U-CONFIDENCE",

        uconf_df
    )

    # =====================================
    # LANGKAH 3
    # TOTAL ITEM UNIK HUIM
    # =====================================

    semua_item_huim = set()

    for itemset in hasil_hui['Itemset']:

        for item in itemset:

            semua_item_huim.add(
                item
            )

    total_item = len(
        semua_item_huim
    )

    print_judul(
        "LANGKAH 3 - TOTAL ITEM UNIK HUIM"
    )

    print(
        "Total Item Unik :",
        total_item
    )

    print(
        "\nContoh Item :"
    )

    print(
        list(
            semua_item_huim
        )[:5]
    )

    # =====================================
    # LANGKAH 4
    # TOTAL HUI
    # =====================================

    total_hui = len(
        hasil_hui
    )

    print_judul(
        "LANGKAH 4 - TOTAL HUI"
    )

    print(
        "Jumlah HUI :",
        total_hui
    )

    # =====================================
    # LANGKAH 5
    # TOTAL UTILITY HUI
    # =====================================

    total_utility_hui = (

        hasil_hui['Utility']
        .sum()
    )

    print_judul(
        "LANGKAH 5 - TOTAL UTILITY HUI"
    )

    print(
        "Total Utility HUI :",
        total_utility_hui
    )

    # =====================================
    # LANGKAH 6
    # AVERAGE U-SUPPORT
    # =====================================

    avg_u_support = round(

        hasil_hui[
            'u-support'
        ].mean(),

        6
    )

    print_judul(
        "LANGKAH 6 - AVERAGE U-SUPPORT"
    )

    print(
        avg_u_support
    )

    # =====================================
    # LANGKAH 7
    # AVERAGE U-CONFIDENCE
    # =====================================

    avg_uconf = (

        round(

            uconf_df[
                'uconf'
            ].mean(),

            6

        )

        if len(uconf_df) > 0

        else 0
    )

    print_judul(
        "LANGKAH 7 - AVERAGE U-CONFIDENCE"
    )

    print(
        avg_uconf
    )

    # =====================================
    # RINGKASAN
    # =====================================

    ringkasan = {

        "total_hui":
            total_hui,

        "total_utility_hui":
            total_utility_hui,

        "avg_total_utility":
            round(

                hasil_hui[
                    'Utility'
                ].mean(),

                2
            ),

        "avg_utility":
            round(

                hasil_hui[
                    'Utility'
                ].mean(),

                2
            ),

        "avg_u_support":
            avg_u_support,

        "avg_uconf":
            avg_uconf,

        "total_item":
            total_item
    }

    print_judul(
        "RINGKASAN EVALUASI"
    )

    print(
        ringkasan
    )

    return (

        hasil_hui,

        uconf_df,

        ringkasan
    )