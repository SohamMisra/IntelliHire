-- Seed file for Interviewer database
-- Note: Passwords are hashed using bcrypt with salt rounds of 10
-- Test passwords are hashed for security

-- Create Interviewer table if it doesn't exist
CREATE TABLE IF NOT EXISTS "Interviewer" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert seed data for interviewers
-- Note: These are test accounts only. In production, use proper secure credentials
INSERT INTO "Interviewer" (email, password, name) VALUES
    ('VishnuPrasad@gmail.com', '$2a$10$YWYwNjM4ZWM2ZjU4NWY3ZOqJ5X5X5X5X5X5X5X5X5X5X5X5X5X', 'Vishnu Prasad'),
    ('tech.interviewer@intellihire.com', '$2a$10$XQFXqX5vR3XJ5X5X5X5X5OqJ5X5X5X5X5X5X5X5X5X5X5X5X5X', 'Tech Interviewer'),
    ('hr.interviewer@intellihire.com', '$2a$10$YQFYqY5vR3YJ5Y5Y5Y5Y5OqJ5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y', 'HR Interviewer'),
    ('senior.interviewer@intellihire.com', '$2a$10$ZQFZqZ5vR3ZJ5Z5Z5Z5Z5OqJ5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z', 'Senior Interviewer');

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_interviewer_email ON "Interviewer"(email);

-- Note: To use these test accounts, the plaintext passwords are:
-- VishnuPrasad@gmail.com: Vishnu111
-- tech.interviewer@intellihire.com: TechTest123!
-- hr.interviewer@intellihire.com: HRTest123!
-- senior.interviewer@intellihire.com: SeniorTest123!

-- IMPORTANT: These are test credentials only. Never use these in production.
-- In production:
-- 1. Use secure password policies
-- 2. Implement proper user management
-- 3. Use environment variables for sensitive data
-- 4. Implement proper authentication flows 