# =========================================
# IMPORT
# =========================================

import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
# =========================================
# FUNGSI TAMPILKAN PROSES
# =========================================

def tampilkan_tahap(
        judul,
        data,
        jumlah=5):

    print("\n")
    print("=" * 60)
    print(judul)
    print("=" * 60)

    print(data.head(jumlah))

    print("\nJumlah Data :", len(data))

# =========================================
# PREPROCESSING
# =========================================

def preprocessing_data(df):

    # =====================================
    # VALIDASI DATA
    # =====================================

    if df is None:
        raise Exception("Dataframe kosong")

    # =====================================
    # HAPUS KOLOM UNNAMED
    # =====================================

    df = df.loc[
        :,
        ~df.columns.astype(str)
        .str.contains("^Unnamed")
    ]

    tampilkan_tahap(
        "SETELAH HAPUS KOLOM UNNAMED",
        df
    )

    # =====================================
    # VALIDASI KOLOM WAJIB
    # =====================================

    kolom_wajib = [

        'Tgl',
        'Laba',
        'Jml',
        'Nama Barang',
        'No Nota',
        'Suplier',
        'Lokasi',
        'Cara',
        'Harga Jual'

    ]

    kolom_tidak_ada = [

        k for k in kolom_wajib

        if k not in df.columns

    ]

    if len(kolom_tidak_ada) > 0:

        raise Exception(

            f"Kolom tidak ditemukan : {kolom_tidak_ada}"

        )

    # =====================================
    # FORMAT TANGGAL
    # =====================================

    df['Tgl'] = pd.to_datetime(

        df['Tgl'],

        errors='coerce'

    )

    # =====================================
    # HAPUS TANGGAL KOSONG
    # =====================================

    df = df.dropna(

        subset=['Tgl']

    )
    
    tampilkan_tahap(
        "SETELAH HAPUS TANGGAL KOSONG",
        df
    )

    # =====================================
    # FILTER TAHUN 2024
    # =====================================

    df = df[

        df['Tgl'].dt.year == 2024

    ]

    tampilkan_tahap(
    "SETELAH FILTER TAHUN 2024",
    df
    )

 
    if len(df) == 0:

        raise Exception(

            "Dataset kosong setelah filter tahun"

        )

    # =====================================
    # BERSIHKAN NO NOTA
    # =====================================

    df['No Nota'] = (

        df['No Nota']
        .astype(str)
        .str.strip()

    )

    df['No Nota'] = df['No Nota'].replace(

        ['nan', 'None', '', '-'],

        np.nan

    )

    # =====================================
    # TAMPILKAN NO NOTA KOSONG (SEBELUM)
    # =====================================

    print("\n" + "="*60)
    print("DATA NO NOTA KOSONG (SEBELUM PERBAIKAN)")
    print("="*60)

    nota_kosong_awal = df[
        df['No Nota'].isna()
    ].copy()

    if len(nota_kosong_awal) > 0:

        print(
            nota_kosong_awal[
                [
                    'Tgl',
                    'Suplier',
                    'Lokasi',
                    'Cara',
                    'No Nota'
                ]
            ].head(5)
        )

        print(
            "\nJumlah Nota Kosong :",
            len(nota_kosong_awal)
        )

    else:

        print("Tidak ada No Nota kosong")

    # =====================================
    # MAPPING NOTA BERDASARKAN
    # TGL + SUPLIER + LOKASI + CARA
    # =====================================

    grup_nota = (

        df.dropna(subset=['No Nota'])

        .groupby([

            'Tgl',
            'Suplier',
            'Lokasi',
            'Cara'

        ])['No Nota']

        .first()

    )

    # =====================================
    # ISI NO NOTA YANG KOSONG
    # =====================================

    def isi_nota(row):

        if pd.notna(row['No Nota']):
            return row['No Nota']

        key = (

            row['Tgl'],
            row['Suplier'],
            row['Lokasi'],
            row['Cara']

        )

        if key in grup_nota.index:

            return grup_nota.loc[key]

        return np.nan

    df['No Nota'] = df.apply(

        isi_nota,

        axis=1

    )

   # =====================================
    # BUAT NOTA OTOMATIS
    # MAKSIMAL 3 BARANG PER NOTA
    # =====================================

    mask_kosong = df['No Nota'].isna()

    if mask_kosong.sum() > 0:

        data_kosong = df.loc[
            mask_kosong
        ].copy()

        hasil_nota = []

        for _, grup in data_kosong.groupby(
            [
                'Tgl',
                'Suplier',
                'Lokasi',
                'Cara'
            ]
        ):

            grup = grup.copy()

            lokasi = (
                str(
                    grup['Lokasi']
                    .iloc[0]
                )
                .upper()
                .replace(" ", "_")
            )

            # kelompokkan per 3 baris
            grup['sub_grup'] = (

                range(len(grup))
            )

            grup['sub_grup'] = (
                grup['sub_grup'] // 3
            ) + 1

            grup['No Nota Baru'] = (

                lokasi

                + "_AUTO_"

                + grup['sub_grup']
                .astype(str)
            )

            hasil_nota.append(grup)

        hasil_nota = pd.concat(
            hasil_nota
        )

        df.loc[
            hasil_nota.index,
            'No Nota'
        ] = hasil_nota[
            'No Nota Baru'
        ]

    # =====================================
    print("\n" + "="*60)
    print("DATA NO NOTA SETELAH PERBAIKAN")
    print("="*60)

    if len(nota_kosong_awal) > 0:

        hasil_perbaikan = df.loc[
            nota_kosong_awal.index,
            [
                'Tgl',
                'Suplier',
                'Lokasi',
                'Cara',
                'Nama Barang',
                'No Nota'
            ]
        ]

    print(
        hasil_perbaikan.head(5)
    )

    print(
        "\nJumlah Berhasil Diperbaiki :",
        len(hasil_perbaikan)
    )

    print(
        "Jumlah Nota Kosong Tersisa :",
        df['No Nota'].isna().sum()
    )
      
    # =====================================
    # KONVERSI NUMERIK
    # =====================================
    df['Sub Total'] = pd.to_numeric(

        df['Sub Total'],

        errors='coerce'

    )

    df['Laba'] = pd.to_numeric(

        df['Laba'],

        errors='coerce'

    )

    df['Jml'] = pd.to_numeric(

        df['Jml'],

        errors='coerce'

    )
    tampilkan_tahap(
    "SETELAH KONVERSI NUMERIK",
    df[
        [
            'Sub Total',
            'Jml',
            'Laba'
        ]
    ]   
    )
    # =====================================
    # TAMPILKAN TIPE DATA
    # =====================================

    print("\n")
    print("="*60)
    print("TIPE DATA SETELAH KONVERSI NUMERIK")
    print("="*60)

    print(
        df[
            [
                'Sub Total',
                'Jml',
                'Laba'
            ]
        ].dtypes
)

    # =====================================
    # HAPUS NULL
    # =====================================

    df = df.dropna(

        subset=[

            'Sub Total',
            'Laba',
            'Jml'

        ]

    )
    tampilkan_tahap(
    "SETELAH HAPUS NULL",
    df
    )

    # =====================================
    # HINDARI PEMBAGIAN 0
    # =====================================

    df = df[

        df['Jml'] != 0

    ]

    # =====================================
    # HARGA JUAL BARU
    # =====================================

    df['Harga_Jual_Baru'] = (

        df['Harga Jual']

        / df['Jml']

    )

    df['Harga_Jual_Baru'] = (

        df['Harga_Jual_Baru']

        .replace(

            [float('inf'), -float('inf')],

            0

        )

        .fillna(0)

        .round(2)

    )
    tampilkan_tahap(
    "SETELAH HITUNG HARGA JUAL BARU",
    df[
        [
            'Nama Barang',
            'Harga Jual',
            'Jml',
            'Harga_Jual_Baru'
        ]
    ]
    )

    # =====================================
    # KEUNTUNGAN PER ITEM
    # =====================================

    df['Keuntungan_per_item'] = (

        df['Laba']

        / df['Jml']

    )
    tampilkan_tahap(
    "SETELAH HITUNG KEUNTUNGAN PER ITEM",
    df[
        [
            'Nama Barang',
            'Laba',
            'Jml',
            'Keuntungan_per_item'
        ]
    ]
    )

    # =====================================
    # VARIASI ITEM
    # =====================================

    variasi = (

        df.groupby(

            'Nama Barang'

        )['Keuntungan_per_item']

        .transform('nunique')

    )

    # =====================================
    # NAMA BARU
    # =====================================

    df['Nama_Baru'] = (

        df['Nama Barang']

        .astype(str)

    )

    df.loc[
        variasi > 1,
        'Nama_Baru'
    ] = (

        df['Nama Barang']
        .astype(str)

        + " "

        + df['Keuntungan_per_item']
            .round(0)
            .astype(int)
            .astype(str)

    )
    tampilkan_tahap(
    "SETELAH PEMBENTUKAN NAMA_BARU",
    df[
        [
            'Nama Barang',
            'Nama_Baru'
        ]
    ]
    )

    # =====================================
    # NOTA BARU
    # =====================================

    df['Nota_Baru'] = (

        df['No Nota']
        .astype(str)

        + " "

        + df['Tgl']
            .dt.strftime('%d-%m')

    )
    tampilkan_tahap(
    "SETELAH PEMBENTUKAN NOTA_BARU",
    df[
        [
            'No Nota',
            'Nota_Baru'
        ]
    ]
    )

    # =====================================
    # HAPUS KOLOM YANG TIDAK DIPERLUKAN
    # =====================================

    kolom_hapus = [

        'Nama Barang',
        'No Nota',
        'Harga Jual',
        'Suplier',
        'Lokasi',
        'Cara',
        'Pembeli',
        'Penerbit'

    ]

    kolom_hapus = [

        c for c in kolom_hapus

        if c in df.columns

    ]

    df = df.drop(

        columns=kolom_hapus

    )

    # =====================================
    # KOLOM AKHIR
    # =====================================

    kolom_final = [

        'No',
        'Nota_Baru',
        'Nama_Baru',
        'Tgl',
        'Jml',
        'Harga Beli',
        'Harga_Jual_Baru',
        'Diskon',
        'Sub Total',
        'Laba',
        'Keuntungan_per_item'

    ]

    kolom_final = [

        c for c in kolom_final

        if c in df.columns

    ]

    df = df[kolom_final]
    tampilkan_tahap(
    "DATA AKHIR PREPROCESSING",
    df
    )

    # =====================================
    # RESET INDEX
    # =====================================

    df = df.reset_index(

        drop=True

    )

    # =====================================
    # INFORMASI HASIL
    # =====================================

    print("\n")
    print("=" * 60)
    print("PREPROCESSING SELESAI")
    print("=" * 60)

    print("Jumlah Data :", len(df))

    total_keuntungan = df['Laba'].sum()

    print("\n")
    print("=" * 60)
    print("RINGKASAN KEUNTUNGAN")
    print("=" * 60)

    print(
        "Total Keuntungan : Rp {:,.0f}".format(
            total_keuntungan
        )
    )

    return df, total_keuntungan