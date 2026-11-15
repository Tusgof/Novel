/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  poweredByHeader: false,
  turbopack: {
    root: import.meta.dirname,
  },
  experimental: {
    staticGenerationRetryCount: 1,
    staticGenerationMaxConcurrency: 1,
    staticGenerationMinPagesPerWorker: 1000,
  },
};

export default nextConfig;
