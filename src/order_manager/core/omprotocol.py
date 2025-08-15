# src/order_manager/core/protocol_basic.py

"""
====================================================================================
⚠ DISCLAIMER ⚠
This script is the public version of the Solana vault balance listener. Which is already powerful enough to be used as a standalone tool for monitoring vault balances in real-time.
It is designed to be simple and easy to use, making it suitable for anyone interested in Sol
It only listens for vault balance changes and does NOT include any trading
strategy or MEV logic.

If you are interested in purchasing the full private strategy version,
contact me in private using the links at:
    https://github.com/NovaStackDev
====================================================================================
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
import websockets
import os
from dotenv import load_dotenv

# Example SOL-USDC main pool vaults (mainnet)
SOL_USDC_VAULTS = {
    "base": ["DQyrAcCrDXQ7NeoqGgDCZwBvWDcYmFCjSb9JtteuvPpz"],   # SOL vault
    "quote": ["HLmqeL62xR1QoZ1HKKbXRrdN1p3phKpxRMb2VVopvBBz"],  # USDC vault
}


class SolanaVaultListener:
    def __init__(self, rpc_ws_url, symbol, vault_accounts, log_updates=True):
        self.rpc_ws_url = rpc_ws_url
        self.symbol = symbol
        self.vault_accounts = vault_accounts
        self.log_updates = log_updates

        self.ws = None
        self.sub_map_accounts = {}  # subscription_id -> side ("base"/"quote")
        self._balances = {"base": None, "quote": None}

    async def connect(self):
        logging.info(f"[VaultListener] Connecting to {self.rpc_ws_url} for {self.symbol}...")
        self.ws = await websockets.connect(self.rpc_ws_url, max_size=None)
        logging.info("[VaultListener] Connected.")

    async def subscribe_vaults(self):
        """Subscribe to base + quote vault accounts for balance changes."""
        for side, accounts in self.vault_accounts.items():
            for acc in accounts:
                sub_msg = {
                    "jsonrpc": "2.0",
                    "id": f"subacct_{side}_{acc}",
                    "method": "accountSubscribe",
                    "params": [
                        acc,
                        {"encoding": "jsonParsed", "commitment": "confirmed"}
                    ]
                }
                await self.ws.send(json.dumps(sub_msg))
                logging.info(f"[VaultListener] Subscribing to {side} vault {acc}")

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    async def run(self, on_event_callback):
        await self.connect()
        await self.subscribe_vaults()

        while True:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)

                # Handle subscription confirmations
                if "result" in data and isinstance(data.get("id"), str):
                    rid = data["id"]
                    if rid.startswith("subacct_"):
                        _, side, acc = rid.split("_", 2)
                        sub_id = data["result"]
                        self.sub_map_accounts[sub_id] = side
                        logging.info(f"[VaultListener] Subscription confirmed for {side} vault {acc} -> ID {sub_id}")
                        continue

                # Handle account notifications
                if "params" in data and "result" in data["params"]:
                    sub_id = data["params"].get("subscription")
                    if sub_id in self.sub_map_accounts:
                        side = self.sub_map_accounts[sub_id]
                        acc_data = data["params"]["result"]["value"]
                        if not acc_data or "data" not in acc_data:
                            continue
                        try:
                            parsed = acc_data["data"]["parsed"]
                            if parsed.get("type") != "account":
                                continue
                            ui_amount = float(parsed["info"]["tokenAmount"]["uiAmount"])
                            self._balances[side] = ui_amount

                            # Emit only when both balances are known
                            if self._balances["base"] is not None and self._balances["quote"] is not None:
                                evt = {
                                    "type": "vault",
                                    "time": self._now_iso(),
                                    "symbol": self.symbol,
                                    "base_balance": self._balances["base"],
                                    "quote_balance": self._balances["quote"]
                                }
                                if self.log_updates:
                                    logging.info("[Vault Update] base=%s quote=%s",
                                                 evt["base_balance"], evt["quote_balance"])
                                on_event_callback(evt)
                        except Exception as e:
                            logging.error(f"[VaultListener] Failed to parse vault balance ({side}): {e}")
                        continue

            except Exception as e:
                logging.error(f"[VaultListener] Error: {e}")
                await asyncio.sleep(0.5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def main():
        def handle_event(evt):
            print(evt)

        load_dotenv()
        HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
        if not HELIUS_API_KEY:
            raise ValueError("Missing HELIUS_API_KEY in .env file")

        RPC_WSS = f"wss://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

        listener = SolanaVaultListener(
            rpc_ws_url=RPC_WSS,
            symbol="SOL-USDC",
            vault_accounts=SOL_USDC_VAULTS,
            log_updates=True,
        )
        await listener.run(handle_event)

    try:
        asyncio.run(main())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
