/** @type {import('next').NextConfig} */
const nextConfig = {
    /* config options here */
    distDir: 'build',
    env: {
      FASTAPI_ENDPOINT: process.env.FASTAPI_ENDPOINT,
      NEXT_PUBLIC_API_TIMEOUT: process.env.NEXT_PUBLIC_API_TIMEOUT,
      API_KEY: process.env.API_KEY
    }
  }
   
module.exports = nextConfig