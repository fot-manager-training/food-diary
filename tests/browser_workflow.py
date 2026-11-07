"""Run against a local server: python tests/browser_workflow.py [base-url].
Requires Python Playwright and Chromium. No external services are used.
"""
import os
import sys
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1280, 'height': 900})
    page.add_init_script("localStorage.setItem('table-selectedDate', JSON.stringify('2026-11-01'))")
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000')
    page.locator('#identity button[value=liza]').click()
    expect(page.locator('.nutrition')).to_contain_text('1499')
    page.locator('[data-edit="0"]').click()
    row = page.locator('.edit-row').first
    row.locator('.edit-name').fill('Мой омлет')
    row.locator('.edit-name').press('Tab')
    row.locator('.edit-details').fill('2 яйца и сыр')
    row.locator('.edit-kcal').fill('320.5')
    page.locator('#add-position').click()
    row2 = page.locator('.edit-row').nth(1)
    row2.locator('.edit-name').fill('Кофе с молоком')
    row2.locator('.edit-name').press('Tab')
    row2.locator('.edit-kcal').fill('30')
    expect(page.locator('#editor-total')).to_contain_text('350,5')
    page.locator('#meal-form button[type=submit]').click()
    expect(page.locator('.nutrition')).to_contain_text('350,5')
    expect(page.locator('.nutrition')).to_contain_text('Итог неполный')
    expect(page.locator('.meal').first).to_contain_text('Мой омлет')
    page.reload()
    expect(page.locator('.meal').first).to_contain_text('Мой омлет')
    expect(page.locator('.nutrition')).to_contain_text('350,5')
    # Fill the rest of the day, including a legitimate zero-calorie position.
    for i, kcal in [(1, '400'), (2, '0'), (3, '500')]:
        page.locator(f'[data-edit="{i}"]').click()
        page.locator('.edit-kcal').fill(kcal)
        page.locator('#meal-form button[type=submit]').click()
    expect(page.locator('.nutrition')).to_contain_text('1 250,5')
    expect(page.locator('.nutrition')).to_contain_text('ИТОГО ЗА ДЕНЬ')
    expect(page.locator('.nutrition .incomplete')).to_have_count(0)
    # Saved dish can be selected on another day, restoring its calories and notes.
    page.locator('[data-day="2"]').click()
    expect(page.locator('.nutrition')).to_contain_text('1499')
    page.locator('[data-edit="0"]').click()
    assert 'Мой омлет' in page.locator('#dish-options').inner_html()
    page.locator('.edit-name').fill('Мой омлет')
    page.locator('.edit-name').press('Tab')
    expect(page.locator('.edit-kcal')).to_have_value('320.5')
    expect(page.locator('.edit-details')).to_have_value('2 яйца и сыр')
    page.locator('#meal-form button[type=submit]').click()
    expect(page.locator('.nutrition')).to_contain_text('320,5')
    # Profiles have separate edits; original data can be restored independently.
    page.locator('#profile').click()
    page.locator('#identity button[value=katya]').click()
    expect(page.locator('.nutrition')).to_have_count(0)
    expect(page.locator('.meal').first).not_to_contain_text('Мой омлет')
    page.locator('#profile').click()
    page.locator('#identity button[value=liza]').click()
    expect(page.locator('.meal').first).to_contain_text('Мой омлет')
    page.locator('[data-edit="0"]').click()
    page.locator('#restore-meal').click()
    expect(page.locator('.nutrition')).to_contain_text('1499')
    expect(page.locator('.meal').first).not_to_contain_text('Мой омлет')
    page.set_viewport_size({'width': 390, 'height': 844})
    page.locator('[data-edit="0"]').click()
    page.locator('#add-position').click()
    page.locator('.edit-row').last.locator('.remove-position').click()
    assert page.locator('.edit-row').count() == 1
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert not errors, errors
    browser.close()
    print('Browser checks passed: editing, sums, incomplete totals, zero calories, persistence, saved dishes, profile isolation, restore, and mobile editor.')
