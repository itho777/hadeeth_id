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

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final state = AppState();
  await state.init();
  await AuthService.instance.init();
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
