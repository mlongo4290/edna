# Gestione Credenziali con Variabili d'Ambiente

EDNA supporta le variabili d'ambiente per mantenere le credenziali al sicuro fuori dal file di configurazione.

## Setup

1. **Copia il file di esempio:**
   ```bash
   cp .env.example .env
   ```

2. **Modifica `.env` con le tue credenziali:**
   ```bash
   nano .env
   ```

3. **Proteggi il file:**
   ```bash
   chmod 600 .env
   ```

## Sintassi nel config.yaml

### Variabile d'ambiente obbligatoria:
```yaml
password: ${CISCO_PASSWORD}
```
Se `CISCO_PASSWORD` non è definita, l'app genererà un errore.

### Variabile con valore di default:
```yaml
username: ${CISCO_USERNAME:-admin}
```
Se `CISCO_USERNAME` non è definita, userà `admin`.

### Variabile vuota come default:
```yaml
enable_secret: ${CISCO_ENABLE_SECRET:-}
```
Se non definita, sarà una stringa vuota.

## Variabili Disponibili

### Credenziali Default
- `EDNA_DEFAULT_USERNAME` - Username di default (default: admin)
- `EDNA_DEFAULT_PASSWORD` - Password di default (default: changeme)

### Cisco
- `CISCO_USERNAME` - Username Cisco (default: admin)
- `CISCO_PASSWORD` - Password Cisco (obbligatoria)
- `CISCO_ENABLE_SECRET` - Enable secret (obbligatoria)

### MikroTik
- `MIKROTIK_USERNAME` - Username MikroTik (default: mkadministrator)
- `MIKROTIK_PASSWORD` - Password MikroTik (obbligatoria)

### Fortinet
- `FORTINET_USERNAME` - Username Fortinet (default: admin)
- `FORTINET_PASSWORD` - Password Fortinet (obbligatoria)

## Sicurezza

✅ **Fai:**
- Mantieni `.env` fuori dal version control (già in `.gitignore`)
- Usa permessi restrittivi: `chmod 600 .env`
- Usa `.env.example` come template (senza credenziali reali)

❌ **Non fare:**
- Non committare `.env` in git
- Non condividere `.env` via email/chat
- Non usare le stesse password in dev e prod

## Aggiungere Nuovi Vendor

Per aggiungere un nuovo vendor (es. Aruba):

1. **Aggiungi le variabili in `.env`:**
   ```bash
   ARUBA_USERNAME=admin
   ARUBA_PASSWORD=your_aruba_password
   ```

2. **Aggiungi il gruppo in `config.yaml`:**
   ```yaml
   groups:
     aruba:
       username: ${ARUBA_USERNAME:-admin}
       password: ${ARUBA_PASSWORD}
   ```

## Deployment in Produzione

### Con systemd:
Aggiungi le variabili nel file service:
```ini
[Service]
EnvironmentFile=/opt/edna/backend/.env
```

### Con Docker:
```bash
docker run --env-file /opt/edna/backend/.env ...
```

### Con Kubernetes:
Usa Secret:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: edna-credentials
data:
  CISCO_PASSWORD: base64_encoded_password
```
