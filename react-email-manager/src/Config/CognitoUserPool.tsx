export const cognitoUserPool = {
  UserPoolId: 'us-east-1_euB1ZeEGS',
  ClientId: '2uq0ko5cur40ss88im6pq8vedj',
  Region: 'us-east-1', // e.g., 'us-east-1'
  IdentityPoolId: 'your-identity-pool-id', // only needed if using AWS services
  Domain: 'https://email-manager-auth-domain.auth.us-east-1.amazoncognito.com',
  RedirectSignIn: 'http://localhost:5173/social-login-confirm-code',
  RedirectSignOut: 'http://localhost:5173',
  Scope: ['email', 'openid', 'phone'],
  ResponseType: 'code' // or 'token' for implicit grant
};