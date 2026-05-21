import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# Persistência no volume montado
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'baseline.db')

# Garantir que a pasta .tmp exista antes do SQLAlchemy tentar criar o arquivo .db
db_dir = os.path.dirname(DB_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()

class BaselineMetrics(Base):
    __tablename__ = 'baseline_metrics'
    
    id = Column(Integer, primary_key=True)
    branch = Column(String, default="main")
    test_coverage = Column(Float, nullable=False)
    critical_vulns = Column(Integer, default=0)
    complexity_score = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_current_baseline():
    """Retorna as métricas atuais da baseline."""
    session = SessionLocal()
    baseline = session.query(BaselineMetrics).order_by(BaselineMetrics.updated_at.desc()).first()
    
    if baseline:
        # Prevenimos erro de detached instance extraindo os dados antes do session.close()
        data = {
            "test_coverage": baseline.test_coverage,
            "critical_vulns": baseline.critical_vulns,
            "complexity_score": baseline.complexity_score
        }
    else:
        data = None
        
    session.close()
    return data

def update_baseline(coverage: float, vulns: int, complexity: float):
    """Atualiza a foto da baseline oficial (ocorre apenas após merges na main)."""
    session = SessionLocal()
    new_baseline = BaselineMetrics(
        test_coverage=coverage,
        critical_vulns=vulns,
        complexity_score=complexity,
        updated_at=datetime.datetime.utcnow()
    )
    session.add(new_baseline)
    session.commit()
    session.close()
    print("[Jarvis] Baseline atualizada com sucesso.")
