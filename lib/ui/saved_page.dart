import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'export_page.dart';
import 'hadith_detail_page.dart';
import 'widgets.dart';

class SavedPage extends StatefulWidget {
  const SavedPage({super.key});

  @override
  State<SavedPage> createState() => _SavedPageState();
}

class _SavedPageState extends State<SavedPage> {
  String _filter = 'All';
  String _query = '';
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final state = context.watch<AppState>();
    final lang = state.lang;
    final all = state.sortedBookmarks;
    final q = _query.toLowerCase();
    final items = all
        .where((b) => _filter == 'All' || b.collection == _filter)
        .where((b) => q.isEmpty || b.translation.toLowerCase().contains(q) || b.arabic.contains(_query) || b.bookTitle.toLowerCase().contains(q))
        .toList();

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: t('Saved', 'Simpanan', lang),
              subtitle: '${all.length} ${t('SAVED NARRATIONS', 'RIWAYAT TERSIMPAN', lang)}',
              actions: [
                IconPill(
                  icon: Icons.file_download_outlined,
                  tooltip: t('Export', 'Ekspor', lang),
                  onTap: all.isEmpty ? () {} : () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ExportPage(bookmarks: items.isEmpty ? all : items))),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
              child: TextField(
                controller: _controller,
                onChanged: (v) => setState(() => _query = v),
                style: HText.bodySm.copyWith(color: p.textPrimary),
                decoration: InputDecoration(
                  isDense: true,
                  hintText: t('Search saved hadith…', 'Cari hadis tersimpan…', lang),
                  hintStyle: HText.bodySm.copyWith(color: p.textMuted),
                  prefixIcon: Icon(Icons.search_rounded, size: 18, color: p.textMuted),
                  filled: true,
                  fillColor: p.surfaceLow,
                  contentPadding: const EdgeInsets.symmetric(vertical: 12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: p.border)),
                  enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: p.border)),
                  focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: p.emerald)),
                ),
              ),
            ),
            SizedBox(
              height: 52,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                children: [
                  ChipButton(label: t('All', 'Semua', lang), selected: _filter == 'All', count: all.length, onTap: () => setState(() => _filter = 'All')),
                  for (final c in state.collections) ...[
                    const SizedBox(width: 8),
                    ChipButton(
                      label: c,
                      selected: _filter == c,
                      count: all.where((b) => b.collection == c).length,
                      onTap: () => setState(() => _filter = c),
                    ),
                  ],
                  const SizedBox(width: 8),
                  ChipButton(label: '+ ${t('New', 'Baru', lang)}', selected: false, onTap: () => _newCollection(state, lang)),
                ],
              ),
            ),
            Expanded(
              child: items.isEmpty
                  ? EmptyState(
                      icon: Icons.bookmark_border_rounded,
                      title: t('Nothing saved yet', 'Belum ada simpanan', lang),
                      message: t('Bookmark a narration while reading and it will appear here, ready for study or export.', 'Tandai riwayat saat membaca dan ia akan muncul di sini, siap dipelajari atau diekspor.', lang),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.fromLTRB(16, 6, 16, 26),
                      itemCount: items.length,
                      itemBuilder: (context, i) => Padding(
                        padding: const EdgeInsets.only(bottom: 11),
                        child: _card(context, items[i], state, lang),
                      ),
                    ),
            ),
            if (all.isNotEmpty)
              Container(
                padding: const EdgeInsets.fromLTRB(16, 10, 16, 12),
                decoration: BoxDecoration(color: p.card, border: Border(top: BorderSide(color: p.border))),
                child: Row(
                  children: [
                    Icon(Icons.local_fire_department_outlined, size: 16, color: p.gold),
                    const SizedBox(width: 6),
                    Text('${state.readsToday} ${t('read today', 'dibaca hari ini', lang)}', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
                    const Spacer(),
                    Text('${all.length} ${t('in library', 'di pustaka', lang)}', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _card(BuildContext context, Bookmark b, AppState state, String lang) {
    final p = context.p;
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => HadithDetailPage(bookId: b.bookId, number: b.number, bookTitle: b.bookTitle))),
      onLongPress: () => _menu(context, b, state, lang),
      padding: const EdgeInsets.fromLTRB(15, 13, 15, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(child: MetaLine(text: '${b.bookTitle.toUpperCase()}  •  #${b.number}')),
              if (b.grade.isNotEmpty) GradeBadge(label: b.grade, tier: 'sahih', small: true),
            ],
          ),
          const SizedBox(height: 10),
          Directionality(
            textDirection: TextDirection.rtl,
            child: Text(
              b.arabic,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: HText.arabic(19).copyWith(color: p.textPrimary),
            ),
          ),
          if (b.translation.isNotEmpty) ...[
            const SizedBox(height: 9),
            Text(b.translation, style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.5), maxLines: 3, overflow: TextOverflow.ellipsis),
          ],
          if (b.note.isNotEmpty) ...[
            const SizedBox(height: 9),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(color: p.dark ? Brand.goldLight.withValues(alpha: 0.08) : Brand.goldSoft.withValues(alpha: 0.35), borderRadius: BorderRadius.circular(9)),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.sticky_note_2_outlined, size: 12, color: p.gold),
                  const SizedBox(width: 6),
                  Expanded(child: Text(b.note, style: HText.labelSm.copyWith(color: p.textSecondary, fontSize: 10, height: 1.4))),
                ],
              ),
            ),
          ],
          const SizedBox(height: 10),
          Row(
            children: [
              Icon(Icons.folder_outlined, size: 12, color: p.textMuted),
              const SizedBox(width: 4),
              Text(b.collection, style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5)),
              const Spacer(),
              Text(formatWhen(b.savedAt, lang), style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9)),
              const SizedBox(width: 8),
              GestureDetector(
                onTap: () => _menu(context, b, state, lang),
                child: Icon(Icons.more_horiz_rounded, size: 16, color: p.textMuted),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _menu(BuildContext context, Bookmark b, AppState state, String lang) async {
    final p = context.p;
    final action = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: p.card,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(18, 16, 18, 10),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('${b.bookTitle} #${b.number}', style: HText.h3.copyWith(color: p.textPrimary, fontSize: 15)),
              const SizedBox(height: 14),
              _menuTile(ctx, p, Icons.edit_note_rounded, t('Edit note', 'Ubah catatan', lang), 'note'),
              _menuTile(ctx, p, Icons.drive_file_move_outline, t('Move to collection', 'Pindah koleksi', lang), 'move'),
              _menuTile(ctx, p, Icons.ios_share_rounded, t('Export citations', 'Ekspor kutipan', lang), 'export'),
              _menuTile(ctx, p, Icons.delete_outline_rounded, t('Remove', 'Hapus', lang), 'delete', danger: true),
            ],
          ),
        ),
      ),
    );
    if (!mounted || action == null) return;
    switch (action) {
      case 'delete':
        await state.removeBookmark(b.key);
        break;
      case 'note':
        final note = await _noteDialog(context, b.note, lang);
        if (note != null) await state.updateNote(b.key, note);
        break;
      case 'move':
        final col = await _collectionDialog(context, state, lang);
        if (col != null) await state.moveToCollection(b.key, col);
        break;
      case 'export':
        if (!mounted) return;
        Navigator.of(context).push(MaterialPageRoute(builder: (_) => ExportPage(bookmarks: [b])));
        break;
    }
  }

  Widget _menuTile(BuildContext ctx, dynamic p, IconData icon, String label, String value, {bool danger = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: GestureDetector(
        onTap: () => Navigator.pop(ctx, value),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(11), border: Border.all(color: p.border)),
          child: Row(
            children: [
              Icon(icon, size: 16, color: danger ? Brand.daif : p.textSecondary),
              const SizedBox(width: 10),
              Text(label, style: HText.bodySm.copyWith(color: danger ? Brand.daif : p.textPrimary)),
            ],
          ),
        ),
      ),
    );
  }

  Future<String?> _noteDialog(BuildContext context, String initial, String lang) async {
    final controller = TextEditingController(text: initial);
    final p = context.p;
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: p.card,
        title: Text(t('Note', 'Catatan', lang), style: HText.h3.copyWith(color: p.textPrimary)),
        content: TextField(
          controller: controller,
          maxLines: 4,
          autofocus: true,
          style: HText.bodySm.copyWith(color: p.textPrimary),
          decoration: InputDecoration(hintText: t('Your reflection…', 'Renungan Anda…', lang), border: const OutlineInputBorder()),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(t('Cancel', 'Batal', lang))),
          TextButton(onPressed: () => Navigator.pop(ctx, controller.text.trim()), child: Text(t('Save', 'Simpan', lang))),
        ],
      ),
    );
    return result;
  }

  Future<String?> _collectionDialog(BuildContext context, AppState state, String lang) async {
    final p = context.p;
    return showModalBottomSheet<String>(
      context: context,
      backgroundColor: p.card,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 18, 20, 12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(t('Move to collection', 'Pindah ke koleksi', lang), style: HText.h3.copyWith(color: p.textPrimary, fontSize: 16)),
              const SizedBox(height: 12),
              for (final c in state.collections)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: GestureDetector(
                    onTap: () => Navigator.pop(ctx, c),
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                      decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(11), border: Border.all(color: p.border)),
                      child: Text(c, style: HText.bodySm.copyWith(color: p.textPrimary)),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _newCollection(AppState state, String lang) async {
    final controller = TextEditingController();
    final p = context.p;
    final name = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: p.card,
        title: Text(t('New collection', 'Koleksi baru', lang), style: HText.h3.copyWith(color: p.textPrimary)),
        content: TextField(
          controller: controller,
          autofocus: true,
          style: HText.bodySm.copyWith(color: p.textPrimary),
          decoration: InputDecoration(hintText: t('Collection name', 'Nama koleksi', lang), border: const OutlineInputBorder()),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(t('Cancel', 'Batal', lang))),
          TextButton(onPressed: () => Navigator.pop(ctx, controller.text.trim()), child: Text(t('Create', 'Buat', lang))),
        ],
      ),
    );
    if (name != null && name.isNotEmpty) {
      await state.addCollection(name);
      if (mounted) setState(() => _filter = name);
    }
  }
}
