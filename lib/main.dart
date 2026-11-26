import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'data/hadeeth_repository.dart';
import 'data/auth_service.dart';
import 'data/download_service.dart';
import 'data/razi_service.dart';
import 'data/search_service.dart';
import 'data/sync_service.dart';
import 'state/app_state.dart';
import 'state/nav_controller.dart';
import 'theme.dart';
import 'ui/app_shell.dart';

/// Tag that prefixes every startup failure in logcat (`adb logcat -s flutter`).
const _crashTag = 'HADEETH_CRASH';

/// Release builds keep stdout, so this stays readable over adb even though the
/// generic Android "runtime exception" dialog shows nothing useful.
void _logCrash(String phase, Object error, StackTrace? stack) {
  // ignore: avoid_print
  print('$_crashTag[$phase] $error');
  if (stack != null) {
    // ignore: avoid_print
    print('$_crashTag[$phase] stack:\n$stack');
  }
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Anything thrown after the first frame must not disappear into a blank
  // screen: log it, and keep the app running.
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    _logCrash('frame', details.exception, details.stack);
  };
  PlatformDispatcher.instance.onError = (error, stack) {
    _logCrash('async', error, stack);
    return true;
  };

  final state = AppState();
  try {
    await state.init();
  } catch (error, stack) {
    // SharedPreferences is the first platform channel touched at startup; if it
    // fails the app would otherwise close before drawing anything at all.
    _logCrash('startup', error, stack);
    runApp(_CrashApp(error: error, stack: stack));
    return;
  }

  try {
    await AuthService.instance.init();
  } catch (error, stack) {
    _logCrash('auth', error, stack);
  }

  SyncService.instance.bind(state);
  runApp(HadeethMobileApp(state: state));
}

class HadeethMobileApp extends StatefulWidget {
  const HadeethMobileApp({super.key, required this.state});

  final AppState state;

  @override
  State<HadeethMobileApp> createState() => _HadeethMobileAppState();
}

class _HadeethMobileAppState extends State<HadeethMobileApp> {
  late final HadeethRepository _repository;
  late final DownloadService _downloads;
  late final SearchService _search;
  late final RaziService _razi;
  final NavController _nav = NavController();

  @override
  void initState() {
    super.initState();
    _repository = HadeethRepository()..preferOffline = widget.state.preferOffline;
    _downloads = DownloadService();
    _search = SearchService();
    _razi = RaziService();
    _loadDownloaded();
  }

  Future<void> _loadDownloaded() async {
    try {
      final ids = await _downloads.downloadedBooks();
      _repository.downloaded.addAll(ids);
      if (mounted) setState(() {});
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: widget.state),
        ChangeNotifierProvider.value(value: _nav),
        Provider.value(value: _repository),
        Provider.value(value: _downloads),
        Provider.value(value: _search),
        Provider.value(value: _razi),
      ],
      child: Consumer<AppState>(
        builder: (context, state, _) {
          _repository.preferOffline = state.preferOffline;
          return MaterialApp(
            title: 'hadeeth.id',
            debugShowCheckedModeBanner: false,
            theme: buildTheme(HP.light),
            darkTheme: buildTheme(HP.darkPalette),
            themeMode: state.themeMode,
            home: const AppShell(),
          );
        },
      ),
    );
  }
}

/// Shown instead of a blank screen when startup fails, so the failure can be
/// read off the phone without a USB cable.
class _CrashApp extends StatelessWidget {
  const _CrashApp({required this.error, this.stack});

  final Object error;
  final StackTrace? stack;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: const Color(0xFF101010),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: ListView(
              children: [
                const Text(
                  'hadeeth.id failed to start',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Screenshot this screen and send it back.',
                  style: TextStyle(color: Colors.white70, fontSize: 13),
                ),
                const SizedBox(height: 18),
                SelectableText(
                  '$error',
                  style: const TextStyle(
                    color: Color(0xFFFF8A80),
                    fontSize: 14,
                    height: 1.4,
                  ),
                ),
                if (stack != null) ...[
                  const SizedBox(height: 18),
                  SelectableText(
                    '$stack',
                    style: const TextStyle(
                      color: Colors.white54,
                      fontSize: 11,
                      height: 1.35,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
