# FrameLive support website

A public-safe, static, five-language website for FrameLive (映刻): product introduction, practical support, the current app privacy notice, and a bounded BinaryWolf template license notice. English, 简体中文, 繁體中文, 日本語 and 한국어 are complete pages. Language switches keep the current section. Policies, FAQs and contact links work without JavaScript. All visual artwork is original CSS; the small SVG brand mark is original. There are no external fonts, analytics, ads, cookies set by site code, or remote media embeds.

## Publication status — November 10, 2026

The owner explicitly authorized the independent public support repository and GitHub Pages publication. The public repository `wpowen/framelive-support` has been created with Issues enabled. The first GitHub Actions verification and Pages deployment succeeded. Anonymous HTTPS readback on November 10, 2026 verified all 31 served artifact files against their local SHA-256 values; `.nojekyll` is the deployment marker and is not a served content check.

- Site: https://wpowen.github.io/framelive-support/
- Support: https://wpowen.github.io/framelive-support/en/support/
- Privacy: https://wpowen.github.io/framelive-support/en/privacy/
- Contact chooser: https://github.com/wpowen/framelive-support/issues/new/choose

No support email has been supplied. Visitors can use the public GitHub Issues channel, which requires a GitHub account. Never upload private photos, Apple orders, device identifiers or unreviewed diagnostic reports. Private media is not required for support. The private App repository and its history remain private and are not part of this repository.

## Preview and verification

From the **private application checkout**, regenerate from the latest App policy sources:

```sh
python3 -B scripts/build_support_site.py
python3 -B -m unittest discover -s Tests/SupportSiteTests -v
python3 -B website/verify_public.py website/public
python3 -m http.server 8765 --bind 127.0.0.1 --directory website/public
```

Open <http://127.0.0.1:8765/>. No server is started by the generator or tests. The root is a readable English landing page, not a script redirect. Stop a manually started preview with Ctrl-C.

| Language | Product | Support | Privacy | License |
| --- | --- | --- | --- | --- |
| English | `/en/` | `/en/support/` | `/en/privacy/` | `/en/licenses/` |
| 简体中文 | `/zh-Hans/` | `/zh-Hans/support/` | `/zh-Hans/privacy/` | `/zh-Hans/licenses/` |
| 繁體中文 | `/zh-Hant/` | `/zh-Hant/support/` | `/zh-Hant/privacy/` | `/zh-Hant/licenses/` |
| 日本語 | `/ja/` | `/ja/support/` | `/ja/privacy/` | `/ja/licenses/` |
| 한국어 | `/ko/` | `/ko/support/` | `/ko/privacy/` | `/ko/licenses/` |

Each support route includes `#contact`; each locale has `/LOCALE/privacy.txt`. Links in normal pages are relative, so both localhost and the GitHub project prefix work. `404.html` uses `/framelive-support/`-prefixed navigation to work even for deeply nested missing production URLs. Preview that special page on a server mounted at the project prefix to test its production navigation.

In the future **standalone support checkout**, there is no App dependency and no build step:

```sh
python3 -B verify_public.py public
python3 -m http.server 8765 --bind 127.0.0.1 --directory public
```

## Update ownership and policy freshness

`App/Resources/PrivacyPolicy-{locale}.txt` in the private app checkout is the sole policy authority. The private-side generator reads the current five files on every build; it does not maintain another authored policy. Public `privacy.txt` files are exact byte copies, and HTML contains the exact decoded text with HTML metacharacters safely escaped. `public/build-manifest.json` binds each policy and every static file to SHA-256, without local paths, timestamps, device identifiers or App implementation details.

The private owner regenerates, runs tests, reviews all changed public files, and synchronizes the allowlisted payload below to the separate support repository after authorization. Never edit generated policy copies in the public repository: request a correction from the private owner and regenerate. A public-repository check verifies policy HTML/text equality and hashes, but cannot independently detect a newer private App policy; freshness belongs to the private owner.

Configuration is public metadata only, in `website/site-config.json` on the private side. `issues_status` is `planned` until the repository and public support channel are actually verified. It is maintenance state, not visitor-page placeholder text. Add an optional real `contact.email` only after the owner supplies and authorizes that mailbox; regenerate to add a localized mail link on support and privacy pages. No keys, tokens, SMTP credentials or workflow secrets are needed. Never store them here.

## Exact independent-repository payload

Copy **only these 37 files**, preserving the paths below relative to the new repository root. The complete path list is also provided in the private-side `website/repository-files.json` for review.

- `public/**`: exactly 32 files accepted by `verify_public.py` (22 HTML pages, five plain-text policies, three assets, `.nojekyll`, and the build manifest).
- `verify_public.py`
- `README.md` (this document)
- `.github/workflows/pages.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/ISSUE_TEMPLATE/support.yml`

Do not copy the app repository, its Git history, `.git`, `App`, `Sources`, private-side `scripts`, tests, full creation ledgers, downloaded media, build output, signing material, or credentials. The site does not require any of them. `content/`, `assets/`, `site-config.json`, `VALIDATION.md` and the private generator remain with the private owner; deployed asset copies already exist in `public/assets/`. Only `public/` is the Pages artifact. README, workflow and verifier are repository infrastructure and are not deployed.

The verifier rejects unexpected files, symlinks, broken internal routes and anchors, missing language switches, mismatched hashes/policies, scripts, embeds and obvious credential patterns. It is a useful boundary check, not proof that arbitrary text contains no possible secret. The owner still reviews the full allowlisted payload.

## GitHub Pages release procedure

The workflow is deliberately stored under `website/.github/workflows/` in the private App checkout, where GitHub Actions will not discover it. It belongs under root `.github/workflows/` **only in the separate support repository**. It also guards the exact `wpowen/framelive-support` name and public visibility.

For a new authorized deployment:

1. Create only the support repository, leaving the main App repository private. Copy the exact allowlisted files, then inspect the entire initial public diff.
2. Enable Issues. Confirm the contact chooser displays the supplied multilingual privacy warning and permits text-only submissions. Do not post a real issue as a deployment test.
3. Set Pages source to **GitHub Actions**. Restrict the `github-pages` environment to `main`; an owner review requirement can be configured there if desired.
4. Commit/push the reviewed payload to `main`, or manually dispatch `Publish FrameLive support`. The workflow validates the committed `public/`, uploads only that directory, and deploys the validated artifact. It never runs the private generator or fetches the private App repository. Permissions are read-only except the deployment job's Pages write and OIDC authentication; no long-lived secret is required.
5. Inspect the Actions result and production pages over HTTPS. Check root, all five locales, privacy plain text, support/Issues chooser, language switching, mobile layout and a deep missing URL handled by `404.html`.
6. Only after readback, change the private-side contact status from `planned` to `available`, document the actual URLs and release evidence, and regenerate when the policy or site changes. Do not describe local checks as successful production deployment.

Workflow reference: [GitHub's custom Pages workflow guide](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). The host may log visitors' IP addresses as disclosed in every language; [GitHub's privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement) governs GitHub services.

## License boundary

`public/assets/binarywolf-template-license.txt` preserves the original MIT notice, Copyright (c) 2023 BinaryWolf, for the wallpaper metadata template. All five license pages limit that explanation to the template. This is not a license for the entire app, its artwork or user media, and not a promise of system wallpaper compatibility. This handoff does not add a blanket license to the app or site.

### Prepare a reviewable standalone folder (local copy only)

From the private application checkout, after regenerating and passing tests, this command materializes the exact allowlist in a **new, empty** local folder. Replace the destination with the owner's review location; it does not initialize Git, create a GitHub repository, push or publish. It rejects an existing destination rather than merging unknown files into it.

```sh
python3 -B - /tmp/framelive-support-review <<'PY'
import json
import shutil
import subprocess
import sys
from pathlib import Path

source = Path('website')
destination = Path(sys.argv[1])
if destination.exists():
    raise SystemExit('Choose a new empty review directory; nothing was overwritten.')
files = json.loads((source / 'repository-files.json').read_text())['files']
subprocess.run([sys.executable, '-B', str(source / 'verify_public.py'), str(source / 'public')], check=True)
for name in files:
    origin = source / name
    if origin.is_symlink() or not origin.is_file():
        raise SystemExit('Invalid allowlisted source: ' + name)
for name in files:
    target = destination / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / name, target)
subprocess.run([sys.executable, '-B', 'verify_public.py', 'public'], cwd=destination, check=True)
print('Prepared', len(files), 'public-repository files for local review.')
PY
```

In that folder, inspect `README.md`, `.github/`, `verify_public.py` and `public/` before approving any external action. A deployment never uses this folder's whole tree as its artifact; the workflow uploads only `public/`.

## Verified public deployment

- Deployment workflow: https://github.com/wpowen/framelive-support/actions/runs/42771778610 (verification and deployment succeeded).
- Public repository: https://github.com/wpowen/framelive-support (37 reviewed files, independent history).
- Anonymous HTTPS content: 31 served files matched the reviewed local artifact hashes. Five localized policy pages matched their plain-text policy files.
- Anonymous Issue submission redirects to GitHub sign-in as disclosed; repository Issues are enabled and the reviewed support form is present. No issue or message was posted as a test, and a human support response was not tested.
- The application repository remains private and has no Pages site enabled.
