---
name: vue
description: "Guide complet Vue 3 : Composition API, Pinia, Vue Router, Vite, Nuxt, composables, slots, testing, optimisation."
tags: [vue, vue3, composition-api, pinia, vue-router, vite, nuxt, composables, slots, typescript, testing]
---

# Vue.js — Framework Progressif

## Architecture Vue 3

### Composition API (recommandée)
```vue
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

const count = ref(0);
const doubled = computed(() => count.value * 2);

watch(count, (newVal, oldVal) => console.log(`count: ${oldVal} → ${newVal}`));
onMounted(() => fetchData());
</script>

<template>
  <button @click="count++">{{ count }} × 2 = {{ doubled }}</button>
</template>
```

### Options API (legacy)
```vue
export default { data() { return { count: 0 } }, computed: { doubled() { ... } } }
```

## Système de Réactivité

### Ref vs Reactive
```ts
const count = ref(0);          // .value pour accès individuel
const state = reactive({ x: 0, y: 0 }); // Accès direct propriétés
const obj = ref({ a: 1 });     // ref + objet = reactive interne
```

### shallowRef / shallowReactive
```ts
const list = shallowRef([...bigArray]); // Pas de tracking profond — meilleur perf
triggerRef(list); // Forcer la mise à jour
```

### watchEffect
```ts
watchEffect(() => console.log(count.value)); // S'exécute immédiatement + réagit aux changements
```

## Composables
```ts
// useCounter.ts
export function useCounter(initial = 0) {
  const count = ref(initial);
  const increment = () => count.value++;
  return { count, increment };
}
```

## Directives
- `v-if`/`v-else-if`/`v-else` — rendu conditionnel
- `v-show` — toggle display CSS
- `v-for` — itération (`:key` obligatoire)
- `v-model` — two-way binding (`.lazy`, `.number`, `.trim`)
- `v-on` (`@`) — événements
- `v-once` — rendu unique
- `v-memo` — mémoïsation (Vue 3.2+)

## Composants

### Props & Emits
```vue
<script setup lang="ts">
const props = defineProps<{ name: string; age?: number }>();
const emit = defineEmits<{ update: [value: string] }>();
</script>
```

### Slots
```vue
<template>
  <div class="card">
    <header><slot name="header" /></header>
    <main><slot /></main>
    <footer><slot name="footer" text="bonjour" /></footer>
  </div>
</template>
```

## Pinia (State Management)
```ts
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0);
  const increment = () => count.value++;
  return { count, increment };
});
```

## Vue Router
```ts
const routes = [
  { path: '/', component: Home },
  { path: '/users/:id', component: UserView, props: true },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
];

router.beforeEach((to, from) => {
  if (to.meta.requiresAuth && !isLoggedIn) return '/login';
});
```

## Nuxt 3
- Auto-imports composants/composables
- SSR, SSG, ISR, Streaming
- Server routes (`/server/api/`)
- `useFetch`, `useAsyncData`, `useState`

```vue
<script setup lang="ts">
const { data: users } = await useFetch('/api/users');
</script>
```

## Testing
```ts
import { mount } from '@vue/test-utils';
it('increments', async () => {
  const wrapper = mount(Counter);
  await wrapper.find('button').trigger('click');
  expect(wrapper.text()).toContain('1');
});
```

## Optimisation
- `v-memo` — templates lourds
- `shallowRef` — grandes listes
- `defineAsyncComponent` — lazy loading
- Vite → Tree-shaking natif ESM

## Pièges Courants
- **Perte de réactivité** — destructurer `reactive()` sans `toRefs()`
- **`v-for` + `v-if`** — ne pas utiliser ensemble
- **Clés** — `:key` avec `id` pour listes dynamiques

## Références
- [Vue 3 Docs](https://vuejs.org)
- [Pinia](https://pinia.vuejs.org)
- [Vue Router](https://router.vuejs.org)
- [Nuxt 3](https://nuxt.com)
- [Vite](https://vitejs.dev)
- [Vue Test Utils](https://test-utils.vuejs.org)