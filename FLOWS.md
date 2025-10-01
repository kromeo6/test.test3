# Authentication Flows Visualized

## 1. SAML 2.0 Flow (Most Common Enterprise)

```
┌─────────┐                                           ┌──────────────┐
│ Browser │                                           │   Okta IdP   │
└────┬────┘                                           └──────┬───────┘
     │                                                        │
     │  1. GET /airflow                                      │
     ├──────────────────────────────────────────►            │
     │                         ┌──────────────┐              │
     │                         │   Airflow    │              │
     │                         │  Web Server  │              │
     │                         └──────┬───────┘              │
     │  2. 302 Redirect to IdP       │                      │
     │◄──────────────────────────────┤                      │
     │                                                        │
     │  3. GET /okta/saml?SAMLRequest=...                   │
     ├───────────────────────────────────────────────────►  │
     │                                                        │
     │  4. Login Form (if not authenticated)                │
     │◄───────────────────────────────────────────────────  │
     │                                                        │
     │  5. Submit credentials + MFA                          │
     ├───────────────────────────────────────────────────►  │
     │                                                        │
     │  6. 302 Redirect with SAML Response                  │
     │◄───────────────────────────────────────────────────  │
     │                                                        │
     │  7. POST /airflow/acs (SAMLResponse=...)             │
     ├──────────────────────────────────────────►            │
     │                         ┌──────────────┐              │
     │                         │   Airflow    │              │
     │                         │  validates   │              │
     │                         │  assertion   │              │
     │                         └──────┬───────┘              │
     │  8. Set session cookie & redirect                     │
     │◄──────────────────────────────┤                      │
     │                                                        │
     │  9. Access Airflow UI (authenticated)                │
     ├──────────────────────────────────────────►            │
     │                                                        │
```

**Key Points:**
- SAML assertion is XML-based
- Contains user info (email, name, groups)
- Digitally signed by IdP
- Airflow validates signature before trusting

---

## 2. OAuth 2.0 / OIDC Flow (Modern Approach)

```
┌─────────┐                                      ┌────────────────┐
│ Browser │                                      │  Google OAuth  │
└────┬────┘                                      └───────┬────────┘
     │                                                    │
     │  1. Click "Login with Google"                    │
     ├──────────────────────────────►                   │
     │                    ┌──────────┐                  │
     │                    │  Airflow │                  │
     │                    └────┬─────┘                  │
     │                                                    │
     │  2. 302 Redirect to Google                       │
     │◄───────────────────┤                             │
     │    (with client_id, redirect_uri, scope)         │
     │                                                    │
     │  3. GET /oauth/authorize?client_id=...          │
     ├────────────────────────────────────────────────► │
     │                                                    │
     │  4. Login form (if needed)                       │
     │◄──────────────────────────────────────────────── │
     │                                                    │
     │  5. Consent screen (first time only)             │
     │◄──────────────────────────────────────────────── │
     │                                                    │
     │  6. User approves                                 │
     ├────────────────────────────────────────────────► │
     │                                                    │
     │  7. 302 Redirect with authorization code         │
     │◄──────────────────────────────────────────────── │
     │    /airflow/callback?code=ABC123                 │
     │                                                    │
     │  8. GET /airflow/callback?code=ABC123            │
     ├──────────────────────────────►                   │
     │                    ┌──────────┐                  │
     │                    │  Airflow │                  │
     │                    └────┬─────┘                  │
     │                         │                         │
     │                         │  9. Exchange code for  │
     │                         │     tokens             │
     │                         ├──────────────────────► │
     │                         │                         │
     │                         │  10. ID token + access │
     │                         │      token (JWT)       │
     │                         │◄────────────────────── │
     │                         │                         │
     │                         │  11. Validate JWT      │
     │                         │      & create session  │
     │                         │                         │
     │  12. Set cookie & redirect                       │
     │◄────────────────────────┤                        │
     │                                                    │
```

**Key Points:**
- Uses authorization code flow (most secure for web apps)
- ID token is a JWT (JSON Web Token)
- Contains user info in token claims
- Refresh token for long-lived sessions

---

## 3. LDAP Flow (Legacy)

```
┌─────────┐                                      ┌────────────────┐
│ Browser │                                      │ Active Directory│
└────┬────┘                                      │   LDAP Server   │
     │                                            └───────┬────────┘
     │  1. GET /airflow                                  │
     ├──────────────────────────────►                   │
     │                    ┌──────────┐                  │
     │                    │  Airflow │                  │
     │                    └────┬─────┘                  │
     │                                                    │
     │  2. Login form                                    │
     │◄───────────────────┤                             │
     │                                                    │
     │  3. Submit username + password                    │
     ├──────────────────────────────►                   │
     │                    ┌──────────┐                  │
     │                    │  Airflow │                  │
     │                    └────┬─────┘                  │
     │                         │                         │
     │                         │  4. LDAP Bind request  │
     │                         │  (check credentials)   │
     │                         ├──────────────────────► │
     │                         │                         │
     │                         │  5. Success/Failure    │
     │                         │◄────────────────────── │
     │                         │                         │
     │                         │  6. LDAP Search        │
     │                         │  (get user groups)     │
     │                         ├──────────────────────► │
     │                         │                         │
     │                         │  7. User attributes    │
     │                         │◄────────────────────── │
     │                         │                         │
     │  8. Set session & redirect                       │
     │◄────────────────────────┤                        │
     │                                                    │
```

**Key Points:**
- Password sent to Airflow (less secure)
- Direct connection to LDAP server
- No SSO - user must login to each app
- Still used in many legacy environments

---

## 4. Token-Based API Authentication

```
┌──────────────┐                              ┌────────────┐
│ API Client   │                              │  Airflow   │
│ (Python/CLI) │                              │  REST API  │
└──────┬───────┘                              └─────┬──────┘
       │                                             │
       │  1. POST /api/v1/auth/login                │
       │     {username: "admin", password: "..."}   │
       ├──────────────────────────────────────────► │
       │                                             │
       │  2. Response with JWT token                │
       │◄──────────────────────────────────────────┤
       │     {token: "eyJhbG...", expires: 3600}    │
       │                                             │
       │  3. Store token                            │
       │                                             │
       │  4. API request with token in header       │
       │     Authorization: Bearer eyJhbG...        │
       ├──────────────────────────────────────────► │
       │                                             │
       │                              5. Validate   │
       │                                 token & exp│
       │                                             │
       │  6. API response                           │
       │◄──────────────────────────────────────────┤
       │                                             │
```

**Key Points:**
- Used for programmatic access
- JWT contains user info and expiry
- Token must be included in every request
- Common for CI/CD pipelines

---

## 5. Enterprise Pattern with Multiple Apps

```
                    ┌─────────────────────────────┐
                    │   Identity Provider (Okta)  │
                    │                             │
                    │  • User Directory           │
                    │  • MFA (Duo, YubiKey)       │
                    │  • Session Management       │
                    │  • SAML/OIDC Endpoints      │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    │   SAML/OIDC Trust   │
                    │                     │
        ┌───────────┴────────┬────────────┴──────────┬──────────┐
        │                    │                       │          │
        ▼                    ▼                       ▼          ▼
┌──────────────┐     ┌──────────────┐       ┌──────────────┐  ...
│   Airflow    │     │   Grafana    │       │   Jenkins    │
│              │     │              │       │              │
│ SAML Enabled │     │ OAuth Enabled│       │ SAML Enabled │
└──────────────┘     └──────────────┘       └──────────────┘

Employee workflow:
1. Login to Okta at 9am (username + password + MFA)
2. Access Airflow → Auto redirected to Okta → Auto logged in (SSO)
3. Access Grafana → Auto redirected to Okta → Auto logged in (SSO)
4. Access Jenkins → Auto redirected to Okta → Auto logged in (SSO)
5. No additional passwords needed!
```

---

## 6. What Happens Behind the Scenes

### User Perspective:
```
You: Click "Airflow Dashboard"
     ↓
Browser: Redirect to company login page
     ↓
You: Enter password + approve push notification (MFA)
     ↓
Browser: Opens Airflow (you're logged in!)
```

### Technical Flow:
```
1. Browser → Airflow: GET /
2. Airflow: "User not authenticated, redirect to IdP"
3. Browser → IdP: "Please authenticate user"
4. IdP → Browser: "Show login form"
5. User: Enters credentials + MFA
6. IdP → Browser: "Here's a signed assertion"
7. Browser → Airflow: "Here's the assertion from IdP"
8. Airflow: Validates assertion signature
9. Airflow: "Signature valid! Create session for user"
10. Airflow → Browser: "Here's a session cookie"
11. Browser → Airflow: All future requests include cookie
```

---

## 7. Security Highlights

### SAML Assertion (Simplified):
```xml
<saml:Assertion>
  <saml:Subject>
    <saml:NameID>john.doe@company.com</saml:NameID>
  </saml:Subject>
  <saml:AttributeStatement>
    <saml:Attribute Name="email">
      <saml:AttributeValue>john.doe@company.com</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="groups">
      <saml:AttributeValue>airflow-admins</saml:AttributeValue>
      <saml:AttributeValue>data-team</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
  <ds:Signature>
    <!-- Digital signature from IdP -->
    <!-- Airflow validates this to ensure it's really from Okta -->
  </ds:Signature>
</saml:Assertion>
```

### JWT Token (OIDC):
```json
{
  "header": {
    "alg": "RS256",
    "kid": "abc123"
  },
  "payload": {
    "iss": "https://accounts.google.com",
    "sub": "1234567890",
    "email": "john.doe@company.com",
    "email_verified": true,
    "iat": 1516239022,
    "exp": 1516242622,
    "groups": ["airflow-admins", "data-team"]
  },
  "signature": "..."
}
```

---

## Summary

**Which flow for which scenario?**

| Scenario | Best Choice | Flow |
|----------|------------|------|
| Web UI for employees | SAML or OIDC | SSO flow (#1 or #2) |
| API access | OAuth 2.0 | Client credentials (#4) |
| Legacy on-premise | LDAP | Direct auth (#3) |
| Mobile app | OIDC | Authorization code + PKCE |
| Service-to-service | OAuth 2.0 | Client credentials |
| Third-party integration | OAuth 2.0 | Delegated access |

**The winner for internal tools like Airflow:**
- 🥇 **SAML 2.0** (60% market share)
- 🥈 **OpenID Connect** (35% market share)  
- 🥉 **LDAP** (5% and declining) 