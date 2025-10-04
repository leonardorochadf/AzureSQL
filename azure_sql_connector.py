#!/usr/bin/env python3
"""
Azure SQL Database Connector para MacBook
Script para conectar e executar queries no Azure SQL Database
"""

import pyodbc
import pandas as pd
import os
from typing import List, Dict, Any, Optional
import json

class AzureSQLConnector:
    def __init__(self, server: str, database: str, username: str, password: str, 
                 driver: str = "ODBC Driver 18 for SQL Server"):
        """
        Inicializa a conexão com Azure SQL Database
        
        Args:
            server: Nome do servidor (ex: 'meuservidor.database.windows.net')
            database: Nome do banco de dados
            username: Nome de usuário
            password: Senha
            driver: Driver ODBC (padrão para macOS)
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.connection = None
        
    def connect(self) -> bool:
        """Estabelece conexão com o banco de dados"""
        try:
            connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout=30;"
            )
            
            self.connection = pyodbc.connect(connection_string)
            print(f"✅ Conectado com sucesso ao {self.database} em {self.server}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {str(e)}")
            return False
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Executa uma query e retorna os resultados como DataFrame
        
        Args:
            query: Query SQL para executar
            
        Returns:
            DataFrame com os resultados ou None se houver erro
        """
        if not self.connection:
            print("❌ Não há conexão ativa. Execute connect() primeiro.")
            return None
            
        try:
            df = pd.read_sql(query, self.connection)
            print(f"✅ Query executada com sucesso. {len(df)} linhas retornadas.")
            return df
            
        except Exception as e:
            print(f"❌ Erro ao executar query: {str(e)}")
            return None
    
    def execute_non_query(self, query: str) -> bool:
        """
        Executa uma query que não retorna dados (INSERT, UPDATE, DELETE, etc.)
        
        Args:
            query: Query SQL para executar
            
        Returns:
            True se executado com sucesso, False caso contrário
        """
        if not self.connection:
            print("❌ Não há conexão ativa. Execute connect() primeiro.")
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            print(f"✅ Query executada com sucesso. {cursor.rowcount} linhas afetadas.")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao executar query: {str(e)}")
            return False
    
    def get_table_info(self, table_name: str = None) -> Optional[pd.DataFrame]:
        """
        Obtém informações sobre tabelas do banco
        
        Args:
            table_name: Nome específico da tabela (opcional)
            
        Returns:
            DataFrame com informações das tabelas
        """
        if table_name:
            query = f"""
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = '{table_name}'
            """
        else:
            query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """
        
        return self.execute_query(query)
    
    def get_table_columns(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        Obtém informações sobre as colunas de uma tabela
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            DataFrame com informações das colunas
        """
        query = f"""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        
        return self.execute_query(query)
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            print("🔌 Conexão fechada.")
            self.connection = None

def main():
    """Exemplo de uso do AzureSQLConnector"""
    
    # Configurações de conexão (substitua pelos seus valores)
    SERVER = "seu-servidor.database.windows.net"
    DATABASE = "seu-banco-de-dados"
    USERNAME = "seu-usuario"
    PASSWORD = "sua-senha"
    
    # Criar instância do conector
    sql_conn = AzureSQLConnector(SERVER, DATABASE, USERNAME, PASSWORD)
    
    # Conectar
    if sql_conn.connect():
        try:
            # Exemplo 1: Listar tabelas
            print("\n📋 Listando tabelas do banco:")
            tables = sql_conn.get_table_info()
            if tables is not None:
                print(tables)
            
            # Exemplo 2: Query personalizada
            print("\n🔍 Executando query personalizada:")
            custom_query = "SELECT TOP 10 * FROM sys.tables"
            result = sql_conn.execute_query(custom_query)
            if result is not None:
                print(result)
            
            # Exemplo 3: Informações de uma tabela específica
            print("\n📊 Informações das colunas de uma tabela:")
            # Substitua 'NomeDaTabela' pelo nome real de uma tabela
            # columns_info = sql_conn.get_table_columns('NomeDaTabela')
            # if columns_info is not None:
            #     print(columns_info)
            
        finally:
            # Sempre fechar a conexão
            sql_conn.close()

if __name__ == "__main__":
    main()