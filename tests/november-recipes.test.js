'use strict';
const assert=require('node:assert/strict'),periods=require('../menu-periods.json');
const n=periods.november;
assert.equal(n.recipes.length,26);
for(const [id,r] of n.recipes.entries()){
 assert.equal(r.id,id);assert.equal(r.source,'Recepty_k_noyabrskomu_menu_Liza_Katya.docx');
 assert.ok(r.ingredients);assert.ok(r.when);assert.ok(r.portions);assert.ok(r.instructions.length>=3);
 assert.ok(!/бутерброд/i.test(r.title));
 for(const related of r.relatedRecipeIds||[])assert.ok(n.recipes[related]);
}
assert.equal(n.recipes[0].ingredients,'Свинина нежирная 300 г; картофель 400 г; масло 10 г; соль, паприка, перец.');
assert.equal(n.recipes[3].instructions.length,5);
assert.ok(n.recipes[3].ingredients.includes('вода 30 мл'));
assert.deepEqual(n.recipes[4].relatedRecipeIds,[3]);
assert.ok(n.recipes[11].ingredients.includes('молоко 80 мл'));
assert.ok(n.recipes[12].portions.includes('90 г креветок'));
assert.deepEqual(n.recipeAliases['Курица с картофельными дольками + салат «Яйцо, огурец, помидор, сыр»'],[2,19]);
assert.deepEqual(n.recipeAliases['Горячий бутерброд с сыром и помидором'],[]);
for(const ids of Object.values(n.recipeAliases))for(const id of ids)assert.ok(n.recipes[id]);
assert.ok(n.recipeGuidance.some(s=>s.includes('проверка разрезом не гарантирует')));
assert.ok(periods.future.recipes.some(r=>r.title==='Тост с сыром и помидором'));
console.log('November recipe checks passed: 26 source recipes, exact ingredients, steps, portions, composite meals and excluded sandwich recipes.');
