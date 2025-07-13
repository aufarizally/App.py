import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Fungsi untuk menghitung metrik penjualan dan ROP
def calculate_metrics(sales_df):
    fruits = sales_df.columns[1:]  # Kolom pertama adalah tanggal
    metrics = {
        'Buah': [],
        'Total Penjualan': [],
        'Rata-rata Harian': [],
        'ROP': [],
        'Status Stok': []
    }
    
    for fruit in fruits:
        daily_avg = sales_df[fruit].mean()
        total_sales = sales_df[fruit].sum()
        
        metrics['Buah'].append(fruit)
        metrics['Total Penjualan'].append(total_sales)
        metrics['Rata-rata Harian'].append(daily_avg)
        
        # Hitung ROP (Reorder Point) = lead_time * rata2 harian
        rop = 2 * daily_avg  # Default lead_time 2 hari
        metrics['ROP'].append(round(rop, 2))
        
        # Contoh status stok (asumsi stok saat ini)
        current_stock = total_sales / len(sales_df) * 3  # Contoh perhitungan
        if current_stock < rop:
            metrics['Status Stok'].append("🚨 Perlu Reorder")
        else:
            metrics['Status Stok'].append("🟢 Aman")
    
    return pd.DataFrame(metrics)

# Konfigurasi halaman
st.set_page_config(layout="wide", page_title="Input Penjualan & Analisis Buah")

# CSS untuk styling
st.markdown("""
<style>
.header {
    padding: 20px;
    background-color: #f0f2f6;
    border-radius: 10px;
    margin-bottom: 20px;
}
.fruit-card {
    padding: 15px;
    border-radius: 10px;
    background-color: #ffffff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
.date-input {
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header"><h1>📊 Input Penjualan Harian & Analisis Buah Terlaris</h1></div>', unsafe_allow_html=True)

# Inisialisasi atau load data penjualan
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(columns=['Tanggal', 'Apel', 'Pisang', 'Anggur', 'Stroberi', 'Mangga', 'Jeruk'])

# Tab untuk input dan analisis
tab1, tab2 = st.tabs(["📝 Input Penjualan", "📈 Analisis & ROP"])

with tab1:
    st.markdown("### Masukkan Data Penjualan Harian")
    
    # Input tanggal
    sale_date = st.date_input("Tanggal Penjualan", datetime.today(), key='sale_date')
    
    # Input penjualan per buah
    st.markdown("**Jumlah Terjual (unit)**")
    cols = st.columns(3)
    
    with cols[0]:
        apel = st.number_input("Apel", min_value=0, key='apel')
        pisang = st.number_input("Pisang", min_value=0, key='pisang')
    with cols[1]:
        anggur = st.number_input("Anggur", min_value=0, key='anggur')
        stroberi = st.number_input("Stroberi", min_value=0, key='stroberi')
    with cols[2]:
        mangga = st.number_input("Mangga", min_value=0, key='mangga')
        jeruk = st.number_input("Jeruk", min_value=0, key='jeruk')
    
    # Tombol submit
    if st.button("Simpan Data Penjualan", key='save_sales'):
        new_row = {
            'Tanggal': sale_date,
            'Apel': apel,
            'Pisang': pisang,
            'Anggur': anggur,
            'Stroberi': stroberi,
            'Mangga': mangga,
            'Jeruk': jeruk
        }
        
        st.session_state.sales_data = pd.concat([
            st.session_state.sales_data, 
            pd.DataFrame([new_row])
        ], ignore_index=True)
        
        st.success("Data penjualan berhasil disimpan!")
    
    # Tampilkan data yang sudah diinput
    st.markdown("### Riwayat Penjualan")
    if not st.session_state.sales_data.empty:
        st.dataframe(st.session_state.sales_data.sort_values('Tanggal', ascending=False))
    else:
        st.info("Belum ada data penjualan yang diinput.")

with tab2:
    if not st.session_state.sales_data.empty:
        # Hitung metrik
        metrics_df = calculate_metrics(st.session_state.sales_data)
        metrics_df = metrics_df.sort_values('Total Penjualan', ascending=False)
        
        # Buah terlaris
        st.markdown("### 🏆 Buah Terlaris")
        top_fruit = metrics_df.iloc[0]
        st.markdown(f"<div style='background-color:#e6f7ff; padding:15px; border-radius:10px;'>"
                    f"<h3 style='color:#1890ff;'>🥇 {top_fruit['Buah']}</h3>"
                    f"<p>Total Penjualan: {int(top_fruit['Total Penjualan'])} unit</p>"
                    f"<p>Rata-rata Harian: {round(top_fruit['Rata-rata Harian'],1)} unit</p>"
                    "</div>", unsafe_allow_html=True)
        
        # Grafik perbandingan penjualan
        st.markdown("### 📊 Perbandingan Penjualan Buah")
        fig, ax = plt.subplots(figsize=(10, 5))
        metrics_df.sort_values('Total Penjualan', ascending=True).plot(
            x='Buah', y='Total Penjualan', kind='barh', ax=ax, color='#52c41a')
        ax.set_title('Total Penjualan per Jenis Buah')
        ax.set_xlabel('Jumlah Terjual (unit)')
        st.pyplot(fig)
        
        # Tabel metrik & ROP
        st.markdown("### 📦 Analisis Persediaan & ROP")
        st.dataframe(metrics_df[['Buah', 'Rata-rata Harian', 'ROP', 'Status Stok']])
        
        # Perhitungan EOQ khusus untuk buah tertentu
        st.markdown("### 🧮 Kalkulator EOQ & ROP Detail")
        selected_fruit = st.selectbox("Pilih Buah untuk Analisis Detail:", metrics_df['Buah'].values)
        
        if selected_fruit:
            fruit_data = metrics_df[metrics_df['Buah'] == selected_fruit].iloc[0]
            
            with st.expander("Kalkulator Lanjutan", expanded=True):
                col1, col2 = st.columns(2)
                lead_time = col1.number_input("Lead Time (hari)", min_value=1, value=2, key=f'lead_time_{selected_fruit}')
                ordering_cost = col1.number_input("Biaya Pemesanan (Rp)", min_value=1, value=10000, key=f'ordering_{selected_fruit}')
                holding_cost = col2.number_input("Biaya Penyimpanan (Rp/unit/hari)", min_value=1, value=500, key=f'holding_{selected_fruit}')
                
                # Hitung ulang ROP dan EOQ
                daily_avg = fruit_data['Rata-rata Harian']
                rop = lead_time * daily_avg
                eoq = np.sqrt((2 * daily_avg * ordering_cost) / holding_cost)
                
                st.metric("Reorder Point (ROP)", f"{rop:.1f} unit")
                st.metric("Economic Order Quantity (EOQ)", f"{eoq:.1f} unit")
                
                # Visualisasi level stok
                st.markdown("**📉 Proyeksi Level Stok**")
                days = np.arange(0, 15)
                stock_levels = np.maximum(0, eoq - daily_avg * days)
                
                fig, ax = plt.subplots(figsize=(10, 3))
                ax.plot(days, stock_levels, label='Level Stok')
                ax.axhline(rop, color='r', linestyle='--', label='ROP')
                ax.fill_between(days, 0, rop, color='red', alpha=0.1, label='Zona Reorder')
                ax.set_title(f'Proyeksi Stok {selected_fruit}')
                ax.legend()
                st.pyplot(fig)
    else:
        st.warning("Silakan input data penjualan terlebih dahulu di tab Input Penjualan")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center; color:#666;'>DIBUAT UNTUK TUGAS UAS MATEMATIKA PEMINATAN</div>", unsafe_allow_html=True)
