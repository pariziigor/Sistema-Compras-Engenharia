from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import io

app = FastAPI(title="API Compras e Engenharia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect('compras_engenharia.db')
    conn.row_factory = sqlite3.Row 
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
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        df.columns = df.columns.str.strip().str.lower()
        
        colunas_necessarias = ['codigo_material', 'descricao', 'quantidade_estoque', 'quantidade_comprada']
        for col in colunas_necessarias:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"A coluna '{col}' está faltando na planilha.")

        conn = get_db_connection()
        cursor = conn.cursor()

        for index, row in df.iterrows():
            valor_unidade = row.get('unidade_medida', 'UN')
            if pd.isna(valor_unidade) or str(valor_unidade).strip() == '':
                unidade = 'UN'
            else:
                unidade = str(valor_unidade).strip().upper()
            
            cursor.execute('''
                INSERT INTO Materiais (codigo_material, descricao, unidade_medida)
                VALUES (?, ?, ?)
                ON CONFLICT(codigo_material) DO UPDATE SET
                    descricao=excluded.descricao,
                    unidade_medida=excluded.unidade_medida
            ''', (str(row['codigo_material']), str(row['descricao']), unidade))

        conn.commit()
        return {"mensagem": f"Sucesso! {len(df)} itens de estoque foram atualizados."}

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
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

        projetos_agrupados = df.groupby('codigo_projeto')
        projetos_processados = 0
        projetos_alterados = 0

        for projeto, itens in projetos_agrupados:
            projeto_str = str(projeto)
            projetos_processados += 1
            
            cursor.execute("SELECT * FROM Projetos WHERE codigo_projeto = ?", (projeto_str,))
            projeto_db = cursor.fetchone()
            
            mudancas = []
            
            if not projeto_db:
                cursor.execute("INSERT INTO Projetos (codigo_projeto) VALUES (?)", (projeto_str,))
                
                for _, row in itens.iterrows():
                    mat = str(row['codigo_material'])
                    qtd = float(row['quantidade_pedida'])
                    
                    cursor.execute("INSERT OR IGNORE INTO Materiais (codigo_material, descricao) VALUES (?, ?)", (mat, "Descrição pendente"))
                    
                    cursor.execute('''
                        INSERT INTO Necessidade_Projeto (codigo_projeto, codigo_material, quantidade_pedida) 
                        VALUES (?, ?, ?)
                    ''', (projeto_str, mat, qtd))
            else:
                for _, row in itens.iterrows():
                    mat = str(row['codigo_material'])
                    nova_qtd = float(row['quantidade_pedida'])
                    
                    cursor.execute('''
                        SELECT quantidade_pedida FROM Necessidade_Projeto 
                        WHERE codigo_projeto = ? AND codigo_material = ?
                    ''', (projeto_str, mat))
                    necessidade_db = cursor.fetchone()
                    
                    if not necessidade_db:
                        mudancas.append(f"Novo material adicionado: {mat} ({nova_qtd})")
                        cursor.execute("INSERT OR IGNORE INTO Materiais (codigo_material, descricao) VALUES (?, ?)", (mat, "Descrição pendente"))
                        cursor.execute('''
                            INSERT INTO Necessidade_Projeto (codigo_projeto, codigo_material, quantidade_pedida) 
                            VALUES (?, ?, ?)
                        ''', (projeto_str, mat, nova_qtd))
                        
                    elif necessidade_db['quantidade_pedida'] != nova_qtd:
                        qtd_antiga = necessidade_db['quantidade_pedida']
                        mudancas.append(f"Material {mat} alterado de {qtd_antiga} para {nova_qtd}")
                        cursor.execute('''
                            UPDATE Necessidade_Projeto SET quantidade_pedida = ? 
                            WHERE codigo_projeto = ? AND codigo_material = ?
                        ''', (nova_qtd, projeto_str, mat))
                
                if mudancas:
                    projetos_alterados += 1
                    descricao_completa = " | ".join(mudancas)
                    
                    cursor.execute('''
                        UPDATE Projetos 
                        SET versao = versao + 1, status = 'Alterado', ultima_alteracao = CURRENT_TIMESTAMP 
                        WHERE codigo_projeto = ?
                    ''', (projeto_str,))
                    
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
    
    cursor.execute('''
        SELECT codigo_projeto, status, data_criacao, ultima_alteracao, versao 
        FROM Projetos
        ORDER BY ultima_alteracao DESC
    ''')
    projetos = [dict(row) for row in cursor.fetchall()]
    
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
    
    cursor.execute('''
        SELECT 
            n.codigo_material,
            m.descricao,
            IFNULL(m.unidade_medida, '-') as unidade_medida,
            SUM(n.quantidade_pedida) as demanda_total_obras,
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