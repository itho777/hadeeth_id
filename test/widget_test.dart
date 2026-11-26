import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hadeeth_id_mobile/main.dart';
import 'package:hadeeth_id_mobile/state/app_state.dart';

void main() {
  testWidgets('app boots to the shell', (WidgetTester tester) async {
    await tester.pumpWidget(HadeethMobileApp(state: AppState()));
    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
