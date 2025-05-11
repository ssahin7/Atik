from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import os
import requests
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import joblib

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

# === Dosya Yolları ===
waste_csv_file = "data/guncellenmis_waste_detect (1).csv"
waste_excel_file = "data/yeni.xlsx"
user_file = "data/users.xlsx"
isletmeler_file = "data/işletmeler.xlsx"  # Türkçe karakterli dosya yolu

# === Model Yükleme ===
model = joblib.load('xgboost_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/match', methods=['POST'])
def match():
    df = pd.read_excel(waste_excel_file)
    query = request.form.get('query', '').lower()
    if not query:
        return jsonify({"message": "Arama boş bırakılamaz."})
    mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)
    results = df[mask]
    if results.empty:
        return jsonify({"message": "Sonuç bulunamadı."})
    output = results[['Atık Kodu', 'Atık Açıklaması', 'NACE Kodu', 'NACE Açıklaması']]
    return jsonify(output.to_dict(orient='records'))

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if not all([username, password, password2, company, email, phone, address]):
            return jsonify({'success': False, 'message': 'Lütfen tüm alanları doldurun.'})
        if password != password2:
            return jsonify({'success': False, 'message': 'Şifreler uyuşmuyor.'})

        if not os.path.exists(user_file):
            users_df = pd.DataFrame(columns=['Kullanıcı Adı', 'Şifre', 'İşletme Adı', 'E-posta', 'Telefon', 'Adres'])
            users_df.to_excel(user_file, index=False)

        users_df = pd.read_excel(user_file)

        if username in users_df['Kullanıcı Adı'].values:
            return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten mevcut.'})

        new_row = {
            'Kullanıcı Adı': username,
            'Şifre': password,
            'İşletme Adı': company,
            'E-posta': email,
            'Telefon': phone,
            'Adres': address
        }

        users_df = pd.concat([users_df, pd.DataFrame([new_row])], ignore_index=True)
        users_df.to_excel(user_file, index=False)

        return jsonify({'success': True, 'message': 'Kayıt başarılı!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Hata oluştu: {str(e)}'})

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({'success': False, 'message': 'Kullanıcı adı ve şifre gerekli.'})

        users_df = pd.read_excel(user_file)
        user_row = users_df[users_df['Kullanıcı Adı'].str.strip() == username.strip()]
        if user_row.empty:
            return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı.'})

        real_password = str(user_row.iloc[0]['Şifre']).strip()
        if password.strip() == real_password:
            session['username'] = username
            return jsonify({'success': True, 'message': 'Giriş başarılı!'})
        else:
            return jsonify({'success': False, 'message': 'Şifre yanlış.'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Hata oluştu: {str(e)}'})

@app.route('/get_profile', methods=['GET'])
def get_profile():
    try:
        username = session.get('username')
        if not username:
            return jsonify({'success': False, 'message': 'Giriş yapılmamış.'})

        users_df = pd.read_excel(user_file)
        user_row = users_df[users_df['Kullanıcı Adı'] == username].iloc[0]
        return jsonify({
            'success': True,
            'company': user_row.get('İşletme Adı', ''),
            'email': user_row.get('E-posta', ''),
            'phone': user_row.get('Telefon', ''),
            'address': user_row.get('Adres', ''),
            'vergi_no': user_row.get('Vergi No', ''),
            'sicil_no': user_row.get('Sicil No', ''),
            'web': user_row.get('Web Sitesi', ''),
            'earsiv': user_row.get('E-Arşiv Mail', ''),
            'nace': user_row.get('NACE Kodu', '')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        username = session.get('username')
        if not username:
            return jsonify({'success': False, 'message': 'Giriş yapılmamış.'})

        users_df = pd.read_excel(user_file)
        user_index = users_df[users_df['Kullanıcı Adı'] == username].index[0]

        users_df.at[user_index, 'İşletme Adı'] = request.form.get('company')
        users_df.at[user_index, 'E-posta'] = request.form.get('email')
        users_df.at[user_index, 'Telefon'] = request.form.get('phone')
        users_df.at[user_index, 'Adres'] = request.form.get('address')
        users_df.at[user_index, 'Vergi No'] = request.form.get('vergi_no')
        users_df.at[user_index, 'Sicil No'] = request.form.get('sicil_no')
        users_df.at[user_index, 'Web Sitesi'] = request.form.get('web')
        users_df.at[user_index, 'E-Arşiv Mail'] = request.form.get('earsiv')
        users_df.at[user_index, 'NACE Kodu'] = request.form.get('nace')

        users_df.to_excel(user_file, index=False)
        return jsonify({'success': True, 'message': 'Profil başarıyla güncellendi!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})

@app.route('/isletmeler', methods=['POST'])
def isletmeleri_getir():
    try:
        atik_kodu = request.form.get('atik_kodu', '').strip()
        if not atik_kodu:
            return jsonify({'success': False, 'message': 'Atık kodu girilmedi.'})

        df = pd.read_excel(isletmeler_file)

        # Kolon adı kesin olarak "waste" değilse, örneğin "Atık Kodu" ise burayı güncelle!
        if 'waste' not in df.columns:
            return jsonify({'success': False, 'message': 'Excel sütunlarında "waste" bulunamadı.'})

        matching = df[df['waste'].astype(str).str.contains(atik_kodu, case=False, na=False)]

        if matching.empty:
            return jsonify({'success': False, 'message': 'Bu atık kodunu işleyen firma bulunamadı.'})

        return jsonify({'success': True, 'firmalar': matching.to_dict(orient='records')})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Sunucu hatası: {str(e)}'})

# === ORS Yardımcıları ===
ORS_API_KEY = "5b3ce3597851110001cf6248379bdba122004719ad7efbf33cd0c929"

def adres_to_coords(adres, api_key):
    try:
        url = "https://api.openrouteservice.org/geocode/search"
        params = {"api_key": api_key, "text": adres, "boundary.country": "TR"}
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        coords = data["features"][0]["geometry"]["coordinates"]
        return coords[::-1]
    except Exception as e:
        print(f"Koordinat hatası: {e}")
        return None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)

@app.route('/tahmin', methods=['POST'])
def tahmin():
    adres = request.form.get('adres')
    atik_kodu = request.form.get('atik_kodu')
    if not adres or not atik_kodu:
        return jsonify({"success": False, "message": "Adres ve atık kodu boş olamaz."})

    sonuc = firma_tahmini_yap(adres, atik_kodu)
    return jsonify(sonuc)

def firma_tahmini_yap(adres, atik_kodu):
    try:
        df = pd.read_csv(waste_csv_file)
        df = df[df['waste'].astype(str).str.strip() == atik_kodu.strip()]

        if df.empty:
            return {"success": False, "message": f"{atik_kodu} kodlu atığı işleyen firma bulunamadı."}

        coords = adres_to_coords(adres, ORS_API_KEY)
        if not coords:
            return {"success": False, "message": "Adres koordinata çevrilemedi."}

        df["mesafe_km"] = df.apply(lambda row: haversine(coords[0], coords[1], row["lat"], row["lon"]), axis=1)

        features = [
            "fiyat", "sistem_suresi", "toplam_satis", "puanlama", "geri_donusum_lisansi",
            "karbon_ayak_izi", "lojistik_uygunluk", "eslesme_orani", "mesafe_km"
        ]

        X_input = df[features].mean().to_frame().T
        pred_encoded = model.predict(X_input)
        pred_label = label_encoder.inverse_transform(pred_encoded)[0]

        if pred_label not in df["firma_adi"].values:
            return {"success": False, "message": f"{pred_label} firması bu atıkla ilişkili değil."}

        secilen = df[df["firma_adi"] == pred_label].sort_values("puanlama", ascending=False).iloc[0]

        return {
            "success": True,
            "firma": pred_label,
            "adres": secilen["adres"],
            "mesafe": secilen["mesafe_km"],
            "puan": secilen["puanlama"],
            "karbon": secilen["karbon_ayak_izi"],
            "eslesme": secilen["eslesme_orani"]
        }

    except Exception as e:
        return {"success": False, "message": f"Beklenmeyen hata: {str(e)}"}

if __name__ == '__main__':
    app.run(debug=True)
