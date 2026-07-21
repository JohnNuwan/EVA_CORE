---
name: nextjs
description: "Guide complet Next.js 14/15 : App Router, Server Components, route handlers, middleware, ISR, caching, auth, déploiement."
tags: [nextjs, app-router, server-components, route-handlers, middleware, isr, caching, auth, vercel, ssr, ssg]
---

# Next.js — Framework React Full-Stack

## Architecture

### Pages Router (legacy) vs App Router (recommandé)
| Feature | Pages Router | App Router |
|---------|-------------|------------|
| Routing | `/pages/` | `/app/` |
| Composants | Client par défaut | Server Components par défaut |
| Layouts | `_app.tsx`, `_document.tsx` | `layout.tsx` imbriqués |
| Data Fetching | `getServerSideProps`, `getStaticProps` | `async` components + `fetch` |
| Streaming | Non | Oui (Suspense boundaries) |
| Middleware | Non | Oui (Edge Runtime) |

## App Router — Structure des Fichiers
```
app/
├── layout.tsx          # Layout racine (obligatoire)
├── page.tsx            # Page /
├── loading.tsx         # Suspense boundary auto
├── error.tsx           # Error boundary
├── not-found.tsx       # 404
├── sitemap.ts          # Sitemap généré
├── robots.ts           # robots.txt
├── api/users/route.ts  # Route handler
├── blog/
│   ├── [slug]/page.tsx # /blog/:slug
│   └── page.tsx        # /blog
└── dashboard/
    └── @sidebar/       # Parallel route
        └── page.tsx
```

## Server Components — Principes
- **Par défaut** : tous les composants dans `/app/` sont **Server Components**
- **`"use client"`** : directive pour hydratation côté client
- **Avantages** : zéro JS bundle, accès direct DB/FS, secrets sécurisés

### Data Fetching
```tsx
// Accès direct DB (Server Component)
async function UsersPage() {
  const users = await db.users.findMany();
  return <UserList users={users} />;
}

// Avec fetch + ISR
async function PostPage({ params }: { params: { slug: string } }) {
  const post = await fetch(`https://api.example.com/posts/${params.slug}`, {
    next: { revalidate: 3600 }, // ISR: 1h
  }).then(r => r.json());
  return <article>{post.content}</article>;
}
```

## Route Handlers (API)
```tsx
// app/api/users/route.ts
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = searchParams.get('page') ?? '1';
  const users = await db.users.findMany({ skip: +page * 20, take: 20 });
  return NextResponse.json(users);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const user = await db.users.create({ data: body });
  return NextResponse.json(user, { status: 201 });
}
```

## Middleware (Edge Runtime)
```ts
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('session')?.value;
  if (!token && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next|static|favicon.ico).*)'],
};
```

## ISR (Incremental Static Regeneration)
```tsx
export async function generateStaticParams() {
  const products = await db.products.findMany({ select: { id: true } });
  return products.map(p => ({ id: p.id.toString() }));
}

// Revalidation on-demand
await revalidatePath('/products');
await revalidateTag('products');
```

## Authentification (NextAuth.js)
```ts
import NextAuth from 'next-auth';
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [Google, Credentials({...})],
  callbacks: {
    session({ session, token }) { session.user.id = token.sub!; return session; },
  },
});
```

## Optimisation
```tsx
// Images
<Image src="/hero.webp" width={1200} height={630} priority placeholder="blur" />

// Fonts
const inter = Inter({ subsets: ['latin'], display: 'swap' });

// Métadonnées
export const metadata: Metadata = {
  title: { default: 'Mon Site', template: '%s | Mon Site' },
  description: 'Description',
};
```

## Déploiement
- **Vercel** — auto depuis GitHub, Edge Functions, ISR natif
- **Docker** — `output: 'standalone'` + Node.js image
- **Self-hosted** — PM2, systemd, CDN (Cloudflare/Nginx)

## Pièges Courants
- **`"use client"` trop large** — descendre au plus bas possible
- **Cache invalidation** — utiliser `revalidateTag`/`revalidatePath` correctement
- **Dynamic routes** — `generateStaticParams` manquant = pas de pré-rendu
- **Middleware** — Edge Runtime, pas Node.js (pas de `fs`, `crypto` native)

## Références
- [Next.js Docs](https://nextjs.org/docs)
- [Data Fetching](https://nextjs.org/docs/app/building-your-application/data-fetching)
- [Caching](https://nextjs.org/docs/app/building-your-application/caching)
- [NextAuth.js](https://authjs.dev)
- [Vercel Deploy](https://vercel.com/docs)