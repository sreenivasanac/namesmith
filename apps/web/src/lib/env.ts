const requiredClientEnv = ["NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY", "NEXT_PUBLIC_API_URL"] as const;

type ClientEnvKeys = (typeof requiredClientEnv)[number];

type ClientEnv = Record<ClientEnvKeys, string>;

function readClientEnv(): ClientEnv {
  const values = {} as ClientEnv;
  for (const key of requiredClientEnv) {
    const value = process.env[key];
    if (!value) {
      if (process.env.NODE_ENV === "production") {
        throw new Error(`Missing required env var: ${key}`);
      }
      console.warn(`[env] Missing ${key}; falling back to empty string in development`);
      values[key] = "";
    } else {
      values[key] = value;
    }
  }
  return values;
}

export const env = readClientEnv();
