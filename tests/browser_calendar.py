"""Calendar, monthly repetition and state migration integration checks."""
import sys
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1280,'height':1000})
    page.clock.install(time=__import__('datetime').datetime.fromisoformat('2026-11-07T12:00:00+00:00'))
    errors=[]
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8000')
    page.locator('#identity button[value=liza]').click()
    expect(page.locator('.datebar h2')).to_have_text('7 ноября')
    expect(page.locator('.calendar-empty')).to_have_count(6) # Sunday, not Monday.
    expect(page.locator('.calendar button')).to_have_count(30)
    expect(page.locator('.ribbon-day.selected span')).to_have_text('сб')
    assert page.locator('.datebar [data-move]').count()==0
    page.locator('[data-month-move="1"]').click()
    expect(page.locator('.calendar-empty')).to_have_count(1) # December starts Tuesday.
    expect(page.locator('.calendar button')).to_have_count(31)
    page.locator('.calendar [data-date="2026-12-01"]').click()
    expect(page.locator('.nutrition')).to_contain_text('ОЦЕНКА СУММЫ ПРОДУКТОВ')
    page.locator('[data-edit="0"]').click()
    while page.locator('.edit-row').count()>1:
        page.locator('.edit-row').last.locator('.remove-position').click()
    page.locator('.edit-name').fill('Тестовое блюдо декабря')
    page.locator('.edit-name').press('Tab')
    page.locator('.edit-kcal').fill('123')
    page.locator('#meal-form button[type=submit]').click()
    expect(page.locator('.meal').first).to_contain_text('123 ккал')
    page.locator('[data-tab=shopping]').click()
    page.locator('[data-item]').first.check()

    def select_date(iso):
        page.locator('[data-tab=recipes]').click()
        page.locator('#recipe-day').fill(iso)
        page.locator('#recipe-day').dispatch_event('change')
        page.locator('[data-tab=menu]').click()

    select_date('2027-01-01')
    expect(page.locator('.nutrition')).to_contain_text('ОЦЕНКА СУММЫ ПРОДУКТОВ')
    expect(page.locator('.meal').first).not_to_contain_text('Тестовое блюдо декабря')
    page.locator('[data-tab=shopping]').click()
    expect(page.locator('.check-row.done')).to_have_count(0)
    select_date('2026-12-01')
    expect(page.locator('.meal').first).to_contain_text('Тестовое блюдо декабря')
    page.locator('[data-tab=shopping]').click()
    expect(page.locator('.check-row.done')).to_have_count(1)
    select_date('2027-01-31')
    expect(page.locator('.nutrition')).to_contain_text('ОЦЕНКА СУММЫ ПРОДУКТОВ') # Menu day 1 on the 31st.
    expect(page.locator('.datebar h2')).to_have_text('31 января')
    expect(page.locator('.ribbon-day.selected span')).to_have_text('вс')
    page.locator('[data-tab=recipes]').click()
    page.locator('[data-filter=tomorrow]').click()
    expect(page.locator('.notice')).to_contain_text('1 февраля')
    select_date('2027-02-28')
    expect(page.locator('.calendar button')).to_have_count(28)
    select_date('2028-02-29')
    expect(page.locator('.calendar button')).to_have_count(29)
    expect(page.locator('.datebar h2')).to_have_text('29 февраля')
    page.locator('.datebar [data-today]').click()
    expect(page.locator('.datebar h2')).to_have_text('7 ноября')
    for width in [320,390,768,1440]:
        page.set_viewport_size({'width':width,'height':844})
        for tab in ['menu','recipes','shopping']:
            page.locator(f'[data-tab={tab}]').click()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width,tab)
    page.set_viewport_size({'width':390,'height':844})
    page.locator('[data-tab=menu]').click()
    page.locator('#calendar-toggle').click()
    expect(page.locator('.calendar')).to_be_visible()
    page.locator('.calendar [data-date="2026-11-09"]').click()
    expect(page.locator('.datebar h2')).to_have_text('9 ноября')
    page.screenshot(path='/tmp/calendar-mobile.png',full_page=True)
    assert page.locator('#profile .cat-liza').count()==1
    assert page.locator('.meal-icon svg').count()==4
    assert page.evaluate("!/[\\p{Extended_Pictographic}]/u.test(document.body.innerText)")
    assert not errors,errors
    # Existing users keep their edits at the real date originally chosen.
    legacy=browser.new_page()
    legacy.add_init_script("""localStorage.setItem('table-user','"liza"');localStorage.setItem('table-start','"2026-11-09"');localStorage.setItem('table-selectedDate','"2026-11-09"');localStorage.setItem('table-menuEdits',JSON.stringify({'liza-1-0':[{name:'Старое блюдо',details:'Порция',kcal:456}]}));""")
    legacy.goto('http://127.0.0.1:8000')
    expect(legacy.locator('.meal').first).to_contain_text('Старое блюдо')
    expect(legacy.locator('.meal').first).to_contain_text('456 ккал')
    browser.close()
    print('Calendar checks passed: real weekday offsets, today, date ribbon, month boundaries, leap years, monthly menu, date-specific edits, monthly shopping and migration.')
