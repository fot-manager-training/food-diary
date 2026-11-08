'use strict';
const assert=require('node:assert/strict'),M=require('../menu-plans.js'),P=require('../shopping-plan.js'),periods=require('../menu-periods.json'),base=require('../data.json'),model=require('../ingredients.json');
assert.equal(M.resolve(periods,'2026-11-07',base,model).data,base);
const nov=M.resolve(periods,'2026-11-08',base,model).data,future=M.resolve(periods,'2026-12-01',base,model).data;
assert.equal(nov.days[7].meals[0].liza,'Горячий бутерброд с сыром и помидором');
assert.equal(nov.days[7].meals[0].katya,'Горячий бутерброд с салями и сыром (без творожка)');
assert.equal(nov.days[29].meals[3].liza,'Горячий бутерброд с сыром и салями');
assert.equal(future.days[0].meals[0].liza,'Хлебцы с сыром, огурцом и яйцом');
assert.equal(future.days[29].meals[3].liza,'Красная рыба с рисом');
assert.equal(M.resolve(periods,'2027-01-01',base,model).data.days[0].meals[0].liza,future.days[0].meals[0].liza);
for(const dataset of [nov,future]){
 assert.equal(dataset.budget,24000);for(const r of dataset.recipes)if(r.title.toLowerCase().startsWith('салат'))assert.ok(!/спиральки|картофель нарежьте/.test(r.body),r.title);
 const sources=dataset.days.filter(d=>d.meals[0].components);
 assert.equal(sources.length,dataset===nov?23:30);
 for(const d of sources){assert.equal(d.kcal,null);assert.equal(d.macros,null);for(const meal of d.meals)for(const who of ['liza','katya']){
  assert.ok(meal.components[who].length);assert.ok(dataset.recipeAliases[meal[who]]);
  for(const c of meal.components[who]){assert.ok(c.amount>=0);assert.ok(Math.abs(c.kcal-c.amount*dataset.products[c.key].kcal100/100)<=.051);assert.notEqual(c.key,'cabbage');}
 }}
 const plan=P.build(dataset,periods.ingredientModel,{monthLength:31});
 for(const trip of plan.trips){const context=plan.context(trip.id);for(const item of context.documentGroups.flatMap(g=>g.items)){
  assert.ok(item.id);assert.ok(item.key);assert.ok(!/готовый рис|готовый картофель|запеченная красная рыба/i.test(item.text),item.text);
 }for(const item of context.dishGroups.flatMap(g=>g.items)){assert.ok(item.key);assert.ok(item.id);}}
 const rice=plan.context(0).items.find(i=>i.key==='rice');assert.ok(rice);
 if(dataset===future){assert.ok(rice.text.includes('Рис сухой'));assert.ok(plan.context(plan.trips.length-1).dishGroups.some(g=>g.days.includes(31)));}
 else {assert.equal(plan.trips[1].startDay,8);assert.equal(plan.trips.at(-1).endDay,30);assert.equal(plan.milkPacks,0);assert.ok(plan.alreadyPurchasedIds.length>0);assert.ok(!plan.alreadyPurchasedIds.some(id=>id.includes(':inspect:')));}
}
console.log('Period checks passed: November dates, future repeat, complete source menus, recipe aliases, food-energy arithmetic, raw shopping units and November stock.');
