# 🛰 Solana Vault Balance Listener — Public Edition

> ⚠ **Disclaimer**  
> This is the **free version** of the Solana vault listener.  
> It **does not** execute trades or use MEV logic.  
> A `strategies/` folder exists with a simple TWAP example, but it’s non-aggressive.  
> If you want to profit, either buy the **pro version** or implement your own strategy.  
> Contact info: [GitHub — NovaStackDev](https://github.com/NovaStackDev)

---

## 🚀 Quick Start

### 1. Clone the repo

git clone https://github.com/NovaStackDev/order-manager-free
cd order-manager-free/src/order_manager/core

### 2. Install dependencies

Make sure you have Python 3.9+ and dependencies installed.

python -V
pip install websockets python-dotenv

### 3. Get a Helius API key
Go to https://helius.dev

Create an account and generate an API key

Keep it safe — we’ll store it in a .env file.

### 4. Create your .env file

In the project root or the same folder as the script, create:

HELIUS_API_KEY=your_helius_api_key_here

### 5. Run the listener

From inside src/order_manager/core, run:

python omprotocol.py

6. Example output
[VaultListener] Connecting to wss://mainnet.helius-rpc.com...
[VaultListener] Connected.
[Vault Update] base=1234.567 quote=89012.34

### ⚙ Extra Configuration

Vault accounts:
Edit SOL_USDC_VAULTS inside omprotocol.py to monitor other vaults.

Logging:
Set log_updates=False in SolanaVaultListener() if you only want callback data without log spam.

### 🛠 Troubleshooting

Missing HELIUS_API_KEY error

→ Check your .env file is in the right folder and contains a valid API key.

Python can’t find the script

→ Make sure you’re inside the folder where omprotocol.py lives, or run:

python -m order_manager.core.omprotocol

No updates showing

→ The vault might not be changing balances at that moment. Try a more active one.


🏁 Final Note
This free version is for monitoring only.
If you want profitable automated strategies, you must either:

Implement your own strategies, logic, etc.. or

Purchase the pro-version. Contact info: [GitHub — NovaStackDev](https://github.com/NovaStackDev)

That’s all — enjoy monitoring the blockchain in real time! 🚀
