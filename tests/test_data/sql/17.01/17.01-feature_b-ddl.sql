

	SET ROLE north;

	CREATE INDEX CONCURRENTLY
		account_user ON account_user(id)
	WHERE created_at IS NULL;
