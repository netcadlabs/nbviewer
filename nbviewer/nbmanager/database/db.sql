CREATE TABLE IF NOT EXISTS notebook (
	id integer PRIMARY KEY,
	tenant_id text NOT NULL,
	code text NOT NULL,
	name text NOT NULL,
	desc text NOT NULL,
	file_name text NOT NULL,
	path text NOT NULL,
	c_date text,
	exe_date text,
	exe_count integer DEFAULT 0,
	cron text,
	timeout integer,
	error text
);
