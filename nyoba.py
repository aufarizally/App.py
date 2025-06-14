import streamlit as st
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sistem Operasi Franchise", layout="wide")

st.title("📦📈🔁 Sistem Operasi Franchise Kopi")
st.markdown("Gabungan Model: *Optimasi Produksi, Persediaan, dan Antrian*")

st.header("1️⃣ Optimasi Produksi")
st.markdown("Hitung total profit berdasarkan jumlah minuman yang diproduksi")

produk = ["Latte", "Cappuccino", "Matcha", "Hazelnut", "Red Velvet"]
profit_per_cup = [5000, 6000, 7000, 8000, 9000]
waktu_per_cup = [2, 3, 2, 4, 3]  # menit

produksi = []
total_waktu = 0
total_profit = 0

st.subheader("Input Jumlah Produksi Harian")
col1, col2, col3 = st.columns(3)
with col1:
    for i, p in enumerate(produk):
        jumlah = st.number_input(f"{p} (cup)", min_value=0, value=0, step=1, key=f"prod_{i}")
        produksi.append(jumlah)
        total_waktu += jumlah * waktu_per_cup[i]
        total_profit += jumlah * profit_per_cup[i]

kapasitas_waktu = 1200  # menit/hari
st.info(f"⏱ Total waktu produksi: {total_waktu} menit dari maksimum {kapasitas_waktu} menit")
st.success(f"💰 Total estimasi profit: Rp{total_profit:,.0f}")

if total_waktu > kapasitas_waktu:
    st.warning("⚠ Produksi melebihi kapasitas waktu harian!")

# Visualisasi
fig, ax = plt.subplots()
ax.bar(produk, produksi, color='skyblue')
ax.set_title("Produksi per Produk")
ax.set_ylabel("Jumlah (cup)")
st.pyplot(fig)

st.divider()
st.header("2️⃣ Model Persediaan (EOQ & ROP)")

st.markdown("Hitung jumlah optimal pembelian bahan baku")

bahan = ["Susu Cair", "Kopi Bubuk", "Bubuk Matcha", "Sirup Hazelnut", "Red Velvet"]
D = st.number_input("Permintaan tahunan (liter/unit)", value=21900)
S = st.number_input("Biaya pemesanan (Rp)", value=100000)
H = st.number_input("Biaya penyimpanan/tahun (Rp/unit)", value=500)
lead_time = st.number_input("Lead time (hari)", value=1)
kebutuhan_per_hari = st.number_input("Kebutuhan rata-rata per hari", value=60.0)
deviasi = st.number_input("Deviasi standar kebutuhan per hari", value=5.0)

st.subheader("📦 Hasil EOQ dan ROP")

eoq = math.sqrt((2 * D * S) / H)
rop = kebutuhan_per_hari * lead_time + 1.65 * deviasi

st.write(f"🔹 *EOQ (Jumlah optimal pemesanan)*: {eoq:.2f} unit")
st.write(f"🔹 *ROP (Titik pemesanan ulang)*: {rop:.2f} unit")

# Visualisasi EOQ
fig2, ax2 = plt.subplots()
q = np.arange(100, int(eoq*2), 100)
total_cost = (D/q)*S + (q/2)*H
ax2.plot(q, total_cost, marker='o')
ax2.axvline(eoq, color='red', linestyle='--', label=f'EOQ = {eoq:.0f}')
ax2.set_title("Total Biaya vs Jumlah Pemesanan")
ax2.set_xlabel("Jumlah Pemesanan")
ax2.set_ylabel("Total Biaya")
ax2.legend()
st.pyplot(fig2)

st.divider()
st.header("3️⃣ Model Antrian Pembelian Bahan Baku")

st.markdown("Simulasi antrian cabang franchise saat melakukan pembelian bahan baku ke pusat")

lambda_rate = st.number_input("Rata-rata cabang datang per jam (λ)", value=8.0)
mu_rate = st.number_input("Rata-rata layanan pusat per jam per petugas (μ)", value=3.0)
c = st.number_input("Jumlah petugas layanan di pusat (c)", min_value=1, value=2)

rho = lambda_rate / (c * mu_rate)

st.subheader("📊 Hasil Evaluasi Antrian")
st.write(f"🔸 Utilisasi sistem (ρ): {rho:.2f}")

if rho >= 1:
    st.error("❌ Sistem tidak stabil! Tingkat kedatangan melebihi kapasitas pelayanan.")
else:
    st.success("✅ Sistem stabil")
    st.write("(Estimasi waktu tunggu dan panjang antrian lebih kompleks untuk c > 1, gunakan simulasi lanjut)")
