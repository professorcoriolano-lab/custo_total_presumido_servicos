import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO

st.set_page_config(
    page_title="Planejamento Tributário | Lucro Presumido",
    page_icon="📊",
    layout="centered"
)

st.markdown("""
<style>
    .main { background-color: #f7f9fc; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .titulo-header {
        background-color: #2c3e50;
        color: white;
        padding: 18px 24px;
        border-radius: 8px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 24px;
    }
    .resultado-box {
        background-color: #2c3e50;
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-top: 16px;
    }
    .section-title {
        color: #2c3e50;
        border-bottom: 2px solid #2c3e50;
        padding-bottom: 4px;
        margin-top: 24px;
        font-size: 15px;
        font-weight: bold;
    }
    .stButton > button {
        background-color: #2ecc71;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 28px;
        border-radius: 6px;
        font-size: 15px;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #27ae60;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="titulo-header">
    📊 PLANEJAMENTO FISCAL E TRABALHISTA ANUAL<br>
    <span style="font-size:13px; font-weight:normal;">Regime: Lucro Presumido — Serviços</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">⚙️ Configurações</div>', unsafe_allow_html=True)

tipo_servico = st.selectbox(
    "Tipo de Serviço",
    [
        "Serviços Gerais / TI / Profissões Regulamentadas (32%)",
        "Transportes de Passageiros (16%)"
    ]
)

col1, col2 = st.columns(2)
with col1:
    faturamento_anual = st.number_input("Faturamento Anual Projetado (R$)", min_value=0.0, value=1200000.0, step=1000.0, format="%.2f")
    salario_mensal = st.number_input("Salário Mensal (R$)", min_value=0.0, value=2000.0, step=100.0, format="%.2f")
with col2:
    prolabore_mensal = st.number_input("Pró-Labore Mensal (R$)", min_value=0.0, value=2000.0, step=100.0, format="%.2f")
    fap = st.number_input("FAP (Fator Acidentário)", min_value=0.5, max_value=2.0, value=1.0, step=0.01, format="%.2f")

rat_pct = st.number_input("RAT (%) — Ex: para 2% digite 2", min_value=0.0, max_value=3.0, value=1.0, step=0.5, format="%.1f")

calcular = st.button("▶ Gerar Planejamento")

if calcular:

    if "32%" in tipo_servico:
        presuncao_irpj = 0.32
        presuncao_csll = 0.32
        tipo_servico_str = tipo_servico
    else:
        presuncao_irpj = 0.16
        presuncao_csll = 0.12
        tipo_servico_str = tipo_servico

    rat = rat_pct / 100
    rat_ajustado = fap * rat

    salario_anual         = salario_mensal * 12
    prolabore_anual       = prolabore_mensal * 12
    decimo_terceiro_anual = salario_mensal * 12
    terco_ferias_anual    = decimo_terceiro_anual / 3
    despesas_folha_sem_encargos = salario_anual + prolabore_anual + decimo_terceiro_anual + terco_ferias_anual

    fgts_folha  = salario_anual * 0.08
    fgts_13     = decimo_terceiro_anual * 0.08
    fgts_ferias = terco_ferias_anual * 0.08
    total_fgts  = fgts_folha + fgts_13 + fgts_ferias

    inss_prolabore = prolabore_anual * 0.20
    inss_salarios  = salario_anual * 0.20
    inss_13        = decimo_terceiro_anual * 0.20
    inss_ferias    = terco_ferias_anual * 0.20
    total_inss     = inss_prolabore + inss_salarios + inss_13 + inss_ferias

    terceiros_salarios = salario_anual * 0.058
    terceiros_13       = decimo_terceiro_anual * 0.058
    terceiros_ferias   = terco_ferias_anual * 0.058
    total_terceiros    = terceiros_salarios + terceiros_13 + terceiros_ferias

    rat_salarios       = salario_anual * rat_ajustado
    rat_13             = decimo_terceiro_anual * rat_ajustado
    rat_ferias         = terco_ferias_anual * rat_ajustado
    total_rat_ajustado = rat_salarios + rat_13 + rat_ferias

    total_encargos_anual     = total_fgts + total_inss + total_terceiros + total_rat_ajustado
    custo_folha_com_encargos = despesas_folha_sem_encargos + total_encargos_anual

    pis_anual    = faturamento_anual * 0.0065
    cofins_anual = faturamento_anual * 0.0300
    iss_anual    = faturamento_anual * 0.0500

    base_irpj_anual = faturamento_anual * presuncao_irpj
    base_csll_anual = faturamento_anual * presuncao_csll

    irpj_subtotal  = base_irpj_anual * 0.15
    csll_anual     = base_csll_anual * 0.09
    adicional_irpj = (base_irpj_anual - 240000) * 0.10 if base_irpj_anual > 240000 else 0
    irpj_total_anual = irpj_subtotal + adicional_irpj

    total_impostos_faturamento = pis_anual + cofins_anual + iss_anual + irpj_total_anual + csll_anual
    custo_total_empresa        = total_impostos_faturamento + custo_folha_com_encargos
    lair_anual                 = faturamento_anual - custo_total_empresa

    def fmt(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    st.markdown('<div class="section-title">1. Despesas Operacionais com Folha (Anual)</div>', unsafe_allow_html=True)
    dados_folha = {
        "Salários Anualizados": salario_anual,
        "Pró-Labore Anualizado": prolabore_anual,
        "13º Salário (Provisão)": decimo_terceiro_anual,
        "1/3 de Férias (Provisão)": terco_ferias_anual,
        "**TOTAL SEM ENCARGOS**": despesas_folha_sem_encargos,
    }
    for k, v in dados_folha.items():
        col_a, col_b = st.columns([3, 1])
        col_a.markdown(k)
        col_b.markdown(f"**{fmt(v)}**")

    st.markdown('<div class="section-title">2. Encargos Sociais Detalhados (Anual)</div>', unsafe_allow_html=True)
    import pandas as pd
    encargos = [
        ("FGTS sobre Salários", "Salários", "8,00%", fgts_folha),
        ("FGTS sobre 13º Salário", "13º Salário", "8,00%", fgts_13),
        ("FGTS sobre 1/3 Férias", "1/3 Férias", "8,00%", fgts_ferias),
        ("INSS sobre Pró-Labore", "Pró-Labore", "20,00%", inss_prolabore),
        ("INSS sobre Salários", "Salários", "20,00%", inss_salarios),
        ("INSS sobre 13º Salário", "13º Salário", "20,00%", inss_13),
        ("INSS sobre 1/3 Férias", "1/3 Férias", "20,00%", inss_ferias),
        ("Terceiros sobre Salários", "Salários", "5,80%", terceiros_salarios),
        ("Terceiros sobre 13º Salário", "13º Salário", "5,80%", terceiros_13),
        ("Terceiros sobre 1/3 Férias", "1/3 Férias", "5,80%", terceiros_ferias),
        (f"RAT Ajustado sobre Salários", "Salários", f"{rat_ajustado*100:.3f}%", rat_salarios),
        (f"RAT Ajustado sobre 13º", "13º Salário", f"{rat_ajustado*100:.3f}%", rat_13),
        (f"RAT Ajustado sobre 1/3 Férias", "1/3 Férias", f"{rat_ajustado*100:.3f}%", rat_ferias),
    ]
    df_enc = pd.DataFrame(encargos, columns=["Encargo", "Base", "Alíquota", "Valor Anual"])
    df_enc["Valor Anual"] = df_enc["Valor Anual"].apply(fmt)
    st.dataframe(df_enc, use_container_width=True, hide_index=True)
    col_a, col_b = st.columns([3, 1])
    col_a.markdown("**TOTAL DOS ENCARGOS**")
    col_b.markdown(f"**{fmt(total_encargos_anual)}**")

    st.markdown('<div class="section-title">3. Impostos sobre Faturamento (Lucro Presumido)</div>', unsafe_allow_html=True)
    impostos = [
        ("PIS", "0,65%", pis_anual),
        ("COFINS", "3,00%", cofins_anual),
        ("ISS (Municipal)", "5,00%", iss_anual),
        ("IRPJ (+ Adicional)", "Presunção 15% (+10%)", irpj_total_anual),
        ("CSLL", "Presunção 9%", csll_anual),
    ]
    df_imp = pd.DataFrame(impostos, columns=["Imposto", "Alíquota", "Valor Anual"])
    df_imp["Valor Anual"] = df_imp["Valor Anual"].apply(fmt)
    st.dataframe(df_imp, use_container_width=True, hide_index=True)
    col_a, col_b = st.columns([3, 1])
    col_a.markdown("**TOTAL DE IMPOSTOS**")
    col_b.markdown(f"**{fmt(total_impostos_faturamento)}**")

    st.markdown('<div class="section-title">4. Demonstrativo de Resultado Operacional</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])
    col_a.write("Faturamento Bruto Total")
    col_b.write(fmt(faturamento_anual))
    col_a, col_b = st.columns([3, 1])
    col_a.write("(-) Folha de Pagamento com Encargos")
    col_b.write(fmt(custo_folha_com_encargos))
    col_a, col_b = st.columns([3, 1])
    col_a.write("(-) Impostos sobre Faturamento")
    col_b.write(fmt(total_impostos_faturamento))

    st.markdown(f"""
    <div class="resultado-box">
        (=) RESULTADO LÍQUIDO OPERACIONAL (LAIR ANUAL): {fmt(lair_anual)}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📈 Distribuição da Receita Bruta</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(7, 7))
    labels = ['PIS/COFINS', 'ISS', 'IRPJ/CSLL', 'Folha Líquida', 'Encargos da Folha', 'Resultado (LAIR)']
    valores = [
        pis_anual + cofins_anual,
        iss_anual,
        irpj_total_anual + csll_anual,
        despesas_folha_sem_encargos,
        total_encargos_anual,
        max(0, lair_anual)
    ]
    colors_pizza = ['#e74c3c', '#e67e22', '#c0392b', '#34495e', '#bdc3c7', '#2ecc71']
    ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors_pizza)
    ax.set_title('Distribuição Anual da Receita Bruta (Faturamento)', pad=20)
    st.pyplot(fig)
    plt.close()

    # --- GERAÇÃO DO PDF COM REPORTLAB ---
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    pdf_buf = BytesIO()
    doc = SimpleDocTemplate(pdf_buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    dark      = rl_colors.HexColor('#2c3e50')
    amarelo   = rl_colors.HexColor('#f9f9db')
    cinza_hdr = rl_colors.HexColor('#f5f5f5')

    style_header  = ParagraphStyle('h', fontSize=13, textColor=rl_colors.white,
                                   backColor=dark, alignment=TA_CENTER,
                                   fontName='Helvetica-Bold', leading=18,
                                   spaceAfter=6, spaceBefore=4)
    style_section = ParagraphStyle('s', fontSize=11, textColor=dark,
                                   fontName='Helvetica-Bold', spaceAfter=4, spaceBefore=10)
    style_normal  = ParagraphStyle('n', fontSize=10, spaceAfter=4)

    def make_table(data, col_widths, total_rows=[]):
        ts = [
            ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
            ('BACKGROUND',  (0,0), (-1,0),  cinza_hdr),
            ('GRID',        (0,0), (-1,-1), 0.4, rl_colors.HexColor('#dddddd')),
            ('FONTSIZE',    (0,0), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [rl_colors.white, rl_colors.HexColor('#fafafa')]),
            ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING',(0,0), (-1,-1), 5),
            ('TOPPADDING',  (0,0), (-1,-1), 3),
            ('BOTTOMPADDING',(0,0),(-1,-1), 3),
        ]
        for r in total_rows:
            ts += [('BACKGROUND', (0,r), (-1,r), amarelo),
                   ('FONTNAME',   (0,r), (-1,r), 'Helvetica-Bold')]
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle(ts))
        return t

    elems = []
    elems.append(Paragraph(
        f"PLANEJAMENTO FISCAL E TRABALHISTA ANUAL<br/>"
        f"<font size=9>Regime: Lucro Presumido — {tipo_servico_str}</font>",
        style_header))
    elems.append(Paragraph(f"<b>Faturamento Projetado Anual:</b> {fmt(faturamento_anual)}", style_normal))

    elems.append(Paragraph("1. Despesas Operacionais com Folha (Acumulado 12 Meses)", style_section))
    d1 = [["Descrição", "Valor Anual (R$)"],
          ["Salários Anualizados",    fmt(salario_anual)],
          ["Pró-Labore Anualizado",   fmt(prolabore_anual)],
          ["13º Salário (Provisão)",  fmt(decimo_terceiro_anual)],
          ["1/3 de Férias (Provisão)",fmt(terco_ferias_anual)],
          ["TOTAL SEM ENCARGOS",      fmt(despesas_folha_sem_encargos)]]
    elems.append(make_table(d1, [120*mm, 55*mm], total_rows=[5]))

    elems.append(Paragraph("2. Encargos Sociais Detalhados (Anual)", style_section))
    d2 = [["Encargo", "Base", "Alíquota", "Valor Anual"],
          ["FGTS sobre Salários",       "Salários",    "8,00%",  fmt(fgts_folha)],
          ["FGTS sobre 13º",            "13º Salário", "8,00%",  fmt(fgts_13)],
          ["FGTS sobre 1/3 Férias",     "1/3 Férias",  "8,00%",  fmt(fgts_ferias)],
          ["INSS sobre Pró-Labore",     "Pró-Labore",  "20,00%", fmt(inss_prolabore)],
          ["INSS sobre Salários",       "Salários",    "20,00%", fmt(inss_salarios)],
          ["INSS sobre 13º",            "13º Salário", "20,00%", fmt(inss_13)],
          ["INSS sobre 1/3 Férias",     "1/3 Férias",  "20,00%", fmt(inss_ferias)],
          ["Terceiros sobre Salários",  "Salários",    "5,80%",  fmt(terceiros_salarios)],
          ["Terceiros sobre 13º",       "13º Salário", "5,80%",  fmt(terceiros_13)],
          ["Terceiros sobre 1/3 Férias","1/3 Férias",  "5,80%",  fmt(terceiros_ferias)],
          ["RAT Ajustado sobre Salários","Salários",   f"{rat_ajustado*100:.3f}%", fmt(rat_salarios)],
          ["RAT Ajustado sobre 13º",    "13º Salário", f"{rat_ajustado*100:.3f}%", fmt(rat_13)],
          ["RAT Ajustado sobre 1/3 Férias","1/3 Férias",f"{rat_ajustado*100:.3f}%",fmt(rat_ferias)],
          ["TOTAL DOS ENCARGOS",        "-", "-",      fmt(total_encargos_anual)]]
    elems.append(make_table(d2, [72*mm, 35*mm, 25*mm, 43*mm], total_rows=[14]))

    elems.append(Paragraph("3. Impostos sobre Faturamento (Lucro Presumido)", style_section))
    d3 = [["Imposto", "Alíquota", "Valor Anual"],
          ["PIS",             "0,65%",               fmt(pis_anual)],
          ["COFINS",          "3,00%",               fmt(cofins_anual)],
          ["ISS (Municipal)", "5,00%",               fmt(iss_anual)],
          ["IRPJ (+ Adicional)","Presunção 15%(+10%)",fmt(irpj_total_anual)],
          ["CSLL",            "Presunção 9%",         fmt(csll_anual)],
          ["TOTAL DE IMPOSTOS","-",                  fmt(total_impostos_faturamento)]]
    elems.append(make_table(d3, [80*mm, 55*mm, 40*mm], total_rows=[6]))

    elems.append(Paragraph("4. Demonstrativo de Resultado Operacional", style_section))
    d4 = [["Faturamento Bruto Total",                fmt(faturamento_anual)],
          ["(-) Folha com Encargos",                 fmt(custo_folha_com_encargos)],
          ["(-) Impostos sobre Faturamento",         fmt(total_impostos_faturamento)],
          ["(=) RESULTADO LÍQUIDO OPERACIONAL (LAIR ANUAL)", fmt(lair_anual)]]
    t4 = Table(d4, colWidths=[120*mm, 55*mm])
    t4.setStyle(TableStyle([
        ('GRID',        (0,0), (-1,-1), 0.4, rl_colors.HexColor('#dddddd')),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS',(0,0),(-1,-2),[rl_colors.white, rl_colors.HexColor('#fafafa')]),
        ('BACKGROUND',  (0,3), (-1,3),  dark),
        ('TEXTCOLOR',   (0,3), (-1,3),  rl_colors.white),
        ('FONTNAME',    (0,3), (-1,3),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,3), (-1,3),  10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING',(0,0), (-1,-1), 5),
        ('TOPPADDING',  (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
    ]))
    elems.append(t4)

    elems.append(Spacer(1, 8*mm))
    img_buf2 = BytesIO()
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.pie(valores, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors_pizza)
    ax2.set_title('Distribuição Anual da Receita Bruta', pad=15)
    fig2.savefig(img_buf2, format='png', bbox_inches='tight', dpi=120)
    img_buf2.seek(0)
    plt.close(fig2)
    elems.append(Image(img_buf2, width=130*mm, height=120*mm))

    doc.build(elems)
    pdf_buf.seek(0)

    st.download_button(
        label="⬇️ Baixar Relatório em PDF",
        data=pdf_buf,
        file_name="Planejamento_Tributario_Lucro_Presumido.pdf",
        mime="application/pdf"
    )
