import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

st.title("💡 Aplikasi Turunan Parsial")

x, y = sp.symbols('x y')
fungsi_str = st.text_input("Masukkan fungsi f(x, y):", "x**2 * y + y**3")

try:
    f = sp.sympify(fungsi_str)
    fx = sp.diff(f, x)
    fy = sp.diff(f, y)

    st.latex(f"f(x, y) = {sp.latex(f)}")
    st.latex(f"\\frac{{\\partial f}}{{\\partial x}} = {sp.latex(fx)}")
    st.latex(f"\\frac{{\\partial f}}{{\\partial y}} = {sp.latex(fy)}")

    x0 = st.number_input("Nilai x₀:", value=1.0)
    y0 = st.number_input("Nilai y₀:", value=2.0)

    f_val = f.subs({x: x0, y: y0})
    fx_val = fx.subs({x: x0, y: y0})
    fy_val = fy.subs({x: x0, y: y0})

    st.write("Nilai fungsi di titik (x₀, y₀):", f_val)
    st.write("Gradien di titik (x₀, y₀):", f"({fx_val}, {fy_val})")

    x_vals = np.linspace(x0 - 2, x0 + 2, 50)
    y_vals = np.linspace(y0 - 2, y0 + 2, 50)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = sp.lambdify((x, y), f, 'numpy')(X, Y)
    Z_tangent = float(f_val) + float(fx_val)*(X - x0) + float(fy_val)*(Y - y0)

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, alpha=0.7, cmap='viridis')
    ax.plot_surface(X, Y, Z_tangent, alpha=0.5, color='red')
    ax.set_title("Permukaan f(x, y) dan bidang singgungnya")
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    st.pyplot(fig)

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
