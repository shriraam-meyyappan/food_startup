import 'package:flutter/material.dart';

import '../cart.dart';
import '../data/demo.dart';

const ink = Color(0xFF132C23);
const cream = Color(0xFFF7F7F0);
const lime = Color(0xFFCFED80);
const muted = Color(0xFF657067);

class Panel extends StatelessWidget {
  const Panel({super.key, required this.child, this.color = Colors.white});
  final Widget child;
  final Color color;
  @override
  Widget build(BuildContext context) => Container(
    width: double.infinity,
    padding: const EdgeInsets.all(22),
    decoration: BoxDecoration(
      color: color,
      borderRadius: BorderRadius.circular(24),
      border: Border.all(color: const Color(0xFFE1E5DC)),
    ),
    child: child,
  );
}

class Eyebrow extends StatelessWidget {
  const Eyebrow(this.text, {super.key});
  final String text;
  @override
  Widget build(BuildContext context) => Text(
    text.toUpperCase(),
    style: const TextStyle(
      fontSize: 10,
      fontWeight: FontWeight.w700,
      letterSpacing: 1.5,
      color: Color(0xFF556749),
    ),
  );
}

class FoodPhoto extends StatelessWidget {
  const FoodPhoto(this.meal, {super.key, this.height = 135});
  final Meal meal;
  final double height;
  @override
  Widget build(BuildContext context) => Image.asset(
    'assets/images/${meal.image}.jpg',
    height: height,
    width: double.infinity,
    fit: BoxFit.cover,
    semanticLabel: '${meal.name}, illustrative photograph',
    errorBuilder: (_, error, stack) => SizedBox(
      height: height,
      child: const Center(child: Icon(Icons.restaurant, size: 48)),
    ),
  );
}

class QuantityControl extends StatelessWidget {
  const QuantityControl({super.key, required this.meal, required this.cart});
  final Meal meal;
  final DemoCart cart;
  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: cart,
    builder: (context, _) {
      final count = cart.quantity(meal);
      if (count == 0) {
        return FilledButton.tonal(
          onPressed: meal.available ? () => cart.change(meal, 1) : null,
          child: Text(
            meal.available ? 'Add +' : 'Unavailable',
            semanticsLabel: meal.available
                ? 'Add ${meal.name}'
                : '${meal.name} unavailable',
          ),
        );
      }
      return Container(
        decoration: BoxDecoration(
          border: Border.all(color: const Color(0xFFE1E5DC)),
          borderRadius: BorderRadius.circular(28),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              tooltip: 'Decrease ${meal.name} quantity',
              onPressed: () => cart.change(meal, -1),
              icon: const Icon(Icons.remove, size: 18),
            ),
            Text('$count', semanticsLabel: '$count portions'),
            IconButton(
              tooltip: 'Increase ${meal.name} quantity',
              onPressed: () => cart.change(meal, 1),
              icon: const Icon(Icons.add, size: 18),
            ),
          ],
        ),
      );
    },
  );
}

class MealCard extends StatelessWidget {
  const MealCard({
    super.key,
    required this.meal,
    required this.cart,
    required this.onDetails,
  });
  final Meal meal;
  final DemoCart cart;
  final VoidCallback onDetails;
  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(bottom: 18),
    clipBehavior: Clip.antiAlias,
    decoration: BoxDecoration(
      color: Colors.white,
      border: Border.all(color: const Color(0xFFE1E5DC)),
      borderRadius: BorderRadius.circular(22),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Semantics(
          button: true,
          label: 'View ${meal.name} details',
          child: InkWell(onTap: onDetails, child: FoodPhoto(meal)),
        ),
        Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Eyebrow('Vegetarian · ${meal.category}'),
              const SizedBox(height: 8),
              InkWell(
                onTap: onDetails,
                child: Text(
                  meal.name,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                meal.description,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: muted, height: 1.5),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 8,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  Text(
                    rupees(meal.price),
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  QuantityControl(meal: meal, cart: cart),
                ],
              ),
            ],
          ),
        ),
      ],
    ),
  );
}
