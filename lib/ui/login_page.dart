import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/auth_service.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'widgets.dart';

/// Email/password registration and sign-in, plus Google OAuth. Supabase Auth is
/// configured at build time via SUPABASE_ANON_KEY; without it the page is never
/// pushed and the app stays local-only.
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _register = false;
  bool _obscure = true;
  String? _message;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusManager.instance.primaryFocus?.unfocus();
    setState(() => _message = null);
    final result = _register
        ? await AuthService.instance.signUp(_email.text, _password.text)
        : await AuthService.instance.signIn(_email.text, _password.text);
    if (!mounted) return;
    if (result == null) {
      Navigator.pop(context);
      return;
    }
    final lang = context.read<AppState>().lang;
    setState(() {
      _message = switch (result) {
        'check_email' => t('Check your inbox to confirm the address, then sign in.',
            'Cek kotak masuk untuk mengonfirmasi alamat, lalu masuk.', lang),
        'login_unavailable' => t('Login is not configured in this build.',
            'Login belum dikonfigurasi pada build ini.', lang),
        _ => _friendly(result, lang),
      };
    });
  }

  String _friendly(String raw, String lang) {
    final s = raw.toLowerCase();
    if (s.contains('invalid_credentials') || s.contains('invalid login')) {
      return t('Wrong email or password.', 'Email atau kata sandi salah.', lang);
    }
    if (s.contains('email_not_confirmed')) {
      return t('Confirm your email first — check your inbox.',
          'Konfirmasi email dulu — cek kotak masuk.', lang);
    }
    if (s.contains('already registered') || s.contains('user_already_exists')) {
      return t('That email is already registered. Try signing in.',
          'Email itu sudah terdaftar. Coba masuk.', lang);
    }
    if (s.contains('timeout') || s.contains('socket') || s.contains('network') || s.contains('clientexception')) {
      return t('Cannot reach the server. Check your connection and try again.',
          'Tidak bisa menghubungi server. Periksa koneksi lalu coba lagi.', lang);
    }
    if (s.contains('weak') || s.contains('password should be')) {
      return t('Use at least 6 characters for the password.',
          'Gunakan minimal 6 karakter untuk kata sandi.', lang);
    }
    return raw.length > 160 ? '${raw.substring(0, 160)}…' : raw;
  }

  Future<void> _google() async {
    setState(() => _message = null);
    final result = await AuthService.instance.signInWithGoogle();
    if (!mounted || result == null) return;
    setState(() => _message = switch (result) {
      'login_unavailable' => t('Login is not configured in this build.',
          'Login belum dikonfigurasi pada build ini.', langOf(context)),
      'oauth_launch_failed' => t('Could not open the Google sign-in page.',
          'Gagal membuka halaman masuk Google.', langOf(context)),
      _ => _friendly(result, langOf(context)),
    });
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.read<AppState>().lang;
    return Scaffold(
      appBar: AppBar(
        title: Text(t('Sign in', 'Masuk', lang)),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 22, 18, 40),
        children: [
          ListenableBuilder(
            listenable: AuthService.instance,
            builder: (context, _) {
              final signedIn = AuthService.instance.signedIn;
              if (!signedIn) return const SizedBox.shrink();
              return Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: CardSurface(
                  child: Text(
                    '${t('Signed in as', 'Masuk sebagai', lang)} ${AuthService.instance.email ?? ''}',
                    style: HText.bodySm.copyWith(color: p.textPrimary),
                  ),
                ),
              );
            },
          ),
          CardSurface(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  t(_register ? 'Create account' : 'Welcome back',
                      _register ? 'Buat akun' : 'Selamat datang kembali', lang),
                  style: HText.h2.copyWith(color: p.textPrimary),
                ),
                const SizedBox(height: 6),
                Text(
                  t('Your sign-in is handled by Supabase Auth.',
                      'Proses masuk ditangani oleh Supabase Auth.', lang),
                  style: HText.bodySm.copyWith(color: p.textMuted),
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: _email,
                  keyboardType: TextInputType.emailAddress,
                  autocorrect: false,
                  decoration: InputDecoration(
                    labelText: t('Email', 'Email', lang),
                    prefixIcon: const Icon(Icons.mail_outline_rounded),
                    border: const OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _password,
                  obscureText: _obscure,
                  decoration: InputDecoration(
                    labelText: t('Password', 'Kata sandi', lang),
                    prefixIcon: const Icon(Icons.lock_outline_rounded),
                    suffixIcon: IconButton(
                      icon: Icon(_obscure
                          ? Icons.visibility_outlined
                          : Icons.visibility_off_outlined),
                      onPressed: () => setState(() => _obscure = !_obscure),
                    ),
                    border: const OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 18),
                ListenableBuilder(
                  listenable: AuthService.instance,
                  builder: (context, _) => PrimaryButton(
                    label: _register
                        ? t('Create account', 'Daftar', lang)
                        : t('Sign in', 'Masuk', lang),
                    icon: Icons.login_rounded,
                    onTap: AuthService.instance.busy ? () {} : _submit,
                  ),
                ),
                const SizedBox(height: 12),
                SecondaryButton(
                  label: t('Continue with Google', 'Lanjut dengan Google', lang),
                  icon: Icons.g_mobiledata_rounded,
                  expand: true,
                  onTap: _google,
                ),
                if (_message != null) ...[
                  const SizedBox(height: 14),
                  Text(_message!, style: HText.bodySm.copyWith(color: p.gold)),
                ],
                const SizedBox(height: 16),
                Center(
                  child: TextButton(
                    onPressed: () => setState(() {
                      _register = !_register;
                      _message = null;
                    }),
                    child: Text(
                      _register
                          ? t('Already have an account? Sign in',
                              'Sudah punya akun? Masuk', lang)
                          : t('No account yet? Register',
                              'Belum punya akun? Daftar', lang),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Text(
            t('After signing in, bookmarks and last-read positions are copied to your account so another device continues where you left off. Without an account everything stays on this device.',
                'Setelah masuk, bookmark dan posisi bacaan terakhir tersalin ke akun sehingga perangkat lain melanjutkan dari titik yang sama. Tanpa akun, semuanya tetap di perangkat ini.',
                lang),
            style: HText.labelSm.copyWith(color: p.textMuted, height: 1.5),
          ),
        ],
      ),
    );
  }
}

String langOf(BuildContext context) => context.read<AppState>().lang;
