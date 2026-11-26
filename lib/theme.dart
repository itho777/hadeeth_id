import 'package:flutter/material.dart';

/// Exact palette taken from the live hadeeth.id stylesheet (css/app.css +
/// the Tailwind token map in index.html): manuscript-paper light mode and the
/// ink-black / slate dark mode, with the emerald + gold accents.
class Brand {
  static const ink = Color(0xFF001932);
  static const inkBlack = Color(0xFF0D0D10);
  static const manuscript = Color(0xFFFDFBF7);
  static const paper = Color(0xFFFCF9F5);
  static const paperLow = Color(0xFFF6F3EF);
  static const paperContainer = Color(0xFFF0EDE9);
  static const paperHigh = Color(0xFFEAE8E4);
  static const paperHighest = Color(0xFFE5E2DE);
  static const outlineLight = Color(0xFFC3C6CF);
  static const outlineMid = Color(0xFF73777F);
  static const textLight = Color(0xFF1C1C1A);
  static const textMutedLight = Color(0xFF43474E);

  static const emerald = Color(0xFF1B5E20);
  static const emeraldBright = Color(0xFF10B981);
  static const gold = Color(0xFF7B5810);
  static const goldLight = Color(0xFFE8D5A3);
  static const goldSoft = Color(0xFFFDCD7B);
  static const indigo = Color(0xFF311B92);

  static const darkCanvas = Color(0xFF0D0D10);
  static const darkNav = Color(0xFF10141A);
  static const darkCard = Color(0xFF1E293B);
  static const darkPanel = Color(0xFF0F172A);
  static const darkElevated = Color(0xFF1E293B);
  static const darkBorder = Color(0xFF334155);
  static const darkText = Color(0xFFF8FAFC);
  static const darkTextSecondary = Color(0xFFD1D5DB);
  static const darkTextMuted = Color(0xFF9CA3AF);

  static const sahih = Color(0xFF10B981);
  static const hasan = Color(0xFFF59E0B);
  static const daif = Color(0xFFEF4444);

  static const arabicFamily = 'Amiri';
  static const latinFamily = 'PlusJakartaSans';
}

@immutable
class HP extends ThemeExtension<HP> {
  const HP({
    required this.dark,
    required this.canvas,
    required this.surface,
    required this.surfaceLow,
    required this.surfaceContainer,
    required this.surfaceHigh,
    required this.card,
    required this.panel,
    required this.border,
    required this.divider,
    required this.primary,
    required this.onPrimary,
    required this.gold,
    required this.goldSoft,
    required this.emerald,
    required this.indigo,
    required this.textPrimary,
    required this.textSecondary,
    required this.textMuted,
    required this.outline,
    required this.navBackground,
  });

  final bool dark;
  final Color canvas;
  final Color surface;
  final Color surfaceLow;
  final Color surfaceContainer;
  final Color surfaceHigh;
  final Color card;
  final Color panel;
  final Color border;
  final Color divider;
  final Color primary;
  final Color onPrimary;
  final Color gold;
  final Color goldSoft;
  final Color emerald;
  final Color indigo;
  final Color textPrimary;
  final Color textSecondary;
  final Color textMuted;
  final Color outline;
  final Color navBackground;

  static const light = HP(
    dark: false,
    canvas: Brand.manuscript,
    surface: Brand.paper,
    surfaceLow: Brand.paperLow,
    surfaceContainer: Brand.paperContainer,
    surfaceHigh: Brand.paperHigh,
    card: Color(0xFFFFFFFF),
    panel: Color(0xFFFFFFFF),
    border: Brand.paperHighest,
    divider: Brand.paperHigh,
    primary: Brand.ink,
    onPrimary: Color(0xFFFFFFFF),
    gold: Brand.gold,
    goldSoft: Brand.goldLight,
    emerald: Brand.emerald,
    indigo: Brand.indigo,
    textPrimary: Brand.textLight,
    textSecondary: Brand.textMutedLight,
    textMuted: Brand.outlineMid,
    outline: Brand.outlineLight,
    navBackground: Color(0xFFFFFFFF),
  );

  static const darkPalette = HP(
    dark: true,
    canvas: Brand.darkCanvas,
    surface: Brand.darkNav,
    surfaceLow: Brand.darkPanel,
    surfaceContainer: Color(0xFF131A24),
    surfaceHigh: Brand.darkElevated,
    card: Brand.darkCard,
    panel: Brand.darkPanel,
    border: Brand.darkBorder,
    divider: Brand.darkElevated,
    primary: Brand.emeraldBright,
    onPrimary: Color(0xFF06110D),
    gold: Color(0xFFE8D5A3),
    goldSoft: Color(0xFFFDCD7B),
    emerald: Brand.emeraldBright,
    indigo: Color(0xFFB7C4FF),
    textPrimary: Brand.darkText,
    textSecondary: Brand.darkTextSecondary,
    textMuted: Brand.darkTextMuted,
    outline: Color(0xFF475569),
    navBackground: Brand.darkNav,
  );

  @override
  HP copyWith({
    bool? dark,
    Color? canvas,
    Color? surface,
    Color? surfaceLow,
    Color? surfaceContainer,
    Color? surfaceHigh,
    Color? card,
    Color? panel,
    Color? border,
    Color? divider,
    Color? primary,
    Color? onPrimary,
    Color? gold,
    Color? goldSoft,
    Color? emerald,
    Color? indigo,
    Color? textPrimary,
    Color? textSecondary,
    Color? textMuted,
    Color? outline,
    Color? navBackground,
  }) {
    return HP(
      dark: dark ?? this.dark,
      canvas: canvas ?? this.canvas,
      surface: surface ?? this.surface,
      surfaceLow: surfaceLow ?? this.surfaceLow,
      surfaceContainer: surfaceContainer ?? this.surfaceContainer,
      surfaceHigh: surfaceHigh ?? this.surfaceHigh,
      card: card ?? this.card,
      panel: panel ?? this.panel,
      border: border ?? this.border,
      divider: divider ?? this.divider,
      primary: primary ?? this.primary,
      onPrimary: onPrimary ?? this.onPrimary,
      gold: gold ?? this.gold,
      goldSoft: goldSoft ?? this.goldSoft,
      emerald: emerald ?? this.emerald,
      indigo: indigo ?? this.indigo,
      textPrimary: textPrimary ?? this.textPrimary,
      textSecondary: textSecondary ?? this.textSecondary,
      textMuted: textMuted ?? this.textMuted,
      outline: outline ?? this.outline,
      navBackground: navBackground ?? this.navBackground,
    );
  }

  @override
  HP lerp(ThemeExtension<HP>? other, double t) {
    if (other is! HP) return this;
    Color c(Color a, Color b) => Color.lerp(a, b, t)!;
    return HP(
      dark: t < 0.5 ? dark : other.dark,
      canvas: c(canvas, other.canvas),
      surface: c(surface, other.surface),
      surfaceLow: c(surfaceLow, other.surfaceLow),
      surfaceContainer: c(surfaceContainer, other.surfaceContainer),
      surfaceHigh: c(surfaceHigh, other.surfaceHigh),
      card: c(card, other.card),
      panel: c(panel, other.panel),
      border: c(border, other.border),
      divider: c(divider, other.divider),
      primary: c(primary, other.primary),
      onPrimary: c(onPrimary, other.onPrimary),
      gold: c(gold, other.gold),
      goldSoft: c(goldSoft, other.goldSoft),
      emerald: c(emerald, other.emerald),
      indigo: c(indigo, other.indigo),
      textPrimary: c(textPrimary, other.textPrimary),
      textSecondary: c(textSecondary, other.textSecondary),
      textMuted: c(textMuted, other.textMuted),
      outline: c(outline, other.outline),
      navBackground: c(navBackground, other.navBackground),
    );
  }
}

/// Shorthand used across the UI: `context.p.<token>`.
extension PaletteContext on BuildContext {
  HP get p => Theme.of(this).extension<HP>() ?? HP.light;
  bool get isDark => Theme.of(this).brightness == Brightness.dark;
}

class HText {
  static const _family = Brand.latinFamily;

  static const display = TextStyle(fontFamily: _family, fontSize: 30, height: 1.18, fontWeight: FontWeight.w700, letterSpacing: -0.6);
  static const h1 = TextStyle(fontFamily: _family, fontSize: 26, height: 1.22, fontWeight: FontWeight.w700, letterSpacing: -0.4);
  static const h2 = TextStyle(fontFamily: _family, fontSize: 21, height: 1.28, fontWeight: FontWeight.w700, letterSpacing: -0.2);
  static const h3 = TextStyle(fontFamily: _family, fontSize: 17, height: 1.32, fontWeight: FontWeight.w600);
  static const body = TextStyle(fontFamily: _family, fontSize: 14.5, height: 1.55, fontWeight: FontWeight.w400);
  static const bodySm = TextStyle(fontFamily: _family, fontSize: 12.5, height: 1.5, fontWeight: FontWeight.w400);
  static const label = TextStyle(fontFamily: _family, fontSize: 11, height: 1.25, fontWeight: FontWeight.w700, letterSpacing: 1.1);
  static const labelSm = TextStyle(fontFamily: _family, fontSize: 10, height: 1.2, fontWeight: FontWeight.w700, letterSpacing: 0.9);

  static TextStyle arabic(double size, {FontWeight weight = FontWeight.w400}) => TextStyle(
        fontFamily: Brand.arabicFamily,
        fontSize: size,
        height: 1.95,
        fontWeight: weight,
        color: null,
      );
}

ThemeData buildTheme(HP p) {
  final scheme = ColorScheme(
    brightness: p.dark ? Brightness.dark : Brightness.light,
    primary: p.primary,
    onPrimary: p.onPrimary,
    secondary: p.gold,
    onSecondary: p.dark ? Brand.darkCanvas : Colors.white,
    tertiary: p.indigo,
    onTertiary: Colors.white,
    error: Brand.daif,
    onError: Colors.white,
    surface: p.canvas,
    onSurface: p.textPrimary,
    surfaceContainerHighest: p.surfaceHigh,
    onSurfaceVariant: p.textSecondary,
    outline: p.outline,
    outlineVariant: p.border,
    shadow: Color(0xFF000000),
    scrim: Color(0xFF000000),
    inverseSurface: p.dark ? Brand.manuscript : Brand.ink,
    onInverseSurface: p.dark ? Brand.ink : Brand.manuscript,
  );

  return ThemeData(
    useMaterial3: true,
    brightness: p.dark ? Brightness.dark : Brightness.light,
    colorScheme: scheme,
    scaffoldBackgroundColor: p.canvas,
    fontFamily: Brand.latinFamily,
    splashFactory: InkSparkle.splashFactory,
    extensions: <ThemeExtension<dynamic>>[p],
    textTheme: TextTheme(
      displayLarge: HText.display.copyWith(color: p.textPrimary),
      headlineLarge: HText.h1.copyWith(color: p.textPrimary),
      headlineMedium: HText.h2.copyWith(color: p.textPrimary),
      headlineSmall: HText.h3.copyWith(color: p.textPrimary),
      titleLarge: HText.h3.copyWith(color: p.textPrimary),
      titleMedium: HText.h3.copyWith(fontSize: 15).copyWith(color: p.textPrimary),
      bodyLarge: HText.body.copyWith(color: p.textPrimary),
      bodyMedium: HText.body.copyWith(color: p.textSecondary),
      bodySmall: HText.bodySm.copyWith(color: p.textMuted),
      labelLarge: HText.label.copyWith(color: p.gold),
      labelMedium: HText.labelSm.copyWith(color: p.textMuted),
      labelSmall: HText.labelSm.copyWith(color: p.textMuted),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: p.canvas,
      surfaceTintColor: Colors.transparent,
      foregroundColor: p.textPrimary,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: HText.h3.copyWith(color: p.textPrimary),
    ),
    dividerTheme: DividerThemeData(color: p.divider, thickness: 1, space: 1),
    cardTheme: CardThemeData(
      color: p.card,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: p.border),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: p.surfaceLow,
      hintStyle: HText.bodySm.copyWith(color: p.textMuted),
      prefixIconColor: p.textMuted,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: p.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: p.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: p.dark ? Brand.emeraldBright : Brand.ink, width: 1.4),
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: p.surfaceLow,
      selectedColor: p.dark ? Brand.emeraldBright : Brand.ink,
      labelStyle: HText.bodySm.copyWith(color: p.textSecondary, fontWeight: FontWeight.w600),
      secondaryLabelStyle: HText.bodySm.copyWith(color: p.dark ? Brand.darkCanvas : Colors.white, fontWeight: FontWeight.w700),
      side: BorderSide(color: p.border),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: p.navBackground,
      surfaceTintColor: Colors.transparent,
      indicatorColor: (p.dark ? Brand.emeraldBright : Brand.ink).withValues(alpha: 0.10),
      height: 66,
      labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      iconTheme: WidgetStateProperty.resolveWith((states) {
        final selected = states.contains(WidgetState.selected);
        return IconThemeData(size: 23, color: selected ? (p.dark ? Brand.emeraldBright : Brand.ink) : p.textMuted);
      }),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        final selected = states.contains(WidgetState.selected);
        return HText.labelSm.copyWith(
          fontSize: 9.5,
          letterSpacing: 0.4,
          color: selected ? (p.dark ? Brand.emeraldBright : Brand.ink) : p.textMuted,
        );
      }),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: p.dark ? Brand.darkElevated : Brand.ink,
      contentTextStyle: HText.bodySm.copyWith(color: Colors.white),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
    bottomSheetTheme: BottomSheetThemeData(
      backgroundColor: p.card,
      surfaceTintColor: Colors.transparent,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(22))),
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: p.card,
      surfaceTintColor: Colors.transparent,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
    ),
    sliderTheme: SliderThemeData(
      activeTrackColor: p.dark ? Brand.emeraldBright : Brand.ink,
      thumbColor: p.dark ? Brand.emeraldBright : Brand.ink,
      inactiveTrackColor: p.border,
    ),
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((s) => s.contains(WidgetState.selected) ? Colors.white : p.textMuted),
      trackColor: WidgetStateProperty.resolveWith((s) => s.contains(WidgetState.selected) ? (p.dark ? Brand.emeraldBright : Brand.emerald) : p.surfaceHigh),
    ),
  );
}
