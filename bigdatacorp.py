import requests

# URL do endpoint da BigDataCorp
url = "https://api.bigdatacorp.com.br/grupo-economico"

# Parâmetros para filtrar o grupo econômico
params = {
    'cnpj': '32785497000197',  # CNPJ da empresa ou grupo
    'token': 'SEU_ACCESS_TOKEN',
}

response = requests.get(url, params=params)

# Verificando a resposta
if response.status_code == 200:
    dados = response.json()
    print(dados)
else:
    print("Erro ao consultar dados:", response.status_code)
