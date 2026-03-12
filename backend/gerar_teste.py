import pandas as pd

def gerar_planilhas_teste():
    # 1. Dados do Estoque (Visão de Suprimentos)
    dados_estoque = {
        'codigo_material': ['MAT-001', 'MAT-002', 'MAT-003', 'MAT-004'],
        'descricao': ['Aço CA50 10mm (kg)', 'Cimento CP II (sc)', 'Perfil UDC Galvanizado (m)', 'Cabo Flexível 2.5mm (m)'],
        'quantidade_estoque': [500, 50, 100, 2000],
        'quantidade_comprada': [300, 0, 50, 0] # O que já está a caminho
    }
    df_estoque = pd.DataFrame(dados_estoque)
    df_estoque.to_excel('planilha_estoque.xlsx', index=False)
    print("✅ planilha_estoque.xlsx gerada com sucesso!")

    # 2. Dados da Engenharia (Visão de Projetos)
    dados_engenharia = {
        'codigo_projeto': ['L008', 'L008', 'L008', 'L009', 'L009'],
        'codigo_material': ['MAT-001', 'MAT-002', 'MAT-004', 'MAT-003', 'MAT-001'],
        'quantidade_pedida': [1000, 40, 3000, 200, 100]
    }
    df_engenharia = pd.DataFrame(dados_engenharia)
    df_engenharia.to_excel('planilha_engenharia.xlsx', index=False)
    print("✅ planilha_engenharia.xlsx gerada com sucesso!")

if __name__ == '__main__':
    gerar_planilhas_teste()