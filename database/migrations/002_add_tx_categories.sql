-- Add missing category columns to transactions table (idempotent)
ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS primary_category TEXT;

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS category TEXT[];

-- Optional: ensure existing NULL arrays are set to empty array (keeps queries simple)
UPDATE transactions SET category = ARRAY[]::TEXT[] WHERE category IS NULL;


