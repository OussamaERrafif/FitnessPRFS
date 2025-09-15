/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  webpack: (config, { isServer }) => {
    // Fix path casing inconsistencies on Windows
    // Disable case-sensitive path checks in Webpack
    config.resolve.cacheWithContext = false
    
    return config
  },
}

export default nextConfig
