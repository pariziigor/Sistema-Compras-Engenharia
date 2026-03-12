import sqlite3

def criar_banco_de_dados():
    conn = sqlite3.connect('compras_engenharia.db')
    cursor = conn.cursor()

    # 1. Tabela de Projetos 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_projeto TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Aberto',
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultima_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
            versao INTEGER DEFAULT 1
        )
    ''')

    # 2. Tabela de Materiais 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_material TEXT UNIQUE NOT NULL,
            descricao TEXT NOT NULL
        )
    ''')

    # 3. Tabela de Estoque e Compras 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Estoque_Compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_material TEXT UNIQUE NOT NULL,
            quantidade_estoque REAL DEFAULT 0.0,
            quantidade_comprada REAL DEFAULT 0.0,
            data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (codigo_material) REFERENCES Materiais(codigo_material)
        )
    ''')

    # 4. Tabela de Necessidade por Projeto 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Necessidade_Projeto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_projeto TEXT NOT NULL,
            codigo_material TEXT NOT NULL,
            quantidade_pedida REAL NOT NULL,
            FOREIGN KEY (codigo_projeto) REFERENCES Projetos(codigo_projeto),
            FOREIGN KEY (codigo_material) REFERENCES Materiais(codigo_material)
        )
    ''')

    # 5. Tabela de Histórico de Alterações 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Historico_Alteracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_projeto TEXT NOT NULL,
            data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
            descricao_mudanca TEXT NOT NULL,
            FOREIGN KEY (codigo_projeto) REFERENCES Projetos(codigo_projeto)
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados 'compras_engenharia.db' e tabelas criados com sucesso!")

if __name__ == '__main__':
    criar_banco_de_dados()