-- Script to clear all transactional data from the database
-- This will preserve the schema but remove all records

-- Disable triggers temporarily for faster deletion
SET session_replication_role = 'replica';

-- Delete in correct order to respect foreign key constraints
-- Start with dependent tables first

-- Delete sales items (depends on sales and products)
DELETE FROM public.sales_items;

-- Delete sales (depends on customers and employees)
DELETE FROM public.sales;

-- Delete products (depends on suppliers)
DELETE FROM public.products;

-- Delete customers
DELETE FROM public.customers;

-- Delete employees
DELETE FROM public.employees;

-- Delete suppliers
DELETE FROM public.suppliers;

-- Re-enable triggers
SET session_replication_role = 'origin';

-- Reset sequences if needed (though we use UUIDs)
-- No sequences to reset since we're using UUID primary keys

-- Verify deletion
SELECT 
  'sales_items' as table_name, COUNT(*) as record_count FROM public.sales_items
UNION ALL
SELECT 'sales', COUNT(*) FROM public.sales
UNION ALL
SELECT 'products', COUNT(*) FROM public.products
UNION ALL
SELECT 'customers', COUNT(*) FROM public.customers
UNION ALL
SELECT 'employees', COUNT(*) FROM public.employees
UNION ALL
SELECT 'suppliers', COUNT(*) FROM public.suppliers;
