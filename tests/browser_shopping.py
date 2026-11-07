"""UI copy, persisted shopping accordions, counters and reduced motion."""
from playwright.sync_api import sync_playwright, expect

REMOVED = [
    'Крупы и спиральки — сухой вес.',
    'Составлено по вашему семейному меню',
    '30 дней заботы о себе и друг о друге',
    'Порция по аппетиту. Кофе с молоком — по желанию.',
    'Меню повторяется с 1-го числа каждого месяца.',
    'Помним о цитрусовых:',
    'Аллергия Кати:',
    'Бюджет, порции и хранение — из документа',
    'За одним столом',
]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':390,'height':844})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto('http://127.0.0.1:8000')
    page.locator('#identity button[value=katya]').click()
    expect(page.locator('.brand')).to_contain_text('Дневник питания')
    assert 'Дневник питания' in page.title()
    for tab in ['menu', 'recipes', 'shopping']:
        page.locator(f'[data-tab={tab}]').click()
        expect(page.locator('body')).to_have_attribute('data-section', tab)
        text = page.locator('body').inner_text()
        for removed in REMOVED:
            assert removed not in text, (tab, removed)
    groups = page.locator('.shopping-group')
    expect(groups).to_have_count(4)
    expect(groups.first.locator('.fold-count')).to_have_text('0 / 5')
    groups.first.locator('.group-heading').click()
    expect(groups.first.locator('[data-item]').first).not_to_be_visible()
    page.reload()
    expect(groups.first.locator('[data-item]').first).not_to_be_visible()
    groups.first.locator('.group-heading').focus()
    page.keyboard.press('Enter')
    expect(groups.first.locator('[data-item]').first).to_be_visible()
    groups.first.locator('[data-item]').first.check()
    expect(groups.first.locator('.fold-count')).to_have_text('1 / 5')
    expect(page.locator('.checklist-heading .fold-count')).to_have_text('1 / 24')
    page.locator('[data-fold-all=close]').click()
    assert page.locator('.shopping-group[open]').count() == 0
    page.reload()
    assert page.locator('.shopping-group[open]').count() == 0
    expect(page.locator('.checklist-heading .fold-count')).to_have_text('1 / 24')
    page.locator('[data-fold-all=open]').click()
    assert page.locator('.shopping-group[open]').count() == 4
    expect(page.locator('#undo')).to_be_disabled()  # Reload cleared history, not the checkmarks.
    page.locator('#reset').click()
    expect(page.locator('.checklist-heading .fold-count')).to_have_text('0 / 24')
    page.locator('#undo').click()
    expect(page.locator('.checklist-heading .fold-count')).to_have_text('1 / 24')
    page.locator('.checklist-heading').click()
    expect(page.locator('.fold-tools')).not_to_be_visible()
    page.reload()
    expect(page.locator('.fold-tools')).not_to_be_visible()
    page.locator('.checklist-heading').click()
    expect(page.locator('.fold-tools')).to_be_visible()
    page.locator('[data-view=dishes]').click()
    assert page.locator('[data-item]').count() == 24
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.emulate_media(reduced_motion='reduce')
    page.locator('[data-tab=menu]').click()
    assert page.evaluate("document.getAnimations().length") == 0
    assert not errors,errors
    browser.close()
    print('Shopping checks passed: removed copy, new name, master/group folding, keyboard, saved state, counts, reset/undo and reduced motion.')
