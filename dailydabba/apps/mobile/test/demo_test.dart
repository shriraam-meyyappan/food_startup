import 'package:flutter_test/flutter_test.dart';
import 'package:dailydabba_mobile/cart.dart';
import 'package:dailydabba_mobile/data/demo.dart';
import 'package:dailydabba_mobile/main.dart';
import 'package:flutter/material.dart';

void main() {
  test('Cart aggregates quantities and prices, removes lines and rejects unavailable meals', () {
    final cart = DemoCart();
    cart.change(meals[0], 2);
    cart.change(meals[1], 1);
    expect(cart.count, 3);
    expect(cart.subtotal, 477);
    cart.change(meals[0], -1);
    expect(cart.subtotal, 328);
    cart.remove(meals[1]);
    cart.change(meals[0], -5);
    cart.change(meals[4], 1);
    expect(cart.items, isEmpty);
    expect(cart.subtotal, 0);
  });
  testWidgets('Navigation and cart empty state work', (tester) async {
    await tester.pumpWidget(const DailyDabbaApp());
    await tester.tap(find.byTooltip('Cart, 0 items'));
    await tester.pumpAndSettle();
    expect(find.text('Your next meal starts here.'), findsOneWidget);
    await tester.tap(find.text('Explore the menu →'));
    await tester.pumpAndSettle();
    expect(find.text('The daily menu'), findsOneWidget);
    await tester.tap(find.byIcon(Icons.person_outline));
    await tester.pumpAndSettle();
    expect(find.text('Welcome, guest'), findsOneWidget);
  });
}
