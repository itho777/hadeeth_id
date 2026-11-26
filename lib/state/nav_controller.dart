import 'package:flutter/material.dart';

/// Coordinates the five root tabs and hand-off prompts (home -> AI assistant).
///
/// [history] is a tab trail, not a route stack: pushed pages (a hadith, a
/// scholar profile) are ordinary routes and pop natively. The trail exists so
/// Android back inside the shell returns to the tab you came from instead of
/// closing the app.
class NavController extends ChangeNotifier {
  int tab = 0;
  String? chatPrompt;

  final List<int> _history = <int>[];

  void go(int index, {String? prompt, bool remember = true}) {
    if (prompt != null) chatPrompt = prompt;
    if (remember && index != tab) {
      _history.add(tab);
      if (_history.length > 12) _history.removeAt(0);
    }
    tab = index;
    notifyListeners();
  }

  /// True when back would move between tabs rather than leave the shell.
  bool get canGoBack => _history.isNotEmpty;

  /// Pops one tab off the trail. Returns false when there is nothing to pop.
  bool back() {
    if (_history.isEmpty) return false;
    tab = _history.removeLast();
    chatPrompt = null;
    notifyListeners();
    return true;
  }

  void consumePrompt() {
    chatPrompt = null;
    notifyListeners();
  }

  /// Clears the prompt without a rebuild — for callers already inside a build.
  void takePrompt() {
    chatPrompt = null;
  }
}
