import 'dart:async';

import 'package:flutter/foundation.dart';

import 'package:supabase_flutter/supabase_flutter.dart';

/// Email/password + Google sign-in against the hadeeth.id Supabase project.
///
/// The anon key is a build-time define, never a checked-in constant:
/// `flutter build apk --release --dart-define=SUPABASE_ANON_KEY=...`
/// Without it the app stays fully local and no login UI is shown.
class AuthService extends ChangeNotifier {
  AuthService._();

  static final AuthService instance = AuthService._();

  static const url = 'https://idokyspokenbmzoegahq.supabase.co';
  static const redirect = 'com.hadeeth.id://login-callback';

  final _key = const String.fromEnvironment('SUPABASE_ANON_KEY');
  StreamSubscription<AuthState>? _subscription;

  bool _configured = false;
  String? _email;
  bool _busy = false;

  bool get configured => _configured;
  String? get email => _email;
  bool get busy => _busy;
  bool get signedIn => _email != null;

  /// Golden/widget tests render the signed-in or signed-out branch without a
  /// network key. Never call from app code.
  @visibleForTesting
  void debugConfigure({String? email}) {
    _configured = true;
    _email = email;
    notifyListeners();
  }

  @visibleForTesting
  void debugReset() {
    _configured = false;
    _email = null;
    notifyListeners();
  }

  /// Null until a build supplies SUPABASE_ANON_KEY; callers then skip cloud work.
  SupabaseClient? get client => _configured ? Supabase.instance.client : null;

  /// Native builds must use a constant custom-scheme URL. A query string changes
  /// the URL's identity and Supabase silently substitutes `site_url`, dropping
  /// the reader on the public website after Google sign-in.
  static String oauthRedirect() => kIsWeb ? Uri.base.origin : redirect;

  Future<void> init() async {
    if (_key.isEmpty || _configured) return;
    try {
      await Supabase.initialize(
        url: url,
        anonKey: _key,
        authOptions: const FlutterAuthClientOptions(autoRefreshToken: true),
      ).timeout(const Duration(seconds: 15));
      final client = Supabase.instance.client;
      _email = client.auth.currentUser?.email;
      _subscription = client.auth.onAuthStateChange.listen((state) {
        _email = state.session?.user.email;
        notifyListeners();
      });
      _configured = true;
      notifyListeners();
    } catch (_) {
      // A bad/expired define leaves the app local; no sign-in UI is offered.
    }
  }

  Future<String?> signIn(String email, String password) async {
    if (!_configured) return 'login_unavailable';
    _setBusy(true);
    try {
      final res = await Supabase.instance.client.auth
          .signInWithPassword(email: email.trim(), password: password)
          .timeout(const Duration(seconds: 25));
      _email = res.user?.email;
      return null;
    } catch (e) {
      return '$e';
    } finally {
      _setBusy(false);
    }
  }

  Future<String?> signUp(String email, String password) async {
    if (!_configured) return 'login_unavailable';
    _setBusy(true);
    try {
      final res = await Supabase.instance.client.auth
          .signUp(email: email.trim(), password: password)
          .timeout(const Duration(seconds: 25));
      _email = res.session?.user.email;
      // Email confirmation is on: no session yet, but the account exists.
      return res.session == null ? 'check_email' : null;
    } catch (e) {
      return '$e';
    } finally {
      _setBusy(false);
    }
  }

  Future<String?> signInWithGoogle() async {
    if (!_configured) return 'login_unavailable';
    _setBusy(true);
    try {
      final ok = await Supabase.instance.client.auth.signInWithOAuth(
        OAuthProvider.google,
        redirectTo: oauthRedirect(),
        authScreenLaunchMode: kIsWeb ? LaunchMode.platformDefault : LaunchMode.externalApplication,
      ).timeout(const Duration(seconds: 30));
      if (!ok) return 'oauth_launch_failed';
      return null;
    } catch (e) {
      return '$e';
    } finally {
      _setBusy(false);
    }
  }

  Future<void> signOut() async {
    if (!_configured) return;
    try {
      await Supabase.instance.client.auth.signOut();
    } catch (_) {}
    _email = null;
    notifyListeners();
  }

  void _setBusy(bool value) {
    _busy = value;
    notifyListeners();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}
