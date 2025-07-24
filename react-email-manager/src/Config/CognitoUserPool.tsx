export const cognitoUserPool = {
  UserPoolId: 'us-east-1_U5Dtpbx6W',
  ClientId: '52e5pb1uipkm8h6lqf94ftbots',
  Region: 'us-east-1', // e.g., 'us-east-1'
  IdentityPoolId: 'your-identity-pool-id', // only needed if using AWS services
  Domain: 'https://email-manager-auth-domain.auth.us-east-1.amazoncognito.com',
  RedirectSignIn: 'http://localhost:5173/social-login-confirm-code',
  RedirectSignOut: 'http://localhost:5173',
  Scope: ['email', 'openid', 'phone'],
  ResponseType: 'code' // or 'token' for implicit grant
};