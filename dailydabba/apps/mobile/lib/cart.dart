import 'package:flutter/foundation.dart';

import 'data/demo.dart';

/// Session-only state. No network, authentication or order submission.
class DemoCart extends ChangeNotifier {
  final Map<String, int> _quantities = {};
  int quantity(Meal meal) => _quantities[meal.id] ?? 0;
  List<Meal> get items => meals.where((meal) => quantity(meal) > 0).toList();
  int get count => items.fold(0, (sum, meal) => sum + quantity(meal));
  int get subtotal =>
      items.fold(0, (sum, meal) => sum + quantity(meal) * meal.price);
  void change(Meal meal, int delta) {
    if (!meal.available) return;
    _quantities[meal.id] = (quantity(meal) + delta).clamp(0, 999);
    notifyListeners();
  }

  void remove(Meal meal) {
    _quantities.remove(meal.id);
    notifyListeners();
  }
}
