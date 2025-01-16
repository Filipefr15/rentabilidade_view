import pandas as pd
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/consulta', methods=['GET'])
def consulta():
  cnpj = request.args.get('cnpj')
  ano = request.args.get('ano')
  mes = request.args.get('mes')

  cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')

  fundo_data = infofundos(cnpj, ano, mes)
  # print(fundo_data)
  if fundo_data.get('error'):
    return render_template('resultado.html', erro=fundo_data['error'])

  return render_template('resultado.html', fundo=fundo_data)


# @app.route('/pegarvendas')
# def pegarvendas():
#   tabela = pd.read_csv('advertising.csv')
#   total_vendas = tabela['Vendas'].sum()
#   resposta = {'total_vendas': total_vendas}
#   return jsonify(resposta)


def infofundos(CNPJ_FUNDO, ano, mes):

  tabela = pd.read_csv(f"inf_diario_fi_{ano}{mes}.csv", sep=";")
  tabela_rent_mes = pd.read_csv('lamina_fi_rentab_mes_202408.csv',
                                sep=";",
                                encoding='latin1')
  tabela_infos_fundos = pd.read_csv('cad_fi.csv',
                                    sep=";",
                                    encoding='latin1',
                                    low_memory=False)

  # Remover pontos, barras e hífen do CNPJ para comparação
  CNPJ_FUNDO = CNPJ_FUNDO.replace('.', '').replace('/',
                                                   '').replace('-',
                                                               '').strip()
  # Filtragem da tabela
  dict_mes_datas = {
      '202408': '2024-08-30',
      '202407': '2024-07-31',
      '202406': '2024-06-28',
      '202405': '2024-05-31',
      '202404': '2024-04-30',
      '202403': '2024-03-28',
      '202402': '2024-02-29',
      '202401': '2024-01-31'
  }
  anomes = f"{ano}{mes}"
  tabela_filtrada = tabela[tabela['DT_COMPTC'] == dict_mes_datas[anomes]]

  mes = int(mes)
  tabela_mes_rentab = tabela_rent_mes[tabela_rent_mes['MES_RENTAB'] == mes]

  tabela_rent_mes_filtrada = tabela_mes_rentab[
      tabela_mes_rentab['CNPJ_FUNDO'].str.replace('.', '').str.replace(
          '/', '').str.replace('-', '').values == CNPJ_FUNDO]

  tabela_infos_fundos_filtrada = tabela_infos_fundos[
      tabela_infos_fundos['CNPJ_FUNDO'].str.replace('.', '').str.replace(
          '/', '').str.replace('-', '').values == CNPJ_FUNDO]

  # Verificar se algum fundo foi encontrado
  fundo_sem_lamina = False
  fundo_sem_pl = False
  if tabela_filtrada.empty and tabela_rent_mes_filtrada.empty:
    return {'error': 'Fundo não encontrado'}
  elif tabela_rent_mes_filtrada.empty:
    fundo_sem_lamina = True
  elif tabela_filtrada.empty:
    fundo_sem_pl = True

  fundo = tabela_filtrada[tabela_filtrada['CNPJ_FUNDO'].str.replace(
      r'[./-]', '', regex=True) == CNPJ_FUNDO]

  # Obtenha os dados do fundo
  if fundo_sem_lamina:
    try:
      nome_fundo = str(tabela_infos_fundos_filtrada['DENOM_SOCIAL'].values[0])
      cnpj_fundo = str(fundo['CNPJ_FUNDO'].values[0])
      referencia_fundo = str(fundo['DT_COMPTC'].values[0])
      total_fundo = float(fundo['VL_TOTAL'].values[0])
      quota_fundo = float(fundo['VL_QUOTA'].values[0])
      patrimonio_liquido_fundo = float(fundo['VL_PATRIM_LIQ'].values[0])
      cotistas_fundo = int(fundo['NR_COTST'].values[0])
      rent_fundo_mes = 'Indisponível'
    except IndexError:
      return {'error': 'Dados do fundo não disponíveis'}

  elif fundo_sem_pl:
    try:
      nome_fundo = str(tabela_infos_fundos_filtrada['DENOM_SOCIAL'].values[0])
      cnpj_fundo = str(tabela_infos_fundos_filtrada['CNPJ_FUNDO'].values[0])
      referencia_fundo = 'Indisponível'
      total_fundo = 'Indisponível'
      quota_fundo = 'Indisponível'
      patrimonio_liquido_fundo = 'Indisponível'
      cotistas_fundo = 'Indisponível'
      rent_fundo_mes = float(
          tabela_rent_mes_filtrada['PR_RENTAB_MES'].values[0])
    except IndexError:
      return {'error': 'Dados do fundo não disponíveis'}

  else:
    try:
      nome_fundo = str(tabela_rent_mes_filtrada['DENOM_SOCIAL'].values[0])
      cnpj_fundo = str(fundo['CNPJ_FUNDO'].values[0])
      referencia_fundo = str(fundo['DT_COMPTC'].values[0])
      total_fundo = float(fundo['VL_TOTAL'].values[0])
      quota_fundo = float(fundo['VL_QUOTA'].values[0])
      patrimonio_liquido_fundo = float(fundo['VL_PATRIM_LIQ'].values[0])
      cotistas_fundo = int(fundo['NR_COTST'].values[0])
      rent_fundo_mes = float(
          tabela_rent_mes_filtrada['PR_RENTAB_MES'].values[0])
    except IndexError:
      return {'error': 'Dados do fundo não disponíveis'}

  if fundo_sem_lamina:
    pass
  else:
    rent_fundo_mes = f"{rent_fundo_mes}%"
  ano, mes, dia = referencia_fundo.split('-')
  referencia_fundo = f"{mes}/{ano}"

  return {
      'cnpj_fundo': cnpj_fundo,
      'dia_referencia': referencia_fundo,
      'total_fundo': total_fundo,
      'valor_cota': quota_fundo,
      'patrimonio_liquido_fundo': patrimonio_liquido_fundo,
      'cotistas_fundo': cotistas_fundo,
      'rent_fundo_mes': rent_fundo_mes,
      'nome_fundo': nome_fundo
  }

  # @app.route('/<CNPJ_FUNDO>/<CNPJ_PARTE_2>', methods=['GET'])
  # def infofundosseparated(CNPJ_FUNDO, CNPJ_PARTE_2):
  #   tabela = pd.read_csv('inf_diario_fi_202408.csv', sep=";")
  #   tabela_rent_mes = pd.read_csv('lamina_fi_rentab_mes_202408.csv',
  #                                 sep=";",
  #                                 encoding='latin1')

  #   # Remover pontos, barras e hífen do CNPJ para comparação
  #   CNPJ_FUNDO += CNPJ_PARTE_2
  #   CNPJ_FUNDO = CNPJ_FUNDO.replace('.', '').replace('/', '').replace('-', '')

  #   # Filtragem da tabela
  #   tabela_filtrada = tabela[tabela['DT_COMPTC'] == '2024-08-30']
  #   tabela_rent_mes_filtrada = tabela_rent_mes[
  #       tabela_rent_mes['CNPJ_FUNDO'].str.replace(r'[./-]', '',
  #                                                 regex=True) == CNPJ_FUNDO]

  #   # Verificar se algum fundo foi encontrado
  #   if tabela_filtrada.empty or tabela_rent_mes_filtrada.empty:
  #     return jsonify({'error': 'Fundo não encontrado'}), 404

  #   fundo = tabela_filtrada[tabela_filtrada['CNPJ_FUNDO'].str.replace(
  #       r'[./-]', '', regex=True) == CNPJ_FUNDO]

  #   # Obtenha os dados do fundo
  #   try:
  #     nome_fundo = str(tabela_rent_mes_filtrada['DENOM_SOCIAL'].values[0])
  #     cnpj_fundo = str(fundo['CNPJ_FUNDO'].values[0])
  #     referencia_fundo = str(fundo['DT_COMPTC'].values[0])
  #     total_fundo = float(fundo['VL_TOTAL'].values[0])
  #     quota_fundo = float(fundo['VL_QUOTA'].values[0])
  #     patrimonio_liquido_fundo = float(fundo['VL_PATRIM_LIQ'].values[0])
  #     cotistas_fundo = int(fundo['NR_COTST'].values[0])
  #     rent_fundo_mes = float(tabela_rent_mes_filtrada['PR_RENTAB_MES'].values[0])
  #   except IndexError:
  #     return jsonify({'error': 'Dados do fundo não disponíveis'}), 404

  #   rent_fundo_mes = str(rent_fundo_mes)
  #   rent_fundo_mes += '%'

  #   resposta = {
  #       'cnpj_fundo': cnpj_fundo,
  #       'dia_referencia': referencia_fundo,
  #       'total_fundo': total_fundo,
  #       'valor_cota': quota_fundo,
  #       'patrimonio_liquido_fundo': patrimonio_liquido_fundo,
  #       'cotistas_fundo': cotistas_fundo,
  #       'rent_fundo_mes': rent_fundo_mes,
  #       'nome_fundo': nome_fundo
  #   }
  #   return jsonify(resposta), 200

  #rodar nossa api


app.run(host='0.0.0.0')
