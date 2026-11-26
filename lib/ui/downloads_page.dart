import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/download_service.dart';
import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'widgets.dart';

class DownloadsPage extends StatefulWidget {
  const DownloadsPage({super.key});

  @override
  State<DownloadsPage> createState() => _DownloadsPageState();
}

class _DownloadsPageState extends State<DownloadsPage> {
  final Map<String, double> _progress = {};
  final Set<String> _working = {};
  List<Book> _books = [];
  bool _loading = true;
  int _bytes = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final books = await context.read<HadeethRepository>().books();
      final bytes = await context.read<DownloadService>().storageBytes();
      if (!mounted) return;
      setState(() {
        _books = books;
        _bytes = bytes;
        _loading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _download(Book book) async {
    final service = context.read<DownloadService>();
    setState(() {
      _working.add(book.id);
      _progress[book.id] = 0;
    });
    try {
      final info = await service.downloadBook(book, onProgress: (v) {
        if (mounted) setState(() => _progress[book.id] = v);
      });
      if (!mounted) return;
      context.read<HadeethRepository>().downloaded.add(book.id);
      await context.read<AppState>().setDownload(info);
      setState(() {
        _working.remove(book.id);
        _progress[book.id] = 1;
        _bytes += info.bytes;
      });
      showSnack(context, '${book.title(context.read<AppState>().lang)} ${t('ready offline', 'siap luring', context.read<AppState>().lang)}');
    } catch (e) {
      if (!mounted) return;
      setState(() => _working.remove(book.id));
      showSnack(context, 'Download failed: $e');
    }
  }

  Future<void> _remove(Book book, AppState state) async {
    final service = context.read<DownloadService>();
    await service.deleteBook(book.id);
    if (!mounted) return;
    context.read<HadeethRepository>().downloaded.remove(book.id);
    await state.removeDownload(book.id);
    final bytes = await service.storageBytes();
    if (mounted) setState(() => _bytes = bytes);
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final state = context.watch<AppState>();
    final lang = state.lang;
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: t('Offline library', 'Pustaka luring', lang),
              subtitle: '${formatBytes(_bytes)} ${t('STORED ON DEVICE', 'TERSIMPAN DI PERANGKAT')}',
              showLogo: false,
              leading: const BackButton2(),
            ),
            Expanded(
              child: _loading
                  ? const LoadingBlock(message: 'Checking local storage…')
                  : ListView(
                      padding: const EdgeInsets.fromLTRB(16, 14, 16, 28),
                      children: [
                        CardSurface(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              SectionLabel(icon: Icons.download_done_outlined, text: t('HOW OFFLINE READING WORKS', 'CARA BACA LURING')),
                              const SizedBox(height: 10),
                              Text(
                                t(
                                  'Each download keeps the chapter index and matn rows on device. Reading, citation and keyword search then work without a connection; AI search and Razi still need the network.',
                                  'Setiap unduhan menyimpan indeks bab dan teks matn di perangkat. Membaca, kutipan, dan pencarian kata kunci lalu bekerja tanpa koneksi; pencarian AI dan Razi tetap membutuhkan jaringan.',
                                  lang,
                                ),
                                style: HText.bodySm.copyWith(color: p.textMuted, height: 1.55),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 18),
                        SectionLabel(icon: Icons.menu_book_outlined, text: t('COLLECTIONS', 'KOLEKSI')),
                        const SizedBox(height: 10),
                        for (final book in _books) _tile(context, book, state, lang),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _tile(BuildContext context, Book book, AppState state, String lang) {
    final p = context.p;
    final done = state.downloads.containsKey(book.id);
    final working = _working.contains(book.id);
    final progress = _progress[book.id] ?? 0;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: CardSurface(
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(10), border: Border.all(color: p.border)),
                  alignment: Alignment.center,
                  child: Text(book.monogram, style: HText.label.copyWith(color: p.emerald)),
                ),
                const SizedBox(width: 11),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(book.title(lang), style: HText.h3.copyWith(color: p.textPrimary, fontSize: 13.5), maxLines: 1, overflow: TextOverflow.ellipsis),
                      const SizedBox(height: 3),
                      Text(
                        done ? formatBytes(state.downloads[book.id]!.bytes) : '${formatNumber(book.totalHadiths)} ${t('hadiths', 'hadis', lang)}',
                        style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5),
                      ),
                    ],
                  ),
                ),
                if (done && !working)
                  GestureDetector(
                    onTap: () => _remove(book, state),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
                      decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(9), border: Border.all(color: p.border)),
                      child: Text(t('Remove', 'Hapus', lang), style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5)),
                    ),
                  )
                else
                  GestureDetector(
                    onTap: working ? null : () => _download(book),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                      decoration: BoxDecoration(
                        color: p.dark ? Brand.emeraldBright : Brand.ink,
                        borderRadius: BorderRadius.circular(9),
                      ),
                      child: Text(
                        working ? '${(progress * 100).toInt()}%' : t('Download', 'Unduh', lang),
                        style: HText.labelSm.copyWith(color: p.dark ? Brand.darkCanvas : Colors.white, fontSize: 9.5),
                      ),
                    ),
                  ),
              ],
            ),
            if (working) ...[
              const SizedBox(height: 10),
              LinearProgressIndicator(value: progress, minHeight: 4, color: p.dark ? Brand.emeraldBright : Brand.emerald, backgroundColor: p.surfaceHigh),
            ],
            if (done)
              Padding(
                padding: const EdgeInsets.only(top: 9),
                child: Row(
                  children: [
                    Icon(Icons.offline_pin_rounded, size: 12, color: p.emerald),
                    const SizedBox(width: 4),
                    Text(t('Available offline', 'Tersedia luring', lang), style: HText.labelSm.copyWith(color: p.emerald, fontSize: 9.5)),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
