# =========================================
# REKOMENDASI.PY (FINAL FIX VERSION)
# HUI PRIORITAS UTAMA
# NON HUI PALING AKHIR
# =========================================

import pandas as pd
import pickle
import os

from collections import defaultdict

# =========================================
# FOLDER
# =========================================

MODEL_FOLDER = 'model'
HASIL_FOLDER = 'hasil_efim'
DATASET_FOLDER = 'dataset'

os.makedirs(MODEL_FOLDER, exist_ok=True)

# =========================================
# LOAD POLA REKOMENDASI AKTIF
# =========================================

def load_model_aktif():

    path = os.path.join(
        MODEL_FOLDER,
        'pola_rekomendasi.txt'
    )

    if not os.path.exists(path):

        raise Exception(
            "Model rekomendasi belum dipilih admin"
        )

    with open(path, 'r') as f:

        nama_model = f.read().strip()

    return nama_model

# =========================================
# LOAD HASIL EFIM
# =========================================

def load_hasil_huim():

    nama_model = load_model_aktif()

    path_hasil = os.path.join(
        HASIL_FOLDER,
        nama_model
    )

    if not os.path.exists(path_hasil):

        raise Exception(
            "File HUIM tidak ditemukan"
        )

    df_hui = pd.read_pickle(
        path_hasil
    )

    return df_hui

# =========================================
# LOAD DATASET
# =========================================

def load_dataset():

    path_dataset = os.path.join(
        DATASET_FOLDER,
        'df_preprocessing.pkl'
    )

    if not os.path.exists(path_dataset):

        raise Exception(
            "Dataset preprocessing tidak ditemukan"
        )

    return pd.read_pickle(
        path_dataset
    )

# =========================================
# AMBIL HARGA ITEM
# =========================================

def get_harga_item(df):

    harga_dict = {}

    for _, row in df.iterrows():

        nama = str(
            row['Nama_Baru']
        ).strip()

        try:

            harga = int(
                float(
                    row['Harga_Jual_Baru']
                )
            )

        except:

            harga = 0

        harga_dict[nama] = harga

        print("\n" + "="*80)
        print("PEMBENTUKAN DATA ITEM DAN HARGA")
        print("="*80)

        for i, (item, harga) in enumerate(
            harga_dict.items()
        ):

            print(item, "=", harga)

            if i >= 4:
                break

    return harga_dict

# =========================================
# BANGUN MODEL REKOMENDASI
# =========================================

def bangun_model_rekomendasi():

    df_hui = load_hasil_huim()

    df_dataset = load_dataset()

    # =====================================
    # SEMUA ITEM
    # =====================================

    semua_item = sorted(

        df_dataset['Nama_Baru']
        .astype(str)
        .unique()
        .tolist()

    )

    # =====================================
    # HARGA ITEM
    # =====================================

    harga_item = get_harga_item(
        df_dataset
    )

    # =====================================
    # RELASI ITEM
    # =====================================

    relasi = defaultdict(dict)

    # =====================================
    # ITEM HUI
    # =====================================

    item_hui = set()

    # =====================================
    # PROSES HASIL HUI
    # =====================================

    for _, row in df_hui.iterrows():

        itemset = row['Itemset']

        utility = row['Utility']

        usupport = row.get(
            'u-support',
            0
        )

        # =================================
        # SKOR FINAL
        # =================================

        skor_final = (

            utility *

            (usupport + 1)

        )

        # =================================
        # SIMPAN ITEM HUI
        # =================================

        for item in itemset:

            item_hui.add(item)

        # =================================
        # RELASI ITEM
        # =================================

        for item in itemset:

            pasangan = (
                set(itemset) - {item}
            )

            for target in pasangan:

                if target not in relasi[item]:

                    relasi[item][target] = 0

                relasi[item][target] += skor_final
        print("\n" + "="*80)
        print("PEMBENTUKAN RELASI ITEM BERDASARKAN HUI")
        print("="*80)

        counter = 0

        for item, pasangan in relasi.items():

            print(f"\nItem : {item}")

            for target, skor in pasangan.items():

                print(
                    f"  -> {target} = {round(skor,2)}"
                )

                counter += 1

                if counter >= 5:
                    break

            if counter >= 5:
                break

    # =====================================
    # ITEM NON HUI
    # =====================================

    item_non_hui = list(

        set(semua_item) - item_hui

    )
    print("\n" + "="*80)
    print("IDENTIFIKASI ITEM HUI DAN NON HUI")
    print("="*80)

    print(
        "\n5 Item HUI Pertama:"
    )

    for item in list(item_hui)[:5]:

        print(item)

    print(
        "\n5 Item NON HUI Pertama:"
    )

    for item in item_non_hui[:5]:

        print(item)


    # =====================================
    # MODEL
    # =====================================

    model = {

        'relasi':
            relasi,

        'item_hui':
            item_hui,

        'item_non_hui':
            item_non_hui,

        'semua_item':
            semua_item,

        'harga_item':
            harga_item
    }

    # =====================================
    # SIMPAN MODEL
    # =====================================

    with open(
        'model/model_rekomendasi.pkl',
        'wb'
    ) as f:

        pickle.dump(
            model,
            f
        )

    print(
        "\nMODEL REKOMENDASI BERHASIL DIBUAT"
    )

# =========================================
# LOAD MODEL
# =========================================

def load_model():

    path = os.path.join(
        MODEL_FOLDER,
        'model_rekomendasi.pkl'
    )

    if not os.path.exists(path):

        bangun_model_rekomendasi()

    with open(path, 'rb') as f:

        return pickle.load(f)

# =========================================
# NORMALISASI TEXT
# =========================================

def normalize_text(text):

    return str(text).strip().lower()

# =========================================
# SEARCH ITEM FLEXIBLE
# =========================================

def cari_item_flexible(
        keyword,
        semua_item
):

    keyword = normalize_text(
        keyword
    )

    keyword_tokens = keyword.split()

    hasil = []

    for item in semua_item:

        item_lower = normalize_text(
            item
        )

        # =================================
        # FULL MATCH
        # =================================

        if keyword == item_lower:

            hasil.append(item)

            continue

        # =================================
        # SUBSTRING MATCH
        # =================================

        if keyword in item_lower:

            hasil.append(item)

            continue

        # =================================
        # TOKEN MATCH
        # =================================

        item_tokens = item_lower.split()

        if any(
            token in item_tokens
            for token in keyword_tokens
        ):

            hasil.append(item)

    # =====================================
    # HAPUS DUPLIKAT
    # =====================================

    hasil = list(
        dict.fromkeys(hasil)
    )
    print("\n" + "="*80)
    print("FLEXIBLE SEARCH")
    print("="*80)

    print(
        "Keyword :",
        keyword
    )

    print(
        "Hasil Pencarian :"
    )

    for item in hasil[:5]:

        print(item)

    return hasil

# =========================================
# SISTEM REKOMENDASI
# HUI SELALU PRIORITAS
# =========================================

def sistem_rekomendasi(
        item_input,
        top_n=10
):

    # =====================================
    # LOAD MODEL
    # =====================================

    model = load_model()

    relasi = model['relasi']

    item_hui = model['item_hui']

    item_non_hui = model['item_non_hui']

    semua_item = model['semua_item']

    harga_item = model['harga_item']

    # =====================================
    # NORMALISASI INPUT
    # =====================================

    item_input = normalize_text(
        item_input
    )

    # =====================================
    # CARI ITEM
    # =====================================

    kandidat_item = cari_item_flexible(

        item_input,
        semua_item

    )

    # =====================================
    # JIKA ITEM TIDAK ADA
    # =====================================

    if len(kandidat_item) == 0:

        return {

            'status':
                False,

            'message':
                'Item tidak ditemukan',

            'rekomendasi':
                []
        }

    # =====================================
    # HASIL REKOMENDASI
    # =====================================

    hasil_hui = []

    hasil_non_hui = []

    added = set()

    # =====================================
    # PROSES ITEM INPUT
    # =====================================

    for kandidat in kandidat_item:

        harga_fix = int(

            harga_item.get(
                kandidat,
                0
            )

        )

        # =================================
        # ITEM INPUT HUI
        # =================================

        if kandidat in item_hui:

            if kandidat not in added:

                hasil_hui.append({

                    'nama_barang':
                        kandidat,

                    'harga_jual':
                        harga_fix,

                    'jenis':
                        'ITEM DICARI HUI'
                })

                added.add(kandidat)

        # =================================
        # ITEM INPUT NON HUI
        # =================================

        else:

            if kandidat not in added:

                hasil_non_hui.append({

                    'nama_barang':
                        kandidat,

                    'harga_jual':
                        harga_fix,

                    'jenis':
                        'ITEM DICARI NON HUI'
                })

                added.add(kandidat)

    # =====================================
    # REKOMENDASI HUI
    # =====================================

    for kandidat in kandidat_item:

        if kandidat in item_hui:

            if kandidat in relasi:

                ranking = sorted(

                    relasi[kandidat].items(),

                    key=lambda x: x[1],

                    reverse=True

                )

                for item_relasi, score in ranking:

                    # =====================
                    # PRIORITAS HUI
                    # =====================

                    if (
                        item_relasi in item_hui
                        and
                        item_relasi not in added
                    ):

                        hasil_hui.append({

                            'nama_barang':
                                item_relasi,

                            'harga_jual':
                                int(
                                    harga_item.get(
                                        item_relasi,
                                        0
                                    )
                                ),

                            'jenis':
                                'HUI'
                        })

                        added.add(
                            item_relasi
                        )

    # =====================================
    # TAMBAHKAN NON HUI PALING AKHIR
    # =====================================

    for kandidat in kandidat_item:

        if kandidat in relasi:

            ranking = sorted(

                relasi[kandidat].items(),

                key=lambda x: x[1],

                reverse=True

            )

            for item_relasi, score in ranking:

                # =========================
                # NON HUI DI AKHIR
                # =========================

                if (
                    item_relasi not in item_hui
                    and
                    item_relasi not in added
                ):

                    hasil_non_hui.append({

                        'nama_barang':
                            item_relasi,

                        'harga_jual':
                            int(
                                harga_item.get(
                                    item_relasi,
                                    0
                                )
                            ),

                        'jenis':
                            'NON HUI'
                    })

                    added.add(
                        item_relasi
                    )

    # =====================================
    # GABUNGKAN HASIL
    # HUI DULU
    # NON HUI TERAKHIR
    # =====================================

    hasil = (

        hasil_hui +

        hasil_non_hui

    )
    print("\n" + "="*80)
    print("PEMBENTUKAN REKOMENDASI")
    print("="*80)

    print(
        "Item Input :",
        item_input
    )

    print(
        "\nRekomendasi HUI:"
    )

    for item in hasil_hui[:5]:

        print(item)

    print(
        "\nRekomendasi NON HUI:"
    )

    for item in hasil_non_hui[:5]:

        print(item)

    # =====================================
    # HAPUS DUPLIKAT
    # =====================================

    unique = []

    seen = set()

    for item in hasil:

        nama = item['nama_barang']

        if nama not in seen:

            unique.append(item)

            seen.add(nama)

    print("\n" + "="*80)
    print("PRIORITAS DAN PENGURUTAN HASIL")
    print("="*80)

    for item in unique[:5]:

        print(
            item['nama_barang'],
            "-",
            item['jenis']
    )

    # =====================================
    # OUTPUT
    # =====================================

    return {

        'status':
            True,

        'item_input':
            item_input,

        'jumlah_rekomendasi':
            len(unique[:top_n]),

        'rekomendasi':
            unique[:top_n]
    }

# =========================================
# LIHAT SEMUA MODEL
# =========================================

def lihat_semua_model():

    files = os.listdir(
        HASIL_FOLDER
    )

    return [

        f for f in files

        if (
            f.endswith('.pkl')
            and
            '_uconf' not in f
        )
    ]

