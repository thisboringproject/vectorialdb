
# Configuración de Base de Datos Vectorial (Postgres + pgvector)

Esta configuración utiliza la imagen oficial `pgvector/pgvector` para proveer capacidades de búsqueda vectorial en PostgreSQL, junto con pgAdmin4 para la gestión visual.

## 1. Archivo `docker-compose.yml`

Crea un archivo llamado `docker-compose.yml` con el siguiente contenido:

```yaml
services:
  # Servicio de Base de Datos (Postgres + pgvector)
  vectordb:
    image: pgvector/pgvector:pg16
    container_name: postgres_vector_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123 # ¡Cambia esto en producción!
      POSTGRES_DB: vector_database
    ports:
      - "5432:5432"
    volumes:
      - vector_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - vector_net

  # Servicio de Administración (pgAdmin 4)
  pgadmin:
    image: dpage/pgadmin4
    container_name: pgadmin_gui
    environment:
      PGADMIN_DEFAULT_EMAIL: boring@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - vectordb
    restart: unless-stopped
    networks:
      - vector_net

# Volúmenes persistentes para que los datos no se pierdan al reiniciar
volumes:
  vector_data:

# Red aislada para comunicación entre contenedores
networks:
  vector_net:
    driver: bridge

```

---

## 2. Pasos para ponerlo en marcha

### Paso 1: Levantar los servicios

En tu terminal, navega a la carpeta donde guardaste el archivo y ejecuta:

```bash
docker-compose up -d

```

### Paso 2: Acceder a pgAdmin

1. Abre tu navegador e ingresa a: `http://localhost:5050`
2. Inicia sesión con las credenciales de pgAdmin:
* **Email:** `boring@admin.com`
* **Password:** `admin`



### Paso 3: Conectar el Servidor (Paso Crítico)

Dentro de pgAdmin, haz clic derecho en **Servers > Register > Server...**

1. **Pestaña General:** Nombre: `VectorDB`.
2. **Pestaña Connection:**
* **Host name/address:** `vectordb` (Es el nombre del servicio en el YAML).
* **Port:** `5432`
* **Maintenance database:** `vector_database`
* **Username:** `admin`
* **Password:** `admi123`



### Paso 4: Activar la extensión y probar

Aunque la imagen tiene la extensión instalada, debes activarla en tu base de datos específica.

Abre la **Query Tool** en pgAdmin (sobre la base de datos `vector_database`) y ejecuta el siguiente script SQL:

```sql
-- 1. Habilitar la extensión vector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Verificar que funciona creando una tabla de prueba
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    content text,
    embedding vector(3) -- Vector de 3 dimensiones como ejemplo
);

-- 3. Insertar datos vectoriales
INSERT INTO items (content, embedding) VALUES 
    ('Item A', '[1,2,3]'),
    ('Item B', '[4,5,6]');

-- 4. Búsqueda de similitud (Distancia Euclidiana <-> L2)
SELECT * FROM items ORDER BY embedding <-> '[1,2,3]' LIMIT 5;

```

---

## 💡 Nota de Rendimiento (Indexación)

Al usar ``pgvector``, recuerda que la indexación es clave para el rendimiento. Cuando tengas miles de registros, no olvides crear un índice **HNSW** (Hierarchical Navigable Small World) para búsquedas aproximadas rápidas, en lugar de escanear toda la tabla:

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);

```
