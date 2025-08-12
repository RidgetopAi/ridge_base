import os
import psycopg2
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433, 
    'database': 'ridge_base',
    'user': 'ridge_user',
    'password': 'ridge_pass'
}

def test_postgres_connection():
    """Test basic PostgreSQL connection"""
    try:
        # Create connection string
        conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

        # Test with SQLAlchemy engine
        engine = create_engine(conn_string)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"🟢 PostgreSQL connected: {version}")

            # Test our schema exists
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
            tables = [row[0] for row in result.fetchall()]
            print(f"🟢 Tables created: {tables}")
        
        return True
    except Exception as e:
        print(f"🔴 PostgreSQL connection failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("🟢 Redis connected")

        # Test basic operation
        r.set('test_key', 'text_value')
        value = r.get('test_key')
        print(f"🟢 Redis test: {value}")
        r.delete('test_key')

        return True
    except Exception as e:
        print(f"🔴 Redis connection failed: {e}")
        return False
if __name__ == '__main__':
    print("Testing database connections...")
    postgres_ok = test_postgres_connection()
    redis_ok = test_redis_connection()

    if postgres_ok and redis_ok:
        print("\n🟢 All database connections working!")
    else:
        print("\n🔴 Some connections failed")

# Add this to the END of your existing src/database.py file:

class Database:
    """Database connection manager for Ridge Base"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Setup SQLAlchemy engine and session maker"""
        conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        self.engine = create_engine(conn_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close a database session"""
        session.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            session = self.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False