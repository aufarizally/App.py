import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from datetime import datetime, timedelta

# Konfigurasi halaman
st.set_page_config(
    page_title="Sistem Optimasi Produksi Terintegrasi",
    page_icon="🏭",
    layout="wide"
)

# Judul utama
st.title("🏭 Sistem Optimasi Produksi Terintegrasi")
st.markdown("**Contoh Industri: Indofood - Kecap, Tepung Bogasari, dan Bumbu Racik**")

# Sidebar untuk navigasi
st.sidebar.title("📊 Menu Navigasi")
menu = st.sidebar.selectbox(
    "Pilih Modul:",
    ["Dashboard Utama", "Optimasi Produksi", "Model Persediaan (EOQ & ROP)", "Model Antrian", "Analisis Terintegrasi"]
)

# Data produk dan bahan baku - WAKTU PRODUKSI DIPERBARUI
PRODUCTS = {
    "Kecap Manis": {
        "bahan_baku": {"Kedelai": 0.3, "Gula Aren": 0.2, "Garam": 0.05, "Air": 0.4},
        "harga_jual": 15000,
        "biaya_produksi": 8000,
        "waktu_produksi": 5/60  # 5 menit = 0.083 jam per unit
    },
    "Tepung Bogasari": {
        "bahan_baku": {"Gandum": 0.8, "Pengawet": 0.02, "Vitamin": 0.01},
        "harga_jual": 12000,
        "biaya_produksi": 7000,
        "waktu_produksi": 9/60  # 9 menit = 0.15 jam per unit
    },
    "Bumbu Racik": {
        "bahan_baku": {"Bawang Merah": 0.25, "Bawang Putih": 0.15, "Cabai": 0.2, "Garam": 0.1, "Rempah": 0.3},
        "harga_jual": 8000,
        "biaya_produksi": 4500,
        "waktu_produksi": 6/60  # 6 menit = 0.1 jam per unit
    }
}

BAHAN_BAKU = {
    "Kedelai": {"harga": 8000, "lead_time": 7, "holding_cost": 0.15},
    "Gula Aren": {"harga": 12000, "lead_time": 5, "holding_cost": 0.12},
    "Garam": {"harga": 3000, "lead_time": 3, "holding_cost": 0.08},
    "Air": {"harga": 500, "lead_time": 1, "holding_cost": 0.05},
    "Gandum": {"harga": 6000, "lead_time": 14, "holding_cost": 0.18},
    "Pengawet": {"harga": 25000, "lead_time": 21, "holding_cost": 0.25},
    "Vitamin": {"harga": 50000, "lead_time": 30, "holding_cost": 0.30},
    "Bawang Merah": {"harga": 15000, "lead_time": 2, "holding_cost": 0.20},
    "Bawang Putih": {"harga": 18000, "lead_time": 3, "holding_cost": 0.22},
    "Cabai": {"harga": 20000, "lead_time": 2, "holding_cost": 0.25},
    "Rempah": {"harga": 35000, "lead_time": 10, "holding_cost": 0.28}
}

def calculate_eoq(demand, order_cost, holding_cost, unit_cost):
    """Menghitung Economic Order Quantity"""
    eoq = math.sqrt((2 * demand * order_cost) / (holding_cost * unit_cost))
    return eoq

def calculate_rop(demand_rate, lead_time, safety_stock=0):
    """Menghitung Reorder Point"""
    rop = (demand_rate * lead_time) + safety_stock
    return rop

def calculate_queue_metrics(arrival_rate, service_rate, servers=1):
    """Menghitung metrik model antrian M/M/1 atau M/M/c"""
    if servers == 1:
        # M/M/1 model
        rho = arrival_rate / service_rate
        if rho >= 1:
            return None  # Sistem tidak stabil
        
        l_q = (rho ** 2) / (1 - rho)  # Panjang antrian
        l_s = rho / (1 - rho)  # Jumlah pelanggan dalam sistem
        w_q = l_q / arrival_rate  # Waktu tunggu dalam antrian
        w_s = l_s / arrival_rate  # Waktu tunggu dalam sistem
        
        return {
            "utilization": rho,
            "avg_queue_length": l_q,
            "avg_system_length": l_s,
            "avg_wait_time": w_q,
            "avg_system_time": w_s
        }
    else:
        # M/M/c model (simplified)
        rho = arrival_rate / (servers * service_rate)
        if rho >= 1:
            return None
        
        # Simplified calculation for M/M/c
        l_s = arrival_rate / (service_rate - arrival_rate/servers)
        w_s = l_s / arrival_rate
        
        return {
            "utilization": rho,
            "avg_system_length": l_s,
            "avg_system_time": w_s,
            "servers": servers
        }

def optimize_production(products, constraints):
    """Optimasi produksi sederhana menggunakan profit per unit waktu"""
    results = []
    
    for product, data in products.items():
        profit_per_unit = data["harga_jual"] - data["biaya_produksi"]
        profit_per_hour = profit_per_unit / data["waktu_produksi"]
        
        results.append({
            "Produk": product,
            "Profit per Unit": profit_per_unit,
            "Waktu Produksi (jam)": data["waktu_produksi"],
            "Waktu Produksi (menit)": data["waktu_produksi"] * 60,
            "Profit per Jam": profit_per_hour,
            "Prioritas": len(results) + 1
        })
    
    # Sorting berdasarkan profit per jam
    results.sort(key=lambda x: x["Profit per Jam"], reverse=True)
    for i, result in enumerate(results):
        result["Prioritas"] = i + 1
    
    return results

# DASHBOARD UTAMA
if menu == "Dashboard Utama":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Produk", len(PRODUCTS))
    with col2:
        st.metric("Total Bahan Baku", len(BAHAN_BAKU))
    with col3:
        total_profit = sum([v["harga_jual"] - v["biaya_produksi"] for v in PRODUCTS.values()])
        st.metric("Total Profit Potensial", f"Rp {total_profit:,}")
    
    st.subheader("📈 Overview Produk")
    
    # Membuat dataframe untuk visualisasi
    df_products = pd.DataFrame([
        {
            "Produk": k,
            "Harga Jual": v["harga_jual"],
            "Biaya Produksi": v["biaya_produksi"],
            "Profit": v["harga_jual"] - v["biaya_produksi"],
            "Waktu Produksi (menit)": v["waktu_produksi"] * 60
        }
        for k, v in PRODUCTS.items()
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(df_products, x="Produk", y=["Harga Jual", "Biaya Produksi"], 
                     title="Perbandingan Harga Jual vs Biaya Produksi")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.pie(df_products, values="Profit", names="Produk", 
                     title="Distribusi Profit per Produk")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Tampilkan tabel waktu produksi yang diperbarui
    st.subheader("⏱️ Waktu Produksi Terbaru")
    st.dataframe(df_products[["Produk", "Waktu Produksi (menit)", "Profit"]], use_container_width=True)

# OPTIMASI PRODUKSI  
elif menu == "Optimasi Produksi":
    st.header("🎯 Optimasi Produksi")
    
    st.subheader("Parameter Optimasi")
    col1, col2 = st.columns(2)
    
    with col1:
        kapasitas_harian = st.number_input("Kapasitas Produksi Harian (jam)", value=16, min_value=8, max_value=24)
        biaya_setup = st.number_input("Biaya Setup per Produk (Rp)", value=500000, min_value=0)
    
    with col2:
        target_profit = st.number_input("Target Profit Harian (Rp)", value=10000000, min_value=0)
        efisiensi_mesin = st.slider("Efisiensi Mesin (%)", 60, 100, 85)
    
    # Hitung optimasi
    optimization_results = optimize_production(PRODUCTS, {
        "kapasitas": kapasitas_harian,
        "efisiensi": efisiensi_mesin / 100
    })
    
    st.subheader("📊 Hasil Optimasi Produksi")
    df_opt = pd.DataFrame(optimization_results)
    st.dataframe(df_opt, use_container_width=True)
    
    # Visualisasi prioritas produksi
    fig3 = px.bar(df_opt, x="Produk", y="Profit per Jam", 
                 color="Prioritas", title="Prioritas Produksi Berdasarkan Profit per Jam")
    st.plotly_chart(fig3, use_container_width=True)
    
    # Simulasi produksi optimal
    st.subheader("🔧 Simulasi Produksi Optimal")
    
    total_waktu = 0
    total_profit = 0
    produksi_plan = []
    
    for result in optimization_results:
        produk = result["Produk"]
        waktu_per_unit = PRODUCTS[produk]["waktu_produksi"]
        profit_per_unit = result["Profit per Unit"]
        
        # Hitung berapa unit yang bisa diproduksi
        sisa_waktu = kapasitas_harian - total_waktu
        unit_maksimal = int(sisa_waktu / waktu_per_unit) if sisa_waktu > 0 else 0
        
        if unit_maksimal > 0:
            waktu_digunakan = unit_maksimal * waktu_per_unit
            profit_dihasilkan = unit_maksimal * profit_per_unit
            
            produksi_plan.append({
                "Produk": produk,
                "Unit Diproduksi": unit_maksimal,
                "Waktu Digunakan (jam)": waktu_digunakan,
                "Waktu Digunakan (menit)": waktu_digunakan * 60,
                "Profit Dihasilkan": profit_dihasilkan
            })
            
            total_waktu += waktu_digunakan
            total_profit += profit_dihasilkan
    
    if produksi_plan:
        df_plan = pd.DataFrame(produksi_plan)
        st.dataframe(df_plan, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Waktu Terpakai", f"{total_waktu:.1f} jam ({total_waktu*60:.0f} menit)")
        with col2:
            st.metric("Efisiensi Waktu", f"{(total_waktu/kapasitas_harian)*100:.1f}%")
        with col3:
            st.metric("Total Profit", f"Rp {total_profit:,.0f}")

# MODEL PERSEDIAAN (EOQ & ROP)
elif menu == "Model Persediaan (EOQ & ROP)":
    st.header("📦 Model Persediaan - EOQ & ROP")
    
    # Pilih bahan baku
    selected_material = st.selectbox("Pilih Bahan Baku:", list(BAHAN_BAKU.keys()))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parameter EOQ")
        annual_demand = st.number_input("Permintaan Tahunan (kg)", value=50000, min_value=1000)
        order_cost = st.number_input("Biaya Pemesanan (Rp)", value=200000, min_value=10000)
        
    with col2:
        st.subheader("Parameter ROP")
        daily_demand = annual_demand / 365
        lead_time = BAHAN_BAKU[selected_material]["lead_time"]
        safety_stock = st.number_input("Safety Stock (kg)", value=500, min_value=0)
        
        st.info(f"Lead Time: {lead_time} hari")
        st.info(f"Permintaan Harian: {daily_demand:.1f} kg")
    
    # Hitung EOQ dan ROP
    unit_cost = BAHAN_BAKU[selected_material]["harga"]
    holding_cost_rate = BAHAN_BAKU[selected_material]["holding_cost"]
    
    eoq = calculate_eoq(annual_demand, order_cost, holding_cost_rate, unit_cost)
    rop = calculate_rop(daily_demand, lead_time, safety_stock)
    
    # Tampilkan hasil
    st.subheader("📊 Hasil Perhitungan")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("EOQ", f"{eoq:.0f} kg")
    with col2:
        st.metric("ROP", f"{rop:.0f} kg")
    with col3:
        total_cost = (annual_demand/eoq) * order_cost + (eoq/2) * holding_cost_rate * unit_cost
        st.metric("Total Cost", f"Rp {total_cost:,.0f}")
    with col4:
        order_frequency = annual_demand / eoq
        st.metric("Frekuensi Pesan", f"{order_frequency:.1f} kali/tahun")
    
    # Grafik inventory level
    st.subheader("📈 Grafik Level Persediaan")
    
    days = np.arange(0, 365)
    inventory_level = []
    current_inventory = eoq
    
    for day in days:
        current_inventory -= daily_demand
        
        # Reorder when reaching ROP
        if current_inventory <= rop and day % (365/order_frequency) < lead_time:
            current_inventory += eoq
        
        inventory_level.append(max(0, current_inventory))
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=days, y=inventory_level, mode='lines', name='Level Persediaan'))
    fig4.add_hline(y=rop, line_dash="dash", line_color="red", annotation_text=f"ROP: {rop:.0f} kg")
    fig4.add_hline(y=safety_stock, line_dash="dot", line_color="orange", annotation_text=f"Safety Stock: {safety_stock} kg")
    fig4.update_layout(title="Simulasi Level Persediaan Sepanjang Tahun", 
                       xaxis_title="Hari", yaxis_title="Jumlah Persediaan (kg)")
    st.plotly_chart(fig4, use_container_width=True)
    
    # Analisis sensitivitas
    st.subheader("🔍 Analisis Sensitivitas")
    
    demand_range = np.linspace(annual_demand * 0.5, annual_demand * 1.5, 10)
    eoq_sensitivity = [calculate_eoq(d, order_cost, holding_cost_rate, unit_cost) for d in demand_range]
    
    fig5 = px.line(x=demand_range, y=eoq_sensitivity, 
                   title="Sensitivitas EOQ terhadap Perubahan Permintaan",
                   labels={"x": "Permintaan Tahunan (kg)", "y": "EOQ (kg)"})
    st.plotly_chart(fig5, use_container_width=True)

# MODEL ANTRIAN
elif menu == "Model Antrian":
    st.header("⏳ Model Antrian")
    
    st.subheader("Simulasi Antrian Produksi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parameter Kedatangan")
        arrival_rate = st.number_input("Tingkat Kedatangan Order (per jam)", value=8.0, min_value=0.1, step=0.1)
        arrival_pattern = st.selectbox("Pola Kedatangan", ["Poisson", "Deterministik"])
        
    with col2:
        st.subheader("Parameter Pelayanan")
        service_rate = st.number_input("Tingkat Pelayanan (per jam)", value=10.0, min_value=0.1, step=0.1)
        num_servers = st.number_input("Jumlah Server/Mesin", value=1, min_value=1, max_value=10)
    
    # Hitung metrik antrian
    queue_metrics = calculate_queue_metrics(arrival_rate, service_rate, num_servers)
    
    if queue_metrics is None:
        st.error("⚠️ Sistem tidak stabil! Tingkat kedatangan melebihi kapasitas pelayanan.")
        st.write("Solusi:")
        st.write("- Kurangi tingkat kedatangan")
        st.write("- Tingkatkan tingkat pelayanan")
        st.write("- Tambah jumlah server/mesin")
    else:
        st.subheader("📊 Metrik Kinerja Antrian")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Utilisasi Sistem", f"{queue_metrics['utilization']:.2%}")
        with col2:
            if 'avg_queue_length' in queue_metrics:
                st.metric("Panjang Antrian Rata-rata", f"{queue_metrics['avg_queue_length']:.2f}")
            else:
                st.metric("Panjang Sistem Rata-rata", f"{queue_metrics['avg_system_length']:.2f}")
        with col3:
            if 'avg_wait_time' in queue_metrics:
                st.metric("Waktu Tunggu (jam)", f"{queue_metrics['avg_wait_time']:.2f}")
            else:
                st.metric("Waktu dalam Sistem (jam)", f"{queue_metrics['avg_system_time']:.2f}")
        with col4:
            cycle_time = 1/service_rate if service_rate > 0 else 0
            st.metric("Cycle Time (jam)", f"{cycle_time:.2f}")
        
        # Grafik utilisasi vs waktu tunggu
        st.subheader("📈 Analisis Kinerja Antrian")
        
        utilization_range = np.linspace(0.1, 0.95, 20)
        wait_times = []
        
        for util in utilization_range:
            temp_arrival = util * service_rate * num_servers
            temp_metrics = calculate_queue_metrics(temp_arrival, service_rate, num_servers)
            if temp_metrics and 'avg_wait_time' in temp_metrics:
                wait_times.append(temp_metrics['avg_wait_time'])
            elif temp_metrics and 'avg_system_time' in temp_metrics:
                wait_times.append(temp_metrics['avg_system_time'])
            else:
                wait_times.append(float('inf'))
        
        fig6 = px.line(x=utilization_range*100, y=wait_times,
                       title="Hubungan Utilisasi vs Waktu Tunggu",
                       labels={"x": "Utilisasi (%)", "y": "Waktu Tunggu (jam)"})
        fig6.add_vline(x=queue_metrics['utilization']*100, line_dash="dash", 
                       line_color="red", annotation_text="Kondisi Saat Ini")
        st.plotly_chart(fig6, use_container_width=True)
        
        # Rekomendasi optimasi
        st.subheader("💡 Rekomendasi Optimasi")
        
        if queue_metrics['utilization'] > 0.8:
            st.warning("Utilisasi tinggi! Pertimbangkan untuk menambah kapasitas.")
        elif queue_metrics['utilization'] < 0.5:
            st.info("Utilisasi rendah. Kapasitas bisa dikurangi untuk efisiensi biaya.")
        else:
            st.success("Utilisasi dalam rentang optimal.")

# ANALISIS TERINTEGRASI
elif menu == "Analisis Terintegrasi":
    st.header("🔗 Analisis Terintegrasi")
    
    st.subheader("Simulasi Sistem Produksi Lengkap")
    
    # Input parameter terintegrasi
    col1, col2 = st.columns(2)
    
    with col1:
        selected_product = st.selectbox("Pilih Produk untuk Analisis:", list(PRODUCTS.keys()))
        monthly_demand = st.number_input("Permintaan Bulanan (unit)", value=1000, min_value=100)
        
    with col2:
        production_capacity = st.number_input("Kapasitas Produksi Harian (unit)", value=50, min_value=10)
        service_level = st.slider("Target Service Level (%)", 90, 99, 95)
    
    # Hitung kebutuhan bahan baku
    product_data = PRODUCTS[selected_product]
    annual_demand = monthly_demand * 12
    
    st.subheader("📊 Analisis Kebutuhan Bahan Baku")
    
    bahan_baku_analysis = []
    total_inventory_cost = 0
    
    for bahan, proporsi in product_data["bahan_baku"].items():
        if bahan in BAHAN_BAKU:
            bahan_demand = annual_demand * proporsi
            bahan_data = BAHAN_BAKU[bahan]
            
            # Hitung EOQ dan ROP untuk setiap bahan
            eoq = calculate_eoq(bahan_demand, 200000, bahan_data["holding_cost"], bahan_data["harga"])
            daily_demand = bahan_demand / 365
            rop = calculate_rop(daily_demand, bahan_data["lead_time"], daily_demand * 2)  # 2 hari safety stock
            
            inventory_cost = (bahan_demand/eoq) * 200000 + (eoq/2) * bahan_data["holding_cost"] * bahan_data["harga"]
            total_inventory_cost += inventory_cost
            
            bahan_baku_analysis.append({
                "Bahan Baku": bahan,
                "Kebutuhan Tahunan (kg)": bahan_demand,
                "EOQ (kg)": eoq,
                "ROP (kg)": rop,
                "Biaya Persediaan (Rp)": inventory_cost
            })
    
    df_bahan = pd.DataFrame(bahan_baku_analysis)
    st.dataframe(df_bahan, use_container_width=True)
    
    # Analisis bottleneck produksi
    st.subheader("🔍 Analisis Bottleneck Produksi")
    
    daily_demand = monthly_demand / 30
    production_time = product_data["waktu_produksi"]
    required_capacity = daily_demand * production_time
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Kebutuhan Kapasitas Harian", f"{required_capacity:.2f} jam")
    with col2:
        capacity_utilization = (required_capacity / (production_capacity * production_time)) * 100
        st.metric("Utilisasi Kapasitas", f"{capacity_utilization:.1f}%")
    with col3:
        st.metric("Total Biaya Persediaan", f"Rp {total_inventory_cost:,.0f}")
    with col4:
        units_per_hour = 1 / production_time
        st.metric("Unit per Jam", f"{units_per_hour:.0f}")
    
    # Model antrian untuk order processing
    st.subheader("⏳ Analisis Antrian Order")
    
    order_arrival_rate = daily_demand / 8  # order per jam (8 jam kerja)
    order_service_rate = production_capacity / 8  # service rate per jam
    
    queue_metrics = calculate_queue_metrics(order_arrival_rate, order_service_rate, 1)
    
    if queue_metrics:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Waktu Tunggu Order", f"{queue_metrics.get('avg_wait_time', 0):.2f} jam")
        with col2:
            st.metric("Panjang Antrian", f"{queue_metrics.get('avg_queue_length', 0):.1f}")
        with col3:
            st.metric("Utilisasi Produksi", f"{queue_metrics['utilization']:.2%}")
    
    # Dashboard integrasi
    st.subheader("📊 Dashboard Terintegrasi")
    
    # Membuat grafik gabungan
    fig_integrated = make_subplots(
        rows=2, cols=2,
        subplot_titles=["Profit vs Biaya", "Level Persediaan", "Kinerja Antrian", "Trend Efisiensi"],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Grafik 1: Profit Analysis
    profit_per_unit = product_data["harga_jual"] - product_data["biaya_produksi"]
    monthly_profit = monthly_demand * profit_per_unit
    
    fig_integrated.add_trace(
        go.Bar(x=["Revenue", "Cost", "Profit"], 
               y=[monthly_demand * product_data["harga_jual"], 
                  monthly_demand * product_data["biaya_produksi"], 
                  monthly_profit],
               name="Financial",
               marker_color=['green', 'red', 'blue']),
        row=1, col=1
    )
    
    # Grafik 2: Inventory Level (contoh untuk bahan utama)
    if bahan_baku_analysis:
        main_material = bahan_baku_analysis[0]
        days = list(range(1, 31))
        inventory_sim = [max(0, main_material["EOQ (kg)"] - (i * main_material["Kebutuhan Tahunan (kg)"]/365)) 
                        for i in days]
        
        fig_integrated.add_trace(
            go.Scatter(x=days, y=inventory_sim, mode='lines+markers', 
                      name="Inventory Level", line=dict(color='orange')),
            row=1, col=2
        )
        
        # Add ROP line
        fig_integrated.add_trace(
            go.Scatter(x=days, y=[main_material["ROP (kg)"]] * len(days), 
                      mode='lines', name="ROP", line=dict(dash='dash', color='red')),
            row=1, col=2
        )
    
    # Grafik 3: Queue Performance - Bar Chart
    if queue_metrics:
        queue_data = ['Utilisasi', 'Waktu Tunggu', 'Panjang Antrian']
        queue_values = [
            queue_metrics['utilization'] * 100,
            queue_metrics.get('avg_wait_time', queue_metrics.get('avg_system_time', 0)) * 10,  # Scale for visibility
            queue_metrics.get('avg_queue_length', queue_metrics.get('avg_system_length', 0)) * 20  # Scale for visibility
        ]
        
        fig_integrated.add_trace(
            go.Bar(x=queue_data, y=queue_values, name="Queue Metrics",
                  marker_color=['blue', 'orange', 'green']),
            row=2, col=1
        )
    
    # Grafik 4: Overall Efficiency Trend
    overall_efficiency = (capacity_utilization + queue_metrics['utilization']*100) / 2 if queue_metrics else capacity_utilization
    
    months = ['Jan', 'Feb', 'Mar',]
