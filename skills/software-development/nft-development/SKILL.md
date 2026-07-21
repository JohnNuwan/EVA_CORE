---
name: nft-development
description: "Développement NFT complet — standards ERC-721/1155, minting, metadata, IPFS/Arweave, marketplaces, auctions, royalties ERC-2981, fractionalization, et NFT dynamiques (ERC-6551, ERC-4907)."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [nft, erc-721, erc-1155, erc-2981, erc-6551, ipfs, arweave, metadata, minting, marketplace, royalties, fractional-nft, soulbound]
    related_skills: [smart-contracts, solidity-advanced, web3-dapp, tokenomics]
---

# Développement NFT — Standards, Minting, Marketplaces & Écosystème

## Quand utiliser ce skill

- Créer une collection NFT (art, gaming, musique, utility tokens)
- Développer un contrat ERC-721 ou ERC-1155 avancé avec minting, royalties, whitelist
- Implémenter un marketplace avec enchères (English, Dutch, Sealed-Bid)
- Gérer le stockage décentralisé des métadonnées (IPFS, Arweave, Arweave Permanweb)
- Construire des NFTs dynamiques (ERC-6551 Token Bound Accounts, ERC-4907 Rentable)

## 1. Standards NFT — Comparaison

| Standard | Usage | Unique | Batch | Semi-Fungible | Metadata on-chain |
|----------|-------|--------|-------|---------------|-------------------|
| **ERC-721** | Collection classique, art, gaming | ✅ Un token = 1 ID | ❌ | ❌ | ❌ (sauf SVG) |
| **ERC-1155** | Gaming, multi-collections | ❌ | ✅ | ✅ (quantité par ID) | ❌ |
| **ERC-998** | Composable (NFT contient d'autres NFTs) | ✅ | ❌ | ❌ | ❌ |
| **ERC-6551** | TBA (Token Bound Account — chaque NFT = wallet) | ✅ | ❌ | ❌ | ❌ |
| **ERC-4907** | Rentable (location temporaire) | ✅ ou ❌ | - | - | ❌ |

## 2. Contrat ERC-721 Avancé avec Toutes les Fonctionnalités

### 2.1 Contrat Complet

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Royalty.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract EVACollection is ERC721, ERC721Enumerable, ERC721URIStorage, ERC721Royalty, Ownable, ReentrancyGuard {
    using Strings for uint256;

    // Configuration
    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MINT_PRICE = 0.08 ether;
    uint256 public constant MAX_PER_WALLET = 5;
    uint256 public constant MAX_PER_TX = 3;
    bytes32 public merkleRoot;  // Pour la whitelist
    string public baseURI;
    string public notRevealedURI;
    bool public revealed;
    bool public publicMintOpen;
    bool public presaleMintOpen;
    uint256 public totalMinted;

    // Mapping des ventes
    mapping(address => uint256) public presaleMinted;
    bool private _lockedMint;  // Reentrancy supplémentaire

    // Events
    event TokenMinted(address indexed to, uint256 indexed tokenId);
    event BaseURIUpdated(string newURI);
    event RoyaltyUpdated(address receiver, uint96 feeNumerator);

    constructor(bytes32 _merkleRoot) ERC721("EVA Collection", "EVAC") {
        merkleRoot = _merkleRoot;
        _setDefaultRoyalty(msg.sender, 500); // 5% royalties
    }

    // Mint public
    function mint(uint256 quantity) external payable nonReentrant {
        require(publicMintOpen, "Public mint not open");
        require(quantity > 0 && quantity <= MAX_PER_TX, "Invalid quantity");
        require(totalMinted + quantity <= MAX_SUPPLY, "Exceeds max supply");
        require(balanceOf(msg.sender) + quantity <= MAX_PER_WALLET, "Exceeds wallet max");
        require(msg.value >= MINT_PRICE * quantity, "Insufficient ETH");
        require(!_lockedMint, "Reentrancy");

        _lockedMint = true;
        for (uint256 i = 0; i < quantity; i++) {
            _safeMint(msg.sender, ++totalMinted);
            emit TokenMinted(msg.sender, totalMinted);
        }
        _lockedMint = false;
    }

    // Mint presale (whitelist Merkle)
    function presaleMint(uint256 quantity, bytes32[] calldata proof) external payable nonReentrant {
        require(presaleMintOpen, "Presale not open");
        require(MerkleProof.verify(proof, merkleRoot, keccak256(abi.encodePacked(msg.sender))), "Not whitelisted");
        require(presaleMinted[msg.sender] + quantity <= MAX_PER_WALLET, "Exceeds presale max");
        require(totalMinted + quantity <= MAX_SUPPLY, "Exceeds max supply");
        require(msg.value >= MINT_PRICE * quantity, "Insufficient ETH");

        presaleMinted[msg.sender] += quantity;
        for (uint256 i = 0; i < quantity; i++) {
            _safeMint(msg.sender, ++totalMinted);
            emit TokenMinted(msg.sender, totalMinted);
        }
    }

    // Airdrop batch (owner)
    function airdrop(address[] calldata recipients) external onlyOwner {
        require(totalMinted + recipients.length <= MAX_SUPPLY, "Exceeds max supply");
        for (uint256 i = 0; i < recipients.length; i++) {
            _safeMint(recipients[i], ++totalMinted);
        }
    }

    // Overrides requis
    function _update(address to, uint256 tokenId, address auth)
        internal override(ERC721, ERC721Enumerable) returns (address) {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 value)
        internal override(ERC721, ERC721Enumerable) {
        super._increaseBalance(account, value);
    }

    function tokenURI(uint256 tokenId)
        public view override(ERC721, ERC721URIStorage) returns (string memory) {
        if (!revealed) return notRevealedURI;
        return bytes(baseURI).length > 0
            ? string(abi.encodePacked(baseURI, tokenId.toString(), ".json"))
            : "";
    }

    function supportsInterface(bytes4 interfaceId)
        public view override(ERC721, ERC721Enumerable, ERC721URIStorage, ERC721Royalty) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    // Admin
    function reveal() external onlyOwner { revealed = true; }
    function setBaseURI(string memory _uri) external onlyOwner { baseURI = _uri; emit BaseURIUpdated(_uri); }
    function setMerkleRoot(bytes32 _merkleRoot) external onlyOwner { merkleRoot = _merkleRoot; }
    function togglePublicMint() external onlyOwner { publicMintOpen = !publicMintOpen; }
    function togglePresaleMint() external onlyOwner { presaleMintOpen = !presaleMintOpen; }
    function withdraw() external onlyOwner { payable(owner()).transfer(address(this).balance); }
}
```

## 3. Métadonnées et Stockage Décentralisé

### 3.1 Format Metadata Standard (OpenSea compliant)

```json
{
  "name": "EVA #0001",
  "description": "EVA Collection — Générative Art NFT",
  "image": "ipfs://QmHash/image.png",
  "external_url": "https://evanft.io/1",
  "animation_url": "ipfs://QmHash/animation.glb",
  "attributes": [
    { "trait_type": "Background", "value": "Deep Space" },
    { "trait_type": "Rarity", "value": "Legendary" },
    { "trait_type": "Power", "value": 99, "max_value": 100, "display_type": "boost_number" },
    { "trait_type": "Level", "value": 5, "max_value": 10, "display_type": "boost_percentage" },
    { "trait_type": "Created At", "value": 1719234567, "display_type": "date" }
  ],
  "properties": {
    "category": "image",
    "creators": [{"address": "0x...", "share": 100}]
  }
}
```

### 3.2 IPFS via Pinata + Filecoin (Lighthouse)

```bash
# Lighthouse (gratuit, 1GB/file)
curl -X POST https://node.lighthouse.storage/api/v0/add \
  -F "file=@metadata/1.json" \
  -H "Authorization: Bearer $LIGHTHOUSE_KEY"
# → { "Hash": "QmHash" }

# Pinata (clé API requise)
curl -X POST https://api.pinata.cloud/pinning/pinFileToIPFS \
  -H "Authorization: Bearer $PINATA_JWT" \
  -F "file=@image.png"
```

### 3.3 Arweave (Permanent Storage)

```bash
# Installer arweave-deploy
npm install -g arweave-deploy

# Déployer fichier sur Arweave
arweave deploy image.png --key-file wallet.json --tags Content-Type image/png

# Déployer metadata
arweave deploy metadata/1.json --key-file wallet.json --tags Content-Type application/json
```

## 4. Marketplace & Enchères

### 4.1 English Auction (Prix ascendant)

```solidity
contract EnglishAuction {
    struct Auction {
        address seller;
        uint256 tokenId;
        uint256 startingPrice;
        uint256 highestBid;
        address highestBidder;
        uint256 endTime;
        bool ended;
    }

    mapping(uint256 => Auction) public auctions;

    function createAuction(uint256 tokenId, uint256 startingPrice, uint256 duration) external {
        IERC721(nft).transferFrom(msg.sender, address(this), tokenId);
        auctions[tokenId] = Auction(msg.sender, tokenId, startingPrice, 0, address(0), block.timestamp + duration, false);
    }

    function bid(uint256 tokenId) external payable {
        Auction storage a = auctions[tokenId];
        require(block.timestamp < a.endTime, "Auction ended");
        require(msg.value > a.highestBid, "Bid too low");

        // Rembourser l'ancien highest bidder
        if (a.highestBid > 0) {
            payable(a.highestBidder).transfer(a.highestBid);
        }

        a.highestBid = msg.value;
        a.highestBidder = msg.sender;
    }

    function end(uint256 tokenId) external {
        Auction storage a = auctions[tokenId];
        require(block.timestamp >= a.endTime, "Not yet ended");
        require(!a.ended, "Already ended");
        a.ended = true;

        if (a.highestBid > 0) {
            // Vainqueur reçoit le NFT, seller reçoit le paiement
            IERC721(nft).safeTransferFrom(address(this), a.highestBidder, tokenId);
            payable(a.seller).transfer(a.highestBid);
        } else {
            // Pas d'enchère : retour au seller
            IERC721(nft).safeTransferFrom(address(this), a.seller, tokenId);
        }
    }
}
```

### 4.2 Dutch Auction (Prix descendant)

```solidity
contract DutchAuction {
    uint256 public startPrice = 10 ether;
    uint256 public endPrice = 1 ether;
    uint256 public duration = 7 days;
    uint256 public startTime;
    address public seller;

    function getCurrentPrice() public view returns (uint256) {
        uint256 elapsed = block.timestamp - startTime;
        if (elapsed >= duration) return endPrice;
        uint256 priceRange = startPrice - endPrice;
        uint256 discount = (priceRange * elapsed) / duration;
        return startPrice - discount;
    }

    function buy() external payable {
        uint256 price = getCurrentPrice();
        require(msg.value >= price, "Insufficient");
        IERC721(nft).safeTransferFrom(address(this), msg.sender, tokenId);
        payable(seller).transfer(price);
        if (msg.value > price) payable(msg.sender).transfer(msg.value - price);
    }
}
```

## 5. Standards Émergents

### 5.1 ERC-6551 — Token Bound Account (TBA)

Chaque NFT devient un wallet (smart account) capable de posséder d'autres tokens, d'interagir avec des protocoles, et de cumuler de l'historique on-chain.

```solidity
// Registry qui crée un compte lié à chaque token
contract ERC6551Registry {
    function createAccount(
        address implementation,
        bytes32 salt,
        uint256 chainId,
        address tokenContract,
        uint256 tokenId
    ) external returns (address) {
        address account = _getAccount(implementation, salt, chainId, tokenContract, tokenId);
        bytes memory code = implementation.code;
        if (account.code.length == 0) {
            address created;
            bytes32 _salt = keccak256(abi.encode(salt, chainId, tokenContract, tokenId));
            assembly { created := create2(0, add(code, 0x20), mload(code), _salt) }
            require(created == account, "Create2 failed");
        }
        return account;
    }
}
```

**Cas d'usage** : Gaming (items dans le personnage NFT), DeFi (une NFT qui stake), DAO (un NFT qui vote), Social (profil on-chain).

### 5.2 ERC-4907 — Rentable NFT (Location)

Ajoute des rôles `user` et `expires` — pratique pour le gaming (louer un skin) ou les terrains virtuels.

```solidity
contract RentableNFT is ERC4907 {
    struct UserInfo {
        address user;
        uint64 expires;
    }
    mapping(uint256 => UserInfo) internal _users;

    function setUser(uint256 tokenId, address user, uint64 expires) external {
        require(ownerOf(tokenId) == msg.sender, "Not owner");
        _users[tokenId] = UserInfo(user, expires);
        emit UpdateUser(tokenId, user, expires);
    }

    function userOf(uint256 tokenId) external view returns (address) {
        if (_users[tokenId].expires >= block.timestamp) return _users[tokenId].user;
        return address(0);
    }
}
```

## 6. Génération d'Art Génératif On-Chain

### P5.js → SVG → On-Chain

```solidity
// SVG directement stocké dans le contrat (généré à partir du tokenId)
function tokenURI(uint256 tokenId) public view override returns (string memory) {
    string memory svg = string(abi.encodePacked(
        "<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500'>",
        "<rect width='500' height='500' fill='", getColor(tokenId), "'/>",
        "<circle cx='250' cy='250' r='", toString(tokenId % 100 + 50),
        "' fill='", getColor(tokenId * 2), "'/>",
        "</svg>"
    ));
    return _formatMetadata(tokenId, svg);
}
```

## 7. NFT Fractionalization

Permettre de fractionner un NFT rare (ex: CryptoPunk) en ERC-20 pour la propriété partielle :

```solidity
contract Fractionalizer {
    IERC721 public nft;
    uint256 public tokenId;
    IERC20 public fractionalToken;

    // Déposer un NFT → recevoir des tokens fractionnés
    function fractionalize(uint256 amount) external {
        nft.safeTransferFrom(msg.sender, address(this), tokenId);
        fractionalToken.mint(msg.sender, amount); // ex: 1 000 000 tokens
    }

    // Racheter le NFT avec les tokens fractionnés
    function buyout() external {
        require(fractionalToken.totalSupply() == amount, "Need all tokens");
        fractionalToken.burn(address(this), amount);
        nft.safeTransferFrom(address(this), msg.sender, tokenId);
    }
}
```

## 8. Checklist de Déploiement NFT

- [ ] Metadata générée et uploadée sur IPFS/Arweave
- [ ] Base URI configurée dans le contrat
- [ ] Royalties configurées (ERC-2981, 5-10%)
- [ ] Merkle tree généré pour la whitelist
- [ ] Test en local (Hardhat) + sur testnet (Sepolia, Goerli)
- [ ] Vérification du contrat sur Etherscan
- [ ] Reveal différé (metadata non révélée jusqu'au mint)
- [ ] Limite de mint par wallet implémentée
