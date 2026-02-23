import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

class ModuloInventario:
    def __init__(self, db):
        self.db = db

    def generar_pdf_inventario(self, datos):
        """Genera HTML para impresión"""
        fecha_actual = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
        filas = ""
        total_valor = 0
        productos_bajos = 0
        
        for p in datos:
            actual = int(p.get('stock') or 0) 
            minimo = int(p.get('stock_minimo') or 0)
            precio = float(p.get('precio_venta') or 0)
            subtotal = actual * precio
            total_valor += subtotal
            
            estilo_stock = 'color: red; font-weight: bold;' if actual <= minimo else ''
            if actual <= minimo: productos_bajos += 1
            
            filas += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">{p.get('barcode', 'S/B')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{p.get('referencia', 'S/R')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{p.get('nombre', 'N/A')}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center; {estilo_stock}">{actual}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${precio:,.2f}</td>
            </tr>
            """

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <h2 style="text-align: center; color: #004A99; border-bottom: 2px solid #004A99;">CIR PANAMÁ - REPORTE</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead style="background: #f2f2f2;">
                    <tr>
                        <th>Barcode</th><th>Ref.</th><th>Producto</th><th>Stock</th><th>Precio</th>
                    </tr>
                </thead>
                <tbody>{filas}</tbody>
            </table>
        </div>
        <script>window.print();</script>
        """
        return html

    def render(self):
        st.header("📦 Inventario CIR")
        
        # --- FORMULARIO DE REGISTRO CON 2 CAMPOS DE CÓDIGO ---
        with st.expander("➕ Registrar Nuevo Producto", expanded=False):
            with st.form("form_nuevo_producto", clear_on_submit=True):
                nombre = st.text_input("Nombre del Producto")
                
                col_c1, col_c2 = st.columns(2)
                barcode_val = col_c1.text_input("Código de Barras (Escáner)")
                referencia_val = col_c2.text_input("Número de Referencia (CIR)")
                
                c1, c2, c3 = st.columns(3)
                costo_input = c1.number_input("Costo de Compra ($)", min_value=0.0, format="%.2f")
                stock = c2.number_input("Stock Inicial", min_value=0, step=1)
                s_min = c3.number_input("Stock Mínimo", min_value=0, step=1)

                p10 = costo_input * 1.10
                if costo_input > 0:
                    st.info(f"💡 Precio Venta Automático (P10): **${p10:.2f}**")

                submit = st.form_submit_button("Guardar Producto", use_container_width=True)
                
                if submit:
                    if nombre and costo_input > 0:
                        nuevo_p = {
                            "nombre": nombre,
                            "barcode": barcode_val,     # Campo 1
                            "referencia": referencia_val, # Campo 2 (Independiente)
                            "precio_costo": costo_input,
                            "stock": stock,
                            "stock_minimo": s_min,
                            "precio_venta": p10
                        }
                        self.db.insert("productos", nuevo_p)
                        st.success(f"✅ {nombre} guardado.")
                        st.rerun()

        # --- LISTADO Y BÚSQUEDA ---
        productos = self.db.fetch("productos")
        query = st.text_input("🔍 Buscar por Nombre, Barcode o Referencia...").lower()

        if productos:
            st.divider()
            for p in productos:
                # Búsqueda en los 3 campos clave
                match = (query in str(p.get('nombre','')).lower() or 
                         query in str(p.get('barcode','')).lower() or 
                         query in str(p.get('referencia','')).lower())
                
                if match:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        
                        c1.write(f"**{p.get('nombre')}**")
                        c1.caption(f"Ref: {p.get('referencia')} | Barcode: {p.get('barcode')}")
                        c1.caption(f"Costo: ${float(p.get('precio_costo') or 0):.2f}")
                        
                        c2.write(f"Stock: `{p.get('stock')}`")
                        c2.write(f"Venta: **${float(p.get('precio_venta') or 0):.2f}**")
                        
                        with c3:
                            st.button("📝 Editar", key=f"btn_edit_{p.get('id')}")