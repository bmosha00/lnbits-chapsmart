# ChapSmart — LNbits Extension

Bitcoin to M-Pesa via Lightning. Send TZS to any Vodacom M-Pesa number directly from your LNbits wallet.

## How It Works

1. User enters phone number, recipient name, and TZS amount
2. Extension gets a live quote from ChapSmart (sats + fee)
3. User confirms — sats are deducted from their LNbits wallet
4. ChapSmart receives the Lightning payment
5. M-Pesa arrives on the recipient's phone in seconds

## Installation

### Step 1: Add Extension Source

In LNbits admin panel:

Settings → Extensions → Extension Sources → click **+** and add:

    https://raw.githubusercontent.com/bmosha00/lnbits-chapsmart/main/manifest.json

### Step 2: Install and Activate

Go to **Extensions** → find **ChapSmart** → click **INSTALL** → select latest version → toggle **Activated**.

### Step 3: Configure API Credentials

Add these to your LNbits `.env` file (or set as environment variables):

    CHAPSMART_API_KEY=chp_your_api_key_here
    CHAPSMART_API_SECRET=your_api_secret_here
    CHAPSMART_ACCOUNT_NUMBER=your_account_number_here
    CHAPSMART_API_URL=https://backend.chapsmart.com

Then restart LNbits.

Contact **support@chapsmart.com** to get API credentials.

## Compatibility

- **LNbits:** v1.5.4+ (Vue 3)
- **Python:** 3.10+
- **Database:** SQLite or PostgreSQL

## User Guide

1. Select your wallet
2. Enter recipient's Vodacom M-Pesa number (074/075/076)
3. Enter recipient's full name (first + last)
4. Enter TZS amount (2,500 — 1,000,000)
5. Click **Get Quote** to see the sats amount
6. Click **Send M-Pesa** to confirm
7. Wait for M-Pesa confirmation

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /chapsmart/api/v1/quote | Invoice key | Get sats quote for TZS amount |
| GET | /chapsmart/api/v1/poll/{quote_id} | Invoice key | Refresh quote price |
| POST | /chapsmart/api/v1/send | Admin key | Execute cashout |
| GET | /chapsmart/api/v1/status/{cashout_id} | Invoice key | Check M-Pesa delivery status |
| GET | /chapsmart/api/v1/cashouts | Invoice key | List cashout history |

## Limits

| Item | Value |
|------|-------|
| Minimum | 2,500 TZS |
| Maximum | 1,000,000 TZS |
| Fee | 2.2% |
| Network | Vodacom M-Pesa only |
| Speed | M-Pesa arrives in seconds |

## License

MIT

## Links

- [ChapSmart](https://chapsmart.com)
- [LNbits](https://lnbits.com)
- [GitHub](https://github.com/bmosha00/lnbits-chapsmart)
