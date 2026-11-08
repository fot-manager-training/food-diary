"""Two source documents, dated transitions, per-product calories and shopping units."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
P=json.loads((Path(__file__).resolve().parents[1]/'menu-periods.json').read_text())
def number(text):return float(text.replace('≈','').replace('\u202f','').replace('\xa0','').replace(' ','').replace(',','.'))
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=b.new_page(viewport={'width':1280,'height':1000},reduced_motion='reduce')
    page.add_init_script("localStorage.setItem('table-selectedDate',JSON.stringify('2026-11-08'))")
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8000')
    page.locator('#identity button[value=liza]').click()
    expect(page.locator('.meal').first.locator('h3')).to_have_text('Горячий бутерброд с сыром и помидором')
    expect(page.locator('aside')).to_contain_text('24 000')
    def change_date(iso):
        page.locator('[data-tab=recipes]').click()
        page.locator('#recipe-day').fill(iso)
        page.locator('#recipe-day').dispatch_event('change')
        page.locator('[data-tab=menu]').click()
        expect(page.locator('body')).to_have_attribute('data-section','menu')
    def set_profile(person):
        page.locator('#profile').click();page.locator(f'#identity button[value={person}]').click()
        expect(page.locator('#profile')).to_contain_text('Лиза' if person=='liza' else 'Катя')
    for person in ['liza','katya']:
        if person=='katya':set_profile(person)
        for period,month,lo in [('november','2026-11',8),('future','2026-12',1)]:
            change_date(f'{month}-{lo:02d}')
            for day in range(lo,31):
                page.locator(f'.ribbon-day[data-day="{day}"]').click()
                d=P[period]['days'][day-1]
                for i,m in enumerate(d['meals']):
                    expect(page.locator('.meal').nth(i).locator('h3')).to_have_text(m[person])
                    expect(page.locator('.meal').nth(i).locator('.calorie-breakdown li')).to_have_count(len(m['components'][person]))
                expected=sum(c['kcal'] for m in d['meals'] for c in m['components'][person])
                assert abs(number(page.locator('.nutrition b').inner_text())-expected)<.02
    print('All source meals and ingredient totals passed.')
    set_profile('liza');change_date('2026-12-01')
    before=number(page.locator('.nutrition b').inner_text())
    page.locator('[data-edit="0"]').click()
    row=page.locator('.edit-row').first
    expect(row.locator('.edit-name')).to_have_value('Хлебцы')
    row.locator('.edit-amount').fill('30')
    row.locator('.edit-density').fill('400')
    expect(row.locator('.edit-kcal')).to_have_value('120')
    row.locator('.edit-kcal').fill('150')
    expect(row.locator('.edit-density')).to_have_value('500')
    page.locator('#meal-form button[type=submit]').click()
    assert abs(number(page.locator('.nutrition b').inner_text())-(before-87.5+150))<.02
    # Cross-period recipes use the next month's actual recipe collection.
    change_date('2026-11-30');page.locator('[data-tab=recipes]').click()
    page.locator('[data-filter=tomorrow]').click()
    expect(page.locator('.notice')).to_contain_text('1 декабря')
    page.locator('.recipe-card').first.click()
    expect(page.locator('#recipe-content')).to_contain_text('Хлебцы с сыром, огурцом и яйцом')
    page.locator('#recipe-dialog .close').click()
    change_date('2026-11-08');page.locator('[data-tab=shopping]').click()
    expect(page.locator('#trip')).to_contain_text('Запасы и докупка на 8–30 ноября')
    expect(page.locator('.shopping-checklist')).to_contain_text('Уже куплено к 7 ноября')
    for i in range(8):
        page.locator('#trip').select_option(str(i))
        for view in ['document','dishes']:
            page.locator(f'[data-view={view}]').click()
            text=page.locator('.check-items').all_text_contents()
            joined=' '.join(text).lower()
            assert 'готовый рис' not in joined
            assert 'готовый картофель' not in joined
            assert 'капуст' not in joined
    change_date('2026-12-13');page.locator('[data-meal="3"]').click()
    expect(page.locator('#recipe-content')).to_contain_text('Спиральки с креветками')
    page.locator('#recipe-dialog .close').click()
    page.set_viewport_size({'width':390,'height':844})
    for tab in ['menu','recipes','shopping']:
        page.locator(f'[data-tab={tab}]').click()
        expect(page.locator('body')).to_have_attribute('data-section',tab)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.locator('[data-tab=menu]').click()
    page.screenshot(path='/tmp/period-products-mobile.png',full_page=True)
    assert not errors,errors
    b.close()
    print('Period browser checks passed: all source meals for both profiles, visible per-product sums, editable weight/energy, period boundary recipes and raw shopping units.')
