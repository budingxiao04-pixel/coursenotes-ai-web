"""Frontend smoke test for KaTeX integration; external CDN rendering not covered."""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    html=(ROOT/'docs/index.html').read_text()
    assert 'katex.min.css' in html and 'katex.min.js' in html
    assert 'mhchem.min.js' in html and 'auto-render.min.js' in html
    html=re.sub(r'<script[^>]*></script>', '', html)
    page.set_content(html)
    page.evaluate("Object.defineProperty(window.crypto, 'randomUUID', {value: () => 'test-' + Math.random().toString(36).slice(2)})")
    page.evaluate('''(()=>{window.katex={render:(raw,el,opts)=>{
        if(opts.trust!==false)throw Error('unsafe KaTeX config');
        el.innerHTML='<span class="katex">MOCK FORMULA</span>';
    }};
    window.renderMathInElement=(el,opts)=>{
        if(opts.trust!==false)throw Error('unsafe auto-render config');
        el.dataset.typeset='yes';
    };return true})()''')
    page.add_script_tag(content=Path('/usr/local/slides_js/node_modules/jszip/dist/jszip.min.js').read_text())
    page.add_script_tag(content=(ROOT/'docs/app.js').read_text())
    assert page.locator('#latexPreview .katex').count()==1
    page.locator('#sampleChem').click()
    assert r'\ce{2H2 + O2 -> 2H2O}' in page.locator('#latexInput').input_value()
    assert page.locator('#latexPreview .katex').count()==1
    page.on('dialog',lambda d:d.accept('普通化學') if d.type=='prompt' else d.accept())
    page.locator('#addSubject').click()
    page.locator('#files').set_input_files(str(ROOT/'examples/demo-formulas.tex'))
    page.wait_for_timeout(400)
    assert '成功匯入 1 份' in page.locator('#status').inner_text()
    page.locator('#ingest').click()
    assert page.locator('#wikiPages').get_attribute('data-typeset')=='yes'
    page.locator('#generate').click()
    assert page.locator('.result-preview').count()==3
    assert all(x=='yes' for x in page.locator('.result-preview').evaluate_all('(els)=>els.map(e=>e.dataset.typeset)'))
    with page.expect_download() as d:
        page.locator('#downloadLatex').click()
    download=d.value
    assert download.suggested_filename=='普通化學_004_LaTeX公式.md',download.suggested_filename
    out=Path('/tmp/coursenotes-latex-test.md')
    download.save_as(str(out))
    assert r'\ce{2H2 + O2 -> 2H2O}' in out.read_text()
    assert not errors,errors
    print('PASS: KaTeX hooks, trust:false, chemistry input, TEX import, Wiki/results typeset, numbered LaTeX Markdown export')
    browser.close()
