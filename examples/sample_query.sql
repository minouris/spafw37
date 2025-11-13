SELECT 
    u.id,
    u.username,
    u.email,
    u.created_at,
    COUNT(o.id) as order_count,
    SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = true
  AND u.created_at >= '2024-01-01'
GROUP BY u.id, u.username, u.email, u.created_at
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC
LIMIT 100;
