import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
import base64

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
st.markdown("""
<div class="titulo-header">
    📊 PLANEJAMENTO FISCAL E TRABALHISTA ANUAL<br>
    <span style="font-size:13px; font-weight:normal;">Regime: Lucro Presumido — Serviços</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FORMULÁRIO DE ENTRADA
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# CÁLCULOS
# ─────────────────────────────────────────────
if calcular:

    # Presunção
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

    # Folha anual
    salario_anual        = salario_mensal * 12
    prolabore_anual      = prolabore_mensal * 12
    decimo_terceiro_anual = salario_mensal * 12
    terco_ferias_anual   = decimo_terceiro_anual / 3
    despesas_folha_sem_encargos = salario_anual + prolabore_anual + decimo_terceiro_anual + terco_ferias_anual

    # FGTS
    fgts_folha  = salario_anual * 0.08
    fgts_13     = decimo_terceiro_anual * 0.08
    fgts_ferias = terco_ferias_anual * 0.08
    total_fgts  = fgts_folha + fgts_13 + fgts_ferias

    # INSS
    inss_prolabore = prolabore_anual * 0.20
    inss_salarios  = salario_anual * 0.20
    inss_13        = decimo_terceiro_anual * 0.20
    inss_ferias    = terco_ferias_anual * 0.20
    total_inss     = inss_prolabore + inss_salarios + inss_13 + inss_ferias

    # Terceiros
    terceiros_salarios = salario_anual * 0.058
    terceiros_13       = decimo_terceiro_anual * 0.058
    terceiros_ferias   = terco_ferias_anual * 0.058
    total_terceiros    = terceiros_salarios + terceiros_13 + terceiros_ferias

    # RAT Ajustado
    rat_salarios   = salario_anual * rat_ajustado
    rat_13         = decimo_terceiro_anual * rat_ajustado
    rat_ferias     = terco_ferias_anual * rat_ajustado
    total_rat_ajustado = rat_salarios + rat_13 + rat_ferias

    total_encargos_anual    = total_fgts + total_inss + total_terceiros + total_rat_ajustado
    custo_folha_com_encargos = despesas_folha_sem_encargos + total_encargos_anual

    # Impostos
    pis_anual    = faturamento_anual * 0.0065
    cofins_anual = faturamento_anual * 0.0300
    iss_anual    = faturamento_anual * 0.0500

    base_irpj_anual = faturamento_anual * presuncao_irpj
    base_csll_anual = faturamento_anual * presuncao_csll

    irpj_subtotal = base_irpj_anual * 0.15
    csll_anual    = base_csll_anual * 0.09

    adicional_irpj = (base_irpj_anual - 240000) * 0.10 if base_irpj_anual > 240000 else 0
    irpj_total_anual = irpj_subtotal + adicional_irpj

    total_impostos_faturamento = pis_anual + cofins_anual + iss_anual + irpj_total_anual + csll_anual
    custo_total_empresa        = total_impostos_faturamento + custo_folha_com_encargos
    lair_anual                 = faturamento_anual - custo_total_empresa

    # ─────────────────────────────────────────
    # EXIBIÇÃO DOS RESULTADOS
    # ─────────────────────────────────────────

    def fmt(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
    import pandas as pd
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

    # ─────────────────────────────────────────
    # GRÁFICO DE PIZZA
    # ─────────────────────────────────────────
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
    colors = ['#e74c3c', '#e67e22', '#c0392b', '#34495e', '#bdc3c7', '#2ecc71']
    ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.set_title('Distribuição Anual da Receita Bruta (Faturamento)', pad=20)
    st.pyplot(fig)
    plt.close()

    # ─────────────────────────────────────────
    # GERAÇÃO DO PDF PARA DOWNLOAD
    # ─────────────────────────────────────────
    img_buf = BytesIO()
    fig2, ax2 = plt.subplots(figsize=(7, 7))
    ax2.pie(valores, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax2.set_title('Distribuição Anual da Receita Bruta (Faturamento)', pad=20)
    fig2.savefig(img_buf, format='png', bbox_inches='tight')
    img_buf.seek(0)
    img_b64 = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close(fig2)

    html_pdf = f'''
<html><head><meta charset="UTF-8">
<style>
  @page {{ size: A4; margin: 12mm; }}
  body {{ font-family: Arial, sans-serif; color: #333; font-size: 10.5px; line-height: 1.3; }}
  .header {{ background-color: #2c3e50; color: white; padding: 12px; text-align: center; font-size: 15px; font-weight: bold; border-radius: 4px; }}
  h3 {{ border-bottom: 2px solid #2c3e50; padding-bottom: 2px; margin-top: 12px; color: #2c3e50; font-size: 12px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 5px 0; }}
  th, td {{ padding: 5px 8px; border: 1px solid #ddd; text-align: left; }}
  th {{ background-color: #f5f5f5; font-weight: bold; }}
  .total-row {{ font-weight: bold; background-color: #f9f9db; }}
  .grand-total {{ font-weight: bold; background-color: #2c3e50; color: white; font-size: 12px; }}
</style></head><body>
<div class="header">PLANEJAMENTO FISCAL E TRABALHISTA ANUAL<br>
<small>Regime: Lucro Presumido - {tipo_servico_str}</small></div>
<p><strong>Faturamento Projetado Anual:</strong> {fmt(faturamento_anual)}</p>

<h3>1. Despesas Operacionais com Folha (Acumulado 12 Meses)</h3>
<table>
  <tr><th>Descrição</th><th>Valor Anual (R$)</th></tr>
  <tr><td>Salários Anualizados</td><td>{fmt(salario_anual)}</td></tr>
  <tr><td>Pró-Labore Anualizado</td><td>{fmt(prolabore_anual)}</td></tr>
  <tr><td>13º Salário (Provisão)</td><td>{fmt(decimo_terceiro_anual)}</td></tr>
  <tr><td>1/3 de Férias (Provisão)</td><td>{fmt(terco_ferias_anual)}</td></tr>
  <tr class="total-row"><td>TOTAL SEM ENCARGOS</td><td>{fmt(despesas_folha_sem_encargos)}</td></tr>
</table>

<h3>2. Encargos Sociais Detalhados (Anual)</h3>
<table>
  <tr><th>Encargo</th><th>Base</th><th>Alíquota</th><th>Valor Anual</th></tr>
  <tr><td>FGTS sobre Salários</td><td>Salários</td><td>8,00%</td><td>{fmt(fgts_folha)}</td></tr>
  <tr><td>FGTS sobre 13º</td><td>13º Salário</td><td>8,00%</td><td>{fmt(fgts_13)}</td></tr>
  <tr><td>FGTS sobre 1/3 Férias</td><td>1/3 Férias</td><td>8,00%</td><td>{fmt(fgts_ferias)}</td></tr>
  <tr><td>INSS sobre Pró-Labore</td><td>Pró-Labore</td><td>20,00%</td><td>{fmt(inss_prolabore)}</td></tr>
  <tr><td>INSS sobre Salários</td><td>Salários</td><td>20,00%</td><td>{fmt(inss_salarios)}</td></tr>
  <tr><td>INSS sobre 13º</td><td>13º Salário</td><td>20,00%</td><td>{fmt(inss_13)}</td></tr>
  <tr><td>INSS sobre 1/3 Férias</td><td>1/3 Férias</td><td>20,00%</td><td>{fmt(inss_ferias)}</td></tr>
  <tr><td>Terceiros sobre Salários</td><td>Salários</td><td>5,80%</td><td>{fmt(terceiros_salarios)}</td></tr>
  <tr><td>Terceiros sobre 13º</td><td>13º Salário</td><td>5,80%</td><td>{fmt(terceiros_13)}</td></tr>
  <tr><td>Terceiros sobre 1/3 Férias</td><td>1/3 Férias</td><td>5,80%</td><td>{fmt(terceiros_ferias)}</td></tr>
  <tr><td>RAT Ajustado sobre Salários</td><td>Salários</td><td>{rat_ajustado*100:.3f}%</td><td>{fmt(rat_salarios)}</td></tr>
  <tr><td>RAT Ajustado sobre 13º</td><td>13º Salário</td><td>{rat_ajustado*100:.3f}%</td><td>{fmt(rat_13)}</td></tr>
  <tr><td>RAT Ajustado sobre 1/3 Férias</td><td>1/3 Férias</td><td>{rat_ajustado*100:.3f}%</td><td>{fmt(rat_ferias)}</td></tr>
  <tr class="total-row"><td>TOTAL DOS ENCARGOS</td><td colspan="2">-</td><td>{fmt(total_encargos_anual)}</td></tr>
</table>

<h3>3. Impostos sobre Faturamento (Lucro Presumido)</h3>
<table>
  <tr><th>Imposto</th><th>Alíquota</th><th>Valor Anual</th></tr>
  <tr><td>PIS</td><td>0,65%</td><td>{fmt(pis_anual)}</td></tr>
  <tr><td>COFINS</td><td>3,00%</td><td>{fmt(cofins_anual)}</td></tr>
  <tr><td>ISS (Municipal)</td><td>5,00%</td><td>{fmt(iss_anual)}</td></tr>
  <tr><td>IRPJ (+ Adicional)</td><td>Presunção 15% (+10%)</td><td>{fmt(irpj_total_anual)}</td></tr>
  <tr><td>CSLL</td><td>Presunção 9%</td><td>{fmt(csll_anual)}</td></tr>
  <tr class="total-row"><td>TOTAL DE IMPOSTOS</td><td>-</td><td>{fmt(total_impostos_faturamento)}</td></tr>
</table>

<h3>4. Demonstrativo de Resultado Operacional</h3>
<table>
  <tr><td>Faturamento Bruto Total</td><td>{fmt(faturamento_anual)}</td></tr>
  <tr><td>(-) Folha com Encargos</td><td>{fmt(custo_folha_com_encargos)}</td></tr>
  <tr><td>(-) Impostos sobre Faturamento</td><td>{fmt(total_impostos_faturamento)}</td></tr>
  <tr class="grand-total"><td>(=) RESULTADO LÍQUIDO OPERACIONAL (LAIR ANUAL)</td><td>{fmt(lair_anual)}</td></tr>
</table>

<div style="text-align:center; margin-top:15px;">
  <img src="data:image/png;base64,{img_b64}" width="420">
</div>
</body></html>
'''

    try:
        from weasyprint import HTML as WP_HTML
        pdf_bytes = WP_HTML(string=html_pdf).write_pdf()
        st.download_button(
            label="⬇️ Baixar Relatório em PDF",
            data=pdf_bytes,
            file_name="Planejamento_Tributario_Lucro_Presumido.pdf",
            mime="application/pdf"
        )
    except ImportError:
        st.info("Para gerar o PDF, instale o WeasyPrint no servidor: `pip install weasyprint`")
        st.download_button(
            label="⬇️ Baixar Relatório em HTML",
            data=html_pdf.encode("utf-8"),
            file_name="Planejamento_Tributario.html",
            mime="text/html"
        )
