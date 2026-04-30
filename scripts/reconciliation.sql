-- Reconciliation script for manual-data-deletion recovery.
-- Target: PostgreSQL (Railway)
-- Safe to run multiple times.

BEGIN;

-- 1) Recompute conversation recency from messages.
UPDATE conversations c
SET last_message_at = lm.max_created_at
FROM (
    SELECT conversation_id, MAX(created_at) AS max_created_at
    FROM messages
    GROUP BY conversation_id
) lm
WHERE c.id = lm.conversation_id
  AND c.last_message_at IS DISTINCT FROM lm.max_created_at;

-- 2) Conversations with no messages must not keep stale timestamps.
UPDATE conversations c
SET last_message_at = NULL
WHERE NOT EXISTS (
    SELECT 1
    FROM messages m
    WHERE m.conversation_id = c.id
)
AND c.last_message_at IS NOT NULL;

-- 3) Normalize external_user_id from users table when missing/empty.
UPDATE conversations c
SET external_user_id = u.external_id
FROM users u
WHERE c.user_id = u.id
  AND (c.external_user_id IS NULL OR btrim(c.external_user_id) = '')
  AND u.external_id IS NOT NULL
  AND btrim(u.external_id) <> '';

-- 4) Create missing users from existing conversations (edge case after manual user deletes + FK disabled).
-- If your DB enforces FK strictly this will insert 0 rows.
INSERT INTO users (tenant_id, external_id)
SELECT DISTINCT c.tenant_id, c.external_user_id
FROM conversations c
LEFT JOIN users u
  ON u.id = c.user_id
WHERE u.id IS NULL
  AND c.external_user_id IS NOT NULL
  AND btrim(c.external_user_id) <> ''
ON CONFLICT (tenant_id, external_id) DO NOTHING;

-- 5) Re-link conversations.user_id by tenant + external_user_id when null or broken.
UPDATE conversations c
SET user_id = u.id
FROM users u
WHERE c.tenant_id = u.tenant_id
  AND c.external_user_id = u.external_id
  AND (c.user_id IS NULL OR c.user_id <> u.id);

-- 6) Optional cleanup for obviously invalid records created by manual edits.
-- 6a) Delete messages without content (keeps role/system integrity).
DELETE FROM messages
WHERE content IS NULL OR btrim(content) = '';

-- 6b) Delete conversations that still have no resolvable user and no messages.
DELETE FROM conversations c
WHERE (c.user_id IS NULL OR NOT EXISTS (SELECT 1 FROM users u WHERE u.id = c.user_id))
  AND NOT EXISTS (SELECT 1 FROM messages m WHERE m.conversation_id = c.id);

-- 7) Ensure channels table has unique tenant/name rows if duplicates were inserted manually.
-- Keep lowest id and delete duplicates.
WITH duplicated AS (
    SELECT tenant_id, name, MIN(id) AS keep_id
    FROM channels
    GROUP BY tenant_id, name
    HAVING COUNT(*) > 1
), to_delete AS (
    SELECT ch.id
    FROM channels ch
    JOIN duplicated d
      ON d.tenant_id = ch.tenant_id
     AND d.name = ch.name
    WHERE ch.id <> d.keep_id
)
DELETE FROM channels
WHERE id IN (SELECT id FROM to_delete);

COMMIT;

-- -----------------------------
-- Post-run verification queries
-- -----------------------------
-- 1) Conversations with stale/incorrect recency
-- SELECT c.id, c.last_message_at, lm.max_created_at
-- FROM conversations c
-- LEFT JOIN (
--   SELECT conversation_id, MAX(created_at) AS max_created_at
--   FROM messages
--   GROUP BY conversation_id
-- ) lm ON lm.conversation_id = c.id
-- WHERE c.last_message_at IS DISTINCT FROM lm.max_created_at;

-- 2) Conversations without user mapping
-- SELECT c.id, c.tenant_id, c.external_user_id, c.user_id
-- FROM conversations c
-- LEFT JOIN users u ON u.id = c.user_id
-- WHERE u.id IS NULL;

-- 3) Duplicate channels
-- SELECT tenant_id, name, COUNT(*)
-- FROM channels
-- GROUP BY tenant_id, name
-- HAVING COUNT(*) > 1;
