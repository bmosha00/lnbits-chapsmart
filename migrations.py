async def m001_initial(db):
    await db.execute(
        """
        CREATE TABLE chapsmart.cashouts (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            recipient_name TEXT NOT NULL,
            amount_tzs INTEGER NOT NULL,
            amount_sats INTEGER DEFAULT 0,
            fee_sats INTEGER DEFAULT 0,
            fee_percent REAL DEFAULT 0.0,
            quote_id TEXT,
            invoice_id TEXT,
            bolt11 TEXT,
            payment_hash TEXT,
            status TEXT DEFAULT 'pending',
            error TEXT,
            created_at INTEGER,
            updated_at INTEGER
        );
        """
    )
