import requests
import base64
import time
import os
from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.signature import Signature
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from config import config

load_dotenv()

# ============================================
# RektCoder — Jupiter Swap Bot
# Buy and sell any Solana token via Jupiter V1
# ============================================

JUPITER_QUOTE_URL = "https://api.jup.ag/swap/v1/quote"
JUPITER_SWAP_URL = "https://api.jup.ag/swap/v1/swap"

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")
JUPITER_API_KEY = os.getenv("JUPITER_API_KEY", "")

if not PRIVATE_KEY:
    raise Exception("PRIVATE_KEY not found in .env file")

wallet = Keypair.from_base58_string(PRIVATE_KEY)
connection = Client(RPC_URL)

# Colors
G = "\033[92m"   # green
Y = "\033[93m"   # yellow
C = "\033[96m"   # cyan
R = "\033[91m"   # red
M = "\033[95m"   # magenta
D = "\033[2m"    # dim
B = "\033[1m"    # bold
X = "\033[0m"    # reset


def sep():
    print(f"  {D}{'─' * 56}{X}")


# ── Step 1: Get quote ────────────────────────
def get_quote(input_mint, output_mint, amount):

    raw_amount = int(amount * 1_000_000_000)
    sol_mint = config["sol_mint"]

    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": str(raw_amount),
        "slippageBps": str(config["slippage_bps"]),
        "restrictIntermediateTokens": "true",
    }

    print(f"  {C}🔍 Fetching quote...{X}")

    headers = {"x-api-key": JUPITER_API_KEY}
    response = requests.get(JUPITER_QUOTE_URL, params=params, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Quote failed: {response.status_code} — {response.text}")

    quote_data = response.json()

    out_amount = int(quote_data["outAmount"]) / 1_000_000_000
    route_labels = " → ".join([r["swapInfo"]["label"] for r in quote_data["routePlan"]])

    print(f"  {G}✅ {amount} {'SOL' if input_mint == sol_mint else 'tokens'} → {out_amount:.6f} {'SOL' if output_mint == sol_mint else 'tokens'}{X}")
    print(f"  {D}   Route: {route_labels} | Impact: {quote_data['priceImpactPct']}% | Slippage: {config['slippage_bps'] / 100}%{X}")

    return quote_data


# ── Step 2: Build transaction ────────────────
def build_swap_transaction(quote_response):

    print(f"  {C}🔨 Building transaction...{X}")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": JUPITER_API_KEY,
    }

    payload = {
        "userPublicKey": str(wallet.pubkey()),
        "quoteResponse": quote_response,
        "dynamicComputeUnitLimit": True,
        "dynamicSlippage": True,
        "prioritizationFeeLamports": {
            "priorityLevelWithMaxLamports": {
                "priorityLevel": "veryHigh",
                "maxLamports": config["priority_fee_lamports"],
            },
        },
    }

    response = requests.post(JUPITER_SWAP_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Build failed: {response.status_code} — {response.text}")

    swap_data = response.json()

    slippage_info = ""
    if "dynamicSlippageReport" in swap_data:
        slippage_info = f" {D}| Dynamic slippage: {swap_data['dynamicSlippageReport']['slippageBps']} bps{X}"

    print(f"  {G}✅ Transaction built{X}{slippage_info}")

    return swap_data["swapTransaction"]


# ── Step 3: Sign and send ────────────────────
def sign_and_send(swap_transaction):

    print(f"  {C}✍️  Signing & sending...{X}")

    raw_tx = base64.b64decode(swap_transaction)
    tx = VersionedTransaction.from_bytes(raw_tx)
    signed_tx = VersionedTransaction(tx.message, [wallet])
    serialized = bytes(signed_tx)

    result = connection.send_raw_transaction(
        serialized,
        opts=TxOpts(skip_preflight=True, max_retries=3),
    )

    txid = result.value

    print(f"  {Y}⏳ Confirming...{X}")

    connection.confirm_transaction(txid, commitment="confirmed")

    # Immediately show success + full clickable link
    sep()
    print(f"  {G}{B}🎉 SWAP CONFIRMED{X}")
    print(f"  {D}🔗 https://solscan.io/tx/{str(txid)}{X}")
    sep()

    return txid


# ── Step 4: Fetch and display results ────────
def print_swap_result(txid):

    txid_sig = Signature.from_string(str(txid))
    wallet_str = str(wallet.pubkey())

    print(f"  {D}Fetching on-chain details...{X}")

    for attempt in range(3):
        wait = 5 + (attempt * 5)
        time.sleep(wait)

        try:
            tx_details = connection.get_transaction(
                txid_sig,
                encoding="jsonParsed",
                max_supported_transaction_version=0,
            )

            if not tx_details or not tx_details.value:
                continue

            meta = tx_details.value.transaction.meta

            pre_sol = meta.pre_balances[0] / 1_000_000_000
            post_sol = meta.post_balances[0] / 1_000_000_000
            sol_change = post_sol - pre_sol
            fee = meta.fee / 1_000_000_000

            # Token changes
            token_line = ""
            pre_tokens = meta.pre_token_balances or []
            post_tokens = meta.post_token_balances or []

            for post in post_tokens:
                if post.owner == wallet_str:
                    mint = str(post.mint)
                    post_amount = float(post.ui_token_amount.ui_amount or 0)
                    pre_amount = 0
                    for pre in pre_tokens:
                        if pre.owner == wallet_str and str(pre.mint) == mint:
                            pre_amount = float(pre.ui_token_amount.ui_amount or 0)
                            break
                    token_change = post_amount - pre_amount
                    if token_change > 0:
                        token_line = f"{G}+{token_change:,.4f} tokens{X}"
                    elif token_change < 0:
                        token_line = f"{R}{token_change:,.4f} tokens{X}"

            for pre in pre_tokens:
                if pre.owner == wallet_str:
                    mint = str(pre.mint)
                    found = any(post.owner == wallet_str and str(post.mint) == mint for post in post_tokens)
                    if not found:
                        pre_amount = float(pre.ui_token_amount.ui_amount or 0)
                        if pre_amount > 0:
                            token_line = f"{R}-{pre_amount:,.4f} tokens{X}"

            # Print summary
            sep()
            print(f"  {B}📊 SWAP SUMMARY{X}")
            sep()
            print(f"  {B}SOL{X}          {Y}{sol_change:+.6f} SOL{X}")
            if token_line:
                print(f"  {B}Tokens{X}       {token_line}")
            print(f"  {B}Fee{X}          {D}{fee:.6f} SOL{X}")
            print(f"  {B}Action{X}       {M}{config['action'].upper()}{X}")
            print(f"  {B}Token{X}        {D}{config['token_address'][:30]}...{X}")
            print(f"  {B}Wallet{X}       {D}{wallet_str[:30]}...{X}")
            sep()

            return

        except Exception:
            pass

    print(f"  {D}Could not fetch on-chain details — check Solscan link above{X}")


# ── Main ─────────────────────────────────────
def execute_swap():

    print()
    sep()
    print(f"  {C}{B}⚡ RektCoder — Jupiter Swap Bot{X}")
    sep()
    print(f"  {B}Wallet{X}       {D}{str(wallet.pubkey())[:30]}...{X}")
    print(f"  {B}Action{X}       {M}{config['action'].upper()}{X}")
    print(f"  {B}Amount{X}       {Y}{config['amount']} {'SOL' if config['action'] == 'buy' else 'tokens'}{X}")
    print(f"  {B}Token{X}        {D}{config['token_address'][:30]}...{X}")
    sep()
    print()

    sol_mint = config["sol_mint"]

    if config["action"] == "buy":
        input_mint = sol_mint
        output_mint = config["token_address"]
        amount = config["amount"]
    else:
        input_mint = config["token_address"]
        output_mint = sol_mint
        amount = config["amount"]

    try:
        quote = get_quote(input_mint, output_mint, amount)
        swap_tx = build_swap_transaction(quote)
        txid = sign_and_send(swap_tx)
        print_swap_result(txid)

    except Exception as e:
        sep()
        print(f"  {R}❌ Swap failed: {e}{X}")
        sep()
        print()


if __name__ == "__main__":
    execute_swap()
