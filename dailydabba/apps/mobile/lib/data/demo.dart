class Meal {
  const Meal(
    this.id,
    this.name,
    this.category,
    this.price,
    this.description,
    this.image, {
    this.available = true,
  });
  final String id, name, category, description, image;
  final int price;
  final bool available;
}

const meals = [
  Meal(
    'thali',
    'The everyday thali',
    'Lunch',
    149,
    'Dal tadka, seasonal sabzi, steamed rice, two rotis and a little pickle.',
    'thali',
  ),
  Meal(
    'paneer',
    'Paneer comfort bowl',
    'Lunch',
    179,
    'Paneer in a rich tomato gravy, with steamed rice and cucumber.',
    'paneer',
  ),
  Meal(
    'dosa',
    'Masala dosa plate',
    'Breakfast',
    99,
    'Crisp dosa with spiced potato filling, sambar and coconut chutney.',
    'dosa',
  ),
  Meal(
    'dinner',
    'Dal & roti dabba',
    'Dinner',
    129,
    'A comforting bowl of dal, three soft rotis and seasonal vegetables.',
    'thali',
  ),
  Meal(
    'idli',
    'Idli & sambar',
    'Breakfast',
    89,
    'Steamed idlis, sambar and coconut chutney.',
    'dosa',
    available: false,
  ),
  Meal(
    'feast',
    'Paneer dinner dabba',
    'Dinner',
    189,
    'Paneer gravy, rotis and jeera rice for a leisurely end to the day.',
    'paneer',
  ),
];

class DemoAddress {
  const DemoAddress(this.name, this.text);
  final String name, text;
}

const addresses = <DemoAddress>[];
const slots = ['12:00–1:00 pm', '1:00–2:00 pm', '7:00–8:00 pm'];

class DemoPlan {
  const DemoPlan(this.period, this.title, this.description, this.price);
  final String period, title, description;
  final int price;
}

const plans = [
  DemoPlan(
    'Weekly',
    'A week, sorted.',
    'A five-lunch plan for your working week.',
    749,
  ),
  DemoPlan(
    'Monthly',
    'Make it a routine.',
    'A twenty-lunch plan for the month ahead.',
    2799,
  ),
];

class DemoOrder {
  const DemoOrder(this.id, this.meal, this.date, this.price, this.step);
  final String id, meal, date;
  final int price, step;
}

const orders = <DemoOrder>[];
const stages = ['Received', 'Preparing', 'Out for delivery', 'Delivered'];
const policyNote =
    'Delivery charges and taxes are not configured. Final payable amount is unavailable.';
String rupees(int value) => '₹$value';
