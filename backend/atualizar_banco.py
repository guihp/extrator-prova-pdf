#!/usr/bin/env python3
"""
Script para atualizar o banco de dados com as novas colunas etapa e progresso
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

def atualizar_banco():
    """Adiciona as colunas etapa e progresso na tabela provas"""
    try:
        # Criar engine
        engine = create_engine(settings.get_postgres_url(), pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Verificar se as colunas já existem
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'provas' 
                AND column_name IN ('etapa', 'progresso')
            """)
            
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            print(f"📋 Colunas existentes: {existing_columns}")
            
            # Adicionar coluna etapa se não existir
            if 'etapa' not in existing_columns:
                print("➕ Adicionando coluna 'etapa'...")
                conn.execute(text("ALTER TABLE provas ADD COLUMN etapa TEXT"))
                conn.commit()
                print("✅ Coluna 'etapa' adicionada com sucesso!")
            else:
                print("ℹ️ Coluna 'etapa' já existe")
            
            # Adicionar coluna progresso se não existir
            if 'progresso' not in existing_columns:
                print("➕ Adicionando coluna 'progresso'...")
                conn.execute(text("ALTER TABLE provas ADD COLUMN progresso INTEGER DEFAULT 0"))
                conn.commit()
                print("✅ Coluna 'progresso' adicionada com sucesso!")
            else:
                print("ℹ️ Coluna 'progresso' já existe")
            
            # Criar índices se não existirem
            print("📊 Criando índices...")
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_provas_status ON provas(status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_provas_progresso ON provas(progresso)"))
                conn.commit()
                print("✅ Índices criados com sucesso!")
            except Exception as e:
                print(f"⚠️ Erro ao criar índices (podem já existir): {e}")
            
            print("\n🎉 Banco de dados atualizado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando atualização do banco de dados...\n")
    sucesso = atualizar_banco()
    sys.exit(0 if sucesso else 1)




