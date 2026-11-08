/* Dated source menus and an explicit, approximate ingredient/energy model. */
(function(root){'use strict';
function resolve(periods,iso,baseData,baseModel){const month=iso.slice(0,7),source=month==='2026-11'&&Number(iso.slice(8))>=8?periods.november:month>='2026-12'?periods.future:null;if(!source)return {data:baseData,model:baseModel};return {data:{...source,products:periods.products,trips:[]},model:periods.ingredientModel};}
const unique=items=>[...new Map(items.filter(i=>i.checkable!==false).map(i=>[i.id,i])).values()];
function buildShopping(data,model,options={}){
 const products=data.products,nov=data.period==='2026-11',tag=nov?'nov26-v1':'future-v1',end=nov?30:(options.monthLength||30),start=data.planningStart;
 const days=data.days.filter(d=>d.day>=start&&d.day<=end&&d.meals[0].components);
 if(end===31)days.push({...data.days[0],day:31});
 const starts=nov?[8,11,15,18,22,25,29]:[1,4,7,11,14,18,21,25,28];
 const windows=starts.map((n,i)=>({id:i+1,day:n,startDay:n,endDay:Math.min(end,(starts[i+1]||end+1)-1),title:nov?(n===8?'8–10 ноября · сначала запасы':`${n}–${Math.min(end,(starts[i+1]||end+1)-1)} ноября`):`Дни ${n}–${Math.min(end,(starts[i+1]||end+1)-1)}`}));
 const demands=new Map(),dishLists=new Map();
 for(const trip of [{id:0,startDay:start,endDay:end},...windows]){
  const total={},dishes=new Map();
  for(const d of days)if(d.day>=trip.startDay&&d.day<=trip.endDay)for(const m of d.meals)for(const who of ['liza','katya']){
   const title=m[who];if(!dishes.has(title))dishes.set(title,{title,keys:new Set(),days:new Set()});const dish=dishes.get(title);dish.days.add(d.day);
   for(const c of m.components[who]){dish.keys.add(c.key);total[c.key]=(total[c.key]||0)+c.amount*products[c.key].purchaseFactor;}
  }
  demands.set(trip.id,total);dishLists.set(trip.id,[...dishes.values()]);
 }
 const stocks={...data.alreadyPurchased},milkPack=Number(options.milkPack)||1000;
 if(Number.isFinite(options.milkStock))stocks.milk=Math.max(0,options.milkStock);
 const initialMilk=stocks.milk||0,lastSupply=new Map(),pantry=new Map();let milkPacks=0;
 const stockItems=Object.entries(data.alreadyPurchased).filter(([key,qty])=>products[key]&&qty>0).map(([key,qty])=>{
  const item={id:`${tag}:stock:${key}`,key,text:['rice','potato'].includes(key)?`${products[key].purchaseName} — из имеющегося запаса`:`${products[key].purchaseName} — ${qty} ${key==='egg'?'шт.':products[key].unit==='ml'?'мл':'г'} уже куплено`,detail:'Уже куплено к 7 ноября; сверьте фактический остаток',checkable:true,alreadyPurchased:true};lastSupply.set(key,item);return item;
 });
 for(const key of data.checkExistingStock||[])stockItems.push({id:`${tag}:inspect:${key}`,key,text:`${key==='rice'?'Рис':'Картофель'} — проверить имеющийся запас`,detail:'Количество и срок хранения уточните дома; этот запас не пересчитываем в сухой или сырой вес',checkable:true});
 function create(key,need,tripId){const p=products[key],pack=key==='milk'?milkPack:p.pack,available=stocks[key]||0,packs=Math.max(0,Math.ceil((need-available-1e-8)/pack)),buy=packs*pack,remaining=Math.max(0,available+buy-need);stocks[key]=remaining;
  if(!packs){const source=lastSupply.get(key);return {...source,id:source?.id||`${tag}:reserve:${key}`,key,text:`${p.purchaseName} — из запаса`,detail:'Повторно покупать не нужно, если запас в наличии',checkable:true,fromStock:true};}
  const unit=key==='egg'?'шт.':p.unit==='ml'?'мл':'г',loose=['chicken','thigh','pork','potato','onion','cucumber','tomato','apple','banana'].includes(key);
  let text=loose?`${p.purchaseName} — ≈${buy} ${unit}`:`${p.purchaseName} — ${packs} уп. по ${pack} ${unit}`;
  if(key==='tuna'||key==='corn')text=`${p.purchaseName} — ${packs} бан. (по ≈${pack} г без заливки)`;
  if((data.checkExistingStock||[]).includes(key))text+=' — только при нехватке запаса';
  const item={id:`${tag}:buy:${tripId}:${key}:${buy}`,key,text,detail:(p.optional?'Необязательно, если хватает бюджета. ':'')+'Оценка закупки по выбранным порциям; сверьте остатки и упаковку',checkable:true,required:need,packs,packSize:pack,remaining,optional:p.optional};lastSupply.set(key,item);if(key==='milk')milkPacks+=packs;return item;
 }
 const monthly=[];
 for(const [key,total] of Object.entries(demands.get(0)))if(products[key].staple){const item=create(key,total,0);monthly.push(item);pantry.set(key,item);}
 const trips=[{id:0,day:0,title:nov?'Запасы и докупка на 8–30 ноября':'Бакалея на месяц',groups:[...(stockItems.length?[{title:'Уже куплено к 7 ноября',items:stockItems}]:[]),{title:'Бакалея — докупить при нехватке',items:monthly.filter(i=>!i.fromStock)}]}];
 // Staples are bought once; perishable ingredients are supplied by the dated windows.
 for(const win of windows){const regular=[],reserve=[];for(const [key,qty] of Object.entries(demands.get(win.id))){const item=products[key].staple?{...pantry.get(key),text:`${products[key].purchaseName} — из месячного запаса`,detail:'Общая отметка с месячной закупкой',fromStock:true}:create(key,qty,win.id);(item.fromStock?reserve:regular).push(item);}
  trips.push({...win,groups:[{title:'Купить — ориентир по порциям',items:regular},{title:'Сначала проверить дома',items:reserve}].filter(g=>g.items.length)});
 }
 function context(tripId){const trip=trips[tripId]||trips[0],local=new Map(trip.groups.flatMap(g=>g.items).map(i=>[i.key,i]));const groups=dishLists.get(trip.id).map(dish=>({title:dish.title,days:[...dish.days],items:[...dish.keys].map(key=>{
   if(trip.id===0&&!products[key].staple)return {key,id:`fresh:${key}`,text:products[key].purchaseName,detail:'Свежий продукт: выберите закупку на нужные даты',checkable:false};
   return {...(local.get(key)||pantry.get(key))};
  })}));
  const referenced=new Set(groups.flatMap(g=>g.items).map(i=>i.id)),rest=trip.groups.flatMap(g=>g.items).filter(i=>!referenced.has(i.id));if(rest.length)groups.push({title:'Остальные запасы и покупки',items:rest});
  return {trip,documentGroups:trip.groups,dishGroups:groups,items:unique(trip.groups.flatMap(g=>g.items))};
 }
 return {trips,context,milkPack,initialMilk,milkRequired:Math.round(demands.get(0).milk||0),milkPacks,estimated:true,alreadyPurchasedIds:stockItems.filter(i=>i.alreadyPurchased).map(i=>i.id)};
}
const api={resolve,buildShopping};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.MealPlans=api;
})(typeof globalThis!=='undefined'?globalThis:this);
