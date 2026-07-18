---
name: blockchain-web3-technology
description: "Compétence niveau expert en blockchain et technologies Web3. Couvre les architectures blockchain (Bitcoin, Ethereum, Solana, Polkadot, Cosmos, Avalanche, Near), les protocoles consensus (PoW, PoS, DPoS, PBFT, HotStuff, Tendermint), les L2 (Rollups, ZK, Optimistic), les DeFi protocoles (Uniswap, Aave, Compound, MakerDAO, Lido), les NFTs, les DAOs, la cryptographie appliquée, le smart contract développement Solidity/Rust/Cairo, les bridges cross-chain, la sécurité blockchain, et l'interopérabilité."
keywords: [blockchain, Web3, Ethereum, Solana, smart contracts, DeFi, rollups, consensus, Solidity]
categories: [cs.CR, cs.DC, cs.GT, cs.NI, cs.MA, q-fin.GN, cs.LG]
---

# Compétence Blockchain et Web3

## Présentation

Cette compétence couvre l'ensemble des technologies blockchain et Web3, des architectures de Layer 1 à la DeFi, en passant par le développement de smart contracts, les L2 et la sécurité blockchain.

---

## Architectures Blockchain

- **Bitcoin** : UTXO model, Bitcoin Script, halving (4 ans), Taproot
- **Ethereum** : EVM (Ethereum Virtual Machine), account model, gas, EIP-1559 (burn), EIP-4844 (blob data)
- **Solana** : SVM (Solana Virtual Machine), proof-of-history (PoH), rent, fees
- **Polkadot** : Relay chain, parachains, parathreads, shared security (XCM)
- **Cosmos** : IBC (Inter-Blockchain Communication), Cosmos SDK, Tendermint
- **Avalanche** : Subnets, X-Chain (asset), C-Chain (EVM), P-Chain (validation)
- **Near** : Sharding Nightshade, account model (named accounts), fees

## Consensus et Scalabilité

- **PoW (Proof of Work)** : Mining, hash rate, difficulty adjustment
- **PoS (Proof of Stake)** : Casper LMD-GHOST, attester committee, finality, slashing
- **DPoS (Delegated Proof of Stake)** : Délégation de validation (EOS, Tron)
- **PBFT** : Practical Byzantine Fault Tolerance
- **HotStuff** : Libra/Diem BFT consensus
- **Tendermint** : BFT consensus (Cosmos)
- **Babylon** : Bitcoin staking protocol for securing PoS chains
- **Restaking / EigenLayer** : Restaking de ETH, AVS (Actively Validated Services)

## L2 et Scalabilité

- **Optimistic Rollups** : Fraud proofs, challenge period (7 jours), sequencer
- **Arbitrum / Optimism / Base** : Rollups Optimistic majeurs
- **ZK-Rollups** : zk-SNARKs, zk-STARKs, validity proofs
- **zkEVM** : Exécution EVM compatible avec preuves zk
- **ZKSync / StarkNet / Scroll / Linea** : Rollups ZK majeurs
- **State Channels (Lightning)** : Canaux de paiement Bitcoin
- **Plasma** : Sidechains avec fraud proofs
- **Sidechains** : Chaînes indépendantes avec bridge

## Smart Contracts Développement

- **Solidity** : Langage principal Ethereum (héritage, libraries, modifiers, events, ABI)
- **Vyper / Huff / Yul** : Langages alternatifs (sécurité, assembly)
- **Rust (Solana / Anchor)** : Développement Solana (Anchor framework)
- **Cairo (StarkNet)** : Langage pour ZK-Rollups (Cairo 1/2)
- **Foundry / Hardhat** : Frameworks de développement (forge, anvil, cast)
- **Security Tools** : Slither, Mythril, Echidna
- **OpenZeppelin** : Libraries standards (ERC20, ERC721, ERC1155)
- **ERC4626** : Tokenized Vaults standard
- **Upgradeability** : Proxy patterns (UUPS, Beacon, Diamond EIP-2535)

## DeFi et Web3

- **AMM (Uniswap)** : v2 (x*y=k), v3 (concentrated liquidity), v4 (hooks)
- **Lending (Aave / Compound)** : Lending pools, interest rates, liquidation
- **Yield (Curve / Convex)** : StableSwap, yield optimization
- **Liquid Staking (Lido)** : stETH, ETH staking liquide
- **Stablecoins (MakerDAO)** : DAI, CDP, stability fees, liquidation
- **Restaking (EigenLayer)** : EigenLayer, AVS, restaking ETH
- **Pendle** : Tokenisation du yield
- **Perpetuals (GMX / dYdX)** : Futures perpétuels on-chain
- **Oracle Manipulation** : Manipulation de prix, oracle attacks
- **MEV (Maximal Extractable Value)** : Flashbots, Searcher, Builder, Relay, ePBS

## NFTs, DAOs et Gouvernance

- **NFTs** : ERC721 metadata, mint, royalty (EIP-2981)
- **NFT Marketplaces** : Blur, OpenSea, marketplace mechanics, bids
- **Fractionalization** : Fractionnement de NFTs
- **DAO Structures** : Moloch, Compound governance, token voting
- **DAO Operations** : Delegation, quorum, timelock, treasury management (Gnosis Safe)
- **ENS** : Ethereum Name Service, domain names
- **Identity / ENS / LENS** : Identité Web3 (LENS Protocol)
- **SocialFi / GameFi** : Finances sociales et gaming on-chain