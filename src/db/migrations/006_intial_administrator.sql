INSERT INTO users(telegram_user_id, telegram_username, is_admin)
VALUES (354285778, 'deadity', TRUE)
ON CONFLICT (telegram_user_id) DO UPDATE SET is_admin=TRUE;
