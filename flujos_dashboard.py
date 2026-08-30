# Crear un Dashboard de flujo de efectivo de un presupuesto ficticio

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Flujo de efectivo",
    layout="wide"
)


def dashboard_series_flujo():

    # =====================================================
    # TÍTULO
    # =====================================================

    st.title("📊 Flujo de efectivo (series semanales)")

    # =====================================================
    # CARGA DE DATOS
    # =====================================================

    archivo = "/Users/judith_frias/Flujo_pto_data/flujos_cubo.xlsx"

    @st.cache_data
    def load_data():

        return pd.read_excel(
            archivo,
            keep_default_na=False
        )

    df = load_data()

    # =====================================================
    # MÉTRICA
    # =====================================================

    metrica = st.sidebar.selectbox(
        "Métrica",
        [
            "Total",
            "Subtotal",
            "Fringes"
        ],
        index=0,
        key="metrica_selector"
    )

    # Variable correspondiente a la métrica
    columna_metrica = {
        "Total": "costo_fr_per",
        "Subtotal": "subtot_per",
        "Fringes": "fr_per"
    }[metrica]

    # =====================================================
    # TIPO DE FECHA
    # =====================================================

    tipo_fecha = st.sidebar.selectbox(
        "Tipo fecha",
        [
            "Fecha semana",
            "Fecha calendario"
        ],
        key="tipo_fecha_selector"
    )

    # =====================================================
    # FILTROS
    # =====================================================

    st.sidebar.header("Filtros")

    def create_filter(
        label,
        options,
        key
    ):

        return st.sidebar.multiselect(
            label,
            options=options,
            default=[],
            key=key
        )

    # =====================================================
    # 1. ETAPA
    # =====================================================

    opciones_etapa = sorted(
        df["etapa"]
        .dropna()
        .unique()
    )

    f_etapa = create_filter(
        "Etapa",
        opciones_etapa,
        "filtro_etapa"
    )

    # =====================================================
    # DATAFRAME DESPUÉS DE ETAPA
    # =====================================================

    df_filtro_etapa = df.copy()

    if f_etapa:

        df_filtro_etapa = df_filtro_etapa[
            df_filtro_etapa["etapa"].isin(f_etapa)
        ]

    # =====================================================
    # 2. TIPO DE COSTO
    # =====================================================

    opciones_tp_costo = sorted(
        df_filtro_etapa["tp_costo_des"]
        .dropna()
        .unique()
    )

    f_tp_costo = create_filter(
        "Tipo costo (ATL/BTL)",
        opciones_tp_costo,
        "filtro_tp_costo"
    )

    # =====================================================
    # DATAFRAME DESPUÉS DE TIPO DE COSTO
    # =====================================================

    df_filtro_tp = df_filtro_etapa.copy()

    if f_tp_costo:

        df_filtro_tp = df_filtro_tp[
            df_filtro_tp["tp_costo_des"].isin(f_tp_costo)
        ]

    # =====================================================
    # 3. CUENTA NIVEL 1
    # =====================================================

    opciones_cuenta_1 = sorted(
        df_filtro_tp["cuenta_des"]
        .dropna()
        .unique()
    )

    f_cuenta_1 = create_filter(
        "Cuenta (nivel 1)",
        opciones_cuenta_1,
        "filtro_cuenta_1"
    )

    # =====================================================
    # DATAFRAME DESPUÉS DE CUENTA NIVEL 1
    # =====================================================

    df_filtro_cuenta_1 = df_filtro_tp.copy()

    if f_cuenta_1:

        df_filtro_cuenta_1 = df_filtro_cuenta_1[
            df_filtro_cuenta_1["cuenta_des"].isin(f_cuenta_1)
        ]

    # =====================================================
    # 4. CUENTA NIVEL 2
    # =====================================================

    opciones_cuenta_2 = sorted(
        df_filtro_cuenta_1["account_des"]
        .dropna()
        .unique()
    )

    f_cuenta_2 = create_filter(
        "Cuenta (nivel 2)",
        opciones_cuenta_2,
        "filtro_cuenta_2"
    )

    # =====================================================
    # DATAFRAME DESPUÉS DE CUENTA NIVEL 2
    # =====================================================

    df_filtro_cuenta_2 = df_filtro_cuenta_1.copy()

    if f_cuenta_2:

        df_filtro_cuenta_2 = df_filtro_cuenta_2[
            df_filtro_cuenta_2["account_des"].isin(f_cuenta_2)
        ]

    # =====================================================
    # 5. CUENTA NIVEL 3
    # =====================================================

    opciones_cuenta_3 = sorted(
        df_filtro_cuenta_2["detalle_des"]
        .dropna()
        .unique()
    )

    f_cuenta_3 = create_filter(
        "Cuenta (nivel 3)",
        opciones_cuenta_3,
        "filtro_cuenta_3"
    )

    # =====================================================
    # NOTAS
    # =====================================================

    st.sidebar.markdown(
        "<p style='font-size:11px; color:gray;'>"
        "Cuenta (nivel 1), refiere a la cuenta presupuestal "
        "en su nivel más agregado."
        "</p>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        "<p style='font-size:11px; color:gray;'>"
        "Cuenta (nivel 2 y nivel 3), refiere a la cuenta "
        "presupuestal en un nivel cada vez más desagregado."
        "</p>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        "<p style='font-size:11px; color:gray;'>"
        "Fuente: Presupuesto CCC."
        "</p>",
        unsafe_allow_html=True
    )

    # =====================================================
    # APLICAR TODOS LOS FILTROS
    # =====================================================

    df_filtered = df.copy()

    if f_etapa:

        df_filtered = df_filtered[
            df_filtered["etapa"].isin(f_etapa)
        ]

    if f_tp_costo:

        df_filtered = df_filtered[
            df_filtered["tp_costo_des"].isin(f_tp_costo)
        ]

    if f_cuenta_1:

        df_filtered = df_filtered[
            df_filtered["cuenta_des"].isin(f_cuenta_1)
        ]

    if f_cuenta_2:

        df_filtered = df_filtered[
            df_filtered["account_des"].isin(f_cuenta_2)
        ]

    if f_cuenta_3:

        df_filtered = df_filtered[
            df_filtered["detalle_des"].isin(f_cuenta_3)
        ]

    # =====================================================
    # DASHBOARD FLUJO
    # =====================================================

    # =====================================================
    # ORDEN DE LAS SEMANAS
    # =====================================================

    orden_semanas = (
        ["DES"] +
        [f"SEM{i:02d}" for i in range(1, 39)]
    )

    # =====================================================
    # SELECCIONAR VARIABLE DE FECHA
    # =====================================================

    if tipo_fecha == "Fecha semana":

        columna_fecha = "date_sem"

        orden_fecha = orden_semanas

    else:

        columna_fecha = "date_fec"

        # Crear orden de date_fec a partir de date_sem

        orden_fecha = (
            df[
                [
                    "date_sem",
                    "date_fec"
                ]
            ]
            .drop_duplicates()
            .assign(
                date_sem=lambda x: pd.Categorical(
                    x["date_sem"],
                    categories=orden_semanas,
                    ordered=True
                )
            )
            .sort_values("date_sem")["date_fec"]
            .tolist()
        )

    # =====================================================
    # AGRUPAR
    # =====================================================

    df_grouped = (
        df_filtered
        .groupby(
            columna_fecha,
            as_index=False
        )[[columna_metrica]]
        .sum()
    )

    # =====================================================
    # ASEGURAR ORDEN
    # =====================================================

    df_grouped[columna_fecha] = pd.Categorical(
        df_grouped[columna_fecha],
        categories=orden_fecha,
        ordered=True
    )

    df_grouped = df_grouped.sort_values(
        columna_fecha
    )

    # =====================================================
    # INCLUIR TODOS LOS PERIODOS
    # =====================================================

    df_grouped = (
        df_grouped
        .set_index(columna_fecha)
        .reindex(orden_fecha)
        .fillna(0)
        .reset_index()
    )

    # =====================================================
    # KPIs
    # =====================================================

    total = df_filtered[
        columna_metrica
    ].sum()

    total_atl = df_filtered.loc[
        df_filtered["tp_costo_des"] == "Above the line",
        columna_metrica
    ].sum()

    total_btl = df_filtered.loc[
        df_filtered["tp_costo_des"] == "Below the line",
        columna_metrica
    ].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💰 Total",
        f"{total:,.0f}"
    )

    col2.metric(
        "📺 ATL",
        f"{total_atl:,.0f}"
    )

    col3.metric(
        "📱 BTL",
        f"{total_btl:,.0f}"
    )

    st.markdown("---")

    # =====================================================
    # COLORES
    # =====================================================

    colores = []

    for periodo in df_grouped[columna_fecha]:

        if tipo_fecha == "Fecha semana":

            if periodo == "DES":

                colores.append("gray")

            elif periodo in [
                "SEM01",
                "SEM02"
            ]:

                colores.append("yellow")

            elif periodo in [
                "SEM03",
                "SEM04",
                "SEM05",
                "SEM06",
                "SEM07",
                "SEM08",
                "SEM09",
                "SEM10"
            ]:

                colores.append("orange")

            elif periodo in [
                "SEM11",
                "SEM12",
                "SEM13",
                "SEM14",
                "SEM15",
                "SEM16",
                "SEM17",
                "SEM18"
            ]:

                colores.append("green")

            elif periodo in [
                "SEM19",
                "SEM20",
                "SEM21",
                "SEM22"
            ]:

                colores.append("blue")

            elif periodo in [
                "SEM23",
                "SEM24",
                "SEM25",
                "SEM26",
                "SEM27",
                "SEM28",
                "SEM29",
                "SEM30",
                "SEM31",
                "SEM32",
                "SEM33",
                "SEM34",
                "SEM35",
                "SEM36",
                "SEM37",
                "SEM38"
            ]:

                colores.append("purple")

            else:

                colores.append("gray")

        else:

            posicion = orden_fecha.index(periodo)

            if posicion == 0:

                colores.append("gray")

            elif posicion in [1, 2]:

                colores.append("yellow")

            elif 3 <= posicion <= 10:

                colores.append("orange")

            elif 11 <= posicion <= 18:

                colores.append("green")

            elif 19 <= posicion <= 22:

                colores.append("blue")

            elif 23 <= posicion <= 38:

                colores.append("purple")

            else:

                colores.append("gray")

    # =====================================================
    # GRÁFICA
    # =====================================================

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_grouped[columna_fecha],

            y=df_grouped[columna_metrica],

            name=metrica,

            marker_color=colores,

            text=df_grouped[columna_metrica],

            texttemplate="%{text:,.0f}",

            textposition="outside"
        )
    )

    # =====================================================
    # CONFIGURACIÓN
    # =====================================================

    fig.update_layout(

        title=f"{metrica} por periodo",

        height=600,

        xaxis=dict(
            title="Periodo",

            categoryorder="array",

            categoryarray=orden_fecha,

            tickangle=-90
        ),

        yaxis=dict(
            title="Pesos"
        ),

        margin=dict(
            t=80,
            b=120
        ),

        showlegend=False
    )

    # =====================================================
    # MOSTRAR GRÁFICA
    # =====================================================

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="flujo"
    )

    # =====================================================
    # TABLA
    # =====================================================

    df_table = df_grouped.copy()

    df_table_display = df_table.copy()

    df_table_display[columna_metrica] = (
        df_table_display[columna_metrica]
        .map(
            lambda x: f"{x:,.0f}"
        )
    )

    # Cambiar nombre de la columna en la tabla
    df_table_display = df_table_display.rename(
        columns={
            columna_metrica: metrica
        }
    )

    with st.expander(
        "Ver montos por semana"
    ):

        st.dataframe(
            df_table_display,
            use_container_width=True
        )


# =========================================================
# EJECUTAR DASHBOARD
# =========================================================

dashboard_series_flujo()


#streamlit run /Users/judith_frias/Flujo_pto_data/flujos_dashboard.py
