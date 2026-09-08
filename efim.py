# =========================================
# FILE : efim.py
# =========================================

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
# =========================================
# BATAS PRINT DFS
# =========================================

DFS_PRINT = 0
MAX_DFS_PRINT = 5

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
        data,
        jumlah=5):

    print_judul(judul)

    try:
        print(data.head(jumlah))
        print(
            "\nJumlah Data :",
            len(data)
        )
    except:
        print(data)

# =========================================
# FAST UTILITY COUNTING
# =========================================

def hitung_utility_itemset(
        transactions,
        target_item):

    total_utility = 0

    for t in transactions:

        util_dict = t['utility_bin']

        if target_item in util_dict:

            total_utility += (
                t['prefix_utility']
                + util_dict[target_item]
            )

    global DFS_PRINT

    if DFS_PRINT < MAX_DFS_PRINT:

        print_judul(
        f"LANGKAH 10 - UTILITY ITEMSET [{target_item}]"
        )

        print(total_utility)
    return total_utility



# =========================================
# UTILITY BIN ARRAY
# =========================================

def buat_utility_bin(pairs):

    utility_bin = {}

    for item, util in pairs:

        utility_bin[item] = util

    return utility_bin


# =========================================
# TRANSACTION MERGING
# =========================================

def merge_transactions(projected):

    merged = {}

    for t in projected:

        key = tuple(
            item for item, _ in t['pairs']
        )

        # =====================================
        # JIKA SUDAH ADA
        # =====================================

        if key in merged:

            merged[key]['prefix_utility'] += (
                t['prefix_utility']
            )

            # =================================
            # JUMLAHKAN UTILITY ITEM
            # =================================

            lama_pairs = merged[key]['pairs']

            baru_pairs = []

            for idx in range(len(lama_pairs)):

                item_lama, util_lama = lama_pairs[idx]
                _, util_baru = t['pairs'][idx]

                baru_pairs.append(
                    (
                        item_lama,
                        util_lama + util_baru
                    )
                )

            merged[key]['pairs'] = baru_pairs

            merged[key]['utility_bin'] = (
                buat_utility_bin(
                    baru_pairs
                )
            )

        # =====================================
        # JIKA BELUM ADA
        # =====================================

        else:

            merged[key] = {

                'tid': t['tid'],

                'pairs': t['pairs'],

                'prefix_utility': t['prefix_utility'],

                'utility_bin': t['utility_bin']
            }

    return list(merged.values())


# =========================================
# PROJECT DATABASE
# =========================================

def project_database(
        transactions,
        target_item):

    projected = []

    for t in transactions:

        pairs = t['pairs']

        for idx, (item, util) in enumerate(pairs):

            if item == target_item:

                new_prefix = (
                    t['prefix_utility']
                    + util
                )

                suffix = pairs[idx + 1:]

                if len(suffix) == 0:
                    break

                projected.append({

                    'tid': t['tid'],

                    'pairs': suffix,

                    'prefix_utility': new_prefix,

                    'utility_bin': buat_utility_bin(
                        suffix
                    )
                })

                break

    # =====================================
    # TRANSACTION MERGING
    # =====================================

    projected = merge_transactions(
        projected
    
    )

    global DFS_PRINT

    if DFS_PRINT < MAX_DFS_PRINT:

        print_judul(
            f"LANGKAH 11 - PROJECTED DATABASE [{target_item}]"
                   )

        for t in projected[:5]:
            print(t)  
    return projected


# =========================================
# HITUNG SU
# =========================================

def hitung_su(projected_db):

    su_dict = {}

    for t in projected_db:

        running_sum = 0

        for item, util in reversed(
                t['pairs']):

            running_sum += util

            su = (
                t['prefix_utility']
                + running_sum
            )

            if item not in su_dict:

                su_dict[item] = 0

            su_dict[item] += su

    return su_dict


# =========================================
# HITUNG LU
# =========================================

def hitung_lu_projected(projected_db):

    lu_dict = {}

    for t in projected_db:

        remaining = sum(
            util for _, util
            in t['pairs']
        )

        for item, util in t['pairs']:

            lu = (
                t['prefix_utility']
                + remaining
            )

            if item not in lu_dict:

                lu_dict[item] = 0

            lu_dict[item] += lu

    return lu_dict


# =========================================
# DFS EFIM


def efim_dfs(
        prefix,
        primary_items,
        secondary_items,
        transactions,
        minutil,
        order_map,
        HUIs):

    for item in primary_items:

        beta = prefix + [item]
        global DFS_PRINT

        boleh_print = DFS_PRINT < MAX_DFS_PRINT

        utility_beta = (
            hitung_utility_itemset(
                transactions,
                item
            )
        )
        if boleh_print:

            print_judul(
                f"LANGKAH 12 - DFS β = {beta}"
            )

        # =====================================
        # SIMPAN HUI
        # =====================================

        if utility_beta >= minutil:

            HUIs.append({

                'Itemset': tuple(beta),

                'Utility': utility_beta
            })
            if boleh_print:
                print(
                    "HUI :",
                    beta,
                    "Utility :",
                    utility_beta
                )
           

        # =====================================
        # PROJECT DATABASE
        # =====================================

        projected_db = project_database(
            transactions,
            item
        )

        if len(projected_db) == 0:

            continue

        # =====================================
        # FAST COUNTING
        # =====================================

        su_dict = hitung_su(
            projected_db
        )
        if boleh_print:

            print_judul(
                f"SU UNTUK β = {beta}"
            )

            print(
                dict(
                    list(
                        su_dict.items()
                    )[:5]
                )
            )

        lu_dict = hitung_lu_projected(
            projected_db
        )
        if boleh_print:

            print_judul(
                f"LU UNTUK β = {beta}"
            )

            print(
                dict(
                    list(
                        lu_dict.items()
                    )[:5]
                )
            )

        # =====================================
        # SECONDARY
        # =====================================

        new_secondary = []

        for z in secondary_items:

            if order_map[z] <= order_map[item]:

                continue

            lu = lu_dict.get(z, 0)

            if lu >= minutil:

                new_secondary.append(z)
        if boleh_print:

            print_judul(
                f"SECONDARY({beta})"
            )

            print(new_secondary[:5])

        # =====================================
        # PRIMARY
        # =====================================

        new_primary = []

        for z in new_secondary:

            su = su_dict.get(z, 0)

            if su >= minutil:

                new_primary.append(z)
        if boleh_print:

            print_judul(
                f"PRIMARY({beta})"
            )

            print(new_primary[:5])

        # =====================================
        # DFS RECURSIVE
        # =====================================

        if boleh_print:
            DFS_PRINT += 1
        if len(new_primary) > 0:
        
            efim_dfs(

                beta,

                new_primary,

                new_secondary,

                projected_db,

                minutil,

                order_map,

                HUIs
            )


# =========================================
# MAIN EFIM
# =========================================

def run_efim(
        df,
        minutil_persen):
    global DFS_PRINT

    DFS_PRINT = 0
    # =========================================
    print_judul(
        "LANGKAH 1 - INISIALISASI α = ∅"
    )

    print(
        "Prefix Awal = []"
    )

    # =====================================
    # TOTAL UTILITY
    # =====================================

    total_utility = (
        df['Laba'].sum()
    )

    minutil = (
        total_utility
        * (minutil_persen / 100)
    )
    # =====================================
    # INFORMASI MINUTIL
    # =====================================

    print_judul("INFORMASI MINUTIL")

    print(f"Total Utility Database : {total_utility:,.2f}")
    print(f"Minutil Input          : {minutil_persen}%")
    print(f"Nilai Minutil          : {minutil:,.2f}")

    # =====================================
    # TU
    # =====================================

    tu = (

        df.groupby('Nota_Baru')['Laba']

        .sum()

        .reset_index()
    )

    tu.columns = [

        'Nota_Baru',

        'TU'
    ]

    df = df.merge(

        tu,

        on='Nota_Baru',

        how='left'
    )
    print_df(
    "LANGKAH 2 - TRANSACTION UTILITY (TU)",
    tu
    )

    # =====================================
    # TWU
    # =====================================

    unik = (

        df[
            [
                'Nama_Baru',
                'Nota_Baru',
                'TU'
            ]
        ]

        .drop_duplicates()
    )

    twu = (

        unik.groupby(
            'Nama_Baru'
        )['TU']

        .sum()

        .reset_index()
    )

    twu.columns = [

        'Item',

        'TWU'
    ]
    print_df(
    "LANGKAH 2 - TRANSACTION WEIGHTED UTILITY (TWU)",
    twu
    )

    # =====================================
    # SECONDARY ROOT
    # =====================================

    secondary_root = twu[
        twu['TWU'] >= minutil
    ].copy()
    print_df(
    "LANGKAH 3 - SECONDARY α",
    secondary_root
    )
    

    # =====================================
    # TRANSACTION SORTING ≻T
    # =====================================

    secondary_root = (
        secondary_root

        .sort_values(
            by=['TWU', 'Item']
        )
    )

    print_df(
    "LANGKAH 4 - SECONDARY α SETELAH DIURUTKAN",
    secondary_root
    )

    secondary_items = (
        secondary_root['Item']
        .tolist()
    )

    order_map = {

        item: idx

        for idx, item in enumerate(
            secondary_items
        )
    }
    print_judul(
    "LANGKAH 5 - TRANSAKSI Mrican1697 16-01 SEBELUM FILTER"
    )

    print(

        df[
            df['Nota_Baru']
            ==
            'Mrican1697 16-01'
        ]

    )

    # =====================================
    # FILTER
    # =====================================

    df_efim = df[
        df['Nama_Baru']
        .isin(secondary_items)
    ].copy()

    df_efim['Order'] = (

        df_efim['Nama_Baru']

        .map(order_map)
    )
    print_judul(
    "LANGKAH 5 - TRANSAKSI Mrican1697 16-01 SETELAH FILTER"
    )

    print(

        df_efim[
            df_efim['Nota_Baru']
            ==
            'Mrican1697 16-01'
        ]

    )

    # =====================================
    # SORTING TRANSACTION
    # =====================================
    cek = df_efim[
    df_efim['Nota_Baru']
    ==
    'Mrican1697 16-01'
    ]

    print_judul(
        "LANGKAH 6 - SEBELUM SORTING ≺T"
    )

    print(cek)
    df_efim = df_efim.sort_values(

        by=[
            'Nota_Baru',
            'Order'
        ]
    )

    cek = df_efim[
    df_efim['Nota_Baru']
    ==
    'Mrican1697 16-01'
    ]

    print_judul(
        "LANGKAH 6 - SETELAH SORTING ≺T"
    )

    print(cek)

    # =====================================
    # DATABASE COMPRESSION
    # =====================================

    df_efim = (

        df_efim.groupby(

            [
                'Nota_Baru',
                'Nama_Baru',
                'Order'
            ],

            as_index=False

        )['Laba']

        .sum()
    )

    # =====================================
    # TRANSACTION DATABASE
    # =====================================

    transactions = []

    for nota, group in df_efim.groupby(
            'Nota_Baru'):

        group = group.sort_values(
            'Order'
        )

        pairs = list(zip(

            group['Nama_Baru'],

            group['Laba']
        ))

        transactions.append({

            'tid': nota,

            'pairs': pairs,

            'prefix_utility': 0,

            'utility_bin': buat_utility_bin(
                pairs
            )
        })

    print_judul(
    "LANGKAH 7 - TRANSACTION DATABASE"
    )

    for t in transactions[:5]:

        print(t)
    
    # =====================================
    # ROOT LU (UTILITY BIN ARRAY LU)
    # =====================================

    utility_bin_lu = {}

    for item in secondary_items:

        utility_bin_lu[item] = 0

    for t in transactions:

        remaining_utility = sum(

            util for _, util in t['pairs']

        )

        for item, util in t['pairs']:

            utility_bin_lu[item] += (

                t['prefix_utility']

                + remaining_utility

            )

    print_judul(
        "LANGKAH 8 - ROOT LU"
    )

    for item, nilai in list(utility_bin_lu.items())[:5]:

        print(
            item,
            "=",
            nilai
        )

    # =====================================
    # ROOT SU (UTILITY BIN SU)
    # =====================================

    utility_bin_su = {}

    for item in secondary_items:

        utility_bin_su[item] = 0

    for t in transactions:

        running = 0

        for item, util in reversed(t['pairs']):

            running += util

            utility_bin_su[item] += (

                t['prefix_utility']

                + running

            )

    print_judul(
        "LANGKAH 9 - ROOT SU"
    )

    for item, nilai in list(utility_bin_su.items())[:5]:

        print(
            item,
            "=",
            nilai
        )

    # =====================================
    # PRIMARY ROOT
    # =====================================

    primary_items = []

    for item in secondary_items:

        if utility_bin_su.get(item, 0) >= minutil:

            primary_items.append(item)

    print_judul(
    "LANGKAH 9 - PRIMARY ROOT"
    )

    print(
        primary_items[:5]
    )

    # =====================================
    # DFS
    # =====================================

    HUIs = []

    efim_dfs(

        [],

        primary_items,

        secondary_items,

        transactions,

        minutil,

        order_map,

        HUIs
    )

    # =====================================
    # HASIL
    # =====================================

    hasil_hui = pd.DataFrame(HUIs)

    if len(hasil_hui) > 0:

        hasil_hui = (

            hasil_hui

            .sort_values(
                by='Utility',
                ascending=False
            )

            .reset_index(drop=True)
        )

    return hasil_hui, transactions