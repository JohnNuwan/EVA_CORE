---
name: react-framework
description: "Guide complet React 18/19 : hooks, composants, state management, Suspense, Server Components, testing, et optimisation."
tags: [react, jsx, hooks, suspense, server-components, state-management, testing, optimisation]
---

# React — Écosystème et Développement

## Architecture Core

### Composants et JSX
- **Composants fonctionnels** — privilégier les fonctions pures, éviter les classes
- **Props** — `interface Props { ... }` avec TypeScript
- **JSX** — syntaxe XML-in-JS, transpilé par SWC (Next.js) ou Babel (Vite/CRA)
- **Fragments** — `<>...</>` ou `<Fragment>` pour éviter les divs inutiles
- **Composition** — `children`, `render props`, slots pattern

### Hooks Fondamentaux
| Hook | Usage |
|------|-------|
| `useState` | État local, lazy initializer |
| `useEffect` | Side effects, cleanup, dépendances |
| `useRef` | Références mutables, DOM, valeur persistante |
| `useCallback` | Mémoïsation de fonctions |
| `useMemo` | Mémoïsation de valeurs calculées |
| `useContext` | Accès au contexte React |
| `useReducer` | État complexe, logique de transition |
| `useId` | IDs uniques pour accessibilité (React 18) |
| `useTransition` | Transitions non-bloquantes |
| `useDeferredValue` | Valeur différée pour UI réactive |
| `useSyncExternalStore` | Store externe (Zustand, Redux) |

### Règles des Hooks
- Toujours appelés au top level (pas de conditions/boucles)
- Toujours dans des composants React ou hooks custom
- Linter `eslint-plugin-react-hooks` obligatoire

## React 18+ Features

### Automatic Batching
```tsx
// React 18 : tous les setState sont batchés, même dans setTimeout/Promises
setCount(c => c + 1);
setFlag(f => !f);
// Un seul re-render
```

### Transitions
```tsx
const [isPending, startTransition] = useTransition();
startTransition(() => {
  setSearchQuery(input); // UI critique pas bloquée
});
```

### Suspense
- **Data Fetching** — `<Suspense fallback={<Loading />}>` + libraries compatibles (Relay, SWR, React Query)
- **Streaming SSR** — Suspense boundaries = points de streaming HTML
- **Selective Hydration** — priorité aux interactions utilisateur

### Server Components (RSC) — Next.js App Router
- Composants async qui s'exécutent uniquement côté serveur
- Pas de `useState`, `useEffect`, `useContext` — côte serveur uniquement
- `"use client"` — directive pour basculer en Client Component
- Sérialisation props server → client via JSON

## State Management

### Local → Global
| Niveau | Solution |
|--------|----------|
| Local | `useState`, `useReducer` |
| Arbre | `useContext` + `useReducer` |
| Global | Zustand, Jotai, Valtio |
| Serveur | React Query, SWR, RTK Query |
| Formulaires | React Hook Form + Zod |

### Zustand (recommandé global)
```tsx
import { create } from 'zustand';
const useStore = create<Store>((set) => ({
  count: 0,
  increment: () => set((s) => ({ count: s.count + 1 })),
}));
```

### React Query (TanStack Query)
```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ['users', id],
  queryFn: () => fetchUser(id),
  staleTime: 5_000,
  gcTime: 60_000,
});
```

## Patterns Avancés

### Compound Components
```tsx
<Select>
  <Select.Trigger />
  <Select.Options>
    <Select.Option value="1">Un</Select.Option>
  </Select.Options>
</Select>
```

### Error Boundaries
```tsx
class ErrorBoundary extends React.Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
}
```

## Testing
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('submit form', async () => {
  render(<MyForm />);
  await userEvent.type(screen.getByLabelText('Nom'), 'Alice');
  await userEvent.click(screen.getByRole('button', { name: 'Envoyer' }));
  expect(screen.getByText('Succès')).toBeInTheDocument();
});
```

## Optimisation

### React.memo / useMemo / useCallback
- `React.memo` — pour composants recevant les mêmes props fréquemment
- `useMemo` — calculs coûteux (filtrage, tri)
- `useCallback` — props callback passées à des enfants memoïsés
- **Ne pas** memoïser par défaut — mesurer d'abord

### Code Splitting
```tsx
const HeavyComponent = lazy(() => import('./Heavy'));
<Suspense fallback={<Spinner />}>
  <HeavyComponent />
</Suspense>
```

### Virtualisation (react-window / tanstack-virtual)
```tsx
<FixedSizeList height={400} itemCount={10000} itemSize={50}>
  {({ index, style }) => <div style={style}>Item {index}</div>}
</FixedSizeList>
```

## Bundling & Build
- **Vite** — recommandé pour SPA (dev ultra-rapide via ESM, build Rollup)
- **Next.js** — recommandé pour SSR/SSG (SWC, Turbopack)
- **Webpack** — legacy, éviter

## Références
- [React Docs](https://react.dev)
- [React 18 Release](https://react.dev/blog/2022/03/29/react-v18)
- [TanStack Query](https://tanstack.com/query/latest)
- [Zustand](https://github.com/pmndrs/zustand)
- [React Testing Library](https://testing-library.com/react)
- [Vitest](https://vitest.dev)