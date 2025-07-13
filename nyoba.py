import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Data contoh penjualan buah (bisa diganti dengan data real)
def generate_sales_data():
    fruits = ['Apel', 'Pisang', 'Anggur', 'Stroberi', 'Mangga', 'Jeruk']
    data = {
        'Tanggal': pd.date_range(end=datetime.today(), periods=30).date,
    }
    
    for fruit in fruits:
        # Generate random sales data with different patterns
        if fruit == 'Pisang':  # Most popular
            data[fruit] = np.random.randint(20, 50, 30)
        elif fruit == 'Apel':  # Second popular
            data[fruit] = np.random.randint(15, 40, 30)
        else:
            data[fruit] = np.random.randint(5, 30, 30)
            
    return pd.DataFrame(data)

# Fungsi untuk menghitung metrik penjualan
def calculate_sales_metrics(df):
    metrics = {
        'Buah': [],
        'Total Penjualan': [],
        'Rata-rata Harian': [],
        'ROP': [],
        'EOQ': [],
        'Status': []
    }
    
    for fruit in df.columns[1:]:
        daily_avg = df[fruit].mean()
        metrics['Buah'].append(fruit)
        metrics['Total Penjualan'].append(df[fruit].sum())
        metrics['Rata-rata Harian'].append(daily_avg)
        
        # Simplified ROP calculation (lead_time * daily_demand)
        # Assume 2 days lead time for all fruits
        metrics['ROP'].append(2 * daily_avg)
        
        # Simplified EOQ calculation
        # Assume ordering cost 10000 and holding cost 500 for all fruits
        metrics['EOQ'].append(np.sqrt((2 * daily_avg * 10000) / 500))
        
        # Stock status (just for demo)
        current_stock = np.random.randint(0, 100)  # Simulate random current stock
        rop_value = 2 * daily_avg
        if current_stock < rop_value:
            metrics['Status'].append(f"🚨 Perlu Reorder (Stok: {current_stock})")
        else:
            metrics['Status'].append(f"🟢 Aman (Stok: {current_stock})")
    
    return pd.DataFrame(metrics)

# Layout Streamlit
st.set_page_config(layout="wide", page_title="Analisis Buah & Perhitungan ROP")

# Header dengan CSS
st.markdown("""
<style>
.header {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.fruit-card {
    padding: 15px;
    border-radius: 10px;
    background-color: #ffffff;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🍊 Analisis Penjualan Buah & Perhitungan ROP</h1></div>', unsafe_allow_html=True)

# Generate sample data
sales_df = generate_sales_data()
metrics_df = calculate_sales_metrics(sales_df)

# Tampilkan metrik utama
st.markdown("### 📊 Performa Penjualan 30 Hari Terakhir")
col1, col2, col3 = st.columns(3)
col1.metric("Total Transaksi", f"{len(sales_df)} hari")
col2.metric("Buah Terlaris", metrics_df.sort_values('Total Penjualan', ascending=False).iloc[0]['Buah'])
col3.metric("Total Penjualan", f"{sales_df.iloc[:,1:].sum().sum()} unit")

# Buat tab untuk analisis
tab1, tab2 = st.tabs(["📈 Analisis Buah", "📦 Manajemen Persediaan"])

with tab1:
    st.markdown("### 🍎 Performa Per jenis Buah")
    
    # Urutkan berdasarkan penjualan
    metrics_df = metrics_df.sort_values('Total Penjualan', ascending=False)
    
    # Tampilkan dalam bentuk kartu
    for idx, row in metrics_df.iterrows():
        with st.expander(f"{row['Buah']} - Total {row['Total Penjualan']} unit", expanded=(idx==0)):
            col1, col2, col3 = st.columns(3)
            col1.metric("Rata-rata Harian", f"{row['Rata-rata Harian']:.1f} unit")
            col2.metric("ROP (Reorder Point)", f"{row['ROP']:.1f} unit")
            col3.metric("Status Persediaan", row['Status'])
            
            # Buat chart untuk buah tersebut
            fig, ax = plt.subplots(figsize=(10, 3))
            ax.plot(sales_df['Tanggal'], sales_df[row['Buah']], label='Penjualan Harian')
            ax.axhline(row['Rata-rata Harian'], color='red', linestyle='--', label='Rata-rata')
            ax.set_title(f'Tren Penjualan {row["Buah"]}')
            ax.legend()
            st.pyplot(fig)

with tab2:
    st.markdown("### 📊 Perhitungan ROP & EOQ")
    
    # Pilih buah untuk perhitungan detail
    selected_fruit = st.selectbox("Pilih Buah untuk Analisis Detail", metrics_df['Buah'].values)
    
    if selected_fruit:
        fruit_data = sales_df[['Tanggal', selected_fruit]]
        avg_daily = fruit_data[selected_fruit].mean()
        
        with st.form(key='rop_calc_form'):
            st.markdown(f"**{selected_fruit}** - Rata-rata penjualan harian: {avg_daily:.1f} unit")
            
            # Input parameter
            col1, col2, col3 = st.columns(3)
            lead_time = col1.number_input("Lead Time (hari)", min_value=1, value=2, key='lead_time')
            ordering_cost = col2.number_input("Biaya Pemesanan (Rp)", min_value=1, value=10000, key='ordering_cost')
            holding_cost = col3.number_input("Biaya Penyimpanan (Rp/unit/hari)", min_value=1, value=500, key='holding_cost')
            
            submit_calc = st.form_submit_button("Hitung EOQ & ROP")
            
            if submit_calc:
                rop = lead_time * avg_daily
                eoq = np.sqrt((2 * avg_daily * ordering_cost) / holding_cost)
                
                st.success(f"**Reorder Point (ROP):** {rop:.1f} unit")
                st.success(f"**Economic Order Quantity (EOQ):** {eoq:.1f} unit")
                
                # Visualisasi level stok
                st.markdown("### 📉 Proyeksi Level Stok")
                
                days = np.arange(0, 20)
                initial_stock = eoq
                stock_levels = np.maximum(0, initial_stock - avg_daily * days)
                reorder_day = np.argmax(stock_levels <= rop)
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(days, stock_levels, label='Level Stok')
                ax.axhline(rop, color='r', linestyle='--', label='ROP')
                if reorder_day < len(days):
                    ax.axvline(reorder_day, color='g', linestyle=':', label='Waktu Reorder')
                ax.set_title(f'Proyeksi Stok {selected_fruit}')
                ax.set_xlabel('Hari')
                ax.set_ylabel('Unit')
                ax.legend()
                st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("""
<style>
.footer {
    text-align: center;
    padding: 10px;
    color: #666;
}
</style>
<div class="footer">
Dibuat oleh Mahasiswa Teknik Informatika untuk UMKM | © 2023
</div>
""", unsafe_allow_html=True)
