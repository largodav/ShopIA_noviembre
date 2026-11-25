# Despliegue público: Tailscale Funnel + GitHub Pages (`largodav/ShopIA_noviembre`)

## 1. Exponer el backend local con Tailscale Funnel (HTTPS)

### Opción A — Usando Tailscale instalado en tu Mac o Windows (recomendada)
En macOS:
```bash
chmod +x infra/tailscale/setup_funnel.sh
./infra/tailscale/setup_funnel.sh 8000
```
En Windows (PowerShell):
```powershell
tailscale funnel --bg 8000
tailscale funnel status
```
Copia la URL pública HTTPS que muestre Tailscale (ejemplo: `https://tu-mac.tailXXXX.ts.net`).

### Opción B — Usando Tailscale dentro de Docker
1. Rellena `TS_AUTHKEY` en `infra/.env` (desde el panel de administración de Tailscale → *Settings → Keys*).
2. Levanta el perfil:
   ```bash
   docker compose -f infra/docker-compose.yml --env-file infra/.env --profile tailscale up -d
   ```

---

## 2. Publicar el Frontend PWA en GitHub Pages

1. Conecta el repositorio local (`codigo/`) con GitHub y sube ramas y etiquetas:
   ```bash
   cd codigo
   git remote add origin https://github.com/largodav/ShopIA_noviembre.git
   git push -u origin main --tags
   ```
2. En GitHub (`https://github.com/largodav/ShopIA_noviembre`):
   - Ve a **Settings → Pages → Build and deployment → Source** y selecciona **GitHub Actions**.
   - Ve a **Settings → Secrets and variables → Actions → Variables** y crea:
     - `VITE_API_BASE_URL` = tu URL HTTPS de Tailscale Funnel (sin barra final, ej. `https://tu-mac.tailXXXX.ts.net`).
     - `VITE_VAPID_PUBLIC_KEY` = el valor de `VAPID_PUBLIC_KEY` de tu `infra/.env`.
     - *(Opcional)* `VITE_BASE_PATH` = `/ShopIA_noviembre/` (ya viene por defecto).
3. Lanza el workflow **Deploy ShopIA PWA to GitHub Pages** (o haz un push a `main`).
4. Tu PWA quedará disponible e instalable en:
   `https://largodav.github.io/ShopIA_noviembre/`
