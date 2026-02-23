import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

class ModuloInventario:
    def __init__(self, db):
        self.db = db

    def generar_pdf_inventario(self, datos):
        """Genera HTML para impresión (Reporte de Inventario)"""
        fecha_actual = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
        filas = ""
        for p in datos:
            actual = int(p.get('stock') or 0) 
            precio = float(p.get('precio_venta') or 0)
            filas += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">{p.get('barcode', 'S/B')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{p.get('referencia', 'S/R')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{p.get('nombre', 'N/A')}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{actual}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${precio:,.2f}</td>
            </tr>
            """

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="text-align: center; color: #004A99; border-bottom: 2px solid #004A99;">CIR PANAMÁ - REPORTE DE INVENTARIO</h2>
            <p style="text-align: center;">Fecha: {fecha_actual}</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead style="background: #f2f2f2;">
                    <tr>
                        <th style="border: 1px solid #ddd; padding: 8px;">Barcode</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Ref.</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Producto</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Stock</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Precio</th>
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
        
        # --- FORMULARIO DE REGISTRO ---
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
                            "barcode": barcode_val,
                            "referencia": referencia_val,
                            "precio_costo": costo_input,
                            "stock": stock,
                            "stock_minimo": s_min,
                            "precio_venta": p10
                        }
                        self.db.insert("productos", nuevo_p)
                        st.success(f"✅ {nombre} guardado exitosamente.")
                        st.rerun()
                    else:
                        st.warning("⚠️ El nombre y el costo son obligatorios.")

        # --- BUSCADOR ---
        productos = self.db.fetch("productos")
        
        col_bus, col_print = st.columns([3, 1])
        with col_print:
            if st.button("🖨️ Reporte", use_container_width=True, type="primary"):
                if productos:
                    st.session_state.print_inv = self.generar_pdf_inventario(productos)

        query = col_bus.text_input("🔍 Buscar por Nombre, Barcode o Referencia...").lower()

        # --- LISTADO TIPO FICHA ---
        if productos:
            st.divider()
            for p in productos:
                # Lógica de búsqueda trilingüe
                match = (query in str(p.get('nombre','')).lower() or 
                         query in str(p.get('barcode','')).lower() or 
                         query in str(p.get('referencia','')).lower())
                
                if match:
                    # DISEÑO DE FICHA TÉCNICA
                    with st.container(border=True):
                        # Título y Botón Editar
                        col_tit, col_edit = st.columns([4, 1])
                        col_tit.subheader(f"📦 {p.get('nombre')}")
                        with col_edit:
                            st.button("📝 Editar", key=f"btn_edit_{p.get('id')}", use_container_width=True)

                        # Cuerpo de la Ficha en 3 columnas
                        c1, c2, c3 = st.columns(3)
                        
                        with c1:
                            st.write("**🆔 Identificadores**")
                            st.caption(f"Ref: `{p.get('referencia', 'N/A')}`")
                            st.caption(f"Barcode: `{p.get('barcode', 'N/A')}`")
                        
                        with c2:
                            actual = int(p.get('stock') or 0)
                            minimo = int(p.get('stock_minimo') or 0)
                            color = "green" if actual > minimo else "red"
                            st.write("**📉 Existencias**")
                            st.markdown(f"Stock: :{color}[**{actual} unidades**]")
                            st.caption(f"Mínimo: {minimo}")

                        with c3:
                            venta = float(p.get('precio_venta') or 0)
                            costo = float(p.get('precio_costo') or 0)
                            st.write("**💰 Valores**")
                            st.write(f"Venta: **${venta:.2f}**")
                            st.caption(f"Costo Ref: ${costo:.2f}")

        if "print_inv" in st.session_state:
            components.html(st.session_state.print_inv, height=0, width=0)
            del st.session_state.print_inv