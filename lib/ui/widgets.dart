import 'package:flutter/material.dart';

import '../theme.dart';

/// English / Indonesian string switch — the UI ships in both languages like the
/// web app. `t('Hello','Halo', lang)`.
String t(String en, String id, [String? lang]) => (lang ?? _activeLang) == 'id' ? id : en;

/// Fallback language for call sites that sit outside a widget build and cannot
/// read [AppState] directly. Kept in sync by [AppShell] on every rebuild.
String _activeLang = 'id';
void setActiveLang(String lang) => _activeLang = lang;

String formatNumber(int n) {
  final s = n.toString();
  final b = StringBuffer();
  for (var i = 0; i < s.length; i++) {
    if (i > 0 && (s.length - i) % 3 == 0) b.write(',');
    b.write(s[i]);
  }
  return b.toString();
}

String formatBytes(int bytes) {
  if (bytes <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  var value = bytes.toDouble();
  var unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit++;
  }
  return '${value.toStringAsFixed(value >= 100 ? 0 : 1)} ${units[unit]}';
}

String formatWhen(DateTime dt, String lang) {
  final now = DateTime.now();
  final diff = now.difference(dt);
  if (diff.inMinutes < 1) return lang == 'id' ? 'baru saja' : 'just now';
  if (diff.inMinutes < 60) return lang == 'id' ? '${diff.inMinutes} menit lalu' : '${diff.inMinutes}m ago';
  if (diff.inHours < 24) return lang == 'id' ? '${diff.inHours} jam lalu' : '${diff.inHours}h ago';
  if (diff.inDays < 7) return lang == 'id' ? '${diff.inDays} hari lalu' : '${diff.inDays}d ago';
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return '${dt.day} ${months[dt.month - 1]} ${dt.year}';
}

/// Tabular Islamic (Umm al-Qura approximation) date — the home header shows the
/// Hijri line next to the Gregorian one, same as the web landing page.
({String hijri, String gregorian}) todayDates(String lang) {
  final now = DateTime.now();
  const gMonths = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const gMonthsId = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
  const gDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const gDaysId = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
  final g = lang == 'id'
      ? '${gDaysId[now.weekday - 1]}, ${now.day} ${gMonthsId[now.month - 1]} ${now.year}'
      : '${gDays[now.weekday - 1]}, ${gMonths[now.month - 1]} ${now.day}, ${now.year}';

  final jd = now.millisecondsSinceEpoch ~/ 86400000 + 2440588;
  final l = jd - 1948440 + 10631;
  final n = (l - 1) ~/ 10631;
  final l2 = l - 10631 * n + 354;
  final j = ((10985 - l2) ~/ 5316) * ((50 * l2) ~/ 17719) + (l2 ~/ 5670) * ((43 * l2) ~/ 15238);
  final l3 = l2 - ((30 - j) ~/ 15) * ((17719 * j) ~/ 50) - (j ~/ 16) * ((15238 * j) ~/ 43) + 29;
  final month = (24 * l3) ~/ 709;
  final day = l3 - ((709 * month) ~/ 24);
  final year = (30 * n + j) - 30;
  const hMonths = ['Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Akhir", 'Jumada al-Awwal', 'Jumada al-Akhir', 'Rajab', "Sha'ban", 'Ramadan', 'Shawwal', "Dhul-Qa'dah", 'Dhul-Hijjah'];
  return (hijri: '$day ${hMonths[(month - 1).clamp(0, 11)]} $year H', gregorian: g);
}

class SectionLabel extends StatelessWidget {
  const SectionLabel({super.key, required this.text, this.actionLabel, this.onAction, this.icon});

  final String text;
  final String? actionLabel;
  final VoidCallback? onAction;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return Row(
      children: [
        if (icon != null) ...[
          Icon(icon, size: 15, color: p.gold),
          const SizedBox(width: 7),
        ],
        Expanded(
          child: Text(text, style: HText.label.copyWith(color: p.gold)),
        ),
        if (actionLabel != null)
          GestureDetector(
            onTap: onAction,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(actionLabel!, style: HText.labelSm.copyWith(color: p.emerald, fontSize: 11)),
                const SizedBox(width: 3),
                Icon(Icons.arrow_forward_rounded, size: 13, color: p.emerald),
              ],
            ),
          ),
      ],
    );
  }
}

class CardSurface extends StatelessWidget {
  const CardSurface({super.key, required this.child, this.padding = const EdgeInsets.all(16), this.radius = 18, this.onTap, this.onLongPress, this.color, this.border});

  final Widget child;
  final EdgeInsetsGeometry padding;
  final double radius;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final Color? color;
  final BoxBorder? border;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final card = Container(
      padding: padding,
      decoration: BoxDecoration(
        color: color ?? p.card,
        borderRadius: BorderRadius.circular(radius),
        border: border ?? Border.all(color: p.border),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: p.dark ? 0.22 : 0.035), blurRadius: 18, offset: const Offset(0, 8)),
        ],
      ),
      child: Material(type: MaterialType.transparency, child: child),
    );
    if (onTap == null && onLongPress == null) return card;
    return GestureDetector(onTap: onTap, onLongPress: onLongPress, child: card);
  }
}

class GradeBadge extends StatelessWidget {
  const GradeBadge({super.key, required this.label, this.tier = 'unknown', this.small = false});

  final String label;
  final String tier;
  final bool small;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final color = switch (tier) {
      'sahih' => Brand.sahih,
      'hasan' => Brand.hasan,
      'daif' => Brand.daif,
      // Registry classification (Jami', Sunan, Musnad…): a neutral tag, so it
      // never reads as an authenticity grade.
      'class' => p.textMuted,
      _ => p.gold,
    };
    return Container(
      padding: EdgeInsets.symmetric(horizontal: small ? 7 : 9, vertical: small ? 3 : 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: p.dark ? 0.16 : 0.11),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Text(
        label,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        style: HText.labelSm.copyWith(fontSize: small ? 9 : 10.5, color: color),
      ),
    );
  }
}

class ArabicBlock extends StatelessWidget {
  const ArabicBlock({super.key, required this.text, this.size, this.align = TextAlign.right, this.color, this.italic = false});

  final String text;
  final double? size;
  final TextAlign align;
  final Color? color;
  final bool italic;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Text(
        text.isEmpty ? '—' : text,
        textAlign: align,
        style: HText.arabic(size ?? 27).copyWith(color: color ?? p.textPrimary),
      ),
    );
  }
}

class EmptyState extends StatelessWidget {
  const EmptyState({super.key, required this.icon, required this.title, required this.message, this.action});

  final IconData icon;
  final String title;
  final String message;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 48),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 62,
              height: 62,
              decoration: BoxDecoration(
                color: p.surfaceLow,
                shape: BoxShape.circle,
                border: Border.all(color: p.border),
              ),
              child: Icon(icon, color: p.textMuted, size: 28),
            ),
            const SizedBox(height: 14),
            Text(title, style: HText.h3.copyWith(color: p.textPrimary), textAlign: TextAlign.center),
            const SizedBox(height: 6),
            Text(message, style: HText.bodySm.copyWith(color: p.textMuted), textAlign: TextAlign.center),
            if (action != null) ...[const SizedBox(height: 16), action!],
          ],
        ),
      ),
    );
  }
}

class LoadingBlock extends StatelessWidget {
  const LoadingBlock({super.key, this.message});

  final String? message;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(width: 26, height: 26, child: CircularProgressIndicator(strokeWidth: 2.4, color: p.emerald)),
            if (message != null) ...[
              const SizedBox(height: 14),
              Text(message!, style: HText.bodySm.copyWith(color: p.textMuted)),
            ],
          ],
        ),
      ),
    );
  }
}

class PrimaryButton extends StatelessWidget {
  const PrimaryButton({super.key, required this.label, required this.onTap, this.icon, this.expand = true, this.tone});

  final String label;
  final VoidCallback onTap;
  final IconData? icon;
  final bool expand;
  final Color? tone;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final bg = tone ?? p.primary;
    final fg = tone == null ? p.onPrimary : (p.dark ? Brand.darkCanvas : Colors.white);
    final btn = FilledButton.icon(
      style: FilledButton.styleFrom(
        backgroundColor: bg,
        foregroundColor: fg,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 13),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        textStyle: HText.body.copyWith(fontWeight: FontWeight.w700, fontSize: 13.5),
      ),
      onPressed: onTap,
      icon: icon == null ? const SizedBox.shrink() : Icon(icon, size: 17),
      label: Text(label),
    );
    return expand ? SizedBox(width: double.infinity, child: btn) : btn;
  }
}

class SecondaryButton extends StatelessWidget {
  const SecondaryButton({super.key, required this.label, required this.onTap, this.icon, this.expand = false});

  final String label;
  final VoidCallback onTap;
  final IconData? icon;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final btn = OutlinedButton.icon(
      style: OutlinedButton.styleFrom(
        foregroundColor: p.textPrimary,
        side: BorderSide(color: p.border),
        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 11),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
        textStyle: HText.body.copyWith(fontWeight: FontWeight.w600, fontSize: 13),
      ),
      onPressed: onTap,
      icon: icon == null ? const SizedBox.shrink() : Icon(icon, size: 16),
      label: Text(label),
    );
    return expand ? SizedBox(width: double.infinity, child: btn) : btn;
  }
}

class ChipButton extends StatelessWidget {
  const ChipButton({super.key, required this.label, required this.selected, required this.onTap, this.count});

  final String label;
  final bool selected;
  final VoidCallback onTap;
  final int? count;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? (p.dark ? Brand.emeraldBright : Brand.ink) : p.surfaceLow,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: selected ? (p.dark ? Brand.emeraldBright : Brand.ink) : p.border),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: HText.labelSm.copyWith(
                fontSize: 11,
                color: selected ? (p.dark ? Brand.darkCanvas : Colors.white) : p.textSecondary,
              ),
            ),
            if (count != null) ...[
              const SizedBox(width: 6),
              Text(
                formatNumber(count!),
                style: HText.labelSm.copyWith(
                  fontSize: 10,
                  color: selected ? (p.dark ? Brand.darkCanvas : Colors.white).withValues(alpha: 0.8) : p.textMuted,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class BrandLogo extends StatelessWidget {
  const BrandLogo({super.key, this.height = 30, this.rounded = true});

  final double height;
  final bool rounded;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return ClipRRect(
      borderRadius: rounded ? BorderRadius.circular(9) : BorderRadius.zero,
      child: Image.asset(
        p.dark ? 'assets/images/logo_dark.jpg' : 'assets/images/logo_light.jpg',
        height: height,
        width: height,
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => Container(
          height: height,
          width: height,
          color: p.surfaceHigh,
          child: Icon(Icons.menu_book_outlined, size: height * 0.6, color: p.gold),
        ),
      ),
    );
  }
}

class PageHeader extends StatelessWidget implements PreferredSizeWidget {
  const PageHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.actions = const [],
    this.showLogo = true,
    this.leading,
  });

  final String title;
  final String? subtitle;
  final List<Widget> actions;
  final bool showLogo;
  final Widget? leading;

  @override
  Size get preferredSize => const Size.fromHeight(74);

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      decoration: BoxDecoration(color: p.canvas, border: Border(bottom: BorderSide(color: p.border))),
      child: Row(
        children: [
          if (leading != null) ...[leading!, const SizedBox(width: 10)] else if (showLogo) ...[const BrandLogo(height: 34), const SizedBox(width: 10)],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(title, style: HText.h3.copyWith(fontSize: 18), maxLines: 1, overflow: TextOverflow.ellipsis),
                if (subtitle != null)
                  Text(subtitle!, style: HText.labelSm.copyWith(color: p.textMuted, letterSpacing: 0.6), maxLines: 1, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
          ...actions,
        ],
      ),
    );
  }
}

class BackButton2 extends StatelessWidget {
  const BackButton2({super.key, this.onTap});

  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return GestureDetector(
      onTap: onTap ?? () => Navigator.of(context).maybePop(),
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(11), border: Border.all(color: p.border)),
        child: Icon(Icons.arrow_back_rounded, size: 18, color: p.textPrimary),
      ),
    );
  }
}

class LangToggle extends StatelessWidget {
  const LangToggle({super.key, required this.lang, required this.onChanged});

  final String lang;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    Widget pill(String code) {
      final active = lang == code;
      return GestureDetector(
        onTap: () => onChanged(code),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: active ? (p.dark ? Brand.emeraldBright : Brand.ink) : Colors.transparent,
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            code.toUpperCase(),
            style: HText.labelSm.copyWith(fontSize: 10, color: active ? (p.dark ? Brand.darkCanvas : Colors.white) : p.textMuted),
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(999), border: Border.all(color: p.border)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [pill('en'), pill('id')]),
    );
  }
}

class IconPill extends StatelessWidget {
  const IconPill({super.key, required this.icon, required this.onTap, this.active = false, this.tooltip});

  final IconData icon;
  final VoidCallback onTap;
  final bool active;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final child = GestureDetector(
      onTap: onTap,
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: active ? (p.dark ? Brand.emeraldBright.withValues(alpha: 0.18) : Brand.ink.withValues(alpha: 0.08)) : p.surfaceLow,
          borderRadius: BorderRadius.circular(11),
          border: Border.all(color: p.border),
        ),
        child: Icon(icon, size: 18, color: active ? (p.dark ? Brand.emeraldBright : Brand.ink) : p.textSecondary),
      ),
    );
    return tooltip == null ? child : Tooltip(message: tooltip!, child: child);
  }
}

/// Small uppercase meta line, e.g. "SAHIH AL-BUKHARI • #1".
class MetaLine extends StatelessWidget {
  const MetaLine({super.key, required this.text, this.color});

  final String text;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    return Text(text, style: HText.labelSm.copyWith(fontSize: 9.5, color: color ?? p.textMuted, letterSpacing: 0.8), maxLines: 1, overflow: TextOverflow.ellipsis);
  }
}

void showSnack(BuildContext context, String message) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
}