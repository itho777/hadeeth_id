import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../state/app_state.dart';
import '../state/nav_controller.dart';
import '../theme.dart';
import 'books_page.dart';
import 'chat_page.dart';
import 'home_page.dart';
import 'profile_page.dart';
import 'topics_page.dart';
import 'widgets.dart';

class AppShell extends StatelessWidget {
  const AppShell({super.key});

  static const _tabs = [
    HomePage(),
    BooksPage(),
    TopicsPage(),
    ChatPage(),
    ProfilePage(inShell: true),
  ];

  /// Android back, in order: dismiss the keyboard, then walk the tab trail,
  /// then ask before leaving. It used to close the app from any screen.
  Future<void> _back(
    BuildContext context,
    NavController nav,
    String lang,
  ) async {
    // Keyboard up? The first back closes it, exactly like a native field.
    if (MediaQuery.viewInsetsOf(context).bottom > 0) {
      FocusManager.instance.primaryFocus?.unfocus();
      return;
    }
    if (nav.back()) return;
    if (!context.mounted) return;
    final leave = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(
          t('Exit hadeeth.id?', 'Keluar dari hadeeth.id?', lang),
          style: HText.h3.copyWith(color: ctx.p.textPrimary),
        ),
        content: Text(
          t(
            'Saved narrations and downloads stay on this device.',
            'Riwayat tersimpan dan unduhan tetap ada di perangkat ini.',
            lang,
          ),
          style: HText.bodySm.copyWith(color: ctx.p.textMuted, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: Text(t('Stay', 'Tetap di sini', lang)),
          ),
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: Text(t('Exit', 'Keluar', lang)),
          ),
        ],
      ),
    );
    if (leave == true && !kIsWeb) await SystemNavigator.pop();
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<AppState>().lang;
    setActiveLang(lang);
    final nav = context.watch<NavController>();
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (didPop) return;
        _back(context, nav, lang);
      },
      child: Scaffold(
        body: IndexedStack(index: nav.tab, children: _tabs),
        bottomNavigationBar: NavigationBar(
          height: 62,
          backgroundColor: context.p.surfaceHigh,
          indicatorColor: context.p.dark
              ? Brand.emeraldBright.withValues(alpha: 0.16)
              : Brand.emerald.withValues(alpha: 0.10),
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          selectedIndex: nav.tab,
          onDestinationSelected: (i) {
            // Leaving a text field behind keeps the keyboard up and hides the
            // bar the user needs to get anywhere else.
            FocusManager.instance.primaryFocus?.unfocus();
            nav.go(i);
          },
          destinations: [
            NavigationDestination(
              icon: const Icon(Icons.home_outlined),
              selectedIcon: const Icon(Icons.home_rounded),
              label: t('Home', 'Beranda', lang),
            ),
            NavigationDestination(
              icon: const Icon(Icons.menu_book_outlined),
              selectedIcon: const Icon(Icons.menu_book_rounded),
              label: t('Books', 'Kitab', lang),
            ),
            NavigationDestination(
              icon: const Icon(Icons.explore_outlined),
              selectedIcon: const Icon(Icons.explore_rounded),
              label: t('Topics', 'Tema', lang),
            ),
            NavigationDestination(
              icon: const Icon(Icons.auto_awesome_outlined),
              selectedIcon: const Icon(Icons.auto_awesome_rounded),
              label: t('Razi', 'Razi', lang),
            ),
            NavigationDestination(
              icon: const Icon(Icons.person_outline_rounded),
              selectedIcon: const Icon(Icons.person_rounded),
              label: t('Profile', 'Profil', lang),
            ),
          ],
        ),
      ),
    );
  }
}
