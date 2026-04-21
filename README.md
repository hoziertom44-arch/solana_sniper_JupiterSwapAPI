# Solana Token Swap Bot — Jupiter API

Buy or sell any Solana token from your terminal using Jupiter Swap API. One command, 3 seconds, on-chain confirmed.

Built by [RektCoder](https://www.youtube.com/@RektCoder)

## What It Does

Swaps any Solana token through Jupiter — the biggest swap aggregator on Solana. Jupiter finds the best route across every DEX (Raydium, Orca, Meteora, Pump.fun, etc.) and executes the trade in seconds.

- Buy: Solana → Token
- Sell: Token → Solana
- Best price across all Solana DEXes
- Dynamic slippage and priority fees
- On-chain confirmation with Solscan link

## Python Version

### Files

- `.env.example` — Private key, RPC URL, Jupiter API key
- `config.py` — Token address, amount, slippage, action
- `swap.py` — Quote → Build → Sign → Send → Confirm
- `requirements.txt` — Dependencies
- `.gitignore` — Excludes .env

### Setup

```bash
cd python
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env.example .env
```

### Configure

1. Edit `.env` — add your private key, RPC URL, and Jupiter API key
2. Edit `config.py` — set your token address, amount, action (buy/sell), slippage

### Get Jupiter API Key

Go to [portal.jup.ag](https://portal.jup.ag) → create free account → copy API key → paste in `.env`

### Run

```bash
python swap.py
```

## TypeScript Version

### Files

- `.env.example` — Private key, RPC URL, Jupiter API key
- `src/config.ts` — Token address, amount, slippage, action
- `src/swap.ts` — Quote → Build → Sign → Send → Confirm
- `src/main.ts` — Entry point
- `package.json` — Dependencies
- `tsconfig.json` — TypeScript config

### Setup

```bash
cd typescript
npm install
cp .env.example .env
```

### Configure

1. Edit `.env` — add your private key, RPC URL, and Jupiter API key
2. Edit `src/config.ts` — set your token address, amount, action, slippage

### Run

```bash
npm start
```

## How It Works

1. **Read Config** — loads token address, amount, slippage, wallet keys
2. **Get Quote** — hits Jupiter API, finds best route and expected output
3. **Build Transaction** — Jupiter returns a serialized transaction ready to sign
4. **Sign & Send** — wallet signs it, sends to Solana, waits for confirmation

Same flow for buy and sell. Only the input/output mints swap.

## Security

- Private key lives in `.env` only — never in code
- `.gitignore` excludes `.env` — never push keys to GitHub
- If someone has your private key they own your wallet

## Example Output
⚡ RektCoder — Jupiter Swap Bot
────────────────────────────────────────
Wallet       mkJ1m91zsooCsp9TC5YQ...
Action       BUY
Amount       0.01 SOL
Token        EAm9mT1W8qTseijesS6Z...
🔍 Fetching quote...
✅ 0.01 SOL → 1.856569 tokens
Route: Meteora DLMM | Impact: 0% | Slippage: 5.0%
🔨 Building transaction...
✅ Transaction built | Dynamic slippage: 80 bps
✍️  Signing & sending...
⏳ Confirming...
────────────────────────────────────────
🎉 SWAP CONFIRMED
🔗 https://solscan.io/tx/4Tujzg6A4Fg...
────────────────────────────────────────
## Links

- 📺 [YouTube — RektCoder](https://www.youtube.com/@RektCoder)
- 📢 [Telegram Channel](https://t.me/rektcoderchannel)
- 💬 [Telegram Community](https://t.me/rektcodercommunity)
- 💻 [GitHub](https://github.com/hoziertom44-arch)

## Disclaimer

This code is for educational purposes only. Trading crypto involves significant risk. Never trade with money you can't afford to lose. This is not financial advice.
