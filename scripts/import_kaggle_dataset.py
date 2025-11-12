"""
Script to download and import Kaggle Perfume E-Commerce Dataset 2024
into the Supabase database.

Requirements:
  pip install kaggle pandas supabase python-dotenv

Setup:
1. Create a Kaggle API token at kaggle.com/account
2. Place kaggle.json in ~/.kaggle/ or set KAGGLE_USERNAME and KAGGLE_KEY
3. Set environment variables for Supabase connection
"""

import os
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service role key for admin operations
USER_ID = os.getenv('ADMIN_USER_ID')  # The UUID of the admin user

# Kaggle dataset
DATASET_NAME = 'kanchana1990/perfume-e-commerce-dataset-2024'
DATASET_PATH = './kaggle_data'

def download_kaggle_dataset():
    """Download the dataset from Kaggle"""
    print("Downloading dataset from Kaggle...")
    os.makedirs(DATASET_PATH, exist_ok=True)
    os.system(f'kaggle datasets download -d {DATASET_NAME} -p {DATASET_PATH} --unzip')
    print("Dataset downloaded successfully!")

def load_dataset():
    """Load the CSV file into a pandas dataframe"""
    # The exact filename may vary, adjust as needed
    csv_files = [f for f in os.listdir(DATASET_PATH) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {DATASET_PATH}")
    
    csv_path = os.path.join(DATASET_PATH, csv_files[0])
    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records")
    print(f"Columns: {list(df.columns)}")
    return df

def create_suppliers(supabase: Client, df: pd.DataFrame):
    """Extract unique brands and create supplier records"""
    print("Creating suppliers...")
    
    # Extract unique brands from the dataset
    brands = df['Brand'].unique() if 'Brand' in df.columns else df.get('brand', df.get('manufacturer', [])).unique()
    
    suppliers = []
    for brand in brands[:50]:  # Limit to first 50 brands
        supplier = {
            'company_name': str(brand),
            'description': f'Supplier for {brand} perfumes',
            'contact_person': f'{brand} Sales Team',
            'email': f'contact@{brand.lower().replace(" ", "")}.com',
            'phone': f'+34 {random.randint(600, 799)} {random.randint(100000, 999999)}',
            'address': f'Calle Perfume {random.randint(1, 100)}, Madrid, España',
            'created_by': USER_ID
        }
        suppliers.append(supplier)
    
    # Insert in batches
    batch_size = 100
    for i in range(0, len(suppliers), batch_size):
        batch = suppliers[i:i + batch_size]
        result = supabase.table('suppliers').insert(batch).execute()
        print(f"Inserted {len(batch)} suppliers")
    
    # Fetch all suppliers to get their IDs
    all_suppliers = supabase.table('suppliers').select('*').execute()
    return {s['company_name']: s['id'] for s in all_suppliers.data}

def create_products(supabase: Client, df: pd.DataFrame, supplier_map: dict):
    """Create product records from the dataset"""
    print("Creating products...")
    
    products = []
    for idx, row in df.iterrows():
        # Map dataset columns to our schema (adjust based on actual dataset structure)
        brand = row.get('Brand', row.get('brand', row.get('manufacturer', 'Unknown')))
        name = row.get('Name', row.get('name', row.get('product_name', f'Perfume {idx}')))
        price = float(row.get('Price', row.get('price', random.uniform(20, 200))))
        
        # Determine tier based on price
        if price >= 100:
            tier = 'premium'
        elif price >= 50:
            tier = 'medium'
        else:
            tier = 'basic'
        
        # Get supplier_id for this brand
        supplier_id = supplier_map.get(str(brand))
        if not supplier_id:
            # Use first supplier as fallback
            supplier_id = list(supplier_map.values())[0]
        
        product = {
            'name': str(name)[:100],  # Limit length
            'description': row.get('Description', row.get('description', f'Premium {brand} fragrance')),
            'brand': str(brand),
            'price': round(price, 2),
            'tier': tier,
            'stock_quantity': random.randint(10, 500),
            'expiry_date': (datetime.now() + timedelta(days=random.randint(365, 1095))).date().isoformat(),
            'supplier_id': supplier_id,
            'created_by': USER_ID
        }
        products.append(product)
        
        # Insert in batches to avoid memory issues
        if len(products) >= 100:
            supabase.table('products').insert(products).execute()
            print(f"Inserted {len(products)} products")
            products = []
    
    # Insert remaining products
    if products:
        supabase.table('products').insert(products).execute()
        print(f"Inserted {len(products)} products")

def create_customers(supabase: Client, num_customers=500):
    """Generate synthetic customer records"""
    print(f"Creating {num_customers} customers...")
    
    first_names = ['Carlos', 'Maria', 'Jose', 'Ana', 'Luis', 'Carmen', 'Juan', 'Isabel', 'Miguel', 'Laura']
    last_names = ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Gonzalez', 'Sanchez', 'Perez', 'Martin', 'Fernandez', 'Diaz']
    
    customers = []
    for i in range(num_customers):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        customer = {
            'first_name': first_name,
            'last_name': last_name,
            'email': f'{first_name.lower()}.{last_name.lower()}{i}@email.com',
            'phone': f'+34 {random.randint(600, 799)} {random.randint(100000, 999999)}',
            'address': f'Calle {random.choice(["Mayor", "Sol", "Gran Via", "Alcala"])} {random.randint(1, 100)}, Madrid',
            'birth_date': (datetime.now() - timedelta(days=random.randint(7300, 25550))).date().isoformat(),
            'created_by': USER_ID
        }
        customers.append(customer)
    
    # Insert in batches
    batch_size = 100
    for i in range(0, len(customers), batch_size):
        batch = customers[i:i + batch_size]
        supabase.table('customers').insert(batch).execute()
        print(f"Inserted {len(batch)} customers")

def create_employees(supabase: Client, num_employees=50):
    """Generate synthetic employee records"""
    print(f"Creating {num_employees} employees...")
    
    first_names = ['Pedro', 'Sofia', 'David', 'Elena', 'Javier', 'Marta', 'Pablo', 'Lucia', 'Diego', 'Clara']
    last_names = ['Ruiz', 'Moreno', 'Jimenez', 'Alvarez', 'Romero', 'Torres', 'Ramirez', 'Gil', 'Serrano', 'Molina']
    
    employees = []
    for i in range(num_employees):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        employee = {
            'first_name': first_name,
            'last_name': last_name,
            'email': f'{first_name.lower()}.{last_name.lower()}{i}@tiendaperfumes.com',
            'phone': f'+34 {random.randint(600, 799)} {random.randint(100000, 999999)}',
            'address': f'Calle Trabajo {random.randint(1, 50)}, Madrid',
            'birth_date': (datetime.now() - timedelta(days=random.randint(7300, 18250))).date().isoformat(),
            'created_by': USER_ID
        }
        employees.append(employee)
    
    # Insert in batches
    batch_size = 50
    for i in range(0, len(employees), batch_size):
        batch = employees[i:i + batch_size]
        supabase.table('employees').insert(batch).execute()
        print(f"Inserted {len(batch)} employees")

def create_sales(supabase: Client, num_sales=1000):
    """Generate synthetic sales records"""
    print(f"Creating {num_sales} sales...")
    
    # Fetch all customers, employees, and products
    customers = supabase.table('customers').select('id').execute().data
    employees = supabase.table('employees').select('id').execute().data
    products = supabase.table('products').select('id, price').execute().data
    
    if not customers or not employees or not products:
        print("Error: Missing required data for sales generation")
        return
    
    for i in range(num_sales):
        # Random customer and employee
        customer_id = random.choice(customers)['id']
        employee_id = random.choice(employees)['id']
        
        # Create sale
        num_items = random.randint(1, 5)
        sale_products = random.sample(products, min(num_items, len(products)))
        
        # Calculate total
        total_amount = sum(p['price'] * random.randint(1, 3) for p in sale_products)
        
        sale = {
            'customer_id': customer_id,
            'employee_id': employee_id,
            'total_amount': round(total_amount, 2),
            'status': random.choice(['completed', 'completed', 'completed', 'pending', 'cancelled']),
            'created_by': USER_ID,
            'created_at': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
        }
        
        sale_result = supabase.table('sales').insert(sale).execute()
        sale_id = sale_result.data[0]['id']
        
        # Create sale items
        sale_items = []
        for product in sale_products:
            quantity = random.randint(1, 3)
            unit_price = product['price']
            subtotal = unit_price * quantity
            
            sale_items.append({
                'sale_id': sale_id,
                'product_id': product['id'],
                'quantity': quantity,
                'unit_price': round(unit_price, 2),
                'subtotal': round(subtotal, 2)
            })
        
        supabase.table('sales_items').insert(sale_items).execute()
        
        if (i + 1) % 100 == 0:
            print(f"Created {i + 1} sales")

def main():
    """Main import process"""
    print("Starting Kaggle dataset import process...")
    
    # Validate environment variables
    if not all([SUPABASE_URL, SUPABASE_KEY, USER_ID]):
        print("Error: Missing required environment variables")
        print("Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, ADMIN_USER_ID")
        return
    
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Download and load dataset
    try:
        download_kaggle_dataset()
        df = load_dataset()
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Proceeding with synthetic data generation...")
        df = pd.DataFrame()  # Empty dataframe as fallback
    
    # Import data
    try:
        # Create suppliers
        if not df.empty and 'Brand' in df.columns:
            supplier_map = create_suppliers(supabase, df)
            create_products(supabase, df, supplier_map)
        else:
            print("Dataset empty or missing Brand column, skipping supplier/product import")
        
        # Create customers and employees
        create_customers(supabase)
        create_employees(supabase)
        
        # Create sales
        create_sales(supabase, num_sales=1000)
        
        print("\n✅ Import completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        raise

if __name__ == "__main__":
    main()
