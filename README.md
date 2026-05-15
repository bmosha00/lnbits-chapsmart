# ChapSmart — LNbits Extension

Bitcoin to M-Pesa via Lightning. Send TZS to any Vodacom M-Pesa number directly from your LNbits wallet.

## How It Works

1. User enters phone number, recipient name, and TZS amount
2. Extension gets a live quote from ChapSmart (sats + fee)
3. User confirms — sats are deducted from their LNbits wallet
4. ChapSmart receives the Lightning payment
5. M-Pesa arrives on the recipient's phone in seconds

## Installation

### From Extension Source URL

Add this URL to your LNbits instance:

```
Server → Server → Extension Sources → Add:
https://raw.githubusercontent.com/bmosha00/lnbits-chapsmart/main/manifest.json
```

Then go to **Extensions** and enable **ChapSmart**.

### Admin Configuration

The LNbits admin must configure ChapSmart API credentials:

```
Server → Server → Extension Settings → ChapSmart:
  API Key: chp_xxx (from ChapSmart)
  API Secret: xxx (from ChapSmart)
  Account Number: xxx (from ChapSmart)
```

Contact ChapSmart at support@chapsmart.com to get API credentials.

## User Guide

1. Select your wallet
2. Enter recipient's Vodacom M-Pesa number (074/075/076)
3. Enter recipient's full name (first + last)
4. Enter TZS amount (2,500 — 1,000,000)
5. Click "Get Quote" to see the sats amount
6. Click "Send M-Pesa" to confirm
7. Wait for M-Pesa confirmation

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/quote | Invoice key | Get sats quote for TZS amount |
| GET | /api/v1/poll/{quote_id} | Invoice key | Refresh quote price |
| POST | /api/v1/send | Admin key | Execute cashout (quote → pay → track) |
| GET | /api/v1/status/{cashout_id} | Invoice key | Check M-Pesa delivery status |
| GET | /api/v1/cashouts | Invoice key | List cashout history |

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
