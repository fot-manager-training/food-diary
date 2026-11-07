'use strict';
const assert=require('node:assert/strict');
const P=require('../shopping-plan.js');
const data=require('../data.json'),model=require('../ingredients.json');
const plan=P.build(data,model);
assert.equal(plan.milkRequired,5200);
assert.equal(plan.milkPacks,6);
assert.equal(P.build(data,model,{milkPack:900}).milkPacks,6);
assert.equal(P.build(data,model,{milkStock:500}).milkPacks,5);
assert.equal(plan.trips[2].groups.flatMap(g=>g.items).find(i=>i.key==='milk').packs,0);
for(const key of ['milk','egg']){
 let stock=0;
 for(const t of plan.trips){for(const i of t.groups.flatMap(g=>g.items).filter(i=>i.key===key)){stock+=i.packs*i.packSize-i.required;assert.equal(stock,i.remaining);assert.ok(stock>=0)}}
}
function ingredients(trip,title){return new Set(plan.context(trip).dishGroups.find(g=>g.title===title).items.map(i=>i.key));}
assert.deepEqual(ingredients(1,'Хлопья с молоком, йогурт и банан'),new Set(['flakes','milk','yogurt','banana']));
for(const key of ['chicken','pasta','oil','ketchup','cabbage','carrot','cucumber','tomato'])assert.ok(ingredients(1,'Грудка со спиральками').has(key),key);
for(const key of ['tuna','egg','corn','cucumber','mayo'])assert.ok(ingredients(1,'Салат с тунцом, яйцом, огурцом и кукурузой').has(key),key);
for(const key of ['mince','onion','seasoning','oats'])assert.ok(ingredients(2,'Котлеты со спиральками').has(key),key);
assert.ok(ingredients(8,'Картофельный салат с яйцом, огурцом и крабовыми палочками').has('crab'));
assert.ok(!model.dishes['Йогурт и печенье'].includes('cucumber'));
// No ingredient is lost by assigning it exclusively to the first matching dish.
const c=plan.context(1),milkIDs=c.dishGroups.filter(g=>g.items.some(i=>i.key==='milk')).flatMap(g=>g.items.filter(i=>i.key==='milk').map(i=>i.id));
assert.ok(milkIDs.length>1);assert.equal(new Set(milkIDs).size,1);
for(let t=0;t<10;t++){
 const context=plan.context(t);
 assert.equal(P.unique(context.dishGroups.flatMap(g=>g.items)).length,context.items.length);
 if(t)assert.ok(context.dishGroups.flatMap(g=>g.items).every(i=>i.checkable),`Missing item in trip ${t}`);
 for(const g of context.dishGroups)assert.ok(g.items.length>0,g.title);
}
// Wednesday dinner belongs to the new batch; Sunday to the next shopping trip.
assert.ok(!plan.context(1).dishGroups.some(g=>g.title==='Котлеты со спиральками'));
assert.ok(plan.context(2).dishGroups.some(g=>g.title==='Котлеты со спиральками'));
assert.ok(!plan.context(2).dishGroups.some(g=>g.title==='Онигири с тунцом и огурец'));
console.log('Shopping model checks passed: complete dishes, shared products, batch boundaries, stock references and package conservation.');
