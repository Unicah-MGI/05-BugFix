-- =====================================================
-- CREATE ADMIN USER - SQL VERSION
-- =====================================================
-- This script creates an admin user profile for the CRM system
-- 
-- PREREQUISITES:
-- 1. Run 000_complete_schema.sql or 001_create_tables.sql first
-- 2. Create the auth user manually in Supabase Dashboard:
--    - Go to Authentication > Users > Add User
--    - Email: admin@tiendaperfumes.com
--    - Password: Admin@123456
--    - Auto Confirm User: YES
-- 3. Copy the User ID (UUID) generated
-- 4. Replace 'PASTE_USER_UUID_HERE' below with the actual UUID
-- 
-- CREDENTIALS:
-- Email: admin@tiendaperfumes.com
-- Password: Admin@123456
-- =====================================================

-- Step 1: Insert admin profile
-- IMPORTANT: Replace 'PASTE_USER_UUID_HERE' with the actual UUID from Supabase Dashboard
INSERT INTO public.profiles (
  id,
  full_name,
  avatar_url,
  created_at,
  updated_at
) VALUES (
  '26c0accf-4568-43fa-94ee-32adaee46719'::uuid,  -- Replace this with actual user UUID
  'Admin Tienda Perfumes',
  NULL,
  NOW(),
  NOW()
) ON CONFLICT (id) DO UPDATE
SET 
  full_name = EXCLUDED.full_name,
  updated_at = NOW();

-- Step 2: Verify the profile was created
SELECT 
  id,
  full_name,
  created_at
FROM public.profiles
WHERE id = 'PASTE_USER_UUID_HERE'::uuid;

-- =====================================================
-- ALTERNATIVE: Automatic Admin Profile Creation
-- =====================================================
-- This function automatically creates a profile when finding
-- the admin user by email

CREATE OR REPLACE FUNCTION create_admin_profile()
RETURNS TABLE (
  user_id uuid,
  email text,
  full_name text,
  status text
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_user_id uuid;
  v_email text := 'admin@tiendaperfumes.com';
  v_full_name text := 'Admin Tienda Perfumes';
BEGIN
  -- Find user by email in auth.users
  SELECT id INTO v_user_id
  FROM auth.users
  WHERE auth.users.email = v_email
  LIMIT 1;

  -- Check if user exists
  IF v_user_id IS NULL THEN
    RETURN QUERY SELECT 
      NULL::uuid,
      v_email,
      NULL::text,
      'ERROR: User not found in auth.users. Please create user in Supabase Dashboard first.'::text;
    RETURN;
  END IF;

  -- Insert or update profile
  INSERT INTO public.profiles (
    id,
    full_name,
    avatar_url,
    created_at,
    updated_at
  ) VALUES (
    v_user_id,
    v_full_name,
    NULL,
    NOW(),
    NOW()
  )
  ON CONFLICT (id) DO UPDATE
  SET 
    full_name = EXCLUDED.full_name,
    updated_at = NOW();

  -- Return success
  RETURN QUERY SELECT 
    v_user_id,
    v_email,
    v_full_name,
    'SUCCESS: Admin profile created/updated successfully'::text;
END;
$$;

-- =====================================================
-- USAGE INSTRUCTIONS
-- =====================================================
-- 
-- METHOD 1 - Manual (If you know the UUID):
-- 1. Replace 'PASTE_USER_UUID_HERE' above with actual UUID
-- 2. Run the INSERT statement
--
-- METHOD 2 - Automatic (Recommended):
-- 1. Create user in Supabase Dashboard first
-- 2. Run this command:
--    SELECT * FROM create_admin_profile();
--
-- VERIFICATION:
-- SELECT * FROM profiles WHERE full_name = 'Admin Tienda Perfumes';
-- =====================================================

-- Uncomment the line below to run the automatic method:
-- SELECT * FROM create_admin_profile();
