 -- comment
--
 --
SELECT * from foo;

--

--meta-psql:do-until-0

WITH sender_data AS (
    SELECT
        document_document.id as document_id,
        document_document.sender_id as manager_id,
        document_document.sender_first_name as first_name,
        document_document.sender_last_name as last_name
    FROM document_document
	    LEFT JOIN account_manager
			ON account_manager.user_id = document_document.sender_id
    	LEFT JOIN document_senderinfo
			ON document_senderinfo.document_id = document_document.id

    WHERE account_manager.user_id IS NOT NULL
        AND document_senderinfo.document_id IS NULL
	LIMIT 5000
)
INSERT INTO document_senderinfo (
    document_id,
    manager_id,
    first_name,
    last_name
)
SELECT sender_data.*
FROM sender_data;


--meta-psql:done
SELECT * from foo;
 --
