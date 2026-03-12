from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import io

app = FastAPI(title="API Compras e Engenharia")

# Configuração de CORS: Permite que o front-end (React) faça requisições para esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função auxiliar para conectar ao banco
def get_db_connection():
    conn = sqlite3.connect('compras_engenharia.db')
    conn.row_factory = sqlite3.Row # Permite acessar as colunas pelo nome
    return conn

@app.get("/")
def home():
    return {"mensagem": "API de Compras e Engenharia rodando perfeitamente!"}

@app.post("/api/upload/estoque")
async def upload_estoque(file: UploadFile = File(...)):
    """
    Recebe a planilha de estoque e compras do setor de Suprimentos.
    Espera-se as colunas: codigo_material, descricao, quantidade_estoque, quantidade_comprada
    """
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Formato inválido. Por favor, envie um arquivo Excel (.xlsx ou .xls).")

    try:
        # Lê o arquivo Excel em memória usando Pandas
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Padroniza os nomes das colunas para evitar erros de digitação na planilha
        df.columns = df.columns.str.strip().str.lower()
        
        # Verifica se as colunas necessárias existem
        colunas_necessarias = ['codigo_material', 'descricao', 'quantidade_estoque', 'quantidade_comprada']
        for col in colunas_necessarias:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"A coluna '{col}' está faltando na planilha.")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Itera sobre as linhas da planilha
        for index, row in df.iterrows():
            # 1. Garante que o material existe no catálogo (Tabela Materiais)
            cursor.execute('''
                INSERT OR IGNORE INTO Materiais (codigo_material, descricao)
                VALUES (?, ?)
            ''', (str(row['codigo_material']), str(row['descricao'])))

            # 2. Atualiza ou insere as quantidades no Estoque (Tabela Estoque_Compras)
            cursor.execute('''
                INSERT INTO Estoque_Compras (codigo_material, quantidade_estoque, quantidade_comprada)
                VALUES (?, ?, ?)
                ON CONFLICT(codigo_material) DO UPDATE SET
                    quantidade_estoque=excluded.quantidade_estoque,
                    quantidade_comprada=excluded.quantidade_comprada,
                    data_atualizacao=CURRENT_TIMESTAMP
            ''', (str(row['codigo_material']), float(row['quantidade_estoque']), float(row['quantidade_comprada'])))

        conn.commit()
        return {"mensagem": f"Sucesso! {len(df)} itens de estoque foram atualizados."}

    except Exception as e:
        if 'conn' in locals():
            conn.rollback() # Desfaz as alterações se der erro
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@app.post("/api/upload/engenharia")
async def upload_engenharia(file: UploadFile = File(...)):
    """
    Recebe a planilha de projetos da Engenharia.
    Espera-se as colunas: codigo_projeto, codigo_material, quantidade_pedida
    """
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Formato inválido. Envie um Excel (.xlsx ou .xls).")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        df.columns = df.columns.str.strip().str.lower()
        
        colunas_necessarias = ['codigo_projeto', 'codigo_material', 'quantidade_pedida']
        for col in colunas_necessarias:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"A coluna '{col}' está faltando.")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Agrupa os dados por projeto para processar um projeto por vez
        projetos_agrupados = df.groupby('codigo_projeto')
        projetos_processados = 0
        projetos_alterados = 0

        for projeto, itens in projetos_agrupados:
            projeto_str = str(projeto)
            projetos_processados += 1
            
            # Verifica se o projeto já existe no banco
            cursor.execute("SELECT * FROM Projetos WHERE codigo_projeto = ?", (projeto_str,))
            projeto_db = cursor.fetchone()
            
            mudancas = []
            
            if not projeto_db:
                # 1. PROJETO NOVO: Insere na tabela de Projetos
                cursor.execute("INSERT INTO Projetos (codigo_projeto) VALUES (?)", (projeto_str,))
                
                # Insere os materiais pedidos para esse novo projeto
                for _, row in itens.iterrows():
                    mat = str(row['codigo_material'])
                    qtd = float(row['quantidade_pedida'])
                    
                    # Garante que o material exista no catálogo para não dar erro de chave estrangeira
                    cursor.execute("INSERT OR IGNORE INTO Materiais (codigo_material, descricao) VALUES (?, ?)", (mat, "Descrição pendente"))
                    
                    cursor.execute('''
                        INSERT INTO Necessidade_Projeto (codigo_projeto, codigo_material, quantidade_pedida) 
                        VALUES (?, ?, ?)
                    ''', (projeto_str, mat, qtd))
            else:
                # 2. PROJETO EXISTENTE: Vamos comparar para ver se houve alteração (Versionamento)
                for _, row in itens.iterrows():
                    mat = str(row['codigo_material'])
                    nova_qtd = float(row['quantidade_pedida'])
                    
                    # Busca a quantidade antiga que estava no banco
                    cursor.execute('''
                        SELECT quantidade_pedida FROM Necessidade_Projeto 
                        WHERE codigo_projeto = ? AND codigo_material = ?
                    ''', (projeto_str, mat))
                    necessidade_db = cursor.fetchone()
                    
                    if not necessidade_db:
                        # Engenharia adicionou um material novo que não estava na versão anterior
                        mudancas.append(f"Novo material adicionado: {mat} ({nova_qtd})")
                        cursor.execute("INSERT OR IGNORE INTO Materiais (codigo_material, descricao) VALUES (?, ?)", (mat, "Descrição pendente"))
                        cursor.execute('''
                            INSERT INTO Necessidade_Projeto (codigo_projeto, codigo_material, quantidade_pedida) 
                            VALUES (?, ?, ?)
                        ''', (projeto_str, mat, nova_qtd))
                        
                    elif necessidade_db['quantidade_pedida'] != nova_qtd:
                        # Engenharia alterou a quantidade de um material existente
                        qtd_antiga = necessidade_db['quantidade_pedida']
                        mudancas.append(f"Material {mat} alterado de {qtd_antiga} para {nova_qtd}")
                        cursor.execute('''
                            UPDATE Necessidade_Projeto SET quantidade_pedida = ? 
                            WHERE codigo_projeto = ? AND codigo_material = ?
                        ''', (nova_qtd, projeto_str, mat))
                
                # Se registra alguma mudança, atualiza a versão do projeto
                if mudancas:
                    projetos_alterados += 1
                    descricao_completa = " | ".join(mudancas) # Junta todas as mudanças em um texto só
                    
                    # Altera o status, sobe a versão e atualiza a data
                    cursor.execute('''
                        UPDATE Projetos 
                        SET versao = versao + 1, status = 'Alterado', ultima_alteracao = CURRENT_TIMESTAMP 
                        WHERE codigo_projeto = ?
                    ''', (projeto_str,))
                    
                    # Salva no histórico para visualização futura no React
                    cursor.execute('''
                        INSERT INTO Historico_Alteracoes (codigo_projeto, descricao_mudanca) 
                        VALUES (?, ?)
                    ''', (projeto_str, descricao_completa))
        
        conn.commit()
        return {
            "mensagem": "Planilha da engenharia processada com sucesso!",
            "resumo": f"{projetos_processados} projetos lidos. {projetos_alterados} projetos sofreram alterações."
        }

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@app.get("/api/projetos")
def listar_projetos():
    """
    Retorna todos os projetos para montar os cards no React.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Puxa os dados principais dos projetos (Abertos, Fechados, Alterados)
    cursor.execute('''
        SELECT codigo_projeto, status, data_criacao, ultima_alteracao, versao 
        FROM Projetos
        ORDER BY ultima_alteracao DESC
    ''')
    projetos = [dict(row) for row in cursor.fetchall()]
    
    # Para cada projeto, já enviamos o histórico junto para quando o usuário clicar no card
    for proj in projetos:
        cursor.execute('''
            SELECT data_alteracao, descricao_mudanca 
            FROM Historico_Alteracoes 
            WHERE codigo_projeto = ?
            ORDER BY data_alteracao DESC
        ''', (proj['codigo_projeto'],))
        proj['historico'] = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return projetos

@app.get("/api/compras/necessidades")
def calcular_necessidades_compras():
    """
    O coração do sistema de suprimentos:
    Calcula Demanda - (Estoque + Pedidos) e retorna só o que precisa ser comprado.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Esta query soma tudo que a engenharia pediu de um material em todos os projetos,
    # subtrai o que já temos e filtra apenas os resultados maiores que zero.
    cursor.execute('''
        SELECT 
            n.codigo_material,
            m.descricao,
            SUM(n.quantidade_pedida) as demanda_total_obras,
            IFNULL(e.quantidade_estoque, 0) as estoque_atual,
            IFNULL(e.quantidade_comprada, 0) as pedidos_colocados,
            (SUM(n.quantidade_pedida) - (IFNULL(e.quantidade_estoque, 0) + IFNULL(e.quantidade_comprada, 0))) as necessidade_real_compra
        FROM Necessidade_Projeto n
        LEFT JOIN Materiais m ON n.codigo_material = m.codigo_material
        LEFT JOIN Estoque_Compras e ON n.codigo_material = e.codigo_material
        GROUP BY n.codigo_material
        HAVING necessidade_real_compra > 0
        ORDER BY necessidade_real_compra DESC
    ''')
    
    necessidades = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return necessidades