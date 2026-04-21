# ============================================
# RektCoder — Jupiter Swap Bot
# Configuration file
# Change these settings before running
# ============================================

config = {

    # ── Token to trade ──────────────────────
    # Paste the mint address of the token you want to buy or sell
    # You can find this on pump.fun, solscan, or any Solana explorer
    "token_address": "PasteTokenMintAddressYouWantToBuyHere",

    # ── Action ──────────────────────────────
    # "buy"  = swap SOL → token
    # "sell" = swap token → SOL
    "action": "buy",

    # ── Amount ──────────────────────────────
    # If buying: amount in SOL (e.g. 0.01 = 0.01 SOL)
    # If selling: amount in tokens
    "amount": 0.01,

    # ── Slippage ────────────────────────────
    # How much price movement you're willing to accept
    # 500 = 5%, 1000 = 10%, 100 = 1%
    # For memecoins, 5-15% is common
    "slippage_bps": 500,

    # ── Priority fee ────────────────────────
    # Higher = faster transaction, but costs more
    # In lamports (1 SOL = 1,000,000,000 lamports)
    # 100000 = 0.0001 SOL — good for normal conditions
    # 1000000 = 0.001 SOL — use during high congestion
    "priority_fee_lamports": 100000,

    # ── SOL mint address ────────────────────
    # This never changes — it's the native SOL address on Solana
    "sol_mint": "So11111111111111111111111111111111111111112",
}
