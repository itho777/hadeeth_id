import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../state/app_state.dart';
import '../theme.dart';
import 'widgets.dart';

/// The donation panel, matching the one on tafseer.id: QRIS for IDR, a BEP20
/// address with its QR for USDT, and a tap-to-copy on the address.
const String kBnbAddress = '0x48dba8551b9c7270ba98eb7667444bcbb216ed95';

Future<void> showDonateSheet(BuildContext context) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => const _DonateSheet(),
  );
}

class _DonateSheet extends StatelessWidget {
  const _DonateSheet();

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.watch<AppState>().lang;
    return DraggableScrollableSheet(
      initialChildSize: 0.86,
      minChildSize: 0.5,
      maxChildSize: 0.94,
      expand: false,
      builder: (context, scroll) => Container(
        decoration: BoxDecoration(
          color: p.surface,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          border: Border.all(color: p.border),
        ),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(18, 12, 12, 6),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      t('Support hadeeth.id', 'Dukung hadeeth.id', lang),
                      style: HText.h3.copyWith(fontSize: 15, color: p.textPrimary),
                    ),
                  ),
                  GestureDetector(
                    onTap: () => Navigator.of(context).pop(),
                    child: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(9), border: Border.all(color: p.border)),
                      child: Icon(Icons.close_rounded, size: 16, color: p.textMuted),
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView(
                controller: scroll,
                padding: const EdgeInsets.fromLTRB(18, 4, 18, 24),
                children: [
                  Text(
                    t(
                      'This app is free and ad-free. Your support helps keep it alive. JazakAllah khairan!',
                      'Aplikasi ini gratis dan tanpa iklan. Dukungan Anda membuatnya tetap hidup. Jazakallahu khairan!',
                      lang,
                    ),
                    textAlign: TextAlign.center,
                    style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.5),
                  ),
                  const SizedBox(height: 18),
                  _panel(
                    context,
                    title: t('Donation (IDR)', 'Donasi (IDR)', lang),
                    note: t('Scan via GoPay, OVO, Dana, QRIS', 'Pindai via GoPay, OVO, Dana, QRIS', lang),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.asset('assets/images/qr_qris.jpg', width: 220, height: 220, fit: BoxFit.contain),
                    ),
                  ),
                  const SizedBox(height: 14),
                  _panel(
                    context,
                    title: t('Donate (USDT)', 'Donasi (USDT)', lang),
                    note: 'BNB Smart Chain (BEP20)',
                    child: Column(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.asset('assets/images/qr_bnb.png', width: 180, height: 180, fit: BoxFit.contain),
                        ),
                        const SizedBox(height: 12),
                        GestureDetector(
                          onTap: () async {
                            await Clipboard.setData(const ClipboardData(text: kBnbAddress));
                            if (context.mounted) showSnack(context, t('Address copied', 'Alamat disalin', lang));
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 10),
                            decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(8), border: Border.all(color: p.border)),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    kBnbAddress,
                                    style: HText.labelSm.copyWith(color: p.textPrimary, fontSize: 9.5, height: 1.3),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Icon(Icons.copy_all_outlined, size: 14, color: p.textMuted),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    t('May Allah reward you abundantly', 'Semoga Allah membalas Anda dengan berlimpah', lang),
                    textAlign: TextAlign.center,
                    style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10, fontStyle: FontStyle.italic),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _panel(BuildContext context, {required String title, required String note, required Widget child}) {
    final p = context.p;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(12), border: Border.all(color: p.border)),
      child: Column(
        children: [
          Text(title, style: HText.body.copyWith(color: p.textPrimary, fontWeight: FontWeight.w700, fontSize: 13)),
          const SizedBox(height: 3),
          Text(note, style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5)),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }
}
