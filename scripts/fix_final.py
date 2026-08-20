import re
import json

ar_dict = {
    'rawi_tabarani': '\u0627\u0644\u0637\u0628\u0631\u0627\u0646\u064a',
    'rawi_ibn_khuzaimah': '\u0627\u0628\u0646 \u062e\u0632\u064a\u0645\u0629',
    'rawi_ibn_hibban': '\u0627\u0628\u0646 \u062d\u0628\u0627\u0646',
    'rawi_al_hakim': '\u0627\u0644\u062d\u0627\u0643\u0645 \u0627\u0644\u0646\u064a\u0633\u0627\u0628\u0648\u0631\u064a',
    'rawi_daraqutni': '\u0627\u0644\u062f\u0627\u0631\u0642\u0637\u0646\u064a',
    'rawi_darimi': '\u0627\u0644\u062f\u0627\u0631\u0645\u064a',
    'rawi_nawawi': '\u0627\u0644\u0646\u0648\u0648\u064a',
    'rawi_syafii': '\u0627\u0644\u0634\u0627\u0641\u0639\u064a',
    'rawi_ibn_hajar': '\u0627\u0628\u0646 \u062d\u062c\u0631 \u0627\u0644\u0639\u0633\u0642\u0644\u0627\u0646\u064a',
    'rawi_baghawi': '\u0627\u0644\u0628\u063a\u0648\u064a',
    'rawi_waliullah': '\u0634\u0627\u0647 \u0648\u0644\u064a \u0627\u0644\u0644\u0647 \u0627\u0644\u062f\u0647\u0644\u0648\u064a',
    'rawi_umar_ibn_al_khattab': '\u0639\u0645\u0631 \u0628\u0646 \u0627\u0644\u062e\u0637\u0627\u0628',
    'rawi_aisha_bint_abi_bakr': '\u0639\u0627\u0626\u0634\u0629 \u0628\u0646\u062a \u0623\u0628\u064a \u0628\u0643\u0631',
    'rawi_abu_hurairah': '\u0623\u0628\u0648 \u0647\u0631\u064a\u0631\u0629',
    'rawi_ibn_umar': '\u0639\u0628\u062f \u0627\u0644\u0644\u0647 \u0628\u0646 \u0639\u0645\u0631',
    'rawi_ibn_abbas': '\u0639\u0628\u062f \u0627\u0644\u0644\u0647 \u0628\u0646 \u0639\u0628\u0627\u0633',
    'rawi_anas_bin_malik': '\u0623\u0646\u0633 \u0628\u0646 \u0645\u0627\u0644\u0643',
    'rawi_jaber_bin_abdullah': '\u062c\u0627\u0628\u0631 \u0628\u0646 \u0639\u0628\u062f \u0627\u0644\u0644\u0647',
    'rawi_abu_said_al_khudri': '\u0623\u0628\u0648 \u0633\u0639\u064a\u062f \u0627\u0644\u062e\u062f\u0631\u064a',
    'rawi_abdullah_bin_masud': '\u0639\u0628\u062f \u0627\u0644\u0644\u0647 \u0628\u0646 \u0645\u0633\u0639\u0648\u062f',
    'rawi_malik_bin_anas': '\u0645\u0627\u0644\u0643 \u0628\u0646 \u0623\u0646\u0633',
    'rawi_al_bukhari': '\u0645\u062d\u0645\u062f \u0628\u0646 \u0625\u0633\u0645\u0627\u0639\u064a\u0644 \u0627\u0644\u0628\u062e\u0627\u0631\u064a',
    'rawi_muslim_ibn_hajjaj': '\u0645\u0633\u0644\u0645 \u0628\u0646 \u0627\u0644\u062d\u062c\u0627\u062c',
    'rawi_abu_dawud': '\u0623\u0628\u0648 \u062f\u0627\u0648\u062f \u0627\u0644\u0633\u062c\u0633\u062a\u0627\u0646\u064a',
    'rawi_al_tirmidhi': '\u0623\u0628\u0648 \u0639\u064a\u0633\u0649 \u0627\u0644\u062a\u0631\u0645\u0630\u064a',
    'rawi_al_nasai': '\u0623\u062d\u0645\u062f \u0628\u0646 \u0634\u0639\u064a\u0628 \u0627\u0644\u0646\u0633\u0627\u0626\u064a',
    'rawi_ibn_majah': '\u0627\u0628\u0646 \u0645\u0627\u062c\u0647 \u0627\u0644\u0642\u0632\u0648\u064a\u0646\u064a',
    'rawi_ahmad': '\u0623\u062d\u0645\u062f \u0628\u0646 \u062d\u0646\u0628\u0644',
    'rawi_al_zuhri': '\u0627\u0628\u0646 \u0634\u0647\u0627\u0628 \u0627\u0644\u0632\u0647\u0631\u064a',
    'rawi_nafi': '\u0646\u0627\u0641\u0639 \u0645\u0648\u0644\u0649 \u0627\u0628\u0646 \u0639\u0645\u0631',
    'rawi_salim': '\u0633\u0627\u0644\u0645 \u0628\u0646 \u0639\u0628\u062f \u0627\u0644\u0644\u0647',
    'rawi_urwah': '\u0639\u0631\u0648\u0629 \u0628\u0646 \u0627\u0644\u0632\u0628\u064a\u0631',
    'rawi_said_bin_jubair': '\u0633\u0639\u064a\u062f \u0628\u0646 \u062c\u0628\u064a\u0631',
    'rawi_sufyan_al_thawri': '\u0633\u0641\u064a\u0627\u0646 \u0628\u0646 \u0639\u064a\u064a\u0646\u0629',
    'rawi_yahya_bin_said': '\u064a\u062d\u064a\u0649 \u0628\u0646 \u0633\u0639\u064a\u062f \u0627\u0644\u0623\u0646\u0635\u0627\u0631\u064a',
    'rawi_abdullah_bin_dinar': '\u0639\u0628\u062f \u0627\u0644\u0644\u0647 \u0628\u0646 \u062f\u064a\u0646\u0627\u0631',
    'rawi_ismail_bin_jafar': '\u0625\u0633\u0645\u0627\u0639\u064a\u0644 \u0628\u0646 \u062c\u0639\u0641\u0631',
    'rawi_qutaibah_bin_said': '\u0642\u062a\u064a\u0628\u0629 \u0628\u0646 \u0633\u0639\u064a\u062f',
    'rawi_atho_bin_yasar': '\u0639\u0637\u0627\u0621 \u0628\u0646 \u064a\u0633\u0627\u0631',
    'rawi_hilal_bin_ali': '\u0647\u0644\u0627\u0644 \u0628\u0646 \u0639\u0644\u064a'
}

html = open('scholars.html', 'r', encoding='utf-8').read()

def replacer(match):
    scholar_id = match.group(1)
    if scholar_id in ar_dict:
        # Reconstruct the string to preserve everything else
        original = match.group(0)
        # Find where name_ar is
        replaced = re.sub(r'name_ar:\s*"[^"]+"', f'name_ar: "{ar_dict[scholar_id]}"', original)
        return replaced
    # fallback without prefix
    if scholar_id.replace('rawi_', '') in ar_dict:
        original = match.group(0)
        replaced = re.sub(r'name_ar:\s*"[^"]+"', f'name_ar: "{ar_dict[scholar_id.replace("rawi_", "")]}"', original)
        return replaced
    return match.group(0)

fixed_html = re.sub(r'id:\s*\'([^\']+)\'[\s\S]*?name_ar:\s*"[^"]+"', replacer, html)

with open('scholars.html', 'w', encoding='utf-8') as f:
    f.write(fixed_html)
print("scholars.html fixed completely using unicode escapes!")
