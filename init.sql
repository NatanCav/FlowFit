-- Script de inicialização do banco MySQL
-- Cria o banco se não existir (redundante, mas seguro)
CREATE DATABASE IF NOT EXISTS flowfit;
USE flowfit;

-- As tabelas serão criadas automaticamente pelo SQLAlchemy
-- Este arquivo pode ser usado para dados iniciais específicos