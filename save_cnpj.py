import pandas as pd
import json
import os

def save_cnpj_list():
    try:
        for delimiter in [',', ';', '\t']:
            try:
                df = pd.read_csv('empresas_b3.csv', delimiter=delimiter, encoding='utf-8')
                if 'CNPJ' in df.columns:
                    break
            except:
                continue
        else:
            raise ValueError("Could not read the CSV file with any common delimiter")

        if 'CNPJ' not in df.columns:
            raise ValueError("CSV file must contain a 'CNPJ' column")

        cnpj_list = []
        for cnpj in df['CNPJ'].dropna():
            clean_cnpj = ''.join(filter(str.isdigit, str(cnpj)))
            if len(clean_cnpj) >= 14:
                cnpj_list.append(clean_cnpj)
            else:
                print(f"Skipping invalid CNPJ: {cnpj}")

        output_file = 'cnpj_list.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_cnpjs': len(cnpj_list),
                'cnpjs': cnpj_list
            }, f, ensure_ascii=False, indent=4)

        print(f"Successfully saved {len(cnpj_list)} CNPJs to {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check if your CSV file is properly formatted and contains a 'CNPJ' column")

if __name__ == "__main__":
    save_cnpj_list()
