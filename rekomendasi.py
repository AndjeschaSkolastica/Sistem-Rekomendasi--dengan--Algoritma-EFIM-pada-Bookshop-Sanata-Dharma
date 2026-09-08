
# HUI PRIORITAS UTAMA

# NON HUI PALING AKHIR

# =========================================
import pandas as pd

import pickle

import os

from collections import defaultdict

pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', None)

pd.set_option('display.width', None)

pd.set_option('display.max_colwidth', None)

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

    print("\n" + "="*80)

    print("LOAD MODEL AKTIF")

    print("="*80)

    print("Model Aktif :", nama_model)


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

    print("\n" + "="*80)

    print("LOAD HASIL HUIM")

    print("="*80)

    print(df_hui.head())
    print("\nJumlah HUI :", len(df_hui))

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
    df = pd.read_pickle(path_dataset)
    print("\n" + "="*80)
    print("LOAD DATASET")
    print("="*80)
    print(df.head())
    print("\nJumlah Data :", len(df))

    return df

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
    # INDEX ITEMSET EFIM
    # =====================================
    itemset_index = defaultdict(list)

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

        # =====================================
        # SIMPAN ITEMSET EFIM
        # =====================================
        for item in itemset:
            itemset_index[item].append({
                "itemset": itemset,
                "utility": utility,
                "u-support": usupport
            })

        # =================================
        # SIMPAN ITEM HUI
        # =================================
        for item in itemset:
            item_hui.add(item)

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
        'itemset_index':
            itemset_index,
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
    # Selalu bangun ulang model
    bangun_model_rekomendasi()
    path = os.path.join(
        MODEL_FOLDER,
        'model_rekomendasi.pkl'
    )
    with open(path, 'rb') as f:
        model = pickle.load(f)

    print("\n" + "="*80)
    print("LOAD MODEL REKOMENDASI")
    print("="*80)
    print("Jumlah Item HUI      :", len(model['item_hui']))
    print("Jumlah Item NON HUI  :", len(model['item_non_hui']))
    print("Jumlah Semua Item    :", len(model['semua_item']))
    print("Jumlah Index Itemset :", len(model['itemset_index']))
    return model

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
  
):

    # =====================================
    # LOAD MODEL
    # =====================================
    model = load_model()
    itemset_index = model['itemset_index']
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
        print("Item tidak ditemukan")
        return {
            'status':
                False,
            'message':
                'Item tidak ditemukan',
            'rekomendasi':
                []
        }
    print("\n" + "="*80)
    print("HASIL PENCARIAN ITEM")
    print("="*80)
    for i,item in enumerate(kandidat_item,1):
        print(i,".",item)
    ada_hui = any(
    item in item_hui
    for item in kandidat_item
    )
    print("\n" + "="*80)
    print("CEK STATUS ITEM")
    print("="*80)
    if ada_hui:
        print("Item termasuk HUI")
    else:
        print("Item bukan HUI")

    # =====================================
    # JIKA ADA DI HUI
    # =====================================
    if ada_hui:
        print("\n" + "="*80)
        print("MEMBANGUN REKOMENDASI HUI")
        print("="*80)
        hasil_paket = []
        barang_hui = {}
        for item in kandidat_item:
            if item not in itemset_index:
                continue
            for paket in itemset_index[item]:
                daftar_item = []
                total_harga = 0
                for x in paket["itemset"]:
                    harga = int(harga_item.get(x, 0))
                    daftar_item.append({
                        "nama_barang": x,
                        "harga": harga
                    })
                    total_harga += harga
                    if x not in kandidat_item:
                        barang_hui[x] = harga
                hasil_paket.append({
                    "Itemset": daftar_item,
                    "Jumlah Item": len(daftar_item),
                    "Total Harga": total_harga
                })

                print("\n" + "-"*60)
                print(f"Bundling #{len(hasil_paket)}")
                print("-"*60)

                for barang in daftar_item:
                    print(
                        barang["nama_barang"],
                        "- Rp",
                        format(barang["harga"],",")
                    )

                print("Jumlah Item :",len(daftar_item))
                print("Total Harga :",total_harga)
        print("\n" + "="*80)
        print("TOTAL BUNDLING")
        print("="*80)
        print("Jumlah Bundling :",len(hasil_paket))
        print("\n"+"="*80)
        print("BARANG HUI HASIL REKOMENDASI")
        print("="*80)

        for i,(barang,harga) in enumerate(sorted(barang_hui.items()),1):
            print(
                i,
                barang,
                "- Rp",
                format(harga,",")

            )
        hasil_non_hui = []
        for item in kandidat_item:
            if item in item_non_hui:
                hasil_non_hui.append({
                    "nama_barang": item,
                    "harga_jual": harga_item.get(item, 0)
                })

        print("\n" + "="*80)
        print("HASIL AKHIR REKOMENDASI HUI")
        print("="*80)
        print("Jumlah Bundling :",len(hasil_paket))
        print("Barang HUI :",len(barang_hui))
        print("\n" + "="*80)
        print("BARANG YANG MASIH BERHUBUNGAN")
        print("="*80)

        for i,item in enumerate(hasil_non_hui,1):
            print(
                i,
                item["nama_barang"],
                "- Rp",
                format(item["harga_jual"],",")
            )
        print("\nJumlah Barang :", len(hasil_non_hui))
        return {
            "status": True,
            "jenis": "HUI",
            "item_input": item_input,
            "jumlah_rekomendasi": len(hasil_paket),
            "paket": hasil_paket,
            "barang_hui": [
                {
                    "nama_barang": k,
                    "harga_jual": v
                }
                for k, v in sorted(barang_hui.items())
            ],
            "barang_non_hui": hasil_non_hui
        }
    # =====================================
    # JIKA ITEM BUKAN HUI
    # =====================================
    hasil_non_hui = []
    print("\n" + "="*80)
    print("REKOMENDASI BARANG YANG MASIH BERHUBUNGAN")
    print("="*80)
    for item in kandidat_item:
        if item in item_non_hui:
            hasil_non_hui.append({
                "nama_barang": item,
                "harga_jual": harga_item.get(item, 0)
            })

    for i,item in enumerate(hasil_non_hui,1):
        print(
            i,
            item["nama_barang"],
            "- Rp",
            format(item["harga_jual"],",")
        )
    print("\nJumlah Rekomendasi :",len(hasil_non_hui))
    return {

        "status": True,
        "jenis": "NON HUI",
        "item_input": item_input,
        "jumlah_rekomendasi": len(hasil_non_hui),
        "rekomendasi": hasil_non_hui
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


