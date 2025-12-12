"""Authentication module with JWT, local users, and LDAP support"""
from datetime import datetime, timedelta
from typing import Optional
from logging import getLogger
from ldap import initialize, set_option, filter, OPT_NETWORK_TIMEOUT, OPT_REFERRALS, OPT_X_TLS_REQUIRE_CERT, OPT_X_TLS_NEVER, INVALID_CREDENTIALS, SCOPE_SUBTREE
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = getLogger(__name__)

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

class TokenData(BaseModel):
    username: str
    role: str = "user"


class AuthService:
    """Authentication service with local and LDAP support"""
    
    def __init__(self, config, db=None):
        self.config = config
        self.db = db
        self.jwt_secret = config.get('jwt', {}).get('secret_key')
        self.jwt_algorithm = config.get('jwt', {}).get('algorithm', 'HS256')
        self.jwt_expire_minutes = config.get('jwt', {}).get('expire_minutes', 1440)
        
        # LDAP settings
        ldap_cfg = config.get('ldap', {})
        self.ldap_enabled = ldap_cfg.get('enabled', False)
        
        # Parse servers (can be single item or list)
        servers = ldap_cfg.get('servers', [])
        if isinstance(servers, str):
            self.ldap_servers = [s.strip() for s in servers.split(',')]
        else:
            self.ldap_servers = servers if isinstance(servers, list) else [servers]
        
        self.ldap_base_dn = ldap_cfg.get('base_dn')
        self.ldap_search_filter = ldap_cfg.get('search_filter', '(uid={username})')
        self.ldap_bind_dn = ldap_cfg.get('bind_dn')
        self.ldap_bind_password = ldap_cfg.get('bind_password')
        self.ldap_timeout = ldap_cfg.get('timeout', 5)
        
        # TLS settings
        tls_cfg = ldap_cfg.get('tls', {})
        self.ldap_tls_verify = tls_cfg.get('verify_cert', False)
        self.ldap_tls_ca_path = tls_cfg.get('ca_cert_path')
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        """Verify plain password against bcrypt hash"""
        return pwd_context.verify(plain, hashed)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password with bcrypt"""
        return pwd_context.hash(password)
    
    def authenticate_local(self, username: str, password: str) -> Optional[TokenData]:
        """Authenticate against local users in database"""
        if not self.db:
            return None
        
        user = self.db.get_user(username)
        if not user:
            return None
        
        if self.verify_password(password, user.get('password_hash', '')):
            return TokenData(username=username, role=user.get('role', 'user'))
        
        return None
    
    def _get_ldap_connection(self, server_uri: str):
        """Create and configure LDAP connection"""
        # Set global TLS option before creating connection
        if not self.ldap_tls_verify:
            set_option(OPT_X_TLS_REQUIRE_CERT, OPT_X_TLS_NEVER)
        
        conn = initialize(server_uri)
        conn.set_option(OPT_NETWORK_TIMEOUT, self.ldap_timeout)
        conn.set_option(OPT_REFERRALS, 0)
        
        return conn
    
    def authenticate_ldap(self, username: str, password: str) -> Optional[TokenData]:
        """Authenticate against LDAP servers with failover support"""
        if not self.ldap_enabled or not self.ldap_servers:
            return None
        
        # Try each server in sequence (failover)
        for server_uri in self.ldap_servers:
            try:
                logger.debug(f"Trying LDAP server: {server_uri}")
                
                # Create connection
                conn = self._get_ldap_connection(server_uri)
                
                # Bind with service account if provided (for search)
                if self.ldap_bind_dn and self.ldap_bind_password:
                    try:
                        conn.simple_bind_s(self.ldap_bind_dn, self.ldap_bind_password)
                    except INVALID_CREDENTIALS:
                        logger.warning(f"LDAP service account bind failed for {server_uri}")
                        conn.unbind_s()
                        continue
                
                # Search for user with custom filter
                search_filter = self.ldap_search_filter.format(username=filter.escape_filter_chars(username))
                logger.debug(f"LDAP search filter: {search_filter}")
                
                results = conn.search_s(self.ldap_base_dn, SCOPE_SUBTREE, search_filter)
                
                if not results or results[0][0] is None:
                    logger.debug(f"LDAP user not found: {username} on {server_uri}")
                    conn.unbind_s()
                    continue
                
                user_dn = results[0][0]
                logger.debug(f"Found user DN: {user_dn}")
                
                # Try to bind as the user with provided password
                try:
                    user_conn = self._get_ldap_connection(server_uri)
                    user_conn.simple_bind_s(user_dn, password)
                    user_conn.unbind_s()
                    
                    logger.info(f"LDAP authentication successful for {username}")
                    return TokenData(username=username, role="user")
                except INVALID_CREDENTIALS:
                    logger.warning(f"LDAP invalid credentials for {username}")
                    conn.unbind_s()
                    continue
                except Exception as e:
                    logger.warning(f"LDAP user bind error for {username}: {e}")
                    conn.unbind_s()
                    continue
            
            except Exception as e:
                logger.warning(f"LDAP connection error for {server_uri}: {e}")
                continue
        
        return None
    
    def authenticate(self, username: str, password: str) -> Optional[TokenData]:
        """Authenticate user with local or LDAP"""
        # Try local first
        token_data = self.authenticate_local(username, password)
        if token_data:
            return token_data
        
        # Try LDAP
        if self.ldap_enabled:
            token_data = self.authenticate_ldap(username, password)
            if token_data:
                return token_data
        
        return None
    
    def create_access_token(self, username: str, role: str = "user") -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_expire_minutes)
        to_encode = {
            "sub": username,
            "role": role,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token and return token data"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            username: str = payload.get("sub")
            role: str = payload.get("role", "user")
            if username is None:
                return None
            return TokenData(username=username, role=role)
        except JWTError:
            return None
