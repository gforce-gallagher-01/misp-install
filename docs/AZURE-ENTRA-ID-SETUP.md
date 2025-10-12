# Azure Entra ID (Azure AD) Authentication Setup for MISP

This guide provides step-by-step instructions for configuring Azure Entra ID (formerly Azure Active Directory) authentication for your MISP instance.

## Overview

Azure Entra ID integration enables:
- **Single Sign-On (SSO)** - Users authenticate with their Microsoft 365 / Azure AD credentials
- **Centralized User Management** - No need to manage separate MISP passwords
- **Group-based Access Control** - Map Azure AD groups to MISP roles (User, Org Admin, Site Admin)
- **Enhanced Security** - Leverage Azure AD MFA, Conditional Access, and security policies

## Prerequisites

1. **Azure AD Tenant** - Your organization must have an Azure AD tenant (comes with Microsoft 365)
2. **Admin Access** - You need Global Administrator or Application Administrator role in Azure AD
3. **MISP Installation** - MISP must be accessible via HTTPS with a valid domain name
4. **Valid SSL Certificate** - Azure AD requires HTTPS endpoints

## Step 1: Register MISP Application in Azure Portal

### 1.1 Create App Registration

1. Navigate to **Azure Portal**: https://portal.azure.com
2. Go to **Azure Active Directory** > **App registrations**
3. Click **+ New registration**
4. Configure the application:

   ```
   Name: MISP Threat Intelligence Platform
   Supported account types: Accounts in this organizational directory only (Single tenant)
   Redirect URI:
     Platform: Web
     URI: https://misp.example.com/users/login
   ```

   > Replace `misp.example.com` with your actual MISP domain

5. Click **Register**

### 1.2 Note Application Details

After registration, you'll see the **Overview** page. Record these values:

- **Application (client) ID** - You'll use this as `AAD_CLIENT_ID`
- **Directory (tenant) ID** - You'll use this as `AAD_TENANT_ID`

Example:
```
Application (client) ID: a1b2c3d4-1234-5678-9abc-def012345678
Directory (tenant) ID: 9876fedc-ba98-7654-3210-fedcba987654
```

## Step 2: Create Client Secret

### 2.1 Generate Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **+ New client secret**
3. Configure:
   ```
   Description: MISP Authentication Secret
   Expires: 24 months (recommended)
   ```
4. Click **Add**
5. **IMPORTANT**: Copy the **Value** immediately - you'll use this as `AAD_CLIENT_SECRET`
   - You won't be able to see it again after leaving this page!

Example:
```
AAD_CLIENT_SECRET: abc123~XyZ.456-DeF789_GhI012
```

## Step 3: Configure API Permissions

### 3.1 Add Microsoft Graph Permissions

1. Go to **API permissions** in your app registration
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Add these permissions:
   - **User.Read** - Read user profile
   - **User.ReadBasic.All** - Read basic user info (optional, for user lookup)
   - **GroupMember.Read.All** - Read group memberships (if using group-based roles)

6. Click **Add permissions**

### 3.2 Grant Admin Consent

1. Click **Grant admin consent for [Your Organization]**
2. Confirm by clicking **Yes**
3. Verify all permissions show **Granted for [Your Organization]** with a green checkmark

## Step 4: Configure MISP .env File

### 4.1 Update Environment Variables

Edit `/opt/misp/.env` and configure these settings:

```bash
##
# Azure Entra ID Configuration
##

# Enable Azure AD authentication
AAD_ENABLE=true

# Azure AD Application Settings (from Azure Portal)
AAD_CLIENT_ID=a1b2c3d4-1234-5678-9abc-def012345678
AAD_TENANT_ID=9876fedc-ba98-7654-3210-fedcba987654
AAD_CLIENT_SECRET=abc123~XyZ.456-DeF789_GhI012

# Redirect URI (must match Azure app registration)
AAD_REDIRECT_URI=https://misp.example.com/users/login

# Provider Settings
AAD_PROVIDER=AzureAD
AAD_PROVIDER_USER=AzureAD
```

### 4.2 Optional: Configure Group-based Role Mapping

If you want to automatically assign MISP roles based on Azure AD group membership:

1. **Create Azure AD Groups**:
   - `MISP-Users` - Regular MISP users
   - `MISP-OrgAdmins` - Organization administrators
   - `MISP-SiteAdmins` - Site administrators

2. **Get Group Object IDs**:
   - In Azure Portal: **Azure AD** > **Groups** > Select group > Copy **Object ID**

3. **Configure in .env**:
   ```bash
   AAD_CHECK_GROUPS=true
   AAD_MISP_USER=12345678-1234-1234-1234-123456789abc
   AAD_MISP_ORGADMIN=23456789-2345-2345-2345-23456789abcd
   AAD_MISP_SITEADMIN=34567890-3456-3456-3456-3456789abcde
   ```

### 4.3 Restart MISP

After updating `.env`, restart MISP containers:

```bash
cd /opt/misp
docker compose down
docker compose up -d
```

## Step 5: Test Authentication

### 5.1 Access MISP Login Page

1. Navigate to your MISP URL: `https://misp.example.com`
2. You should see an **Azure AD Login** button
3. Click the button to test authentication

### 5.2 First Login

1. You'll be redirected to Microsoft login page
2. Sign in with your Azure AD credentials
3. If prompted, consent to the permissions
4. You'll be redirected back to MISP and automatically logged in

### 5.3 Verify User Account

After first login:
1. Log in to MISP as the admin user (with local password)
2. Go to **Administration** > **List Users**
3. Verify the Azure AD user was created
4. Adjust role and permissions as needed

## Step 6: Security Best Practices

### 6.1 Conditional Access Policies

Consider configuring Azure AD Conditional Access for additional security:

1. **Multi-Factor Authentication (MFA)** - Require MFA for MISP access
2. **Device Compliance** - Require managed/compliant devices
3. **Location-based Access** - Block access from untrusted locations
4. **Sign-in Risk Policies** - Block suspicious sign-ins

Configure in Azure Portal: **Azure AD** > **Security** > **Conditional Access**

### 6.2 Mixed Authentication Mode

You can enable both Azure AD and local authentication:

- Users can choose Azure AD or local login
- Useful during migration or for service accounts
- Local admin account remains available for emergency access

Mixed mode is enabled by default. Users will see both login options.

### 6.3 Monitoring and Auditing

Monitor authentication activity:

1. **Azure AD Sign-in Logs**: Azure Portal > **Azure AD** > **Sign-ins**
   - View successful/failed MISP logins
   - Identify suspicious activity
   - Track user access patterns

2. **MISP Audit Logs**: MISP > **Administration** > **Logs**
   - Track user actions within MISP
   - Correlate with Azure AD logs

## Troubleshooting

### Issue: "Redirect URI mismatch" Error

**Cause**: The redirect URI in Azure app registration doesn't match MISP configuration.

**Solution**:
1. Verify `BASE_URL` in `/opt/misp/.env` matches your actual domain
2. Verify redirect URI in Azure app registration: `https://YOUR_DOMAIN/users/login`
3. Both must match exactly (including HTTPS)

### Issue: Users Can't See Azure AD Login Button

**Cause**: Azure AD is not enabled or containers need restart.

**Solution**:
```bash
# Verify AAD_ENABLE=true in .env
grep AAD_ENABLE /opt/misp/.env

# Restart containers
cd /opt/misp
docker compose down
docker compose up -d
```

### Issue: Authentication Works but User Has No Access

**Cause**: User created but not assigned to any role or organization.

**Solution**:
1. Log in as admin
2. Go to **Administration** > **List Users**
3. Find the Azure AD user
4. Click **Edit**
5. Set appropriate role and organization

### Issue: Group-based Roles Not Working

**Cause**: Missing API permissions or incorrect group IDs.

**Solution**:
1. Verify **GroupMember.Read.All** permission is granted in Azure app
2. Verify group Object IDs in `.env` are correct
3. Check MISP logs for errors: `docker compose logs misp-core | grep -i azure`

### Issue: "Invalid Client Secret" Error

**Cause**: Client secret expired or incorrect.

**Solution**:
1. Generate new client secret in Azure Portal
2. Update `AAD_CLIENT_SECRET` in `.env`
3. Restart MISP: `docker compose down && docker compose up -d`

## Advanced Configuration

### Multi-Tenant Support

To allow users from multiple Azure AD tenants:

1. In Azure app registration, change **Supported account types** to:
   - "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"

2. Update `AAD_TENANT_ID` to `common`:
   ```bash
   AAD_TENANT_ID=common
   ```

### Custom Token Claims

To map additional Azure AD attributes to MISP:

1. In Azure app registration, go to **Token configuration**
2. Add optional claims (email, groups, UPN, etc.)
3. These will be available to MISP during authentication

## Reference

### MISP Role IDs

When configuring group-based role mapping:

- **Role ID 1** - Site Admin (full system access)
- **Role ID 2** - Org Admin (manage organization)
- **Role ID 3** - User (read/write events)
- **Role ID 4** - Publisher (publish events)
- **Role ID 5** - Sync User (API sync access)
- **Role ID 6** - Read Only (view-only access)

### Azure AD Authentication Flow

1. User clicks "Azure AD Login" on MISP
2. MISP redirects to Azure AD authorization endpoint
3. User authenticates with Azure AD
4. Azure AD returns authorization code to MISP
5. MISP exchanges code for access token
6. MISP validates token and creates/updates user account
7. User is logged into MISP

### Useful Links

- Azure Portal: https://portal.azure.com
- Azure AD Documentation: https://docs.microsoft.com/en-us/azure/active-directory/
- MISP Documentation: https://www.misp-project.org/
- MISP Docker: https://github.com/MISP/misp-docker

## Support

For issues:
1. Check MISP logs: `docker compose logs misp-core`
2. Check Azure AD sign-in logs in Azure Portal
3. Consult MISP community: https://www.misp-project.org/community/
4. Review MISP GitHub issues: https://github.com/MISP/MISP/issues

---

**tKQB Enterprises MISP Deployment**
