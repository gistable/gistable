-- Create a view that represents a user such that
-- every value is the most recent non-null value
-- for each requested column (if such a value exists)
CREATE OR REPLACE VIEW users AS (
SELECT user_base.*,
       credentials.*,
       metadata.*
FROM user_base
LEFT JOIN user_deletion ON user_deletion.user_id=user_base.id
LEFT JOIN LATERAL (
     SELECT
     first_not_null(email ORDER BY time DESC) AS email
     FROM user_credentials
     WHERE user_id=user_base.id
) AS credentials ON true
LEFT JOIN LATERAL (
     SELECT
     first_not_null(firstname ORDER BY TIME DESC) AS firstname,
     first_not_null(lastname ORDER BY TIME DESC) AS lastname
     FROM user_metadata
     WHERE user_id=user_base.id
) AS metadata ON true
WHERE user_deletion.id IS NULL
);
