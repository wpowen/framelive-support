#!/usr/bin/env python3
"""Standalone checks for the future public repository; no private App dependency."""
import argparse
import hashlib
import json
import posixpath
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

LOCALES = ('en', 'zh-Hans', 'zh-Hant', 'ja', 'ko')
PAGES = ('', 'support/', 'privacy/', 'licenses/')
EXPECTED = {'index.html', '404.html', '.nojekyll', 'build-manifest.json',
            'assets/style.css', 'assets/icon.svg', 'assets/binarywolf-template-license.txt'}
EXPECTED.update(lang+'/'+page+'index.html' for lang in LOCALES for page in PAGES)
EXPECTED.update(lang+'/privacy.txt' for lang in LOCALES)
SECRET = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|/Users/|/Volumes/|\b(?:AKIA)[A-Z0-9]{16}\b')


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.policy = []
        self.in_policy = False
        self.lang = None
        self.languages = {}
        self.summaries = 0
        self.h1 = 0
        self.text = []
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag in ('script', 'iframe', 'form', 'object', 'embed', 'video', 'audio', 'base'):
            raise ValueError('Non-static or embedded content: '+tag)
        if any(name.lower().startswith('on') for name in attrs):
            raise ValueError('Executable HTML handler')
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                raise ValueError('Duplicate HTML id')
            self.ids.add(attrs['id'])
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'pre' and attrs.get('id') == 'app-privacy':
            self.in_policy = True
        if tag == 'summary':
            self.summaries += 1
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a' and 'hreflang' in attrs:
            self.languages[attrs['hreflang']] = attrs.get('href')
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append((tag, attrs[key]))
        if 'srcset' in attrs or 'style' in attrs:
            raise ValueError('Unreviewed inline asset reference')

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.in_policy = False

    def handle_data(self, data):
        self.text.append(data)
        if self.in_policy:
            self.policy.append(data)


def target_for(current, url, site_url):
    parsed = urlsplit(url)
    base = urlsplit(site_url)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in ('https', 'mailto') or parsed.username or parsed.password:
            raise ValueError('Unsafe URL scheme or credentials')
        if parsed.scheme == 'mailto':
            if parsed.query or parsed.fragment or '\n' in unquote(url) or '\r' in unquote(url):
                raise ValueError('Unsafe mail URL')
            return None
        if parsed.netloc != base.netloc or not parsed.path.startswith(base.path):
            # External navigation is allowed; external assets are rejected by verify.
            if parsed.query or parsed.fragment:
                raise ValueError('Unreviewed external URL parameters')
            return None
        path = parsed.path[len(base.path):]
    elif parsed.path.startswith('/'):
        if not parsed.path.startswith(base.path):
            raise ValueError('Link escapes Pages project prefix')
        path = parsed.path[len(base.path):]
    elif not parsed.path:
        path = current
    else:
        path = posixpath.normpath(posixpath.join(posixpath.dirname(current), unquote(parsed.path)))
    if parsed.query or path.startswith('../'):
        raise ValueError('Link escapes output or uses query parameters')
    if not path:
        path = 'index.html'
    if path.endswith('/') or parsed.path.endswith('/') and path != 'index.html' or path == '.':
        path = path.rstrip('/') + '/index.html' if path != '.' else 'index.html'
    return path, unquote(parsed.fragment)


def verify(root):
    root = Path(root)
    if root.is_symlink():
        raise ValueError('Symlink output root')
    all_entries = list(root.rglob('*'))
    if any(p.is_symlink() for p in all_entries):
        raise ValueError('Symlinks are not public artifacts')
    actual = {p.relative_to(root).as_posix() for p in all_entries if p.is_file()}
    if actual != EXPECTED:
        raise ValueError('Public file allowlist mismatch: missing=%s extra=%s' % (sorted(EXPECTED-actual), sorted(actual-EXPECTED)))
    manifest = json.loads((root/'build-manifest.json').read_text(encoding='utf-8'))
    if manifest['schema_version'] != 1 or set(manifest['files']) != EXPECTED-{'build-manifest.json'}:
        raise ValueError('Invalid public manifest')
    pages = {}
    for name in sorted(actual):
        data = (root/name).read_bytes()
        if name != 'build-manifest.json' and hashlib.sha256(data).hexdigest() != manifest['files'][name]:
            raise ValueError('Artifact hash mismatch: '+name)
        text = data.decode('utf-8')
        if SECRET.search(text):
            raise ValueError('Possible private content in '+name)
        if name.endswith('.html'):
            pages[name] = Page(text)
    for name, page in pages.items():
        if page.lang not in LOCALES or page.h1 != 1 or set(page.languages) != set(LOCALES):
            raise ValueError('Missing document language, heading or language switch: '+name)
        for tag, url in page.links:
            target = target_for(name, url, manifest['site_url'])
            if target is None:
                if tag != 'a' and tag != 'link':
                    raise ValueError('External media asset: '+name)
                if tag == 'link' and not url.startswith(manifest['site_url']):
                    raise ValueError('External stylesheet or link resource')
                continue
            path, fragment = target
            if path not in actual:
                raise ValueError('Broken internal link: '+name+' -> '+url)
            if fragment and (path not in pages or fragment not in pages[path].ids):
                raise ValueError('Broken fragment: '+name+' -> '+url)
    if set(manifest['policy_sha256']) != set(LOCALES):
        raise ValueError('Missing policy provenance')
    for lang in LOCALES:
        raw = (root/lang/'privacy.txt').read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest['policy_sha256'][lang]:
            raise ValueError('Policy hash mismatch')
        if ''.join(pages[lang+'/privacy/index.html'].policy) != raw.decode('utf-8'):
            raise ValueError('HTML policy differs from plain-text policy')
        support = pages[lang+'/support/index.html']
        if support.summaries < 9 or 'contact' not in support.ids or 'contact-warning' not in support.ids:
            raise ValueError('Missing FAQ or safe contact')
    css = (root/'assets/style.css').read_text(encoding='utf-8')
    if re.search(r'@import|url\s*\(|expression\s*\(', css, re.I):
        raise ValueError('Unexpected CSS asset request or executable expression')
    svg = (root/'assets/icon.svg').read_text(encoding='utf-8')
    if re.search(r'<script|<foreignObject|\bhref\s*=|\bon\w+\s*=', svg, re.I):
        raise ValueError('Unexpected executable or external SVG content')
    return len(actual)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', type=Path, default=Path(__file__).resolve().parent/'public')
    args = parser.parse_args()
    print('Verified %d allowlisted static files; links, policy consistency, hashes and public boundaries passed.' % verify(args.directory))
