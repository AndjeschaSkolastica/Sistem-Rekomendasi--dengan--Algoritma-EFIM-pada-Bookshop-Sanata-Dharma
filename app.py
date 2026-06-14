# =========================================
# FILE : app.py
# =========================================

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)

import pandas as pd
import os
import glob
import time

from preprocessing import preprocessing_data
from efim import run_efim
from evaluasi import evaluasi_hui
from rekomendasi import sistem_rekomendasi
from datetime import timedelta

# =========================================
# FLASK
# =========================================

app = Flask(__name__)

app.secret_key = "HUIM_SECRET_KEY"

# SESSION LOGIN
app.permanent_session_lifetime = timedelta(days=7)

# =========================================
# FOLDER
# =========================================

UPLOAD_FOLDER = 'uploads'
DATASET_FOLDER = 'dataset'
HASIL_FOLDER = 'hasil_efim'
MODEL_FOLDER = 'model'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)
os.makedirs(HASIL_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

# =========================================
# SESSION PROTECTION
# =========================================

@app.before_request
def proteksi_halaman():

    halaman_public = [

        'login',
        'static'

    ]

    # =====================================
    # JIKA BELUM LOGIN
    # =====================================

    if request.endpoint not in halaman_public:

        if "role" not in session:

            return redirect(
                url_for('login')
            )

    # =====================================
    # HALAMAN ADMIN
    # =====================================

    if request.path.startswith('/admin'):

        if session.get("role") != "admin":

            return redirect(
                url_for('login')
            )

    # =====================================
    # HALAMAN USER
    # =====================================

    if request.path.startswith('/user'):

        if session.get("role") != "user":

            return redirect(
                url_for('login')
            )

# =========================================
# LOGIN
# =========================================

@app.route("/", methods=["GET", "POST"])
def login():

    # =====================================
    # SUDAH LOGIN
    # =====================================

    if session.get("role") == "admin":

        return redirect(
            url_for("admin_dashboard")
        )

    if session.get("role") == "user":

        return redirect(
            url_for("user_dashboard")
        )

    error = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # =====================================
        # LOGIN ADMIN
        # =====================================

        if username == "admin" and password == "admin123":

            session.permanent = True

            session["role"] = "admin"

            return redirect(
                url_for("admin_dashboard")
            )

        # =====================================
        # LOGIN USER
        # =====================================

        elif username == "user" and password == "user123":

            session.permanent = True

            session["role"] = "user"

            return redirect(
                url_for("user_dashboard")
            )

        else:

            error = "Username atau password salah"

    return render_template(
        "login.html",
        error=error
    )

# =========================================
# LOGOUT
# =========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for('login')
    )

# =========================================
# ADMIN DASHBOARD
# =========================================

@app.route('/admin_dashboard')
def admin_dashboard():

    total_dataset = len(
        glob.glob('dataset/*.pkl')
    )

    total_model = len(
        glob.glob('hasil_efim/*.pkl')
    )

    total_upload = len(
        glob.glob('uploads/*')
    )

    total_hui = 0

    semua_model = glob.glob(
        'hasil_efim/*.pkl'
    )

    for file in semua_model:

        try:

            df = pd.read_pickle(file)

            total_hui += len(df)

        except:
            pass

    statistik = {

        'total_dataset': total_dataset,

        'total_model': total_model,

        'total_upload': total_upload,

        'total_hui': total_hui

    }

    return render_template(

        'admin/admin_dashboard.html',

        statistik=statistik

    )

# =========================================
# USER DASHBOARD
# =========================================

@app.route('/user_dashboard')
def user_dashboard():

    return render_template(
        'user/user_home.html'
    )

# =========================================
# HALAMAN UPLOAD
# =========================================

@app.route('/admin/upload')
def halaman_upload():

    return render_template(
        'admin/upload_data.html'
    )

# =========================================
# PROSES UPLOAD
# =========================================

@app.route('/admin/proses_upload', methods=['POST'])
def proses_upload():

    try:

        files = request.files.getlist('files')

        if len(files) == 0:

            flash('File belum dipilih')

            return redirect(
                url_for('halaman_upload')
            )

        semua_df = []
        total_keuntungan = 0

        for file in files:

            if file.filename == '':
                continue

            path_file = os.path.join(
                UPLOAD_FOLDER,
                file.filename
            )

            file.save(path_file)

            df_excel = pd.read_excel(
                path_file
            )

            df_bersih, keuntungan_file = preprocessing_data(
                df_excel
            )

            total_keuntungan += keuntungan_file


            semua_df.append(df_bersih)

        if len(semua_df) == 0:

            flash('Dataset kosong')

            return redirect(
                url_for('halaman_upload')
            )

        df_final = pd.concat(

            semua_df,

            ignore_index=True

        )

        path_dataset = os.path.join(

            DATASET_FOLDER,

            'df_preprocessing.pkl'

        )

        df_final.to_pickle(path_dataset)

        preview_data = df_final.head(50).to_dict(
            orient='records'
        )
        kolom = df_final.columns.tolist()

        total_transaksi = (
            df_final['Nota_Baru'].nunique()
        )

        total_item = (
            df_final['Nama_Baru'].nunique()
        )

        total_utility = (
            df_final['Laba'].sum()
        )

        return render_template(

            'admin/hasil_preprocessing.html',

            data=preview_data,

            kolom=kolom,

            total_data=len(df_final),
            total_keuntungan=round(
                total_keuntungan,
                2
            ),
                
            total_transaksi=total_transaksi,

            total_item=total_item,

            total_utility=round(
                total_utility,
                2
            )

        )

    except Exception as e:

        return f"""
        <h1>ERROR PREPROCESSING</h1>
        <pre>{str(e)}</pre>
        """

# =========================================
# INPUT MINUTIL
# =========================================

@app.route('/admin/minutil')
def input_minutil():

    return render_template(
        'admin/input_minutil.html'
    )

# =========================================
# PROSES EFIM
# =========================================

@app.route('/admin/proses_efim', methods=['POST'])
def proses_efim():

    try:

        # =====================================
        # AMBIL MINUTIL
        # =====================================

        minutil = float(
            request.form['minutil']
        )

        # =====================================
        # VALIDASI MINUTIL
        # =====================================

        if minutil < 0.1:

            flash(
                'Minutil minimal adalah 0.1'
            )

            return redirect(
                url_for('input_minutil')
            )

        if minutil > 10:

            flash(
                'Minutil maksimal adalah 10'
            )

            return redirect(
                url_for('input_minutil')
            )

        # =====================================
        # CEK MINUTIL SUDAH ADA
        # =====================================

        path_ringkasan = os.path.join(
            MODEL_FOLDER,
            'ringkasan_model.pkl'
        )

        if os.path.exists(path_ringkasan):

            df_cek = pd.read_pickle(
                path_ringkasan
            )

            daftar_minutil = (

                df_cek['minutil']
                .astype(float)
                .round(4)
                .tolist()

            )

            if round(minutil, 4) in daftar_minutil:

                flash(
                    f'Minutil {minutil} sudah pernah diproses. '
                    f'Silakan masukkan nilai lain.'
                )

                return redirect(
                    url_for('input_minutil')
                )

        # =====================================
        # CEK DATASET
        # =====================================

        path_dataset = os.path.join(
            DATASET_FOLDER,
            'df_preprocessing.pkl'
        )

        if not os.path.exists(path_dataset):

            flash('Dataset belum tersedia')

            return redirect(
                url_for('input_minutil')
            )

        # =====================================
        # LOAD DATASET
        # =====================================

        df = pd.read_pickle(
            path_dataset
        )

        total_utility_database = (
            df['Laba'].sum()
        )

        # =====================================
        # TOTAL TRANSAKSI
        # =====================================

        total_transaksi = (
            df['Nota_Baru']
            .nunique()
        )

        # =====================================
        # TOTAL ITEM
        # =====================================

        total_item = (
            df['Nama_Baru']
            .nunique()
        )

        # =====================================
        # RUN EFIM
        # =====================================

        start_time = time.time()

        hasil_hui, transactions = run_efim(
            df,
            minutil
        )

        end_time = time.time()

        waktu_proses = round(
            end_time - start_time,
            4
        )

        # =====================================
        # TIDAK ADA HUI
        # =====================================

        if len(hasil_hui) == 0:

            flash(
                'Tidak ada HUI ditemukan'
            )

            return redirect(
                url_for('input_minutil')
            )

        # =====================================
        # EVALUASI HUI
        # =====================================

        hasil_hui, uconf_df, ringkasan = evaluasi_hui(

            hasil_hui,
            transactions,
            total_utility_database

        )

        # =====================================
        # SORT HUI
        # =====================================

        hasil_hui = hasil_hui.sort_values(
            by='Utility',
            ascending=False
        )

        # =====================================
        # NAMA FILE
        # =====================================

        nama_file = (

            f'hasil_minutil_'
            f'{str(minutil).replace(".", "_")}.pkl'

        )

        path_hasil = os.path.join(
            HASIL_FOLDER,
            nama_file
        )

        # =====================================
        # SIMPAN HASIL HUI
        # =====================================

        hasil_hui.to_pickle(path_hasil)

        # =====================================
        # SIMPAN UCONF
        # =====================================

        nama_uconf = nama_file.replace(
            '.pkl',
            '_uconf.pkl'
        )

        path_uconf = os.path.join(
            HASIL_FOLDER,
            nama_uconf
        )

        uconf_df.to_pickle(path_uconf)

        # =====================================
        # HITUNG TOTAL ITEM UNIK DI HUI
        # =====================================

        semua_item = set()

        for itemset in hasil_hui['Itemset']:

            for item in itemset:

                semua_item.add(item)

        total_item_hui = len(semua_item)

        # =====================================
        # DATA MODEL
        # =====================================

        data_model = {

            'minutil': minutil,

            'total_hui': ringkasan['total_hui'],

            'total_item': total_item_hui,

            'avg_total_utility': ringkasan['avg_total_utility'],

            'avg_u_support': ringkasan['avg_u_support'],

            'avg_uconf': ringkasan['avg_uconf'],

            'waktu_proses': round(waktu_proses, 4),

            'nama_file': nama_file

        }

        # =====================================
        # SIMPAN RINGKASAN
        # =====================================

        if os.path.exists(path_ringkasan):

            df_model = pd.read_pickle(
                path_ringkasan
            )

            df_model = pd.concat(

                [
                    df_model,
                    pd.DataFrame([data_model])
                ],

                ignore_index=True

            )

        else:

            df_model = pd.DataFrame(
                [data_model]
            )

        df_model.to_pickle(
            path_ringkasan
        )

        # =====================================
        # TAMPILKAN HASIL
        # =====================================

        # =====================================
        # SIMPAN KE SESSION
        # =====================================

        session['minutil'] = minutil
        session['nama_file'] = nama_file
        session['total_hui'] = ringkasan['total_hui']
        session['avg_total_utility'] = ringkasan['avg_total_utility']
        session['avg_u_support'] = ringkasan['avg_u_support']
        session['avg_uconf'] = ringkasan['avg_uconf']
        session['waktu_proses'] = waktu_proses
        session['total_item'] = ringkasan['total_item']
        


        # =====================================
        # REDIRECT KE HALAMAN HASIL
        # =====================================

        return redirect(
            url_for('halaman_hasil_huim')
        )

    except Exception as e:

        return f"""
        <h1>ERROR EFIM</h1>
        <pre>{str(e)}</pre>
        """
    
# =========================================
# HALAMAN HASIL HUIM
# =========================================

@app.route('/admin/hasil_huim')
def halaman_hasil_huim():

    nama_file = session.get('nama_file')

    # =====================================
    # LOAD FILE HUI
    # =====================================

    path_hasil = os.path.join(
        HASIL_FOLDER,
        nama_file
    )

    hasil_hui = []

    if os.path.exists(path_hasil):

        df_hui = pd.read_pickle(path_hasil)

        hasil_hui = df_hui.to_dict(
            orient='records'
        )

    # =====================================
    # LOAD FILE UCONF
    # =====================================

    nama_uconf = nama_file.replace(
        '.pkl',
        '_uconf.pkl'
    )

    path_uconf = os.path.join(
        HASIL_FOLDER,
        nama_uconf
    )

    uconf_df = []

    if os.path.exists(path_uconf):

        df_uconf = pd.read_pickle(path_uconf)

        uconf_df = df_uconf.to_dict(
            orient='records'
        )

    return render_template(

        'admin/hasil_huim.html',

        hasil_hui=hasil_hui,

        uconf_df=uconf_df,

        minutil=session.get('minutil'),

        nama_file=nama_file,

        total_hui=session.get('total_hui'),

        avg_total_utility=session.get('avg_total_utility'),

        avg_u_support=session.get('avg_u_support'),

        avg_uconf=session.get('avg_uconf'),

        waktu_proses=session.get('waktu_proses'),

        total_item=session.get('total_item'),

       
    )

# =========================================
# HALAMAN PILIH MODEL
# =========================================

@app.route('/admin/pilih-model')
def halaman_pilih_model():

    path_model = os.path.join(
        MODEL_FOLDER,
        'ringkasan_model.pkl'
    )

    if not os.path.exists(path_model):

        models = []

    else:

        df_model = pd.read_pickle(
            path_model
        )

        models = df_model.to_dict(
            orient='records'
        )

    return render_template(

        'admin/pilih_model.html',

        models=models

    )
@app.route('/admin/detail_model/<path:nama_file>')
def detail_model(nama_file):

    path_file = os.path.join(
        HASIL_FOLDER,
        nama_file
    )

    if not os.path.exists(path_file):

        return jsonify({
            'error': 'File tidak ditemukan'
        }), 404

    # =====================================
    # LOAD HUI
    # =====================================

    hasil_hui = pd.read_pickle(path_file)

    # =====================================
    # LOAD UCONF
    # =====================================

    nama_uconf = nama_file.replace(
        '.pkl',
        '_uconf.pkl'
    )

    path_uconf = os.path.join(
        HASIL_FOLDER,
        nama_uconf
    )

    if os.path.exists(path_uconf):

        uconf_df = pd.read_pickle(path_uconf)

    else:

        uconf_df = pd.DataFrame()

    # =====================================
    # TOTAL ITEM UNIK HUI
    # =====================================

    semua_item = set()

    for itemset in hasil_hui['Itemset']:

        for item in itemset:

            semua_item.add(item)

    total_item_hui = len(semua_item)

    # =====================================
    # RESPONSE
    # =====================================

    response = {

        'nama_file': nama_file,

        'total_hui': len(hasil_hui),

        'total_item': total_item_hui,

        'avg_total_utility':
            round(
                hasil_hui['Utility'].mean(),
                2
            ),

        'avg_u_support': round(
            hasil_hui['u-support'].mean(),
            6
        ),

        'avg_uconf': round(
            uconf_df['uconf'].mean(),
            6
        ) if len(uconf_df) > 0 else 0,

        'hasil_hui': hasil_hui.to_dict(
            orient='records'
        ),

        'uconf_df': uconf_df.to_dict(
            orient='records'
        )

    }

    return jsonify(response)

# =========================================
# SIMPAN MODEL
# =========================================

@app.route('/simpan-model', methods=['POST'])
def simpan_model():

    model_terpilih = request.form.get(
        'model_terpilih'
    )

    # =====================================
    # JIKA BELUM PILIH MODEL
    # =====================================

    if model_terpilih is None:

        return redirect(
            url_for('halaman_pilih_model')
        )

    # =====================================
    # SIMPAN POLA REKOMENDASI
    # =====================================

    with open(
        'model/pola_rekomendasi.txt',
        'w'
    ) as f:

        f.write(
            str(model_terpilih)
        )

    # =====================================
    # TANPA FLASH MESSAGE
    # =====================================

    return redirect(
        url_for('halaman_pilih_model')
    )
# =========================================
# PROSES REKOMENDASI
# =========================================

@app.route('/user/proses_rekomendasi', methods=['POST'])
def proses_rekomendasi():

    item_input = request.form['item']

    hasil = sistem_rekomendasi(item_input)

    # ambil list rekomendasi
    rekomendasi = hasil.get('rekomendasi', [])

    return render_template(
        'user/hasil_rekomendasi.html',
        hasil=hasil,
        rekomendasi=rekomendasi
    )

# =========================================
# RUN
# =========================================

if __name__ == '__main__':

    app.run(debug=True) 