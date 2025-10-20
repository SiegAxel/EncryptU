
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


## Normas ISO y Estándares Aplicables

* 1. ISO/IEC 27001 – Gestión de seguridad de la información


* 2. ISO/IEC 27002 – Controles de seguridad de la información


* 3. ISO/IEC 25010 – Calidad del producto de software


* 4. ISO/IEC 12207 – Ciclo de vida del software


* 5. ISO 9001 – Gestión de la calidad


* 6. ISO/IEC 29100 – Marco de privacidad de la información


* 7. ISO 26000 – Responsabilidad social


* 8. OWASP ASVS – Application Security Verification Standard (no es ISO, pero altamente relevante)


* 9. OWASP Top 10 – Principales riesgos de seguridad en aplicaciones web