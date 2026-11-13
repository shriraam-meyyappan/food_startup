import 'package:flutter/material.dart';

import 'cart.dart';
import 'data/demo.dart';
import 'widgets/common.dart';

void main() => runApp(const DailyDabbaApp());

class DailyDabbaApp extends StatelessWidget {
  const DailyDabbaApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'DailyDabba',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: cream,
      colorScheme: ColorScheme.fromSeed(
        seedColor: ink,
        primary: ink,
        secondary: const Color(0xFF6C873A),
        secondaryContainer: lime,
        surface: Colors.white,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: cream,
        foregroundColor: ink,
        surfaceTintColor: Colors.transparent,
      ),
      textTheme: const TextTheme(
        headlineLarge: TextStyle(
          fontSize: 38,
          fontWeight: FontWeight.w500,
          letterSpacing: -1.5,
          color: ink,
        ),
        headlineMedium: TextStyle(
          fontSize: 29,
          fontWeight: FontWeight.w500,
          letterSpacing: -1,
          color: ink,
        ),
        titleLarge: TextStyle(
          fontSize: 21,
          fontWeight: FontWeight.w600,
          letterSpacing: -.5,
          color: ink,
        ),
        bodyMedium: TextStyle(color: ink, height: 1.5),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(minimumSize: const Size(48, 48)),
      ),
      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: Colors.white,
        indicatorColor: lime,
      ),
    ),
    home: const DemoShell(),
  );
}

class DemoShell extends StatefulWidget {
  const DemoShell({super.key});
  @override
  State<DemoShell> createState() => _DemoShellState();
}

class _DemoShellState extends State<DemoShell> {
  final cart = DemoCart();
  int tab = 0;
  String category = 'Lunch';
  int sampleDay = 0;
  final scroll = ScrollController();
  @override
  void dispose() {
    cart.dispose();
    scroll.dispose();
    super.dispose();
  }

  void go(int value) {
    setState(() => tab = value);
    if (scroll.hasClients) scroll.jumpTo(0);
  }

  void openCart() => Navigator.of(context).push(
    MaterialPageRoute<void>(
      builder: (_) => CartScreen(
        cart: cart,
        onMenu: () {
          Navigator.pop(context);
          go(1);
        },
      ),
    ),
  );
  void details(Meal meal) => showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    builder: (context) => SafeArea(
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(20),
                child: FoodPhoto(meal),
              ),
              const SizedBox(height: 20),
              Eyebrow('${meal.category}'),
              const SizedBox(height: 12),
              Text(
                meal.name,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 12),
              Text(meal.description),
              const SizedBox(height: 14),
              const Text(
                'Images are for illustration. Contact the kitchen for ingredient and allergen information before ordering.',
                style: TextStyle(color: muted),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    rupees(meal.price),
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  QuantityControl(meal: meal, cart: cart),
                ],
              ),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Close details'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
  Widget title(String eyebrow, String text, String description) => Padding(
    padding: const EdgeInsets.only(bottom: 24),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(eyebrow),
        const SizedBox(height: 12),
        Text(text, style: Theme.of(context).textTheme.headlineLarge),
        const SizedBox(height: 12),
        Text(description, style: const TextStyle(color: muted)),
      ],
    ),
  );
  Widget modeSwitch(bool plansSelected) => Padding(
    padding: const EdgeInsets.only(bottom: 18),
    child: Row(
      children: [
        Expanded(
          child: plansSelected
              ? FilledButton(
                  onPressed: () => go(2),
                  child: const Text('Subscription plans'),
                )
              : TextButton(
                  onPressed: () => go(2),
                  child: const Text('Subscription plans'),
                ),
        ),
        Expanded(
          child: !plansSelected
              ? FilledButton(
                  onPressed: () => go(0),
                  child: const Text('Daily specials'),
                )
              : TextButton(
                  onPressed: () => go(0),
                  child: const Text('Daily specials'),
                ),
        ),
      ],
    ),
  );
  Widget greeting() => Padding(
    padding: const EdgeInsets.only(bottom: 16),
    child: Text(
      'Hey there, what’s cooking today?',
      style: Theme.of(context).textTheme.titleLarge,
    ),
  );
  Widget promo(bool planMode) => Padding(
    padding: const EdgeInsets.only(bottom: 18),
    child: Panel(
      color: const Color(0xFFE9EDDF),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Eyebrow(
                  planMode
                      ? 'A routine that feels like you'
                      : 'A little taste of home',
                ),
                const SizedBox(height: 8),
                Text(
                  planMode
                      ? 'Your week, with meals sorted.'
                      : 'Ready for a good meal?',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  planMode
                      ? 'Subscriptions opening soon'
                      : 'Pick your favourite. Build your dabba.',
                  style: const TextStyle(fontSize: 12),
                ),
                if (!planMode)
                  const Padding(
                    padding: EdgeInsets.only(top: 8),
                    child: Text(
                      'Ordering opens soon',
                      style: TextStyle(fontSize: 10, color: muted),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          if (planMode)
            const Icon(Icons.event_repeat, size: 48, color: muted)
          else
            ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: SizedBox(
                width: 85,
                child: FoodPhoto(meals.first, height: 100),
              ),
            ),
        ],
      ),
    ),
  );
  Widget menu(bool home) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      if (home) ...[
        greeting(),
        modeSwitch(false),
      ] else
        title(
          'Find your everyday favourite',
          'The daily menu',
          'Find your everyday favourite.',
        ),
      Wrap(
        spacing: 8,
        runSpacing: 6,
        children:
            (home
                    ? ['Breakfast', 'Lunch', 'Dinner']
                    : ['All', 'Breakfast', 'Lunch', 'Dinner'])
                .map(
                  (c) => ChoiceChip(
                    label: Text(c),
                    selected: category == c,
                    onSelected: (_) => setState(() => category = c),
                    selectedColor: lime,
                  ),
                )
                .toList(),
      ),
      const SizedBox(height: 16),
      promo(false),
      Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('Today’s meals', style: Theme.of(context).textTheme.titleLarge),
          if (home)
            TextButton(
              onPressed: () {
                setState(() => category = 'All');
                go(1);
              },
              child: const Text('Full menu ↗'),
            ),
        ],
      ),
      const SizedBox(height: 12),
      SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: meals
              .where((m) => category == 'All' || m.category == category)
              .map(
                (m) => SizedBox(
                  width: 250,
                  child: Padding(
                    padding: const EdgeInsets.only(right: 12),
                    child: MealCard(
                      meal: m,
                      cart: cart,
                      onDetails: () => details(m),
                    ),
                  ),
                ),
              )
              .toList(),
        ),
      ),
      if (home) ...[
        const SizedBox(height: 8),
        Text('More to explore', style: Theme.of(context).textTheme.titleLarge),
        const Text(
          'From the menu',
          style: TextStyle(fontSize: 11, color: muted),
        ),
        const SizedBox(height: 12),
        ...[meals[2], meals[3]].map(
          (m) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Panel(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: SizedBox(
                          width: 48,
                          child: FoodPhoto(m, height: 48),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          m.name,
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(rupees(m.price)),
                      QuantityControl(meal: m, cart: cart),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    ],
  );
  Widget subscriptions() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      greeting(),
      modeSwitch(true),
      promo(true),
      SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: plans.indexed
              .map(
                (entry) => SizedBox(
                  width: 270,
                  child: Padding(
                    padding: const EdgeInsets.only(right: 12, bottom: 18),
                    child: Panel(
                      color: entry.$1 == 0
                          ? const Color(0xFFF2DED0)
                          : const Color(0xFFEFEDC9),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Eyebrow('${entry.$2.period} plan'),
                          const SizedBox(height: 12),
                          Text(
                            entry.$2.title,
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            entry.$2.description,
                            style: const TextStyle(fontSize: 12),
                          ),
                          const SizedBox(height: 14),
                          Row(
                            children: meals
                                .take(3)
                                .map(
                                  (m) => Expanded(
                                    child: Padding(
                                      padding: const EdgeInsets.only(right: 4),
                                      child: ClipRRect(
                                        borderRadius: BorderRadius.circular(8),
                                        child: FoodPhoto(m, height: 54),
                                      ),
                                    ),
                                  ),
                                )
                                .toList(),
                          ),
                          const SizedBox(height: 14),
                          const Text(
                            '◉ Familiar Indian favourites\n◉ Meal week\n◉ Policies to be confirmed',
                            style: TextStyle(fontSize: 11, height: 2),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            '${rupees(entry.$2.price)} / plan',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 16),
                          FilledButton(
                            onPressed: () => Navigator.push(
                              context,
                              MaterialPageRoute<void>(
                                builder: (_) => PlanDetail(plan: entry.$2),
                              ),
                            ),
                            child: const Text('View plan ↗'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              )
              .toList(),
        ),
      ),
      Panel(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Meal calendar',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text(
              'Explore the weekly menu. Subscriptions open soon.',
              style: TextStyle(fontSize: 11, color: muted),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 6,
              children: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].indexed
                  .map(
                    (d) => ChoiceChip(
                      label: Text(d.$2),
                      selected: sampleDay == d.$1,
                      onSelected: (_) => setState(() => sampleDay = d.$1),
                    ),
                  )
                  .toList(),
            ),
            const SizedBox(height: 18),
            Text(
              meals[[0, 1, 3, 0, 5][sampleDay]].name,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text(
              'Editing, skipping and pausing are unavailable.',
              style: TextStyle(fontSize: 12, color: muted),
            ),
          ],
        ),
      ),
      const SizedBox(height: 18),
      const Text(
        'Credit conversion, skips, pauses, refunds, taxes and delivery fees are not yet defined. Final pricing will be confirmed before purchase.',
        style: TextStyle(color: muted, fontSize: 12),
      ),
    ],
  );

  Widget history() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      title('YOUR DAILYDABBA', 'Your orders', 'Your meals, all in one place.'),
      Panel(
        child: Column(
          children: [
            const Icon(Icons.receipt_long_outlined, size: 48),
            const SizedBox(height: 16),
            Text(
              'No orders yet',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            const Text(
              'Your orders will appear here once ordering is available.',
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () => go(1),
              child: const Text('Explore the menu →'),
            ),
          ],
        ),
      ),
    ],
  );
  Widget account() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      title('YOUR LITTLE CORNER', 'My account', 'Welcome to DailyDabba.'),
      Panel(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Welcome, guest',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            const Text('Sign in to manage your profile and orders.'),
            const SizedBox(height: 16),
            const FilledButton(
              onPressed: null,
              child: Text('Sign in coming soon'),
            ),
          ],
        ),
      ),
      const SizedBox(height: 20),
      const Panel(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Saved addresses'),
            SizedBox(height: 12),
            Text(
              'No saved addresses. Sign in will be available soon. You can then add a delivery address.',
            ),
          ],
        ),
      ),
    ],
  );
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text(
        'DailyDabba ●',
        style: TextStyle(fontWeight: FontWeight.w700, letterSpacing: -1),
      ),
      actions: [
        ListenableBuilder(
          listenable: cart,
          builder: (context, _) => Padding(
            padding: const EdgeInsets.only(right: 12),
            child: IconButton(
              tooltip: 'Cart, ${cart.count} items',
              onPressed: openCart,
              icon: Badge(
                label: Text('${cart.count}'),
                backgroundColor: ink,
                child: const Icon(Icons.shopping_bag_outlined),
              ),
            ),
          ),
        ),
      ],
    ),
    body: SafeArea(
      child: Column(
        children: [
          Container(
            width: double.infinity,
            color: const Color(0xFFE9EEDF),
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: const Text(
              'Familiar flavours. Fresh routines.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 10),
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              controller: scroll,
              padding: const EdgeInsets.all(20),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 680),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (tab < 2)
                        const Padding(
                          padding: EdgeInsets.only(bottom: 22),
                          child: Text(
                            '⌖ Bengaluru / Delivery area',
                            style: TextStyle(color: muted, fontSize: 12),
                          ),
                        ),
                      [
                        () => menu(true),
                        () => menu(false),
                        subscriptions,
                        history,
                        account,
                      ][tab](),
                      const SizedBox(height: 28),
                      const Center(
                        child: Text(
                          'A little taste of home. Every day.',
                          style: TextStyle(color: muted, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    ),
    bottomNavigationBar: NavigationBar(
      selectedIndex: tab,
      onDestinationSelected: go,
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.home_outlined),
          selectedIcon: Icon(Icons.home),
          label: 'Home',
        ),
        NavigationDestination(icon: Icon(Icons.restaurant_menu), label: 'Menu'),
        NavigationDestination(
          icon: Icon(Icons.calendar_month_outlined),
          label: 'Plans',
        ),
        NavigationDestination(
          icon: Icon(Icons.receipt_long_outlined),
          label: 'Orders',
        ),
        NavigationDestination(
          icon: Icon(Icons.person_outline),
          label: 'Account',
        ),
      ],
    ),
  );
}

class CartScreen extends StatelessWidget {
  const CartScreen({super.key, required this.cart, required this.onMenu});
  final DemoCart cart;
  final VoidCallback onMenu;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Your cart')),
    body: SafeArea(
      child: ListenableBuilder(
        listenable: cart,
        builder: (context, _) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const Eyebrow('YOUR NEXT MEAL'),
            const SizedBox(height: 22),
            if (cart.items.isEmpty)
              Panel(
                child: Column(
                  children: [
                    const Icon(
                      Icons.shopping_bag_outlined,
                      size: 56,
                      color: muted,
                    ),
                    const SizedBox(height: 20),
                    Text(
                      'Your next meal starts here.',
                      style: Theme.of(context).textTheme.headlineMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Add a favourite from the menu to fill your dabba.',
                    ),
                    const SizedBox(height: 22),
                    FilledButton(
                      onPressed: onMenu,
                      child: const Text('Explore the menu →'),
                    ),
                  ],
                ),
              )
            else ...[
              ...cart.items.map(
                (m) => Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Panel(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          m.name,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 10),
                        Text(
                          '${rupees(m.price)} each · ${rupees(m.price * cart.quantity(m))}',
                        ),
                        const SizedBox(height: 10),
                        Wrap(
                          spacing: 20,
                          crossAxisAlignment: WrapCrossAlignment.center,
                          children: [
                            QuantityControl(meal: m, cart: cart),
                            TextButton(
                              onPressed: () => cart.remove(m),
                              child: Text(
                                'Remove',
                                semanticsLabel: 'Remove ${m.name}',
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              PriceSummary(cart: cart),
              const SizedBox(height: 20),
              FilledButton(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute<void>(
                    builder: (_) => CheckoutScreen(cart: cart),
                  ),
                ),
                child: const Text('Continue to checkout →'),
              ),
              TextButton(
                onPressed: onMenu,
                child: const Text('Continue browsing'),
              ),
            ],
          ],
        ),
      ),
    ),
  );
}

class PriceSummary extends StatelessWidget {
  const PriceSummary({super.key, required this.cart});
  final DemoCart cart;
  @override
  Widget build(BuildContext context) => Panel(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Meal subtotal'),
            Text(
              rupees(cart.subtotal),
              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 20),
            ),
          ],
        ),
        const Divider(height: 30),
        const Text('Delivery & taxes · To be confirmed'),
        const SizedBox(height: 12),
        const Text(policyNote, style: TextStyle(color: muted, fontSize: 12)),
      ],
    ),
  );
}

class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key, required this.cart});
  final DemoCart cart;
  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Checkout')),
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Panel(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Ordering opens soon'),
                SizedBox(height: 12),
                Text(
                  'Address selection, delivery slots and payment will be available when ordering opens. No payment will be taken.',
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          PriceSummary(cart: widget.cart),
          const SizedBox(height: 20),
          const FilledButton(
            onPressed: null,
            child: Text('Place order unavailable'),
          ),
        ],
      ),
    ),
  );
}

class PlanDetail extends StatelessWidget {
  const PlanDetail({super.key, required this.plan});
  final DemoPlan plan;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Subscription details')),
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Eyebrow('${plan.period} plan'),
          const SizedBox(height: 20),
          Text(plan.title, style: Theme.of(context).textTheme.headlineLarge),
          const SizedBox(height: 20),
          Text(plan.description),
          const SizedBox(height: 20),
          Text(
            '${rupees(plan.price)} / plan',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 24),
          const Panel(
            child: Text(
              'Meal: The everyday thali\nDelivery schedule to be confirmed.\n\nSchedule, credit conversion, skip, pause and refund rules are to be confirmed. Delivery charges and taxes are not configured.',
            ),
          ),
          const SizedBox(height: 24),
          const FilledButton(
            onPressed: null,
            child: Text('Subscription purchase unavailable'),
          ),
        ],
      ),
    ),
  );
}
