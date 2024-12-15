/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    config.module.rules.push({
      test: /\.csv$/,
      loader: 'raw-loader',
    })
    return config
  },
}

module.exports = nextConfig
