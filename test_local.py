"""Smoke test: frontend local ingest, duplicate avoidance, wiki query, export."""
import os
import subprocess
import time
from pathlib import Path
from zipfile import ZipFile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
server=subprocess.Popen(['python','-m','http.server','8765','--directory',str(ROOT/'docs')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(accept_downloads=True)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        html=(ROOT/'docs'/'index.html').read_text()
        import re
        html=re.sub(r'<script[^>]*></script>', '', html)
        page.set_content(html)
        page.evaluate("Object.defineProperty(window.crypto, 'randomUUID', {value: () => 'test-' + Math.random().toString(36).slice(2)})")
        page.add_script_tag(content=Path('/usr/local/slides_js/node_modules/jszip/dist/jszip.min.js').read_text())
        page.add_script_tag(content=(ROOT/'docs'/'app.js').read_text())
        page.on('dialog',lambda d:d.accept('普通生物學') if d.type=='prompt' else d.accept())
        page.locator('#addSubject').click()
        page.locator('#files').set_input_files(str(ROOT/'examples'/'demo-lesson.txt'))
        page.wait_for_timeout(800)
        print('STATUS',repr(page.locator('#status').inner_text()),'ERRORS',errors,flush=True)
        page.locator('#ingest').click()
        assert '1 個主題頁' in page.locator('#wikiSummary').inner_text()
        page.locator('.wiki-page summary').first.click()
        assert '細胞膜' in page.locator('#wikiPages').inner_text()
        n1=page.locator('#wikiPages').text_content().count('原文摘錄')
        page.locator('#ingest').click()
        assert page.locator('#wikiPages').text_content().count('原文摘錄')==n1
        page.locator('#question').fill('細胞膜')
        page.locator('#ask').click()
        assert 'demo-lesson.txt' in page.locator('#answer').inner_text()
        with page.expect_download() as d:
            page.locator('#wikiExport').click()
        item=d.value
        assert item.suggested_filename=='普通生物學_Wiki知識庫.zip'
        item.save_as('/tmp/coursenotes-wiki-test.zip')
        with ZipFile('/tmp/coursenotes-wiki-test.zip') as z:
            names=z.namelist()
            assert any(x.endswith('wiki/index.md') for x in names)
            assert any(x.endswith('wiki/pages/course-overview.md') for x in names)
            assert any(x.endswith('wiki/log.md') for x in names)
        page.locator('#generate').click()
        assert '本機整理完成' in page.locator('#status').inner_text()
        assert '普通生物學_001_雙語重點.md' in page.locator('#results').inner_text()
        assert not errors, errors
        print('PASS: subject, TXT import, wiki ingest, no duplicate, query, wiki ZIP, naming, local fallback')
        browser.close()
finally:
    server.terminate()
    server.wait(timeout=5)
