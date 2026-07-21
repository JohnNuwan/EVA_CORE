---
name: svelte
description: "Guide complet Svelte 5 : runes, snippets, stores, SvelteKit, réactivité, transitions, optimisation."
tags: [svelte, svelte5, runes, sveltekit, stores, réactivité, transitions, compiler, vite]
---

# Svelte — Framework Compilé

## Philosophie

Svelte est un **compilateur** qui transforme les composants en JavaScript vanilla optimisé à la build. Pas de virtual DOM — mises à jour poussées directement au DOM. Bundle plus petit, runtime zéro, meilleures performances.

## Svelte 5 — Runes (nouveau système de réactivité)

### $state
```svelte
<script>
  let count = $state(0);
  let user = $state({ name: 'Alice', age: 30 });
</script>
<button onclick={() => count++}>{count}</button>
```

### $derived
```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);
  let status = $derived.by(() => count > 10 ? 'high' : 'low');
</script>
```

### $effect
```svelte
<script>
  let count = $state(0);
  $effect(() => {
    console.log(`count changed to ${count}`);
    return () => console.log('cleanup');
  });
</script>
```

### $props / $bindable
```svelte
<script>
  let { name, age = 25, ...rest } = $props();
  let { value = $bindable() } = $props();
</script>
<input bind:value />
<h1>Bonjour {name}</h1>
```

## Composants — Template

```svelte
{#if user.loggedIn}
  <p>Bienvenue {user.name}</p>
{:else}
  <button onclick={login}>Connexion</button>
{/if}

{#each items as item, i (item.id)}
  <div>{i + 1}. {item.name}</div>
{/each}

{#await promise}
  <p>Chargement...</p>
{:then value}
  <p>{value}</p>
{:catch error}
  <p>Erreur : {error.message}</p>
{/await}
```

## SvelteKit — Framework Full-Stack
```
src/
├── routes/
│   ├── +page.svelte       # Page
│   ├── +layout.svelte     # Layout
│   ├── +page.server.ts    # Load (serveur)
│   └── [slug]/+page.svelte
└── lib/
```

### Load Functions
```ts
export const load: PageServerLoad = async ({ params, fetch }) => {
  const product = await db.product.findUnique({ where: { id: params.slug } });
  return { product };
};
```

## Transitions & Animations
```svelte
<script>
  import { fade, fly, scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  let show = $state(true);
</script>

{#if show}
  <div transition:fly={{ y: 200, duration: 300 }}>Anime</div>
{/if}

{#each items as item (item.id)}
  <div animate:flip>{item.name}</div>
{/each}
```

## Optimisation
- Pas de runtime framework (compilé à la build)
- Bundles 2–5× plus petits que React
- Pas de virtual DOM diffing
- Treeshaking natif

## Pièges Courants
- **`$state()`** — ne peut être utilisé que dans `.svelte` ou `.svelte.js`
- **Migrer 4 → 5** — `on:click` → `onclick`, `$:` → `$derived`/`$effect`
- **SSR** — utiliser `browser` check pour accès `window`

## Références
- [Svelte 5 Docs](https://svelte.dev/docs)
- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [Runes Guide](https://svelte.dev/blog/runes)
- [Testing Library Svelte](https://testing-library.com/docs/svelte-testing-library/intro)