export type Meal = { id: string; name: string; category: 'Breakfast' | 'Lunch' | 'Dinner'; price: number; description: string; image: string; available: boolean; tag: string };
export const meals: Meal[] = [
 {id:'thali',name:'The everyday thali',category:'Lunch',price:149,description:'Dal tadka, seasonal sabzi, steamed rice, two rotis and a little pickle. Familiar favourites, together on one plate.',image:'thali',available:true,tag:'House favourite'},
 {id:'paneer',name:'Paneer comfort bowl',category:'Lunch',price:179,description:'Paneer in a rich tomato gravy, with steamed rice and a side of cucumber.',image:'paneer',available:true,tag:'Something special'},
 {id:'dosa',name:'Masala dosa plate',category:'Breakfast',price:99,description:'A crisp dosa with spiced potato filling, sambar and coconut chutney.',image:'dosa',available:true,tag:'Morning favourite'},
 {id:'dinner',name:'Dal & roti dabba',category:'Dinner',price:129,description:'A comforting bowl of dal, three soft rotis and seasonal vegetables.',image:'thali',available:true,tag:'Simple comforts'},
 {id:'idli',name:'Idli & sambar',category:'Breakfast',price:89,description:'Steamed idlis served with sambar and coconut chutney.',image:'dosa',available:false,tag:'Sold out'},
 {id:'feast',name:'Paneer dinner dabba',category:'Dinner',price:189,description:'Paneer gravy, rotis and jeera rice for a leisurely end to the day.',image:'paneer',available:true,tag:'Evening favourite'},
];
export const addresses: {name:string; text:string}[] = [];
export const slots = ['12:00–1:00 pm', '1:00–2:00 pm', '7:00–8:00 pm'];
export const plans = [{name:'A week, sorted.',period:'Weekly',price:749,description:'A five-lunch plan for your working week.',color:'peach'}, {name:'Make it a routine.',period:'Monthly',price:2799,description:'A twenty-lunch plan for the month ahead.',color:'yellow'}];
export const rupees = (value: number) => `₹${value.toLocaleString('en-IN')}`;
export const policyNote = 'Delivery charges and taxes are not configured. Final payable amount is unavailable.';
