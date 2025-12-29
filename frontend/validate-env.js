#!/usr/bin/env node
/**
 * Environment Variables Validation Script
 *
 * Validates that all required environment variables are set and properly formatted
 * for the Todo Web Application frontend.
 *
 * Usage:
 *     node validate-env.js
 *
 * Exit codes:
 *     0 - All validations passed
 *     1 - One or more validations failed
 */

const fs = require('fs');
const path = require('path');

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[91m',
  green: '\x1b[92m',
  yellow: '\x1b[93m',
  blue: '\x1b[94m',
};

// Helper functions for colored output
const printHeader = (text) => {
  console.log(`\n${colors.bright}${colors.blue}${'='.repeat(70)}${colors.reset}`);
  console.log(`${colors.bright}${colors.blue}${text.padStart((70 + text.length) / 2).padEnd(70)}${colors.reset}`);
  console.log(`${colors.bright}${colors.blue}${'='.repeat(70)}${colors.reset}\n`);
};

const printSuccess = (text) => {
  console.log(`${colors.green}✓${colors.reset} ${text}`);
};

const printWarning = (text) => {
  console.log(`${colors.yellow}⚠${colors.reset} ${text}`);
};

const printError = (text) => {
  console.log(`${colors.red}✗${colors.reset} ${text}`);
};

const printInfo = (text) => {
  console.log(`${colors.blue}ℹ${colors.reset} ${text}`);
};

/**
 * Validate API URL format
 * @param {string} url - API URL to validate
 * @returns {[boolean, string]} - [isValid, message]
 */
function validateApiUrl(url) {
  if (!url) {
    return [false, 'NEXT_PUBLIC_API_URL is not set'];
  }

  try {
    const parsed = new URL(url);

    // Check scheme
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return [false, `Invalid protocol '${parsed.protocol}'. Expected 'http:' or 'https:'`];
    }

    // Production warning
    if (parsed.protocol === 'http:' &&
        !parsed.hostname.includes('localhost') &&
        parsed.hostname !== '127.0.0.1') {
      return [false, 'Production API URL should use https://, not http://'];
    }

    // Check for trailing slash
    if (url.endsWith('/')) {
      printWarning('  API URL should not end with a trailing slash');
    }

    return [true, `Valid API URL: ${url}`];
  } catch (e) {
    return [false, `Invalid URL format: ${e.message}`];
  }
}

/**
 * Validate JWT secret strength
 * @param {string} secret - JWT secret to validate
 * @returns {[boolean, string]} - [isValid, message]
 */
function validateJwtSecret(secret) {
  if (!secret) {
    return [false, 'BETTER_AUTH_SECRET is not set'];
  }

  // Check for default/insecure values
  const insecureValues = [
    'your-secret-key-change-in-production',
    'changeme',
    'secret',
    'password',
  ];

  if (insecureValues.includes(secret.toLowerCase())) {
    return [false, 'BETTER_AUTH_SECRET is using a default/insecure value'];
  }

  // Check length
  if (secret.length < 32) {
    return [false, `BETTER_AUTH_SECRET is too short (${secret.length} chars). Minimum: 32 characters`];
  }

  // Check entropy
  const uniqueChars = new Set(secret.split('')).size;
  if (uniqueChars < 16) {
    return [false, `BETTER_AUTH_SECRET has low entropy (only ${uniqueChars} unique characters)`];
  }

  // Check character variety
  const hasLetter = /[a-zA-Z]/.test(secret);
  const hasNumber = /[0-9]/.test(secret);
  const hasSpecial = /[^a-zA-Z0-9]/.test(secret);

  if (!hasLetter || !hasNumber) {
    return [false, 'BETTER_AUTH_SECRET should contain letters, numbers, and optionally special characters'];
  }

  return [true, `Strong secret key (${secret.length} characters)`];
}

/**
 * Check all required environment variables
 * @returns {Object} - Validation results
 */
function checkEnvVars() {
  const results = {};

  printHeader('Environment Variables Validation');

  // Load .env.local if it exists
  const envFile = path.join(__dirname, '.env.local');
  if (fs.existsSync(envFile)) {
    printInfo(`Loading environment variables from: ${envFile}\n`);
    const envContent = fs.readFileSync(envFile, 'utf-8');
    envContent.split('\n').forEach(line => {
      line = line.trim();
      if (line && !line.startsWith('#')) {
        const [key, ...valueParts] = line.split('=');
        if (key) {
          process.env[key.trim()] = valueParts.join('=').trim();
        }
      }
    });
  } else {
    printWarning(`.env.local file not found at: ${envFile}`);
    printInfo('Checking system environment variables...\n');
  }

  // Required variables
  console.log(`${colors.bright}Required Variables:${colors.reset}\n`);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
  const [apiUrlValid, apiUrlMsg] = validateApiUrl(apiUrl);
  if (apiUrlValid) {
    printSuccess(`NEXT_PUBLIC_API_URL: ${apiUrlMsg}`);
    results.NEXT_PUBLIC_API_URL = true;
  } else {
    printError(`NEXT_PUBLIC_API_URL: ${apiUrlMsg}`);
    results.NEXT_PUBLIC_API_URL = false;
  }

  const secret = process.env.BETTER_AUTH_SECRET || '';
  const [secretValid, secretMsg] = validateJwtSecret(secret);
  if (secretValid) {
    printSuccess(`BETTER_AUTH_SECRET: ${secretMsg}`);
    results.BETTER_AUTH_SECRET = true;
  } else {
    printError(`BETTER_AUTH_SECRET: ${secretMsg}`);
    results.BETTER_AUTH_SECRET = false;
  }

  return results;
}

/**
 * Print validation summary
 * @param {Object} results - Validation results
 */
function printSummary(results) {
  printHeader('Validation Summary');

  const total = Object.keys(results).length;
  const passed = Object.values(results).filter(v => v).length;
  const failed = total - passed;

  if (failed === 0) {
    printSuccess(`All ${total} validations passed!`);
    printInfo('\nYour environment is properly configured.');
  } else {
    printError(`${failed} of ${total} validations failed`);
    printInfo('\nPlease fix the errors above before running the application.');
  }
}

/**
 * Print security recommendations
 */
function printRecommendations() {
  printHeader('Security Recommendations');

  const recommendations = [
    '1. Never commit .env.local files to version control',
    '2. Use different secrets for development and production',
    '3. Generate JWT secrets with cryptographically secure random generators:',
    '   node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'base64\'))"',
    '4. Ensure BETTER_AUTH_SECRET matches the backend configuration',
    '5. Use HTTPS for API URLs in production (never HTTP)',
    '6. Store secrets in secure environment variable systems (Vercel Secrets, etc.)',
    '7. Rotate secrets periodically (every 90 days)',
    '8. Never expose API keys or secrets in client-side code',
  ];

  recommendations.forEach(rec => printInfo(rec));
}

/**
 * Print example .env.local file
 */
function printExampleEnv() {
  printHeader('Example .env.local File');

  const example = `# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication (must match backend)
BETTER_AUTH_SECRET=your-strong-secret-key-at-least-32-characters-long
`;

  console.log(example);
}

/**
 * Check if backend secret matches
 */
function checkBackendSecretMatch() {
  const frontendSecret = process.env.BETTER_AUTH_SECRET;
  if (!frontendSecret) return;

  const backendEnvFile = path.join(__dirname, '..', 'backend', '.env');
  if (!fs.existsSync(backendEnvFile)) {
    printWarning('\nCannot verify backend secret match: backend/.env not found');
    return;
  }

  const backendEnvContent = fs.readFileSync(backendEnvFile, 'utf-8');
  let backendSecret = '';

  backendEnvContent.split('\n').forEach(line => {
    line = line.trim();
    if (line.startsWith('BETTER_AUTH_SECRET=')) {
      backendSecret = line.split('=')[1].trim();
    }
  });

  if (backendSecret && frontendSecret !== backendSecret) {
    printHeader('Secret Mismatch Warning');
    printError('BETTER_AUTH_SECRET does not match between frontend and backend!');
    printInfo('Frontend and backend must use the same JWT secret for authentication to work.');
    printInfo('\nFrontend secret length: ' + frontendSecret.length);
    printInfo('Backend secret length: ' + backendSecret.length);
  } else if (backendSecret) {
    printHeader('Backend Verification');
    printSuccess('BETTER_AUTH_SECRET matches between frontend and backend');
  }
}

/**
 * Main validation function
 */
function main() {
  try {
    // Run validations
    const results = checkEnvVars();

    // Check backend secret match
    checkBackendSecretMatch();

    // Print summary
    printSummary(results);

    // Check if any validation failed
    const anyFailed = Object.values(results).some(v => !v);

    if (anyFailed) {
      printRecommendations();
      printExampleEnv();
      process.exit(1);
    }

    // Print recommendations even on success
    printRecommendations();

    process.exit(0);
  } catch (error) {
    printError(`Unexpected error: ${error.message}`);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  validateApiUrl,
  validateJwtSecret,
  checkEnvVars,
};
