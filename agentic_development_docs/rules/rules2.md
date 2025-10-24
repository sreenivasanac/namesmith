# Next.js 15 + Supabase SSR Cookie Management Rules

## Overview

Next.js 15 App Router introduces strict constraints on where cookies can be modified. This document outlines best practices for handling cookies in Next.js 15 applications, particularly when using Supabase SSR authentication.

## The Problem

### Common Error
```
Error: Cookies can only be modified in a Server Action or Route Handler.
Read more: https://nextjs.org/docs/app/api-reference/functions/cookies#options
```

### Root Cause
- **Next.js 15 Constraint**: Cookies can ONLY be modified in Server Actions and Route Handlers
- **Server Components**: Can read cookies but CANNOT write/modify them
- **Supabase Behavior**: `auth.getSession()` may trigger token refresh, which attempts to write new cookies
- **Conflict**: When Supabase tries to refresh tokens in a Server Component, it violates Next.js constraints

## Next.js 15 Cookie Constraints

### Where Cookies CAN Be Modified
✅ **Route Handlers** (`app/api/.../route.ts`)
```typescript
export async function GET(request: Request) {
  const response = NextResponse.next();
  response.cookies.set('name', 'value', options);
  return response;
}
```

✅ **Server Actions** (`'use server'` functions)
```typescript
'use server'
export async function myAction() {
  const cookieStore = await cookies();
  cookieStore.set('name', 'value', options);
}
```

### Where Cookies CANNOT Be Modified
❌ **Server Components** (pages, layouts)
```typescript
// This will throw an error if Supabase tries to write cookies
export default async function Page() {
  const cookieStore = await cookies();
  cookieStore.set('name', 'value'); // ❌ ERROR
}
```

❌ **Middleware** (read-only in Next.js 15+)
```typescript
export function middleware(request: NextRequest) {
  // Can read but not write cookies in middleware
}
```

## Supabase SSR Architecture Patterns

### Pattern 1: Server Components (Read-Only)

**Use Case**: Pages and layouts that need to check authentication

**Key Principle**: Use `getUser()` for auth checks, avoid triggering session refresh

```typescript
// lib/auth/supabase-server.ts
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

export async function createSupabaseServerClient() {
  const cookieStore = await cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        async getAll() {
          return cookieStore.getAll().map(({ name, value }) => ({ name, value }));
        },
        async setAll() {
          // Server Components cannot mutate cookies; writes are handled in Route Handlers.
        },
      },
    }
  );
}
```

**Usage in Server Components**:
```typescript
// app/dashboard/page.tsx
export default async function DashboardPage() {
  const supabase = await createSupabaseServerClient();
  
  // ✅ Use getUser() for auth checks (doesn't refresh session)
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    redirect("/login");
  }
  
  // ✅ Only call getSession() when you need the access token
  const { data: { session } } = await supabase.auth.getSession();
  const accessToken = session?.access_token ?? "";
  
  // Use accessToken for API calls...
}
```

### Pattern 2: Route Handlers (Read-Write)

**Use Case**: OAuth callbacks, token exchange, API endpoints that need to modify auth state

**Key Principle**: Route Handlers can write cookies through the Response object

```typescript
// app/api/auth/callback/route.ts
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");

  if (code) {
    const cookieStore = await cookies();
    const response = NextResponse.redirect(new URL("/dashboard", request.url));
    
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          async getAll() {
            return cookieStore.getAll().map(({ name, value }) => ({ name, value }));
          },
          async setAll(cookiesToSet) {
            // ✅ Write cookies through the Response object
            for (const { name, value, options } of cookiesToSet) {
              if (!value) {
                response.cookies.delete(name);
              } else {
                response.cookies.set(name, value, options);
              }
            }
          },
        },
      }
    );

    // Exchange code for session (will write cookies through setAll above)
    await supabase.auth.exchangeCodeForSession(code);

    return response;
  }

  return NextResponse.redirect(new URL("/login", request.url));
}
```

### Pattern 3: Client Components (Browser)

**Use Case**: Client-side authentication state, real-time auth listeners

**Key Principle**: Use browser client for client-side operations

```typescript
// lib/auth/supabase-browser.ts
import { createBrowserClient } from "@supabase/ssr";

export function createSupabaseBrowserClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

**Usage with React Hooks**:
```typescript
// hooks/useAccessToken.ts
"use client";

import { useEffect, useState } from "react";
import { createSupabaseBrowserClient } from "@/lib/auth/supabase-browser";

export function useAccessToken(): string | null {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [supabase] = useState(() => createSupabaseBrowserClient());

  useEffect(() => {
    let isMounted = true;

    // Get initial session
    supabase.auth.getSession().then(({ data }) => {
      if (!isMounted) return;
      setAccessToken(data.session?.access_token ?? null);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async () => {
      const { data } = await supabase.auth.getSession();
      setAccessToken(data.session?.access_token ?? null);
    });

    return () => {
      isMounted = false;
      subscription.unsubscribe();
    };
  }, [supabase]);

  return accessToken;
}
```

## Key Principles (Generic - Any Next.js 15 Project)

### 1. Separation of Concerns
- **Read Operations**: Server Components can read cookies
- **Write Operations**: Only Route Handlers and Server Actions can write cookies
- **Never mix**: Don't try to write cookies in Server Components

### 2. Auth Check Strategy
- Use lightweight auth checks (`getUser()`) that don't trigger session refresh
- Only fetch full session data (`getSession()`) when you need the access token
- Minimize session refresh attempts in Server Components

### 3. Cookie Write Pattern
```typescript
// ❌ WRONG: Direct cookie mutation in Server Component
const cookieStore = await cookies();
cookieStore.set('name', 'value'); // Will fail

// ✅ CORRECT: Write through Response in Route Handler
const response = NextResponse.next();
response.cookies.set('name', 'value', options);
return response;
```

### 4. Client-Side State Management
- Use React hooks for managing auth state on the client
- Implement cleanup patterns (`isMounted` flag) to prevent memory leaks
- Subscribe to auth state changes for real-time updates

### 5. Error Handling
```typescript
// ✅ GOOD: Defensive access token handling
const { data: { session } } = await supabase.auth.getSession();
const accessToken = session?.access_token ?? "";

// Handle case where token might be missing
if (!accessToken) {
  // Redirect or show error
}
```

## Supabase-Specific Best Practices

### getUser() vs getSession()

**getUser()**:
- ✅ Validates JWT token server-side
- ✅ Does NOT trigger cookie refresh
- ✅ Safe for Server Components
- ✅ Use for authentication checks
- ❌ Doesn't provide access token

**getSession()**:
- ✅ Returns full session with access token
- ⚠️ MAY trigger session refresh
- ⚠️ May attempt to write cookies
- ✅ Use when you need access token
- ⚠️ Use carefully in Server Components

### Decision Tree

```
Do you need the access token?
├─ NO → Use getUser() only
│   └─ Check if user exists, redirect if needed
│
└─ YES → Use getUser() first, then getSession()
    ├─ Check user exists with getUser()
    └─ Fetch session with getSession() only if user exists
```

## Troubleshooting Common Pitfalls

### Issue 1: "Cookies can only be modified" error in Server Component

**Symptom**: Error when loading pages/layouts
**Cause**: Supabase trying to refresh session in Server Component
**Solution**: 
1. Make `setAll()` a no-op in Server Component client config
2. Use `getUser()` instead of `getSession()` for auth checks
3. Handle cookie writes in Route Handlers only

### Issue 2: Session not persisting after login

**Symptom**: User logged in but session disappears on refresh
**Cause**: Cookies not being written properly in auth callback
**Solution**: Ensure auth callback Route Handler writes cookies through Response object

### Issue 3: Access token undefined in Server Component

**Symptom**: `session?.access_token` is undefined
**Cause**: Session might not be loaded or expired
**Solution**: 
```typescript
const { data: { session } } = await supabase.auth.getSession();
const accessToken = session?.access_token ?? "";

if (!accessToken) {
  // Handle missing token: redirect to login or show error
  redirect("/login");
}
```

### Issue 4: Race conditions in client-side auth state

**Symptom**: Component updates after unmounting, React warnings
**Cause**: Async operations completing after component unmount
**Solution**: Use `isMounted` flag pattern:
```typescript
useEffect(() => {
  let isMounted = true;
  
  asyncOperation().then(result => {
    if (!isMounted) return;
    setState(result);
  });
  
  return () => {
    isMounted = false;
  };
}, []);
```

## Migration Checklist

When upgrading to Next.js 15 or implementing proper cookie handling:

- [ ] Audit all Server Components for direct `cookieStore.set()` calls
- [ ] Replace `getSession()` with `getUser()` for auth checks in Server Components
- [ ] Implement no-op `setAll()` in Server Component Supabase client config
- [ ] Move all cookie writes to Route Handlers or Server Actions
- [ ] Update auth callback to write cookies through Response object
- [ ] Add defensive null checks for `session?.access_token`
- [ ] Implement `isMounted` pattern in client-side auth hooks
- [ ] Test authentication flow: login, logout, refresh, protected routes
- [ ] Verify session persistence across page navigation

## References

- [Next.js Cookies Documentation](https://nextjs.org/docs/app/api-reference/functions/cookies)
- [Supabase SSR Guide](https://supabase.com/docs/guides/auth/server-side/nextjs)
- [Next.js 15 App Router](https://nextjs.org/docs/app)

---

**Last Updated**: Based on Next.js 15.5.5 and @supabase/ssr 0.7.0
