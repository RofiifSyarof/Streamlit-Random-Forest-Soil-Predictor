import streamlit as st
import joblib
import numpy as np
import pandas as pd
from PIL import Image

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi Kesuburan Tanah", 
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load model (dengan error handling)
@st.cache_resource
def load_model():
    try:
        model = joblib.load('best_rf_model.joblib')
        st.success("Model berhasil dimuat!")
        return model
    except FileNotFoundError:
        st.error("File model tidak ditemukan. Pastikan 'best_rf_model.joblib' ada di direktori yang benar.")
        return None
    except Exception as e:
        st.error(f"Gagal memuat model: {str(e)}")
        return None

model = load_model()

# CSS untuk mempercantik tampilan
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #28a745;
    }
    .st-b7 {
        color: white;
    }
    .css-1aumxhk {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar untuk informasi tambahan
with st.sidebar:
    st.header("Tentang Aplikasi")
    st.markdown("""
    Aplikasi ini memprediksi kesuburan tanah berdasarkan parameter:
    - Nutrisi (N, P, K)
    - pH dan EC
    - Kandungan organik
    - Mikronutrien (Zn, Fe, Cu, Mn, B)
    """)
    
    # Tambahkan gambar atau logo
    try:
        image = Image.open('soil_fertility.png')  # Ganti dengan path gambar Anda
        st.image(image, caption='Ilustrasi Kesuburan Tanah')
    except:
        pass
    
    st.markdown("---")
    st.caption("© 2025 Muhammad Rofiif Syarof Nur Aufaa. All rights reserved.")

# Judul aplikasi
st.title("🌱 Prediksi Kesuburan Tanah")
st.markdown("Masukkan parameter tanah di bawah ini untuk mendapatkan prediksi kesuburan:")

# Bagi layout menjadi 3 kolom
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Makronutrien")
    N = st.number_input("Nitrogen (N) [mg/kg]", min_value=0.0, step=0.1, value=20.0)
    P = st.number_input("Fosfor (P) [mg/kg]", min_value=0.0, step=0.1, value=15.0)
    K = st.number_input("Kalium (K) [mg/kg]", min_value=0.0, step=0.1, value=25.0)
    pH = st.number_input("pH [0-14]", min_value=0.0, max_value=14.0, step=0.1, value=6.5)

with col2:
    st.subheader("Karakteristik Tanah")
    EC = st.number_input("EC (dS/m)", min_value=0.0, step=0.1, value=0.5)
    OC = st.number_input("Organic Carbon (%)", min_value=0.0, max_value=100.0, step=0.1, value=1.5)
    S = st.number_input("Sulfur (S) [mg/kg]", min_value=0.0, step=0.1, value=10.0)
    Zn = st.number_input("Zinc (Zn) [mg/kg]", min_value=0.0, step=0.1, value=2.0)

with col3:
    st.subheader("Mikronutrien")
    Fe = st.number_input("Iron (Fe) [mg/kg]", min_value=0.0, step=0.1, value=5.0)
    Cu = st.number_input("Copper (Cu) [mg/kg]", min_value=0.0, step=0.1, value=1.0)
    Mn = st.number_input("Manganese (Mn) [mg/kg]", min_value=0.0, step=0.1, value=4.0)
    B = st.number_input("Boron (B) [mg/kg]", min_value=0.0, step=0.1, value=0.5)

# Tombol prediksi
if st.button("**Prediksi Kesuburan**", type="primary", use_container_width=True):
    if None in [N, P, K, pH, EC, OC, S, Zn, Fe, Cu, Mn, B]:
        st.warning("Harap isi semua parameter!")
    elif model is None:
        st.error("Model tidak tersedia. Silakan cek file model.")
    else:
        with st.spinner("🔍 Menganalisis data tanah..."):
            try:
                # Konversi input ke array numpy
                input_data = np.array([[N, P, K, pH, EC, OC, S, Zn, Fe, Cu, Mn, B]])
                
                # Prediksi
                prediction = model.predict(input_data)[0]
                proba = model.predict_proba(input_data)[0]  # Probabilitas
                confidence = max(proba) * 100
                
                # Simpan hasil di session state
                st.session_state['last_prediction'] = {
                    'result': prediction,
                    'confidence': confidence,
                    'input_data': input_data
                }
                
            except Exception as e:
                st.error(f"Terjadi error saat prediksi: {str(e)}")

# Tampilkan hasil (jika ada)
if 'last_prediction' in st.session_state:
    pred = st.session_state['last_prediction']
    
    st.markdown("---")
    st.subheader("Hasil Prediksi Kesuburan Tanah")
    
    # Tampilkan input data dalam tabel
    st.markdown("**Parameter Input:**")
    input_df = pd.DataFrame(
        pred['input_data'],
        columns=['N', 'P', 'K', 'pH', 'EC', 'OC', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'B'],
        index=['Nilai']
    ).T
    st.dataframe(input_df.style.format("{:.1f}"), height=400)
    
    # Tampilkan hasil prediksi
    col_result, col_confidence = st.columns(2)
    
    with col_result:
        if pred['result'] == 1:
            st.success(f"**✅ Tanah SUBUR**")
        else:
            st.error(f"**❌ Tanah KURANG SUBUR**")
    
    with col_confidence:
        st.metric("Tingkat Kepercayaan", f"{pred['confidence']:.1f}%")
        st.progress(int(pred['confidence']))
    
    # Rekomendasi lebih detail
    st.markdown("---")
    st.subheader("Rekomendasi")
    
    if pred['result'] == 1:
        st.markdown("""
            **Tanah Anda dalam kondisi subur. Berikut rekomendasi pemeliharaan:**
            
            - ✅ **Pertahankan kadar bahan organik** dengan penambahan kompos/pupuk kandang
            - 🔄 **Rotasi tanaman** untuk menjaga keseimbangan nutrisi
            - 🌾 **Pilih tanaman bernilai tinggi** yang sesuai dengan karakteristik tanah
            - 📊 **Pantau parameter tanah** secara berkala (3-6 bulan sekali)
        """)
    else:
        st.markdown("""
            **Tanah Anda membutuhkan perbaikan. Berikut rekomendasi tindakan:**
            
            - 🌱 **Tambahkan pupuk organik** (kompos/pupuk kandang) 5-10 ton/ha
            - 🧪 **Perbaiki pH tanah**:
              - Jika pH < 6: Tambahkan kapur pertanian
              - Jika pH > 7.5: Berikan belerang atau bahan organik
            - ⚖️ **Pupuk berimbang** sesuai kebutuhan:
              - Defisiensi N: Pupuk urea/ZA
              - Defisiensi P: Pupuk SP-36/rock phosphate
              - Defisiensi K: Pupuk KCl/ZK
            - 📞 **Konsultasikan dengan ahli tanah** untuk analisis lebih mendalam
        """)
        
        # Tampilkan parameter yang perlu diperhatikan
        st.markdown("**Parameter yang perlu diperbaiki:**")
        problematic_params = []
        threshold_values = {
            'N': 20, 'P': 15, 'K': 20, 'pH': (6, 7), 'OC': 1.5, 'Zn': 2, 'Fe': 4.5, 'Mn': 2
        }
        
        for param, value in zip(['N', 'P', 'K', 'pH', 'OC', 'Zn', 'Fe', 'Mn'], 
                              [N, P, K, pH, OC, Zn, Fe, Mn]):
            if param in threshold_values:
                if param == 'pH':
                    if value < threshold_values[param][0] or value > threshold_values[param][1]:
                        problematic_params.append(f"{param} (Nilai: {value}, Ideal: {threshold_values[param][0]}-{threshold_values[param][1]})")
                else:
                    if value < threshold_values[param]:
                        problematic_params.append(f"{param} (Nilai: {value}, Minimal ideal: {threshold_values[param]})")
        
        if problematic_params:
            st.warning("\n".join([f"- {param}" for param in problematic_params]))
        else:
            st.info("Semua parameter dalam rentang normal, tetapi kombinasi faktor lain mempengaruhi kesuburan.")

# Catatan tambahan
st.markdown("---")
st.caption("""
    ℹ️ **Catatan:**  
    - Gunakan data hasil pengukuran laboratorium untuk akurasi maksimal  
    - Prediksi ini berdasarkan model machine learning dan bersifat sebagai panduan awal  
    - Kondisi lapangan mungkin memerlukan penyesuaian tambahan  
    - Update terakhir model: Mei 2025
""")