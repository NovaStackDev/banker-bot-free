import { Raydium } from "@raydium-io/raydium-sdk-v2";
import { Connection } from "@solana/web3.js";

const connection = new Connection("https://api.mainnet-beta.solana.com");

async function main() {
  const raydium = await Raydium.load({ connection });

  // Ensure lexicographic order of mints
  const mintA = "Es9vMFrzaCER1HVGz2RGVR1qQyYnXzGzaJtJ8WQmqwY"; // USDT
  const mintB = "So11111111111111111111111111111111111111112"; // SOL

  const poolInfo = await raydium.api.fetchPoolByMints({
    mint1: mintA,
    mint2: mintB,
  });

  console.log(JSON.stringify(poolInfo.data, null, 2));
}

main();
