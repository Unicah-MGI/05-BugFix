# Guía de Importación del Dataset de Kaggle

Esta guía explica cómo limpiar los datos existentes e importar el Perfume E-Commerce Dataset 2024 desde Kaggle.

## Requisitos Previos

1. **Cuenta de Kaggle**: Necesitas una cuenta en [kaggle.com](https://www.kaggle.com)
2. **API Token de Kaggle**: 
   - Ve a https://www.kaggle.com/account
   - Haz clic en "Create New API Token"
   - Descarga el archivo `kaggle.json`
   - Colócalo en `~/.kaggle/kaggle.json` (Linux/Mac) o `C:\Users\<username>\.kaggle\kaggle.json` (Windows)

3. **Python 3.8+** instalado en tu sistema

4. **Variables de entorno de Supabase**:
   - `SUPABASE_URL`: Tu URL de Supabase
   - `SUPABASE_SERVICE_ROLE_KEY`: Service role key (no la anon key)
   - `ADMIN_USER_ID`: UUID del usuario admin que creará los registros

## Pasos de Instalación

### 1. Instalar Dependencias Python

\`\`\`bash
pip install kaggle pandas supabase python-dotenv
\`\`\`

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

\`\`\`env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
ADMIN_USER_ID=uuid-del-usuario-admin
\`\`\`

Para obtener el `ADMIN_USER_ID`:
1. Ve a tu dashboard de Supabase
2. Authentication → Users
3. Copia el UUID del usuario admin

### 3. Limpiar Datos Existentes

Ejecuta el script SQL en el SQL Editor de Supabase:

\`\`\`sql
-- Copia y pega el contenido de scripts/010_clear_transactional_data.sql
\`\`\`

Este script eliminará todos los datos transaccionales pero mantendrá la estructura de la base de datos.

### 4. Ejecutar Script de Importación

\`\`\`bash
python scripts/import_kaggle_dataset.py
\`\`\`

El script hará lo siguiente:
1. Descargar el dataset de Kaggle
2. Crear proveedores basados en las marcas del dataset
3. Importar productos con precios y detalles del dataset
4. Generar 500 clientes sintéticos
5. Generar 50 empleados sintéticos
6. Crear 1,000 ventas con items relacionados

## Estructura del Dataset

El dataset de Kaggle contiene aproximadamente 2,000 registros de perfumes con columnas como:
- **Brand/Marca**: Marca del perfume
- **Name/Nombre**: Nombre del producto
- **Price/Precio**: Precio del producto
- **Description/Descripción**: Descripción del perfume
- **Category/Categoría**: Categoría del producto
- **Rating/Calificación**: Calificaciones de usuarios

## Personalización

### Ajustar Cantidad de Datos

Puedes modificar el número de registros generados editando el script:

\`\`\`python
# En scripts/import_kaggle_dataset.py

# Línea ~180 - Cambiar número de clientes
create_customers(supabase, num_customers=500)  # Cambia 500 al número deseado

# Línea ~182 - Cambiar número de empleados
create_employees(supabase, num_employees=50)  # Cambia 50 al número deseado

# Línea ~185 - Cambiar número de ventas
create_sales(supabase, num_sales=1000)  # Cambia 1000 al número deseado
\`\`\`

### Mapeo de Columnas

Si el dataset tiene nombres de columnas diferentes, actualiza el mapeo en la función `create_products`:

\`\`\`python
# Línea ~85-90
brand = row.get('Brand', row.get('brand', row.get('manufacturer', 'Unknown')))
name = row.get('Name', row.get('name', row.get('product_name', f'Perfume {idx}')))
price = float(row.get('Price', row.get('price', random.uniform(20, 200))))
\`\`\`

## Verificación

Después de la importación, verifica los datos en Supabase:

\`\`\`sql
-- Contar registros en cada tabla
SELECT 
  'suppliers' as tabla, COUNT(*) as registros FROM suppliers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'sales', COUNT(*) FROM sales
UNION ALL
SELECT 'sales_items', COUNT(*) FROM sales_items;
\`\`\`

## Solución de Problemas

### Error: "No kaggle.json found"
- Asegúrate de que el archivo `kaggle.json` esté en `~/.kaggle/`
- Verifica los permisos del archivo: `chmod 600 ~/.kaggle/kaggle.json`

### Error: "Missing required environment variables"
- Verifica que el archivo `.env` esté en la raíz del proyecto
- Confirma que todas las variables estén configuradas correctamente

### Error: "Could not authenticate"
- Verifica que `SUPABASE_SERVICE_ROLE_KEY` sea la service role key, no la anon key
- Confirma que el `ADMIN_USER_ID` sea un UUID válido de un usuario existente

### Dataset no descarga
- Verifica tu conexión a internet
- Confirma que tu token de Kaggle sea válido
- Verifica que el dataset esté público: https://www.kaggle.com/datasets/kanchana1990/perfume-e-commerce-dataset-2024

## Rollback (Revertir Cambios)

Si necesitas revertir la importación:

1. Ejecuta de nuevo el script de limpieza:
\`\`\`sql
-- scripts/010_clear_transactional_data.sql
\`\`\`

2. Opcionalmente, ejecuta el script de seeding original:
\`\`\`sql
-- scripts/002_seed_test_data.sql
\`\`\`

## Notas Adicionales

- La importación puede tardar 5-10 minutos dependiendo de tu conexión
- Se generan datos sintéticos para clientes, empleados y ventas para complementar el dataset
- Los precios se categorizan automáticamente en tiers: premium (>100€), medium (50-100€), basic (<50€)
- Las fechas de vencimiento de productos se generan aleatoriamente entre 1-3 años en el futuro
