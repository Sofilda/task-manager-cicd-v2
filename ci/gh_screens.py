"""Скриншоты страниц GitHub Actions (публичный репозиторий) для отчёта ЛР №4."""
import os

import requests
from playwright.sync_api import sync_playwright

REPO = os.environ['GITHUB_REPOSITORY']
API = f'https://api.github.com/repos/{REPO}'
H = {'Authorization': f"Bearer {os.environ['GH_TOKEN']}", 'Accept': 'application/vnd.github+json'}
OUT = 'gh-evidence'
os.makedirs(OUT, exist_ok=True)

runs = requests.get(f'{API}/actions/workflows/ci.yml/runs?per_page=20', headers=H, timeout=30).json()['workflow_runs']
runs = sorted(runs, key=lambda r: r['run_number'])
lines = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1366, 'height': 900}, locale='ru-RU')
    for r in runs:
        n = r['run_number']
        lines.append(f"ci #{n}: event={r['event']} conclusion={r['conclusion']} sha={r['head_sha'][:7]} url={r['html_url']}")
        page.goto(r['html_url'], wait_until='networkidle')
        page.wait_for_timeout(3000)
        page.screenshot(path=f'{OUT}/ci_run{n}_summary.png', full_page=True)
        jobs = requests.get(f"{API}/actions/runs/{r['id']}/jobs", headers=H, timeout=30).json()['jobs']
        for ji, j in enumerate(jobs):
            step = next((s for s in j['steps'] if s['name'] == 'Build and test'), None)
            lines.append(f"  job {j['name']}: {j['conclusion']}; steps: " +
                         ', '.join(f"{s['number']}:{s['name']}={s['conclusion']}" for s in j['steps']))
            page.goto(j['html_url'], wait_until='networkidle')
            page.wait_for_timeout(3000)
            page.screenshot(path=f'{OUT}/ci_run{n}_job{ji}.png')
            if step:
                page.goto(f"{j['html_url']}#step:{step['number']}:1", wait_until='networkidle')
                page.wait_for_timeout(6000)
                for needle in ['Tests run:', 'Rule violated', 'BUILD']:
                    loc = page.get_by_text(needle).last
                    if loc.count():
                        loc.scroll_into_view_if_needed()
                        page.wait_for_timeout(800)
                        page.screenshot(path=f"{OUT}/ci_run{n}_job{ji}_step_{needle.split()[0].strip(':').lower()}.png")
            log = requests.get(f"{API}/actions/jobs/{j['id']}/logs", headers=H, timeout=60)
            if log.ok:
                open(f'{OUT}/ci_run{n}_job{ji}_log.txt', 'w', encoding='utf-8').write(log.text)
    jr = requests.get(f'{API}/actions/workflows/jenkins-demo.yml/runs?per_page=5', headers=H, timeout=30).json()['workflow_runs']
    if jr:
        page.goto(jr[0]['html_url'], wait_until='networkidle')
        page.wait_for_timeout(3000)
        page.screenshot(path=f'{OUT}/jenkins_demo_run.png', full_page=True)
        lines.append(f"jenkins-demo #{jr[0]['run_number']}: {jr[0]['conclusion']} url={jr[0]['html_url']}")
    page.goto(f'https://github.com/{REPO}/actions', wait_until='networkidle')
    page.wait_for_timeout(3000)
    page.screenshot(path=f'{OUT}/actions_list.png')
    browser.close()
open(f'{OUT}/runs.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
