# Server recon — AWS box hosting mirrorborn.us (44.248.235.76)

Read-only inspection, 2026-10-31 (~21:10–21:15 CDT), via aletheia-core hop
(Muse VM → wbic16@100.88.154.1 → wbic16@44.248.235.76). Nothing was changed
on either server. Hostname `ip-172-30-1-197`, user `wbic16`.
Note: `sudo -n` fails ("a password is required"), so root-only data
(`/etc/letsencrypt/live/*` contents) could not be read — flagged where relevant.

## Box basics
- OS: Ubuntu 24.04.5 LTS (Noble), kernel 7.0.0-1014-aws, x86_64
- Disk: 991 GB root, 42 GB used, **950 GB free (5%)**
- systemd 255, system state `running`
- python3: **3.12.3** at /usr/bin/python3

## 1. nginx
- **nginx 1.24.0 (Ubuntu)** at /usr/sbin/nginx; /etc/nginx present, standard layout.
- sites-enabled (22 vhosts): apertureshift.com, athenaeum.ai, edit.phext.io,
  hb-aeromotive.com, lattice.ai, mc.phext.io, mirrorborn.us, principia.ai,
  quickfork.net, singularitywatch.org, sotafomo.com, sq.mirrorborn.us, all the
  staging.* subdomains (incl. **staging.bickfordllamaranch.com**), visionquest.me,
  wishnode.net.
- **mirrorborn.us pattern** (sites-available/mirrorborn.us): port 80 → 301 to
  HTTPS with a `/.well-known/acme-challenge/` exception rooted at the docroot;
  port 443 `ssl http2`, `root /sites/web/mirrorborn.us`, Let's Encrypt cert,
  TLSv1.2/1.3, HSTS preload + nosniff/SAMEORIGIN/XSS/Referrer-Policy headers,
  `try_files $uri $uri/ =404`, 5-minute expiry on pages, plus proxy locations
  to local upstreams (3001 arena, 3002 sq_cloud, 3333 mental-space).
- **Docroot convention: `/sites/web/<domain>/`** — confirmed by `ls /sites/web/`:
  apertureshift.com, bickfordllamaranch.com, hb-aeromotive.com, mirrorborn.us,
  quickfork.net, singularitywatch.org, sotafomo.com, visionquest.me,
  wishnode.net, and staging.* mirrors of most of them.
- **Apache: NOT on this box.** No apache2/apachectl binary, no /etc/apache2,
  service inactive, no processes. The Apache/2.4.62 response the public
  bickfordllamaranch.com currently serves therefore comes from **somewhere
  else** (not this AWS box) — earlier recon showed that public page (210 B,
  style.css + llamas.webp) also differs from anything on disk here.
- **Bickford on this box already:**
  - `/sites/web/bickfordllamaranch.com/` exists but holds only a **113-byte
    placeholder index.html** ("<h1>Bickford Llama Ranch</h1>", no css/img).
  - `/etc/nginx/sites-available/bickfordllamaranch.com` exists (Jun 12):
    full mirrorborn-style HTTPS vhost, root /sites/web/bickfordllamaranch.com,
    cert path /etc/letsencrypt/live/bickfordllamaranch.com/ — **but it is NOT
    in sites-enabled**, so nginx is not serving it.
  - `/sites/web/staging.bickfordllamaranch.com/` is a fuller ranch site
    (index/about/contact/for-sale/herd.html, style.css, img/, Oct 23,
    root-owned), served by an **enabled HTTP-only** vhost (no TLS, noindex),
    header notes it was managed by a `deploy-ranch.sh`.
  - **No admin.bickfordllamaranch.com anything**: no vhost, no docroot, no cert.

## 2. certbot / certificates
- **certbot 2.9.0** (/usr/bin/certbot, python3-certbot-nginx installed).
- TLS source for all vhosts: Let's Encrypt via certbot, certs referenced as
  `/etc/letsencrypt/live/<name>/fullchain.pem`.
- Certificate names known from `/etc/letsencrypt/renewal/` (readable):
  apertureshift.com (+ -0001), edit.phext.io, hb-aeromotive.com, mc.phext.io,
  mirrorborn.us (+ -0001), quickfork.net, singularitywatch.org, sotafomo.com,
  sq.mirrorborn.us, staging.{apertureshift, mirrorborn.us, quickfork,
  singularitywatch, sotafomo, visionquest, wishnode}, visionquest.me, wishnode.net.
- **No renewal config for bickfordllamaranch.com or staging.bickfordllamaranch.com**
  — despite the (disabled) public vhost referencing a bickford cert. So a
  bickford cert either never existed here or is not under certbot management
  on this box; treat TLS for the ranch domains as **not yet set up**.
- **Expiry dates could not be obtained**: `certbot certificates` needs root,
  non-interactive sudo requires a password, and /etc/letsencrypt/live is
  root-only. (Dates seen via this VM's egress proxy are the proxy's own
  intercept CA, not the real certs — discarded.) Getting expiries needs an
  interactive sudo session on the box.

## 3. SQ
- **SQ is installed**: `/usr/local/bin/sq` (14 MB, Feb 13 2026). A probe run
  in /tmp printed **"SQ v0.5.6"** — note this is *older* than the v0.6.0 used
  in local prototype testing; the /api/v2 surface should be re-checked against
  v0.5.6 before deploy, or SQ upgraded on the box.
- Already running (systemd): `sq-router.service` on **port 1337**
  (multi-tenant, /etc/sq/tenants.json), `sq-backend-wbic16.service` on **1338**,
  `sq-backend-demo.service` on **1339**; plus phext-edit (127.0.0.1:8080) and
  phext-lanes (127.0.0.1:7841). SQ data dirs live under /var/lib/sq/tenants/.
  A new ranch instance is therefore a *new* unit/port, not the first SQ here.
- **Port 18765 is FREE** (verified no listener; also re-verified after the
  version probe on 18799 exited — nothing left running).
- Listening ports overall: 22, 80, 443, 1337–1339 (SQ), 3333, 7841 (localhost),
  8080 (localhost).

## 4. Mail
- **Nothing installed**: no postfix, sendmail, msmtp, exim4, ssmtp, nullmailer,
  not even mail/mailx. No /etc/postfix/main.cf, no /etc/msmtprc, no ~/.msmtprc,
  no /etc/exim4. **There is currently no way for this box to send email.**
  The reminder module will need an SMTP path added from zero: either install
  msmtp/postfix, or have remind.py speak SMTP directly to an external provider
  (stdlib smtplib — no install needed, but needs provider creds in env config).

## 5. Basic Auth tooling
- **htpasswd: NOT installed** (apache2-utils absent, consistent with no Apache).
- **openssl 3.0.13 IS present** at /usr/bin/openssl — sufficient by itself:
  `openssl passwd -apr1` generates hashes nginx's auth_basic accepts, so no
  package install is strictly required for Basic Auth.
- /etc/nginx exists with standard includes (fastcgi/proxy/scgi/uwsgi params).

## 6. Implications for the deploy plan
1. Follow the mirrorborn pattern exactly: docroot `/sites/web/<domain>/`,
   certbot nginx plugin, HSTS header set — all proven on this box.
2. admin.bickfordllamaranch.com is greenfield: new docroot
   `/sites/web/admin.bickfordllamaranch.com`, new vhost, new certbot cert
   (needs the DNS A record pointing here first), Basic Auth via openssl-
   generated htpasswd file.
3. The disabled public bickford vhost + placeholder docroot suggest a prior
   half-start; enabling/replacing it is a decision for Will, and the live
   public site is hosted elsewhere today, so DNS currently points elsewhere.
4. SQ version gap (box v0.5.6 vs local v0.6.0) is the one real compatibility
   check before deploying the admin app against the box.
5. Email reminders need a from-scratch SMTP choice — nothing to inherit.
