"""Authored, verified answers for the ten starter questions shown in the UI.

Every answer is grounded in a row actually read from cdn.hadeeth.id: reference,
grade and wording come from that row. Razi-generated replies are deliberately
NOT used here — two of them answered a hadith question with Qur'an verses and
must never be shipped as a prepared answer again.
"""
import io, json

L = []

def add(lang, question, reply):
    L.append({'lang': lang, 'question': question, 'reply': reply})

EN_Q = [
    'What does the hadith about intentions say?',
    'Can you walk me through the isnad of the hadith about intentions?',
    'Which hadith warns about riba?',
    'What are the major sins according to hadith?',
    'What hadith says about truthfulness?',
    'Which hadith stresses honouring parents?',
    'What is the reward for praying in congregation?',
    'What hadith teaches good treatment of neighbours?',
    'When does Ramadan fasting start and end according to hadith?',
    'What hadith explains lawful, unlawful and doubtful matters?',
]

ID_Q = [
    'Apa isi hadis tentang niat?',
    'Bagaimana sanad hadis tentang niat?',
    'Hadis apa yang memperingatkan tentang riba?',
    'Apa saja dosa besar menurut hadis?',
    'Apa hadis tentang kejujuran?',
    'Hadis apa tentang berbakti kepada orang tua?',
    'Apa pahala salat berjamaah?',
    'Apa hadis tentang bertetangga dengan baik?',
    'Kapan puasa Ramadan dimulai dan diakhiri menurut hadis?',
    'Apa hadis tentang halal, haram, dan syubhat?',
]

R = {
    1: 'https://hadeeth.id/hadith.html?book=bukhari&id=1',
    2: 'https://hadeeth.id/hadith.html?book=muslim&id=2995',
    3: 'https://hadeeth.id/hadith.html?book=bukhari&id=6182',
    4: 'https://hadeeth.id/hadith.html?book=bukhari&id=5629',
    5: 'https://hadeeth.id/hadith.html?book=bukhari&id=6980',
    6: 'https://hadeeth.id/hadith.html?book=bukhari&id=611',
    7: 'https://hadeeth.id/hadith.html?book=muslim&id=4757',
    8: 'https://hadeeth.id/hadith.html?book=bukhari&id=1776',
    9: 'https://hadeeth.id/hadith.html?book=bukhari&id=50',
}

add('en', EN_Q[0], (
    f'[Sahih al-Bukhari 1]({R[1]}) — grade **Shahih** (mutashil, marfuʿ), narrated by ʿUmar bin al-Khattab.\n\n'
    'The Prophet ﷺ said: “The reward of deeds depends upon the intentions, and every person will get the reward '
    'according to what he has intended. So whoever emigrated for worldly benefits or for a woman to marry, his '
    'emigration was for what he emigrated for.”\n\n'
    'The ruling is about the inner motive: the same outward act is rewarded according to why it was done.'
))
add('id', ID_Q[0], (
    f'[Sahih al-Bukhari 1]({R[1]}) — derajat **Shahih** (sanad mutashil, marfuʿ), dari ʿUmar bin al-Khattab.\n\n'
    'Nabi ﷺ bersabda: “Semua perbuatan tergantung niatnya, dan setiap orang akan mendapatkan sesuai dengan apa '
    'yang diniatkannya. Barangsiapa hijrah karena dunia atau karena wanita yang ingin dinikahinya, maka hijrahnya '
    'itu sesuai dengan niatnya.”\n\n'
    'Yang diatur adalah niat di balik amalan: amal yang sama diganjar berbeda sesuai tujuannya.'
))

chain_en = ('Abdullah bin Az Zubair → Sufyan bin ʿUyainah → Yahya bin Saʿid al-Ansari → '
            'Muhammad bin Ibrahim → Alqamah bin Waqqash → Umar bin al-Khattab → the Prophet ﷺ')
chain_id = ('Abdullah bin Az Zubair → Sufyan bin ʿUyainah → Yahya bin Saʿid al-Anshari → '
            'Muhammad bin Ibrahim → Alqamah bin Waqash → Umar bin al-Khattab → Nabi ﷺ')
add('en', EN_Q[1], (
    f'[Sahih al-Bukhari 1]({R[1]}) records this chain in transmission order:\n\n{chain_en}\n\n'
    'Status in the registry: **mutashil** (connected), **marfuʿ** (reached the Prophet ﷺ), grade **Shahih**. '
    'The names are taken from the narrator list on the hadith page; open any name for the narrator profile.'
))
add('id', ID_Q[1], (
    f'[Sahih al-Bukhari 1]({R[1]}) mencatat sanad ini menurut urutan periwayatan:\n\n{chain_id}\n\n'
    'Status di registri: **mutashil** (bersambung), **marfuʿ** (sampai kepada Nabi ﷺ), derajat **Shahih**. '
    'Nama-nama diambil dari daftar perawi pada halaman hadis; ketuk nama untuk melihat profilnya.'
))

add('en', EN_Q[2], (
    f'[Sahih Muslim 2995]({R[2]}) — grade **Shahih**, narrated by Jabir.\n\n'
    'The Prophet ﷺ cursed the one who takes interest, the one who pays it, the one who records it and the two '
    'witnesses, and said: “They are all equal.”\n\n'
    'This is the hadith on riba itself, not a Qurʾanic verse. The Qurʾanic ruling appears separately at 2:275, '
    '2:279 and 3:130.'
))
add('id', ID_Q[2], (
    f'[Sahih Muslim 2995]({R[2]}) — derajat **Shahih**, dari Jabir.\n\n'
    'Rasulullah ﷺ melaknat pemakan riba, orang yang menyuruh makan riba, juru tulisnya, dan saksi-saksinya. '
    'Beliau bersabda: “Mereka semua sama.”\n\n'
    'Ini hadis tentang riba, bukan ayat Al-Qurʾan. Dalil Al-Qurʾannya terpisah, yaitu Q.S. 2:275, 2:279, dan 3:130.'
))

add('en', EN_Q[3], (
    f'[Sahih al-Bukhari 6182]({R[3]}) — grade **Shahih**, narrated by ʿAbdullah bin ʿAmr.\n\n'
    'The Prophet ﷺ named the greatest sins as: joining partners with Allah, being undutiful to one’s parents, '
    'unlawful killing, and taking a false oath (al-ghamus).\n\n'
    'The list begins with the right of Allah, then the rights of parents and other people.'
))
add('id', ID_Q[3], (
    f'[Sahih al-Bukhari 6182]({R[3]}) — derajat **Shahih**, dari Abdullah bin Amr.\n\n'
    'Nabi ﷺ menyebut dosa besar: menyekutukan Allah, durhaka kepada orang tua, membunuh tanpa hak, dan '
    'bersumpah palsu (al-ghamus).\n\n'
    'Urutannya dimulai dari hak Allah, lalu hak orang tua dan sesama manusia.'
))

add('en', EN_Q[4], (
    f'[Sahih al-Bukhari 5629]({R[4]}) — grade **Shahih**, narrated by ʿAbdullah (bin Masʿud).\n\n'
    '“Truthfulness leads to righteousness, and righteousness leads to Paradise. Falsehood leads to wickedness, '
    'and wickedness leads to the Fire.” A person keeps telling the truth until he is recorded with Allah as '
    'truthful — and keeps lying until he is recorded as a liar.\n\n'
    'The hadith describes character as something formed by repeated small choices.'
))
add('id', ID_Q[4], (
    f'[Sahih al-Bukhari 5629]({R[4]}) — derajat **Shahih**, dari Abdullah bin Masʿud.\n\n'
    '“Sesungguhnya kejujuran membimbing kepada kebaikan, dan kebaikan membimbing ke surga. Kedustaan membimbing '
    'kepada kejahatan, dan kejahatan membimbing ke neraka.” Seseorang terus berlaku jujur hingga ia dicatat sebagai '
    'orang yang jujur; demikian pula sebaliknya.\n\n'
    'Hadis ini menggambarkan karakter yang terbentuk dari pilihan kecil yang diulang.'
))

add('en', EN_Q[5], (
    f'[Sahih al-Bukhari 6980]({R[5]}) — grade **Shahih**, narrated by Ibn Masʿud.\n\n'
    'Asked which deed is best, the Prophet ﷺ answered: prayer at its fixed time, being good and dutiful to one’s '
    'parents, then jihad in Allah’s cause.\n\n'
    'Honouring parents is placed directly after the daily prayers, before other recommended works.'
))
add('id', ID_Q[5], (
    f'[Sahih al-Bukhari 6980]({R[5]}) — derajat **Shahih**, dari Ibnu Masʿud.\n\n'
    'Ketika ditanya amalan apa yang paling utama, Nabi ﷺ menjawab: salat tepat pada waktunya, berbakti kepada '
    'orang tua, lalu jihad di jalan Allah.\n\n'
    'Berbakti kepada orang tua diletakkan tepat setelah salat wajib, sebelum amalan sunat lainnya.'
))

add('en', EN_Q[6], (
    f'[Sahih al-Bukhari 611]({R[6]}) — grade **Shahih**, narrated by Abu Huraira.\n\n'
    'Prayer in congregation is twenty-five times greater than prayer alone at home or in the market. For every '
    'step taken towards the mosque, a degree is raised and a sin is erased, and angels keep asking Allah’s '
    'blessing and forgiveness while the person remains at the place of prayer.\n\n'
    'The reward covers both the prayer itself and the walk to it.'
))
add('id', ID_Q[6], (
    f'[Sahih al-Bukhari 611]({R[6]}) — derajat **Shahih**, dari Abu Hurairah.\n\n'
    'Salat berjamaah pahalanya dua puluh lima kali lipat dibanding salat sendirian di rumah atau di pasar. '
    'Setiap langkah menuju masjid mengangkat satu derajat dan menghapus satu dosa; malaikat terus memohon '
    'berkah dan ampunan selama orang itu tetap di tempat salatnya.\n\n'
    'Pahalanya mencakup salatnya dan juga perjalanan menuju masjid.'
))

add('en', EN_Q[7], (
    f'[Sahih Muslim 4757]({R[7]}) — grade **Shahih**, narrated by Ibn ʿUmar.\n\n'
    '“Gabriel kept urging me about the neighbour, until I thought he would soon give the neighbour a right of '
    'inheritance.”\n\n'
    'The phrasing is a strong emphasis on neighbourly rights, not a ruling that neighbours actually inherit.'
))
add('id', ID_Q[7], (
    f'[Sahih Muslim 4757]({R[7]}) — derajat **Shahih**, dari Ibnu Umar.\n\n'
    '“Sesungguhnya Jibril terus-menerus berpesan kepadaku tentang tetangga, hingga aku menduga ia akan '
    'memberikan hak waris kepada tetangga.”\n\n'
    'Redaksi ini adalah penekanan kuat pada hak tetangga, bukan ketetapan bahwa tetangga benar-benar mendapat '
    'bagian warisan.'
))

add('en', EN_Q[8], (
    f'[Sahih al-Bukhari 1776]({R[8]}) — grade **Shahih**, narrated by Abu Huraira.\n\n'
    '“Start fasting on seeing the crescent, and give up fasting on seeing the crescent [of Shawwal]; if the sky '
    'is overcast, complete thirty days of Shaʿban.”\n\n'
    'The hadith sets sighting as the start and end, with thirty days of Shaʿban as the fallback when the new moon '
    'cannot be seen.'
))
add('id', ID_Q[8], (
    f'[Sahih al-Bukhari 1776]({R[8]}) — derajat **Shahih**, dari Abu Hurairah.\n\n'
    '“Berpuasalah kalian dengan melihatnya (hilal) dan berbukalah dengan melihatnya pula. Apabila kalian tertutup '
    '(awan), maka sempurnakanlah bilangan bulan Syakban tiga puluh hari.”\n\n'
    'Hadis ini menetapkan rukyah sebagai penentu awal dan akhir puasa, dengan tiga puluh hari Syakban sebagai '
    'pengganti bila hilal tidak terlihat.'
))

add('en', EN_Q[9], (
    f'[Sahih al-Bukhari 50]({R[9]}) — grade **Shahih**, narrated by an-Nuʿman bin Bashir.\n\n'
    '“Both legal and illegal things are evident, but in between them there are doubtful things. Whoever saves '
    'himself from the doubtful things saves his religion and his honour; whoever indulges in them is like a '
    'shepherd who grazes his flock at the edge of a forbidden pasture.”\n\n'
    'The practical rule: when a matter is doubtful, stepping away from it is the safer course.'
))
add('id', ID_Q[9], (
    f'[Sahih al-Bukhari 50]({R[9]}) — derajat **Shahih**, dari an-Nuʿman bin Basyir.\n\n'
    '“Perkara yang halal dan yang haram itu jelas, tetapi di antara keduanya ada perkara syubhat. Barangsiapa '
    'menjauhi syubhat, ia telah menyelamatkan agama dan kehormatannya; barangsiapa terjerumus ke dalamnya, ia '
    'seperti penggembala yang menggembalakan ternaknya di tepi padang terlarang.”\n\n'
    'Kaidah praktisnya: bila sesuatu meragukan, menjauhinya lebih selamat.'
))

assert len(L) == 20, len(L)
for path in ('assets/data/razi_seeds.json', 'tool/seed_answers.json'):
    with io.open(path, 'w', encoding='utf-8') as f:
        json.dump({f"{e['lang']}|{e['question']}": e for e in L}, f, ensure_ascii=False, indent=1) if 'assets' in path else json.dump(L, f, ensure_ascii=False, indent=1)
print(f'wrote {len(L)} prepared answers (10 EN + 10 ID)')
