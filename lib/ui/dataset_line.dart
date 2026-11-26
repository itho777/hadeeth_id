import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../theme.dart';

/// Freshness of the shipped registry snapshot. The app itself always loads
/// books and rows from cdn.hadeeth.id at runtime; this line tells the reader
/// which snapshot that CDN served when this build was made.
class DatasetLine extends StatefulWidget {
  const DatasetLine({super.key, required this.lang});

  final String lang;

  @override
  State<DatasetLine> createState() => _DatasetLineState();
}

class _DatasetLineState extends State<DatasetLine> {
  Map<String, dynamic>? _info;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final raw = await rootBundle.loadString('assets/data/dataset_info.json');
      if (!mounted) return;
      setState(() => _info = jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      // Missing asset just hides the line; the page still renders.
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final info = _info;
    if (info == null) return const SizedBox.shrink();
    final updated = DateTime.parse('${info['updated']}').toUtc().add(const Duration(hours: 7));
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
    const monthsEn = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    final names = widget.lang == 'id' ? months : monthsEn;
    final date = '${updated.day} ${names[updated.month - 1]} ${updated.year} '
        '${updated.hour.toString().padLeft(2, '0')}:${updated.minute.toString().padLeft(2, '0')} WIB';
    final count = '${info['hadiths']}'.replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+$)'),
      (m) => '${m[1]}${widget.lang == 'id' ? '.' : ','}',
    );
    return Text(
      widget.lang == 'id'
          ? '${info['books']} koleksi · $count hadis · diperbarui $date · langsung dari cdn.hadeeth.id'
          : '${info['books']} collections · $count hadiths · updated $date · live from cdn.hadeeth.id',
      style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5, height: 1.5),
    );
  }
}
