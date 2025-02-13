import requests
import json
import time
from pathlib import Path

def load_cnpj_list(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def fetch_cnpj_data(cnpj):
    url = f'https://receitaws.com.br/v1/cnpj/{cnpj}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Failed to fetch data for CNPJ {cnpj}'}
    except Exception as e:
        return {'error': str(e)}

def display_company_data(data):
    if 'error' in data:
        print(f"Erro: {data['error']}")
        return
    
    print("\n=== Dados da Empresa ===")
    print(f"Nome: {data.get('nome', 'N/A')}")
    print(f"Nome Fantasia: {data.get('fantasia', 'N/A')}")
    print(f"CNPJ: {data.get('cnpj', 'N/A')}")
    print(f"Status: {data.get('situacao', 'N/A')}")
    print(f"Abertura: {data.get('abertura', 'N/A')}")
    print(f"Tipo: {data.get('tipo', 'N/A')}")
    print(f"Porte: {data.get('porte', 'N/A')}")
    print(f"Natureza Jurídica: {data.get('natureza_juridica', 'N/A')}")
    print(f"Capital Social: R$ {data.get('capital_social', 'N/A')}")
    print("------------------------\n")

def main():
    cnpj_list = load_cnpj_list('cnpj_list.json')
    results = []

    for cnpj in cnpj_list['cnpjs']:
        print(f'\nConsultando CNPJ: {cnpj}')
        data = fetch_cnpj_data(cnpj)
        display_company_data(data)
        results.append(data)
        time.sleep(20)

    output_path = Path('cnpj_results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f'Resultados salvos em {output_path}')

if __name__ == '__main__':
    main()
