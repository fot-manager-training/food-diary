/* Pure shopping planner: shared products, recipe coverage and package carry-over. */
(function(root){
'use strict';
const norm=s=>s.toLowerCase().replaceAll('ё','е');
const unique=items=>[...new Map(items.filter(i=>i.checkable!==false).map(i=>[i.id,i])).values()];
function includesMeal(trips,trip,d,i){if(trip.id===0)return true;const next=trips[trip.id+1];const start=(trip.day||1)*4+(trip.id%2===0?3:0),end=next?(next.day*4+(next.id%2===0?3:0)):31*4;return d*4+i>=start&&d*4+i<end;}
function build(data,model,options={}){
 if(data.componentPlanning)return (typeof module!=='undefined'&&module.exports?require('./menu-plans.js'):root.MealPlans).buildShopping(data,model,options);
 const milkPack=Number(options.milkPack)||1000;
 const stocks={milk:Math.max(0,Number(options.milkStock)||0),egg:0};
 const trips=data.trips.map(t=>({...t,groups:t.groups.map(g=>({...g,items:g.items.map(item=>{
  const key=model.itemKeys[item.id],copy={...item,key,sourceId:item.id,checkable:true};if(key==='rice'){copy.text=t.id===0?'Рис сухой — 1 упаковка 1 кг':'Рис сухой — из месячного запаса';copy.detail='Ориентир закупки; сначала проверьте остаток'}if(key==='potato'&&/готовый/.test(copy.text)){copy.text=t.id===0?'Картофель сырой — ориентир 1,5 кг':'Картофель сырой — из запаса';copy.detail='Ориентир с учётом очистки; точный выход зависит от приготовления'}if(key==='fish'&&/запеч/.test(copy.text))copy.text='Филе красной рыбы сырое или замороженное — ориентир 300 г';
  if(key==='milk'||key==='egg'){
   const required=Number(item.text.match(/(\d+)\s*(?:мл|шт\.)/)[1]),pack=key==='milk'?milkPack:10;
   const before=stocks[key],packs=Math.max(0,Math.ceil((required-before)/pack));stocks[key]+=packs*pack-required;
   copy.id=`${item.id}:pack:${pack}:${packs}`;copy.required=required;copy.packs=packs;copy.packSize=pack;copy.remaining=stocks[key];
   const unit=key==='milk'?'мл':'шт.',name=key==='milk'?'Молоко':'Яйца';
   copy.text=packs?`${name} — ${packs} уп. × ${pack} ${unit}`:`${name} — ${required} ${unit} из остатка`;
   copy.detail=`Нужно ${required} ${unit}. ${packs?'Плановый остаток после использования: '+stocks[key]+' '+unit+'.':'Новую упаковку не добавляем; проверьте остаток дома.'}`;
  }
  if(g.title==='Взять из запаса')copy.detail='Из домашнего запаса — повторно покупать не нужно';
  return copy;
 })}))}));
 const extras=[{id:'recipe-onion',key:'onion',text:'Репчатый лук — для котлет',detail:'В рецепте есть лук, в исходном списке его не было'},{id:'recipe-seasoning',key:'seasoning',text:'Соль и привычные специи',detail:'Проверить дома'},{id:'recipe-dill',key:'dill',text:'Укроп — для красной рыбы',detail:'По желанию'}].map(i=>({...i,checkable:true}));
 trips[0].groups.push({title:'Для рецептов — проверить дома',items:extras});
 const pantry=new Map(trips[0].groups.flatMap(g=>g.items).map(i=>[i.key,i]));
 // Withdrawals from pantry reference the very same checkbox as the monthly purchase.
 for(const trip of trips.slice(1))for(const g of trip.groups)if(g.title==='Взять из запаса')g.items=g.items.map(i=>({...i,id:pantry.get(i.key)?.id||i.id}));
 const allProducts=new Map();
 for(const trip of trips.slice(1))for(const g of trip.groups)if(g.title!=='Взять из запаса')for(const item of g.items){
  if(!allProducts.has(item.key))allProducts.set(item.key,[]);allProducts.get(item.key).push(item);
 }
 function ingredientKeys(text){const t=norm(text),keys=Object.entries(model.products).filter(([,v])=>new RegExp(v.pattern,'u').test(t)).map(([key])=>key);if(keys.includes('oats')&&keys.includes('flakes'))keys.splice(keys.indexOf('flakes'),1);if(keys.includes('tema')){const i=keys.indexOf('yogurt');if(i>=0)keys.splice(i,1)}return [...new Set(keys)];}
 function dishesFor(trip){const dishes=new Map();
  const add=(title,keys,day)=>{if(!dishes.has(title))dishes.set(title,{title,keys:new Set(),days:new Set()});const dish=dishes.get(title);keys.forEach(k=>dish.keys.add(k));dish.days.add(day)};
  for(const d of data.days)for(let i=0;i<4;i++)if(includesMeal(data.trips,trip,d.day,i)){
   const m=d.meals[i];for(const who of ['liza','katya'])add(m[who],model.dishes[m[who]]||ingredientKeys(m[who]),d.day);
   const dessert=m.lizaPortion.split(' + десерт ')[1];if(dessert)add('Десерт: '+dessert,ingredientKeys(dessert),d.day);
   if(i===0)add('Кофе с молоком',['coffee','milk'],d.day);
  }
  return [...dishes.values()];
 }
 function context(tripId){const trip=trips[tripId],local=new Map(trip.groups.flatMap(g=>g.items).map(i=>[i.key,i])),dishes=dishesFor(trip),extraItems=new Map();
  const groups=dishes.map(dish=>({title:dish.title,days:[...dish.days],note:dish.keys.has('cabbage')&&dish.keys.has('tomato')?'Овощи: выберите сочетание капусты с морковью или огурца с помидором.':'',items:[...dish.keys].map(key=>{
   let item=local.get(key)||pantry.get(key);
   if(!item){const future=allProducts.get(key)||[],name=model.products[key].name;item={id:'fresh-'+key,key,text:name,checkable:false,detail:tripId===0?'Свежий продукт: покупается в закупках на неделю':'Проверьте дома или добавьте к покупке: в исходном списке этого продукта нет'};}
   if(item.checkable!==false&&!local.has(key))extraItems.set(item.id,item);
   return {...item,detail:key==='oats'&&/котлет/.test(dish.title)?'Для котлет — только если масса рыхлая. '+(item.detail||''):item.detail};
  })}));
  const documentGroups=trip.groups.map(g=>({...g,items:g.items.map(i=>({...i}))}));
  if(extraItems.size)documentGroups.push({title:'Из запаса — нужно для этих блюд',items:[...extraItems.values()]});
  // Products not tied to a dish (e.g. reserve sweets) remain visible.
  const referenced=new Set(groups.flatMap(g=>g.items).map(i=>i.id)),rest=documentGroups.flatMap(g=>g.items).filter(i=>!referenced.has(i.id));
  if(rest.length)groups.push({title:'Остальные продукты и запас',items:rest});
  return {trip,documentGroups,dishGroups:groups,items:unique(documentGroups.flatMap(g=>g.items))};
 }
 return {context,trips,milkPack,milkRequired:trips.flatMap(t=>t.groups.flatMap(g=>g.items)).filter(i=>i.key==='milk').reduce((n,i)=>n+i.required,0),milkPacks:trips.flatMap(t=>t.groups.flatMap(g=>g.items)).filter(i=>i.key==='milk').reduce((n,i)=>n+i.packs,0)};
}
const api={build,unique,includesMeal};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ShoppingPlan=api;
})(typeof globalThis!=='undefined'?globalThis:this);
