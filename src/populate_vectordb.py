import psycopg2
import numpy as np
from pgvector.psycopg2 import register_vector
import random

# --- CONFIGURACIÓN ---
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "vector_database",
    "user": "admin",
    "password": "admin123"
}

# Definimos 3 dimensiones para coincidir con el ejemplo anterior.
# En un caso real con OpenAI usarías 1536, o con HuggingFace 384/768.
VECTOR_DIM = 3 

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    # Esto es CRÍTICO: Permite a psycopg2 entender el tipo de dato 'vector'
    register_vector(conn)
    return conn

def setup_database(cursor):
    print("🛠️  Configurando base de datos...")
    # Asegurar que la extensión existe
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Reiniciar la tabla para pruebas limpias
    cursor.execute("DROP TABLE IF EXISTS documents;")
    
    # Crear tabla con la dimensión específica
    create_table_query = f"""
    CREATE TABLE documents (
        id bigserial PRIMARY KEY,
        title text,
        content text,
        embedding vector({VECTOR_DIM})
    );
    """
    cursor.execute(create_table_query)
    print("✅ Tabla 'documents' creada.")

def generate_fake_data(num_records=10):
    print(f"🎲 Generando {num_records} registros de prueba...")
    data = []
    topics = ["Inteligencia Artificial", "Bases de Datos", "Docker", "Python", "Cloud"]
    
    for i in range(num_records):
        title = f"{random.choice(topics)} - Artículo {i+1}"
        content = f"Este es un contenido de prueba generado automáticamente para el ID {i+1}."
        
        # Generar un vector aleatorio normalizado (simulando un embedding real)
        # Usamos numpy para crear floats aleatorios
        vector = np.random.rand(VECTOR_DIM).astype(np.float32)
        
        data.append((title, content, vector))
    
    return data

def insert_data(conn, data):
    cur = conn.cursor()
    print("🚀 Insertando datos en Postgres...")
    
    # Inserción eficiente
    query = "INSERT INTO documents (title, content, embedding) VALUES (%s, %s, %s)"
    
    try:
        cur.executemany(query, data)
        conn.commit()
        print(f"✅ Se insertaron {len(data)} registros exitosamente.")
    except Exception as e:
        print(f"❌ Error al insertar: {e}")
        conn.rollback()
    finally:
        cur.close()

def search_similarity(conn):
    cur = conn.cursor()
    print("\n🔍 Probando búsqueda semántica...")
    
    # Vector de consulta (simulado)
    query_vector = np.random.rand(VECTOR_DIM).astype(np.float32)
    print(f"   Vector Query: {query_vector}")
    
    # Búsqueda usando el operador <-> (Distancia Euclidiana/L2)
    # O podrías usar <=> para Similitud Coseno
    search_sql = """
    SELECT title, content, embedding <-> %s AS distance
    FROM documents
    ORDER BY distance ASC
    LIMIT 3;
    """
    
    cur.execute(search_sql, (query_vector,))
    results = cur.fetchall()
    
    print("\n🏆 Top 3 Resultados más cercanos:")
    for row in results:
        print(f"   - [Distancia: {row[2]:.4f}] {row[0]}")
    
    cur.close()

if __name__ == "__main__":
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        setup_database(cursor)
        
        fake_data = generate_fake_data(20) # Generamos 20 documentos
        insert_data(connection, fake_data)
        
        search_similarity(connection)
        
        cursor.close()
        connection.close()
        print("\n✨ Script finalizado correctamente.")
        
    except Exception as e:
        print(f"\n❌ Error crítico de conexión: {e}")
        print("Asegúrate de que el contenedor Docker esté corriendo con: docker-compose up -d")