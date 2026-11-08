"""Dish coverage, shared checkbox counts, package preferences and glass navigation."""
from playwright.sync_api import sync_playwright, expect
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    # Historical October plan remains available as a regression fixture.
    page.add_init_script("localStorage.setItem('table-selectedDate',JSON.stringify('2026-10-01'))")
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8000')
    page.locator('#identity button[value=liza]').click()
    page.locator('[data-tab=shopping]').click()
    page.locator('#trip').select_option('1')
    page.locator('[data-view=dishes]').click()
    breakfast=page.locator('.shopping-group').filter(has=page.get_by_role('heading',name='Хлопья с молоком, йогурт и банан',exact=True))
    expect(breakfast).to_have_count(1)
    for word in ['хлопья','Молоко','йогурт','банан']:
        expect(breakfast).to_contain_text(word)
    lunch=page.locator('.shopping-group').filter(has=page.get_by_role('heading',name='Грудка со спиральками',exact=True))
    for word in ['куриная грудка','спиральки','масло','кетчуп','капуста','морковь','огурцы','помидоры']:
        expect(lunch).to_contain_text(word)
    milk=breakfast.locator('[data-item^="1-1-4:pack:"]')
    milk.check()
    coffee=page.locator('.shopping-group').filter(has=page.get_by_role('heading',name='Кофе с молоком',exact=True))
    expect(coffee.locator('[data-item^="1-1-4:pack:"]')).to_be_checked()
    expect(page.locator('.checklist-heading .fold-count')).to_have_text('1 / 34')
    page.locator('#undo').click()
    expect(breakfast.locator('[data-item^="1-1-4:pack:"]')).not_to_be_checked()
    expect(coffee.locator('[data-item^="1-1-4:pack:"]')).not_to_be_checked()
    page.locator('#trip').select_option('2')
    expect(page.locator('.shopping-checklist')).to_contain_text('Молоко — 500 мл из остатка')
    page.locator('.package-options summary').click()
    expect(page.locator('.package-options')).to_contain_text('6 уп. по 1000 мл')
    page.locator('#milk-pack').select_option('900')
    expect(page.locator('#milk-pack')).to_have_value('900')
    page.locator('#milk-stock').fill('500')
    page.locator('#milk-stock').press('Tab')
    page.reload()
    expect(page.locator('#milk-pack')).to_have_value('900')
    expect(page.locator('#milk-stock')).to_have_value('500')
    page.locator('.package-options summary').click()
    nav=page.locator('.main-nav')
    assert '0.74' in nav.evaluate('(el)=>getComputedStyle(el).backgroundColor')
    assert nav.evaluate('(el)=>getComputedStyle(el).backdropFilter') != 'none'
    for width in [320,390,768,1440]:
        page.set_viewport_size({'width':width,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path='/tmp/shopping-ingredients.png',full_page=True)
    assert not errors, errors
    browser.close()
    print('Ingredient UI checks passed: complete breakfast/lunch, shared milk checks, unique progress, undo, carry-over, package settings and translucent navigation.')
