---
name: nlp-seq2seq
description: Use when working with sequence-to-sequence models — RNN encoder-decoder, LSTM, GRU, attention mechanisms (Bahdanau, Luong), beam search, teacher forcing, Neural Machine Translation, text summarization, et architectures séquentielles classiques.
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, seq2seq, rnn, lstm, gru, attention, beam-search, teacher-forcing, nmt, encoder-decoder]
    related_skills: [nlp-transformers, nlp-t5, nlp-bert, nlp-gpt, nlp-evaluation]
---

# Sequence-to-Sequence — Modèles Séquentiels et Traduction

## Vue d'ensemble

Les modèles Sequence-to-Sequence (Sutskever et al., 2014) transforment une séquence d'entrée en une séquence de sortie de longueur potentiellement différente. Bien que largement remplacés par les Transformers, les architectures RNN/LSTM/GRU restent importantes pour comprendre les fondations du NLP moderne, pour l'inférence sur des devices à faibles ressources, et pour le traitement de séquences temporelles.

Ce skill couvre : l'architecture encodeur-décodeur RNN, les mécanismes d'attention (Bahdanau, Luong), les stratégies d'entraînement (teacher forcing, scheduled sampling), l'inférence (beam search, greedy decoding), les variantes (BiRNN, RNN-T), et les implémentations pratiques.

## Quand l'utiliser

- Vous implémentez un seq2seq from scratch pour l'apprentissage
- Vous travaillez avec des séquences longues sur des devices à mémoire contrainte
- Vous faites de la traduction automatique, de la summarization, ou du speech-to-text avec RNN
- Vous voulez comprendre les mécanismes d'attention en partant du cadre historique
- Vous déployez sur des systèmes embarqués où les Transformers sont trop lourds

## Architecture Encodeur-Décodeur

### Encodeur RNN

L'encodeur lit la séquence d'entrée token par token et produit un état caché final qui résume la phrase.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class EncoderRNN(nn.Module):
    def __init__(self, vocab_size, emb_dim, hidden_dim, n_layers=2, dropout=0.3):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.rnn = nn.LSTM(emb_dim, hidden_dim, n_layers, dropout=dropout, batch_first=True, bidirectional=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, src):
        # src: [batch, src_len]
        embedded = self.dropout(self.embedding(src))
        # embedded: [batch, src_len, emb_dim]
        outputs, (hidden, cell) = self.rnn(embedded)
        # outputs: [batch, src_len, hidden_dim]
        # hidden: [n_layers, batch, hidden_dim]
        return outputs, hidden, cell
```

**Variante Bidirectionnelle (BiRNN) :** Les deux directions sont concaténées.

### Décodeur RNN

Le décodeur génère la séquence de sortie token par token, conditionné par le contexte de l'encodeur.

```python
class DecoderRNN(nn.Module):
    def __init__(self, vocab_size, emb_dim, hidden_dim, n_layers=2, dropout=0.3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.rnn = nn.LSTM(emb_dim + hidden_dim, hidden_dim, n_layers, dropout=dropout, batch_first=True)
        self.fc_out = nn.Linear(hidden_dim, vocab_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, input, hidden, cell, context):
        # input: [batch, 1] (token courant)
        # context: [batch, hidden_dim] (vecteur contexte)
        embedded = self.dropout(self.embedding(input))
        # Concaténer l'embedding avec le contexte
        rnn_input = torch.cat((embedded, context.unsqueeze(1)), dim=-1)
        output, (hidden, cell) = self.rnn(rnn_input, (hidden, cell))
        prediction = self.fc_out(output.squeeze(1))
        return prediction, hidden, cell
```

## Mécanismes d'Attention

### Bahdanau Attention (Additive, 2015)

**Principe :** Calculer un score d'alignement entre chaque état caché de l'encodeur et l'état courant du décodeur, puis pondérer les états encodeurs par softmax.

```
e_ij = v_a^T · tanh(W_a · s_{i-1} + U_a · h_j)
α_ij = softmax(e_ij)
c_i = Σ α_ij · h_j
```

```python
class BahdanauAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.W = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.U = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.v = nn.Linear(hidden_dim, 1, bias=False)

    def forward(self, decoder_hidden, encoder_outputs):
        # decoder_hidden: [batch, hidden_dim]
        # encoder_outputs: [batch, src_len, hidden_dim]

        # Ajouter une dimension pour la diffusion
        decoder_hidden = decoder_hidden.unsqueeze(1)  # [batch, 1, hidden_dim]

        # Score = v · tanh(W·h_dec + U·h_enc)
        score = self.v(torch.tanh(self.W(decoder_hidden) + self.U(encoder_outputs)))
        # score: [batch, src_len, 1]

        # Poids d'attention
        attn_weights = F.softmax(score.squeeze(-1), dim=-1)  # [batch, src_len]

        # Contexte = somme pondérée des états encodeurs
        context = torch.bmm(attn_weights.unsqueeze(1), encoder_outputs)  # [batch, 1, hidden_dim]
        return context.squeeze(1), attn_weights
```

### Luong Attention (Multiplicative, 2015)

Plus simple et plus rapide que Bahdanau. Trois variantes :

```python
class LuongAttention(nn.Module):
    def __init__(self, hidden_dim, method="general"):
        super().__init__()
        self.method = method

        if method == "general":
            self.W = nn.Linear(hidden_dim, hidden_dim, bias=False)
        elif method == "concat":
            self.W = nn.Linear(hidden_dim * 2, hidden_dim, bias=False)
            self.v = nn.Linear(hidden_dim, 1, bias=False)

    def score(self, decoder_hidden, encoder_output):
        # decoder_hidden: [batch, hidden_dim]
        # encoder_output: [batch, src_len, hidden_dim]
        if self.method == "dot":
            return torch.bmm(decoder_hidden.unsqueeze(1), encoder_output.transpose(1, 2))
        elif self.method == "general":
            return torch.bmm(self.W(decoder_hidden).unsqueeze(1), encoder_output.transpose(1, 2))
        elif self.method == "concat":
            dec_expanded = decoder_hidden.unsqueeze(1).expand(-1, encoder_output.size(1), -1)
            concat = torch.tanh(self.W(torch.cat((dec_expanded, encoder_output), dim=-1)))
            return self.v(concat).transpose(1, 2)

    def forward(self, decoder_hidden, encoder_outputs):
        scores = self.score(decoder_hidden, encoder_outputs)
        attn_weights = F.softmax(scores.squeeze(1), dim=-1).unsqueeze(1)
        context = torch.bmm(attn_weights, encoder_outputs)
        return context.squeeze(1), attn_weights.squeeze(1)
```

## Stratégies d'Entraînement

### Teacher Forcing

À chaque pas de temps, le décodeur reçoit le token **véritable** (ground truth) comme entrée, pas sa propre prédiction.

```python
def train_step(src, trg, encoder, decoder, criterion, teacher_forcing_ratio=1.0):
    batch_size, trg_len = trg.shape
    outputs = torch.zeros(batch_size, trg_len, target_vocab_size)

    encoder_outputs, hidden, cell = encoder(src)
    input = trg[:, 0]  # token <SOS>

    for t in range(1, trg_len):
        context, _ = attention(hidden[-1], encoder_outputs)
        output, hidden, cell = decoder(input.unsqueeze(1), hidden, cell, context)
        outputs[:, t] = output

        # Teacher forcing
        teacher_force = random.random() < teacher_forcing_ratio
        input = trg[:, t] if teacher_force else output.argmax(-1)

    loss = criterion(outputs.view(-1, target_vocab_size), trg.view(-1))
    return loss
```

**Ratio de teacher forcing :** typiquement 1.0 au début, décroît à 0.5-0.0 vers la fin (scheduled sampling).

### Scheduled Sampling (Bengio et al., 2015)

Décroissance progressive du teacher forcing :
```python
def scheduled_sampling_ratio(step, total_steps, strategy="linear"):
    if strategy == "linear":
        return max(0.0, 1.0 - step / total_steps)
    elif strategy == "exponential":
        return 0.5 ** (step / (total_steps * 0.1))
    elif strategy == "inverse_sigmoid":
        return total_steps / (total_steps + math.exp(step / total_steps))
```

## Inférence

### Greedy Decoding
```python
def greedy_decode(src, encoder, decoder, attention, max_len=50):
    encoder_outputs, hidden, cell = encoder(src)
    input = torch.tensor([[SOS_TOKEN]])
    outputs = []

    for _ in range(max_len):
        context, _ = attention(hidden[-1], encoder_outputs)
        output, hidden, cell = decoder(input, hidden, cell, context)
        pred = output.argmax(-1).item()
        outputs.append(pred)
        if pred == EOS_TOKEN:
            break
        input = torch.tensor([[pred]])

    return outputs
```

### Beam Search

**Principe :** Garder les k meilleures hypothèses à chaque pas.

```python
def beam_search(src, encoder, decoder, attention, beam_width=3, max_len=50):
    encoder_outputs, hidden, cell = encoder(src)
    context, _ = attention(hidden[-1], encoder_outputs)

    # Initialisation : k = 1
    beams = [(0.0, [SOS_TOKEN], hidden, cell, context)]

    for _ in range(max_len):
        candidates = []
        for score, seq, h, c, ctx in beams:
            if seq[-1] == EOS_TOKEN:
                candidates.append((score, seq, h, c, ctx))
                continue

            input = torch.tensor([[seq[-1]]])
            output, new_h, new_c = decoder(input, h, c, ctx)

            log_probs = F.log_softmax(output, dim=-1)
            top_k = log_probs.topk(beam_width)

            for i in range(beam_width):
                token = top_k.indices[0, i].item()
                new_score = score + top_k.values[0, i].item()
                candidates.append((new_score, seq + [token], new_h, new_c, ctx))

        # Trier et garder les meilleurs
        beams = sorted(candidates, key=lambda x: x[0] / len(x[1]), reverse=True)[:beam_width]

        # Stop si tous finis par EOS
        if all(b[1][-1] == EOS_TOKEN for b in beams):
            break

    return max(beams, key=lambda x: x[0])[1]
```

**Normalisation de la longueur :** diviser le score par `len(seq)^α` (α=0.6-0.7 typiquement) pour éviter le biais vers les séquences courtes.

## Attention Visuelle

```python
def plot_attention(attention_weights, src_tokens, tgt_tokens):
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(10, 8))
    sns.heatmap(attention_weights, xticklabels=src_tokens, yticklabels=tgt_tokens,
                cmap="viridis", annot=True, fmt=".2f")
    plt.xlabel("Source")
    plt.ylabel("Target")
    plt.title("Matrice d'alignement Attention")
    plt.show()
```

## Comparaison des Unités Récurrentes

| Unité | Paramètres | Problème gradient | Performance | Utilisation |
|-------|-----------|-------------------|-------------|-------------|
| RNN simple | d² + d | Vanishing/exploding | ★★ | Rare |
| LSTM | 4(d² + d) | Vanishing contrôlé | ★★★★ | Standard |
| GRU | 3(d² + d) | Vanishing contrôlé | ★★★★ | Efficace |
| BiLSTM | 8(d² + d) | Contexte bidirectionnel | ★★★★★ | Performance |

## Pièges Courants (Common Pitfalls)

1. **Vanishing gradient sur les longues séquences.** Utiliser LSTM/GRU avec gradient clipping (max_norm=1.0).
2. **Teacher forcing à 100%.** Le modèle ne se remet jamais de ses propres erreurs en inférence → scheduled sampling.
3. **Oubli de l'initialisation correcte.** `init_weights` uniforme ou xavier pour éviter l'instabilité.
4. **Beam search non normalisé.** Favorise les séquences courtes. Utiliser length normalization.
5. **Attention visualisée mais pas utilisée.** Vérifier que le vecteur contexte est correctement intégré.
6. **Batch size trop petit.** Les RNN sont sensibles au bruit du gradient avec batch < 16.

## Liste de vérification (Checklist)

- [ ] Unité récurrente adaptée (LSTM pour long terme, GRU pour efficacité)
- [ ] Mécanisme d'attention choisi (Bahdanau pour flexibilité, Luong pour rapidité)
- [ ] Teacher forcing ratio décroît pendant l'entraînement
- [ ] Gradient clipping activé (max_norm=1.0-5.0)
- [ ] Beam search avec length normalization pour l'inférence
- [ ] Normalisation initiale des poids (xavier uniform)
- [ ] Visualisation de l'attention pour la validation
