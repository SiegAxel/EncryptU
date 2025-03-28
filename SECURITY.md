
---

### 📄 **3. SECURITY.md** (Política de Seguridad)

```markdown
# 🔒 Política de Seguridad

## 🚨 Reportar Vulnerabilidades
Si encuentras una vulnerabilidad, **NO abras un issue público**. Envía un correo a `security@dominio.com` con:
- Descripción detallada del problema.
- Pasos para reproducir.
- Impacto potencial.

Te responderemos en ≤48 horas y trabajaremos contigo para resolverlo.

## 🛡️ Prácticas de Seguridad en EncryptU
- **Claves Maestras**: Nunca se almacenan ni transmiten.
- **Encriptación**: AES-256-GCM con autenticación integrada.
- **Derivación de Claves**: PBKDF2 con 310,000 iteraciones (NIST recomendado).
- **Auditorías**: Revisiones de código semestrales por terceros.

## ⚠️ Advertencias de Diseño
- **Recuperación de Clave**: Imposible por diseño. Los usuarios deben recordar su clave maestra.
- **Offline First**: Sin servidores centrales. Todos los datos son locales.