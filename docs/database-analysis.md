# EncryptU Database Architecture Analysis

## Current Database Usage

### Web Application Database
- **Primary Database**: PostgreSQL
- **ORM**: Prisma
- **Connection**: Through environment variable `DATABASE_URL`
- **Models Implemented**: User, PasswordEntry, Category, ShareLink
- **Location**: `web/prisma/schema.prisma`

### Desktop Application Database
- **Primary Database**: SQLite
- **Location**: `desktop/controllers/src/database/encryptu_api.db`
- **Authentication**: Argon2 password hashing
- **Features**: Local data storage with cloud synchronization

## Alternative Relational Database Models

### 1. Enhanced Web Application Model

```sql
-- Enhanced User Management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(32),
    account_status VARCHAR(20) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT false,
    email_verification_token VARCHAR(100),
    password_reset_token VARCHAR(100),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Enhanced Password Management
CREATE TABLE password_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    username VARCHAR(100),
    password_encrypted TEXT NOT NULL,
    url TEXT,
    notes TEXT,
    tags TEXT[], -- Array of tags
    custom_fields JSONB, -- Dynamic custom fields
    strength_score INTEGER CHECK (strength_score >= 0 AND strength_score <= 100),
    last_used TIMESTAMP,
    is_favorite BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,
    auto_lock_minutes INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Categories and Organization
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#3b82f6',
    icon VARCHAR(50),
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Password History for Recovery
CREATE TABLE password_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    password_entry_id UUID NOT NULL REFERENCES password_entries(id) ON DELETE CASCADE,
    old_password_encrypted TEXT NOT NULL,
    changed_by UUID NOT NULL REFERENCES users(id),
    change_reason VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Secure Sharing System
CREATE TABLE share_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    password_entry_id UUID NOT NULL REFERENCES password_entries(id) ON DELETE CASCADE,
    token VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    max_access_count INTEGER,
    access_count INTEGER DEFAULT 0,
    require_authentication BOOLEAN DEFAULT true,
    allowed_ips TEXT[], -- Array of allowed IP addresses
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Access Logging
CREATE TABLE access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Enhanced Desktop Application Model

```sql
-- Desktop-specific local database schema
CREATE TABLE local_settings (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    data_type VARCHAR(20) DEFAULT 'string',
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action VARCHAR(20) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
    table_name VARCHAR(50) NOT NULL,
    record_id TEXT NOT NULL,
    data TEXT, -- JSON data for the operation
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'synced', 'failed'
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_retry_at TIMESTAMP
);

CREATE TABLE cached_passwords (
    id TEXT PRIMARY KEY, -- Corresponds to web password_entry.id
    title TEXT NOT NULL,
    username TEXT,
    password_encrypted TEXT NOT NULL,
    url TEXT,
    notes TEXT,
    category_name TEXT,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_dirty BOOLEAN DEFAULT false -- Mark for sync when modified locally
);
```

### 3. Audit and Compliance Model

```sql
-- Security Audit Trail
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    risk_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Compliance and Policy Management
CREATE TABLE security_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    policy_name VARCHAR(100) NOT NULL,
    settings JSONB NOT NULL, -- Policy configuration
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Data Retention Rules
CREATE TABLE retention_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    entity_type VARCHAR(50) NOT NULL,
    retention_days INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'DELETE', 'ARCHIVE', 'ANONYMIZE'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Team and Organization Model

```sql
-- Organization Management
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(100) UNIQUE,
    settings JSONB,
    subscription_plan VARCHAR(50),
    subscription_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Team Membership
CREATE TABLE team_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- 'owner', 'admin', 'member', 'viewer'
    permissions JSONB,
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMP,
    joined_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);

-- Shared Vaults
CREATE TABLE shared_vaults (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    settings JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vault_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vault_id UUID NOT NULL REFERENCES shared_vaults(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_level VARCHAR(20) NOT NULL, -- 'read', 'write', 'admin'
    granted_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(vault_id, user_id)
);
```

## Database Choice Recommendations

### For Web Application
- **Current Choice**: PostgreSQL ✅ Excellent choice
- **Alternative**: MySQL 8.0+ (Good performance, wide support)
- **Alternative**: SQLite (For smaller deployments)

### For Desktop Application
- **Current Choice**: SQLite ✅ Perfect for desktop
- **Alternative**: Embedded PostgreSQL (For more complex desktop needs)
- **Alternative**: LevelDB (For key-value storage needs)

## Migration Strategy

### Web Application
1. Set up Prisma with PostgreSQL
2. Create migration scripts
3. Implement data access layer
4. Add database seeding for development

### Desktop Application
1. Maintain SQLite for local storage
2. Implement cloud sync with PostgreSQL
3. Add conflict resolution
4. Implement backup/restore functionality

## Performance Considerations

### Indexing Strategy
```sql
-- Performance indexes
CREATE INDEX idx_password_entries_user_id ON password_entries(user_id);
CREATE INDEX idx_password_entries_category ON password_entries(category_id);
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_share_links_token ON share_links(token);
CREATE INDEX idx_access_logs_user_id ON access_logs(user_id);
CREATE INDEX idx_access_logs_created_at ON access_logs(created_at);
```

### Connection Pooling
- Web: Use connection pooling (PgBouncer, etc.)
- Desktop: Single connection with proper transaction management

## Security Best Practices

1. **Encryption at Rest**
   - Database-level encryption
   - Application-level encryption for sensitive fields

2. **Access Control**
   - Role-based permissions
   - Audit logging
   - Session management

3. **Data Validation**
   - Input sanitization
   - Constraint validation
   - Type checking

4. **Backup Strategy**
   - Automated backups
   - Point-in-time recovery
   - Cross-region replication

## Conclusion

Both applications are using appropriate databases for their use cases:
- **Web Application**: PostgreSQL provides scalability and advanced features
- **Desktop Application**: SQLite offers lightweight, file-based storage

The enhanced models provide a roadmap for advanced features like team collaboration, audit trails, and compliance requirements.