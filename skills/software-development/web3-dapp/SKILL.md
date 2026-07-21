---
name: web3-dapp
description: "Développement complet d'applications Web3 — intégration wallets (MetaMask, WalletConnect), ethers.js/viem, wagmi/rainbowkit, web3.py, signatures EIP-712, The Graph, IPFS, et architectures décentralisées full-stack."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [web3, dapp, ethers, viem, wagmi, web3py, metamask, walletconnect, siwe, eip-1193, the-graph, ipfs, react, nextjs]
    related_skills: [smart-contracts, solidity-advanced, defi-protocols, nft-development]
---

# Développement Web3 — Architecture Full-Stack Décentralisée

## Quand utiliser ce skill

- Construire une dApp complète (frontend React/Next.js + blockchain + The Graph)
- Intégrer des wallets (MetaMask, WalletConnect, Coinbase Wallet)
- Implémenter l'authentification Web3 (SIWE — Sign In With Ethereum)
- Développer un backend web3 en Python (web3.py, ape, brownie)
- Indexer des événements on-chain avec The Graph ou GraphQL custom
- Gérer le stockage décentralisé (IPFS, Arweave, Filecoin)

## 1. Architecture d'une dApp Moderne

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│  Next.js / Vite + React + TypeScript + Tailwind  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │wagmi/rain┐  │ethersjs/ │  │ SIWE Auth    │  │
│  │bowkit    │  │viem      │  │              │  │
│  │(wallet)  │  │(blockch.)│  │(signature)   │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
└──────────────────┬──────────────────────────────┘
                   │ RPC / EIP-1193
┌──────────────────▼──────────────────────────────┐
│                 Blockchain                        │
│  Ethereum / Polygon / Arbitrum / Optimism / Base  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Smart    │  │ Events   │  │ State        │  │
│  │ Contracts│  │ (logs)   │  │ (storage)    │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
└──────────────────┬──────────────────────────────┘
                   │ GraphQL / WebSocket
┌──────────────────▼──────────────────────────────┐
│                 Backend (optionnel)               │
│  The Graph (indexing) / IPFS (storage)            │
│  / Backend custom (Node/Express, Python/FastAPI)  │
└─────────────────────────────────────────────────┘
```

## 2. Stack Frontend Web3

### 2.1 Initialisation du Projet (Next.js + wagmi + RainbowKit)

```bash
# Créer le projet
npx create-next-app@latest eva-dapp --typescript --tailwind --app
cd eva-dapp

# Installer les dépendances web3
npm install wagmi viem@2.x @rainbow-me/rainbowkit@2.x @tanstack/react-query
```

### 2.2 Configuration du Provider Web3

```typescript
// app/providers.tsx
'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WagmiProvider } from 'wagmi';
import { RainbowKitProvider, darkTheme } from '@rainbow-me/rainbowkit';
import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { mainnet, polygon, arbitrum, optimism, base } from 'wagmi/chains';
import '@rainbow-me/rainbowkit/styles.css';

const config = getDefaultConfig({
  appName: 'EVA DApp',
  projectId: process.env.NEXT_PUBLIC_WC_PROJECT_ID!, // WalletConnect Cloud
  chains: [mainnet, polygon, arbitrum, optimism, base],
  ssr: true,
});

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider theme={darkTheme()} coolMode>
          {children}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}
```

### 2.3 Composant d'Interaction avec un Smart Contract

```typescript
// components/MintButton.tsx
'use client';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';
import { parseEther } from 'viem';
import { evaCollectionABI } from '@/abi/EVACollection';

const CONTRACT_ADDRESS = '0x...';

export function MintButton({ quantity = 1 }: { quantity?: number }) {
  const { data: mintHash, writeContract, isPending } = useWriteContract();
  const { isLoading, isSuccess } = useWaitForTransactionReceipt({ hash: mintHash });
  const { data: totalSupply } = useReadContract({
    address: CONTRACT_ADDRESS,
    abi: evaCollectionABI,
    functionName: 'totalMinted',
  });

  const handleMint = async () => {
    writeContract({
      address: CONTRACT_ADDRESS,
      abi: evaCollectionABI,
      functionName: 'mint',
      args: [quantity],
      value: parseEther((0.08 * quantity).toString()),
    });
  };

  return (
    <div>
      <p>Total minted: {totalSupply?.toString() ?? '...'}</p>
      <button
        onClick={handleMint}
        disabled={isPending || isLoading}
        className="px-4 py-2 bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50"
      >
        {isPending ? 'Confirm in wallet...' : isLoading ? 'Minting...' : `Mint ${quantity} NFT`}
      </button>
      {isSuccess && <p>✅ Minted! Tx: {mintHash}</p>}
    </div>
  );
}
```

### 2.4 Sign In With Ethereum (SIWE)

```typescript
// lib/siwe.ts
import { SiweMessage } from 'siwe';
import { getAccount, signMessage } from '@wagmi/core';
import { config } from '@/app/providers';

export async function authenticate() {
  const { address, chainId } = getAccount(config);
  if (!address || !chainId) throw new Error('Wallet not connected');

  // 1. Récupérer un nonce depuis le serveur
  const nonceRes = await fetch('/api/auth/nonce');
  const { nonce } = await nonceRes.json();

  // 2. Créer le message SIWE
  const message = new SiweMessage({
    domain: window.location.host,
    address,
    statement: 'Sign in to EVA DApp',
    uri: window.location.origin,
    version: '1',
    chainId,
    nonce,
  });

  // 3. Signer le message
  const signature = await signMessage(config, {
    message: message.prepareMessage(),
  });

  // 4. Vérifier côté serveur
  const verifyRes = await fetch('/api/auth/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, signature }),
  });

  return verifyRes.json();
}
```

## 3. Backend Python avec web3.py

### 3.1 Configuration

```python
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
import json, os

# Connexion
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL", "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY")))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Pour Polygon, Arbitrum

# Account (signature locale)
account = Account.from_key(os.getenv("PRIVATE_KEY"))
print(f"Connected: {w3.is_connected()}, Address: {account.address}")
```

### 3.2 Lecture et Écriture Smart Contract

```python
# Abi + Address
with open("abi/Token.json") as f:
    abi = json.load(f)
contract = w3.eth.contract(address="0x...", abi=abi)

# Lire (call — gratuit)
total_supply = contract.functions.totalSupply().call()
balance = contract.functions.balanceOf(account.address).call()
print(f"Supply: {total_supply}, Balance: {balance}")

# Écrire (transaction — payante) avec gestion de gas
tx = contract.functions.transfer(
    Web3.to_checksum_address("0xRecipient"),
    Web3.to_wei(100, "ether")
).build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 100000,
    'gasPrice': w3.eth.gas_price,
})

signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)  # web3.py < 7
# Ou : w3.eth.send_raw_transaction(signed.raw_transaction)  # web3.py >= 7
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Status: {receipt['status']}, Gas used: {receipt['gasUsed']}")
```

### 3.3 Écoute d'Événements en Temps Réel

```python
import asyncio
from web3 import AsyncWeb3

async def listen_events():
    async_w3 = AsyncWeb3(AsyncWeb3.WebSocketProvider("wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"))

    contract = async_w3.eth.contract(address="0x...", abi=abi)
    event_filter = contract.events.Transfer.create_filter(from_block="latest")

    while True:
        try:
            events = await event_filter.get_new_entries()
            for event in events:
                print(f"Transfer: {event.args.from} → {event.args.to}, value={event.args.value}")
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(2)

asyncio.run(listen_events())
```

## 4. The Graph — Indexation On-Chain

### 4.1 Création d'un Subgraph

```yaml
# subgraph.yaml
specVersion: 1.0.0
indexerHints:
  prune: auto
schema:
  file: ./schema.graphql
dataSources:
  - kind: ethereum
    name: EVACollection
    network: mainnet
    source:
      address: "0x..."
      abi: EVACollection
      startBlock: 15000000
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.7
      language: wasm/assemblyscript
      entities:
        - Token
        - Owner
      abis:
        - name: EVACollection
          file: ./abis/EVACollection.json
      eventHandlers:
        - event: Transfer(indexed address,indexed address,indexed uint256)
          handler: handleTransfer
      file: ./src/mapping.ts
```

```typescript
// src/mapping.ts
import { Transfer as TransferEvent } from "../generated/EVACollection/EVACollection";
import { Token, Owner } from "../generated/schema";

export function handleTransfer(event: TransferEvent): void {
  // Mettre à jour l'owner
  let token = Token.load(event.params.tokenId.toString());
  if (!token) {
    token = new Token(event.params.tokenId.toString());
    token.creator = event.params.from;
  }
  token.owner = event.params.to;
  token.save();

  // Mettre à jour le compteur de l'owner
  let owner = Owner.load(event.params.to.toHex());
  if (!owner) {
    owner = new Owner(event.params.to.toHex());
    owner.tokenCount = 0;
  }
  owner.tokenCount += 1;
  owner.save();
}
```

## 5. WalletConnect — Intégration Mobile

```typescript
// Via RainbowKit déjà configuré (section 2.2)
// Support natif de WalletConnect, MetaMask, Coinbase Wallet, Ledger, etc.

// Connexion manuelle sans RainbowKit
import { createWalletClient, custom } from 'viem';
import { mainnet } from 'viem/chains';

const walletClient = createWalletClient({
  chain: mainnet,
  transport: custom(window.ethereum!),
});

// Connexion
const [address] = await walletClient.requestAddresses();
// Switch chain
await walletClient.switchChain({ id: 137 });  // Polygon
```

## 6. IPFS — Stockage Décentralisé

### 6.1 Upload via API (Pinata / Lighthouse)

```typescript
// src/lib/ipfs.ts
const PINATA_JWT = process.env.NEXT_PUBLIC_PINATA_JWT;

export async function uploadToIPFS(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
    method: 'POST',
    headers: { Authorization: `Bearer ${PINATA_JWT}` },
    body: formData,
  });

  const { IpfsHash } = await res.json();
  return `ipfs://${IpfsHash}`;
}

export async function uploadMetadata(metadata: object): Promise<string> {
  const res = await fetch('https://api.pinata.cloud/pinning/pinJSONToIPFS', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${PINATA_JWT}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(metadata),
  });

  const { IpfsHash } = await res.json();
  return `ipfs://${IpfsHash}`;
}
```

### 6.2 Lecture depuis IPFS

```typescript
// IPFS Gateway (public)
// https://ipfs.io/ipfs/<CID>
// https://<CID>.ipfs.dweb.link

function ipfsUrl(cid: string): string {
  return `https://ipfs.io/ipfs/${cid}`;
}
```

## 7. Déploiement

### 7.1 Build + Deploy Frontend

```bash
# Vercel (recommandé pour Next.js)
npm run build
vercel --prod

# Netlify
npm run build
netlify deploy --prod --dir=out
```

### 7.2 Env Variables

```env
# .env.local
NEXT_PUBLIC_WC_PROJECT_ID=xxx          # WalletConnect Cloud ID
NEXT_PUBLIC_ALCHEMY_KEY=xxx            # RPC endpoint
NEXT_PUBLIC_CONTRACT_ADDRESS=0x...
NEXT_PUBLIC_PINATA_JWT=xxx             # IPFS pinning
```

### 7.3 Vérification Etherscan

```bash
npx hardhat verify --network polygon 0xContractAddress "arg1" "arg2"
```

## 8. Checklist de Sécurité d'une dApp

- [ ] **Never trust user input** — valider tous les args côté contrat + frontend
- [ ] **No private keys in frontend** — utiliser des providers (Alchemy/Infura) côté serveur
- [ ] **SIWE authentication** — vérifier signature et nonce côté backend
- [ ] **RPC rate limiting** — limiter les appels RPC, utiliser caching (React Query, SWR)
- [ ] **WalletConnect Project ID** — obligatoire, gratuit sur cloud.walletconnect.com
- [ ] **HTTPS only** — les wallets refusent de se connecter en HTTP
- [ ] **Environment variables** — NEXT_PUBLIC_ seulement pour les vars exposées
- [ ] **Gas estimation** — toujours estimer avant d'envoyer une tx
- [ ] **Error handling** — gérer les rejets de tx (user cancelled, out of gas)
