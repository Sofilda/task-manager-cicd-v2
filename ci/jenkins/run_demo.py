"""Запускает контрольные сценарии варианта 2 в Jenkins и снимает скриншоты интерфейса.

Результат: каталог evidence/ — журналы сборок (logs/), сводка (summary.json)
и скриншоты страниц Jenkins (screenshots/).
"""
import json
import os
import time

import requests
from playwright.sync_api import sync_playwright

J = 'http://localhost:8080'
JOB = 'Task-Manager-Variant2'
OUT = 'evidence'
os.makedirs(f'{OUT}/logs', exist_ok=True)
os.makedirs(f'{OUT}/screenshots', exist_ok=True)

SCENARIOS = [
    {'BRANCH': 'main', 'CHECK_MODE': 'FULL'},
    {'BRANCH': 'main', 'CHECK_MODE': 'UNIT'},
    {'BRANCH': 'main', 'CHECK_MODE': 'COMPILE'},
    {'BRANCH': 'feature/extra-test', 'CHECK_MODE': 'FULL'},
    {'BRANCH': 'no-such-branch', 'CHECK_MODE': 'FULL'},
    {'BRANCH': 'main; echo hacked', 'CHECK_MODE': 'FULL'},
]


def trigger(params):
    r = requests.post(f'{J}/job/{JOB}/buildWithParameters', params=params, timeout=30)
    r.raise_for_status()
    queue_url = r.headers['Location'].rstrip('/') + '/api/json'
    for _ in range(600):
        q = requests.get(queue_url, timeout=30).json()
        if q.get('executable'):
            return q['executable']['number']
        time.sleep(2)
    raise RuntimeError('build did not leave the queue')


def wait_build(n):
    for _ in range(900):
        b = requests.get(f'{J}/job/{JOB}/{n}/api/json', timeout=30).json()
        if not b['building']:
            return b
        time.sleep(3)
    raise RuntimeError(f'build {n} did not finish')


summary = []
for params in SCENARIOS:
    n = trigger(params)
    print(f'Build #{n} started with {params}', flush=True)
    b = wait_build(n)
    log = requests.get(f'{J}/job/{JOB}/{n}/consoleText', timeout=60).text
    with open(f'{OUT}/logs/build-{n}.txt', 'w', encoding='utf-8') as f:
        f.write(log)
    tests = None
    t = requests.get(f'{J}/job/{JOB}/{n}/testReport/api/json?tree=failCount,passCount,skipCount', timeout=30)
    if t.ok:
        tests = t.json()
    stages = None
    s = requests.get(f'{J}/job/{JOB}/{n}/wfapi/describe', timeout=30)
    if s.ok:
        stages = [(st['name'], st['status'], st['durationMillis']) for st in s.json().get('stages', [])]
    item = {'number': n, 'params': params, 'result': b['result'], 'duration_ms': b['duration'],
            'description': b.get('description'), 'tests': tests, 'stages': stages,
            'artifacts': [a['relativePath'] for a in b.get('artifacts', [])]}
    summary.append(item)
    print(json.dumps(item, ensure_ascii=False), flush=True)

with open(f'{OUT}/summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

FIND_JS = """([needle, first]) => {
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n, hit = null;
  while ((n = w.nextNode())) { if (n.textContent.includes(needle)) { hit = n; if (first) break; } }
  if (!hit) return false;
  hit.parentElement.scrollIntoView({block: 'center'});
  return true;
}"""


def shot(page, name, url, needle=None, first=True, wait=1500):
    page.goto(J + url, wait_until='networkidle')
    page.wait_for_timeout(wait)
    if needle:
        ok = page.evaluate(FIND_JS, [needle, first])
        print(f'{name}: needle {needle!r} found={ok}', flush=True)
        page.wait_for_timeout(500)
    page.screenshot(path=f'{OUT}/screenshots/{name}.png')


nums = [s['number'] for s in summary]
job = f'/job/{JOB}'
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1366, 'height': 768}, locale='ru-RU')
    shot(page, '01_build_with_parameters', job + '/build?delay=0sec')
    shot(page, '02_b1_full_checkout', f'{job}/{nums[0]}/console', 'Проверяется commit')
    shot(page, '03_b1_full_tests', f'{job}/{nums[0]}/console', 'Tests run:', first=False)
    shot(page, '04_b1_test_report', f'{job}/{nums[0]}/testReport/')
    shot(page, '05_b2_unit', f'{job}/{nums[1]}/console', 'Tests run:', first=False)
    shot(page, '06_b3_compile', f'{job}/{nums[2]}/console', 'Unit Tests', first=False)
    shot(page, '07_b4_feature_checkout', f'{job}/{nums[3]}/console', 'Проверяется commit')
    shot(page, '08_b4_feature_tests', f'{job}/{nums[3]}/console', 'Tests run: 15')
    shot(page, '09_b4_test_report', f'{job}/{nums[3]}/testReport/')
    shot(page, '10_b5_no_branch', f'{job}/{nums[4]}/console', "Couldn't find any revision")
    shot(page, '11_b6_invalid', f'{job}/{nums[5]}/console', 'Недопустимое имя ветки')
    shot(page, '12_job_page', job + '/', wait=4000)
    browser.close()
print('done', flush=True)
