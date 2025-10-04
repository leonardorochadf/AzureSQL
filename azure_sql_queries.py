#!/usr/bin/env python3
"""
Exemplos de Queries Úteis para Azure SQL Database
Script com queries comuns para análise e manutenção
"""

from azure_sql_connector import AzureSQLConnector
import pandas as pd
from typing import Optional

class AzureSQLQueries:
    def __init__(self, connector: AzureSQLConnector):
        self.connector = connector
    
    def get_database_info(self) -> Optional[pd.DataFrame]:
        """Informações gerais do banco de dados"""
        query = """
        SELECT 
            DB_NAME() as DatabaseName,
            @@VERSION as SQLVersion,
            GETDATE() as CurrentDateTime,
            USER_NAME() as CurrentUser
        """
        return self.connector.execute_query(query)
    
    def get_table_sizes(self) -> Optional[pd.DataFrame]:
        """Tamanho das tabelas no banco"""
        query = """
        SELECT 
            t.NAME AS TableName,
            s.Name AS SchemaName,
            p.rows AS RowCounts,
            CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS TotalSpaceMB,
            CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS UsedSpaceMB, 
            CAST(ROUND(((SUM(a.total_pages) - SUM(a.used_pages)) * 8) / 1024.00, 2) AS NUMERIC(36, 2)) AS UnusedSpaceMB
        FROM sys.tables t
        INNER JOIN sys.indexes i ON t.OBJECT_ID = i.object_id
        INNER JOIN sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
        INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
        LEFT OUTER JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE t.NAME NOT LIKE 'dt%' 
            AND t.is_ms_shipped = 0
            AND i.OBJECT_ID > 255 
        GROUP BY t.Name, s.Name, p.Rows
        ORDER BY TotalSpaceMB DESC
        """
        return self.connector.execute_query(query)
    
    def get_index_fragmentation(self) -> Optional[pd.DataFrame]:
        """Fragmentação dos índices"""
        query = """
        SELECT 
            OBJECT_NAME(ips.object_id) AS TableName,
            i.name AS IndexName,
            ips.index_type_desc,
            ips.avg_fragmentation_in_percent,
            ips.page_count,
            CASE 
                WHEN ips.avg_fragmentation_in_percent > 30 THEN 'REBUILD'
                WHEN ips.avg_fragmentation_in_percent > 5 THEN 'REORGANIZE'
                ELSE 'OK'
            END AS Recommendation
        FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
        INNER JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
        WHERE ips.avg_fragmentation_in_percent > 0
            AND ips.page_count > 100
        ORDER BY ips.avg_fragmentation_in_percent DESC
        """
        return self.connector.execute_query(query)
    
    def get_slow_queries(self, top: int = 10) -> Optional[pd.DataFrame]:
        """Queries mais lentas (requer Query Store habilitado)"""
        query = f"""
        SELECT TOP {top}
            qt.query_sql_text,
            rs.avg_duration/1000 as avg_duration_ms,
            rs.avg_cpu_time/1000 as avg_cpu_time_ms,
            rs.avg_logical_io_reads,
            rs.execution_count,
            rs.last_execution_time
        FROM sys.query_store_query_text qt
        INNER JOIN sys.query_store_query q ON qt.query_text_id = q.query_text_id
        INNER JOIN sys.query_store_plan p ON q.query_id = p.query_id
        INNER JOIN sys.query_store_runtime_stats rs ON p.plan_id = rs.plan_id
        WHERE rs.last_execution_time > DATEADD(day, -7, GETDATE())
        ORDER BY rs.avg_duration DESC
        """
        return self.connector.execute_query(query)
    
    def get_connection_info(self) -> Optional[pd.DataFrame]:
        """Informações sobre conexões ativas"""
        query = """
        SELECT 
            session_id,
            login_name,
            host_name,
            program_name,
            client_interface_name,
            login_time,
            last_request_start_time,
            status
        FROM sys.dm_exec_sessions
        WHERE is_user_process = 1
        ORDER BY login_time DESC
        """
        return self.connector.execute_query(query)
    
    def get_blocking_sessions(self) -> Optional[pd.DataFrame]:
        """Sessões bloqueadas"""
        query = """
        SELECT 
            blocking_session_id,
            session_id,
            wait_type,
            wait_time,
            wait_resource,
            resource_description
        FROM sys.dm_exec_requests
        WHERE blocking_session_id <> 0
        """
        return self.connector.execute_query(query)
    
    def get_database_usage_stats(self) -> Optional[pd.DataFrame]:
        """Estatísticas de uso do banco"""
        query = """
        SELECT 
            DB_NAME() as DatabaseName,
            (SELECT COUNT(*) FROM sys.tables) as TableCount,
            (SELECT COUNT(*) FROM sys.views) as ViewCount,
            (SELECT COUNT(*) FROM sys.procedures) as ProcedureCount,
            (SELECT COUNT(*) FROM sys.functions) as FunctionCount,
            (SELECT COUNT(*) FROM sys.triggers) as TriggerCount
        """
        return self.connector.execute_query(query)
    
    def run_maintenance_script(self) -> bool:
        """Executa o script de manutenção AzureSQLMaintenance"""
        query = "EXEC AzureSQLMaintenance 'all', @LogToTable=1"
        return self.connector.execute_non_query(query)
    
    def get_table_row_counts(self) -> Optional[pd.DataFrame]:
        """Contagem de linhas por tabela"""
        query = """
        SELECT 
            SCHEMA_NAME(t.schema_id) AS SchemaName,
            t.name AS TableName,
            SUM(p.rows) AS RowCount
        FROM sys.tables t
        INNER JOIN sys.partitions p ON t.object_id = p.object_id
        WHERE p.index_id IN (0, 1)
        GROUP BY t.schema_id, t.name
        ORDER BY RowCount DESC
        """
        return self.connector.execute_query(query)

def main():
    """Exemplo de uso das queries"""
    
    # Configurações (substitua pelos seus valores)
    SERVER = "seu-servidor.database.windows.net"
    DATABASE = "seu-banco-de-dados"
    USERNAME = "seu-usuario"
    PASSWORD = "sua-senha"
    
    # Criar conector
    sql_conn = AzureSQLConnector(SERVER, DATABASE, USERNAME, PASSWORD)
    
    if sql_conn.connect():
        try:
            queries = AzureSQLQueries(sql_conn)
            
            print("📊 Informações do Banco de Dados:")
            db_info = queries.get_database_info()
            if db_info is not None:
                print(db_info)
            
            print("\n📏 Tamanhos das Tabelas:")
            table_sizes = queries.get_table_sizes()
            if table_sizes is not None:
                print(table_sizes.head(10))
            
            print("\n🔧 Fragmentação dos Índices:")
            fragmentation = queries.get_index_fragmentation()
            if fragmentation is not None:
                print(fragmentation.head(10))
            
            print("\n📈 Contagem de Linhas por Tabela:")
            row_counts = queries.get_table_row_counts()
            if row_counts is not None:
                print(row_counts.head(10))
            
        finally:
            sql_conn.close()

if __name__ == "__main__":
    main()