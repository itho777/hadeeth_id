-- SEED BOOKS DATA
INSERT INTO public.books (id, title_ar, title_en, title_id, author_ar, author_en, death_year_ah, total_hadiths, total_chapters, grade_summary, order_index)
VALUES ('bukhari', 'صحيح البخاري', 'Sahih al-Bukhari', 'Shahih Bukhari', 'الإمام محمد بن إسماعيل البخاري', 'Imam Muhammad al-Bukhari', 256, 7589, 97, 'صحيح متفق عليه (Sahih)', 1)
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.books (id, title_ar, title_en, title_id, author_ar, author_en, death_year_ah, total_hadiths, total_chapters, grade_summary, order_index)
VALUES ('nawawi', 'الأربعون النووية', 'Forty Hadith of an-Nawawi', 'Hadits Arba''in An-Nawawi', 'الإمام يحيى بن شرف النووي', 'Imam Yahya ibn Sharaf al-Nawawi', 676, 42, 1, 'صحيح ومقبول (Sahih & Hasan)', 2)
ON CONFLICT (id) DO NOTHING;

-- SEED CHAPTERS DATA
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c1', 'bukhari', 1, 'Revelation', 'Revelation', 'Revelation', 1, 7)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c2', 'bukhari', 2, 'Belief', 'Belief', 'Belief', 8, 58)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c3', 'bukhari', 3, 'Knowledge', 'Knowledge', 'Knowledge', 59, 134)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c4', 'bukhari', 4, 'Ablutions (Wudu'')', 'Ablutions (Wudu'')', 'Ablutions (Wudu'')', 135, 247)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c5', 'bukhari', 5, 'Bathing (Ghusl)', 'Bathing (Ghusl)', 'Bathing (Ghusl)', 248, 293)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c6', 'bukhari', 6, 'Menstrual Periods', 'Menstrual Periods', 'Menstrual Periods', 294, 333)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c7', 'bukhari', 7, 'Rubbing hands and feet with dust (Tayammum)', 'Rubbing hands and feet with dust (Tayammum)', 'Rubbing hands and feet with dust (Tayammum)', 334, 348)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c8', 'bukhari', 8, 'Prayers (Salat)', 'Prayers (Salat)', 'Prayers (Salat)', 349, 520)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c9', 'bukhari', 9, 'Times of the Prayers', 'Times of the Prayers', 'Times of the Prayers', 522, 602)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c10', 'bukhari', 10, 'Call to Prayers (Adhaan)', 'Call to Prayers (Adhaan)', 'Call to Prayers (Adhaan)', 603, 875)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c11', 'bukhari', 11, 'Friday Prayer', 'Friday Prayer', 'Friday Prayer', 876, 941)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c12', 'bukhari', 12, 'Fear Prayer', 'Fear Prayer', 'Fear Prayer', 942, 947)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c13', 'bukhari', 13, 'The Two Festivals (Eids)', 'The Two Festivals (Eids)', 'The Two Festivals (Eids)', 948, 989)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c14', 'bukhari', 14, 'Witr Prayer', 'Witr Prayer', 'Witr Prayer', 990, 1004)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c15', 'bukhari', 15, 'Invoking Allah for Rain (Istisqaa)', 'Invoking Allah for Rain (Istisqaa)', 'Invoking Allah for Rain (Istisqaa)', 1005, 1039)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c16', 'bukhari', 16, 'Eclipses', 'Eclipses', 'Eclipses', 1040, 1066)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c17', 'bukhari', 17, 'Prostration During Recital of Qur''an', 'Prostration During Recital of Qur''an', 'Prostration During Recital of Qur''an', 1067, 1079)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c18', 'bukhari', 18, 'Shortening the Prayers (At-Taqseer)', 'Shortening the Prayers (At-Taqseer)', 'Shortening the Prayers (At-Taqseer)', 1080, 1119)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c19', 'bukhari', 19, 'Prayer at Night (Tahajjud)', 'Prayer at Night (Tahajjud)', 'Prayer at Night (Tahajjud)', 1120, 1187)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c20', 'bukhari', 20, 'Virtues of Prayer at Masjid Makkah and Madinah', 'Virtues of Prayer at Masjid Makkah and Madinah', 'Virtues of Prayer at Masjid Makkah and Madinah', 1188, 1197)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c21', 'bukhari', 21, 'Actions while Praying', 'Actions while Praying', 'Actions while Praying', 1198, 1223)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c22', 'bukhari', 22, 'Forgetfulness in Prayer', 'Forgetfulness in Prayer', 'Forgetfulness in Prayer', 1224, 1236)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c23', 'bukhari', 23, 'Funerals (Al-Janaa''iz)', 'Funerals (Al-Janaa''iz)', 'Funerals (Al-Janaa''iz)', 1237, 1394)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c24', 'bukhari', 24, 'Obligatory Charity Tax (Zakat)', 'Obligatory Charity Tax (Zakat)', 'Obligatory Charity Tax (Zakat)', 1395, 1512)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c25', 'bukhari', 25, 'Hajj (Pilgrimage)', 'Hajj (Pilgrimage)', 'Hajj (Pilgrimage)', 1513, 1772)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c26', 'bukhari', 26, '`Umrah (Minor pilgrimage)', '`Umrah (Minor pilgrimage)', '`Umrah (Minor pilgrimage)', 1773, 1805)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c27', 'bukhari', 27, 'Pilgrims Prevented from Completing the Pilgrimage', 'Pilgrims Prevented from Completing the Pilgrimage', 'Pilgrims Prevented from Completing the Pilgrimage', 1806, 1820)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c28', 'bukhari', 28, 'Penalty of Hunting while on Pilgrimage', 'Penalty of Hunting while on Pilgrimage', 'Penalty of Hunting while on Pilgrimage', 1821, 1866)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c29', 'bukhari', 29, 'Virtues of Madinah', 'Virtues of Madinah', 'Virtues of Madinah', 1867, 1890)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c30', 'bukhari', 30, 'Fasting', 'Fasting', 'Fasting', 1891, 2007)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c31', 'bukhari', 31, 'Praying at Night in Ramadaan (Taraweeh)', 'Praying at Night in Ramadaan (Taraweeh)', 'Praying at Night in Ramadaan (Taraweeh)', 2008, 2013)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c32', 'bukhari', 32, 'Virtues of the Night of Qadr', 'Virtues of the Night of Qadr', 'Virtues of the Night of Qadr', 2014, 2024)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c33', 'bukhari', 33, 'Retiring to a Mosque for Remembrance of Allah (I''tikaf)', 'Retiring to a Mosque for Remembrance of Allah (I''tikaf)', 'Retiring to a Mosque for Remembrance of Allah (I''tikaf)', 2025, 2046)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c34', 'bukhari', 34, 'Sales and Trade', 'Sales and Trade', 'Sales and Trade', 2047, 2238)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c35', 'bukhari', 35, 'Sales in which a Price is paid for Goods to be Delivered Later (As-Salam)', 'Sales in which a Price is paid for Goods to be Delivered Later (As-Salam)', 'Sales in which a Price is paid for Goods to be Delivered Later (As-Salam)', 2239, 2256)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c36', 'bukhari', 36, 'Shuf''a', 'Shuf''a', 'Shuf''a', 2257, 2259)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c37', 'bukhari', 37, 'Hiring', 'Hiring', 'Hiring', 2260, 2286)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c38', 'bukhari', 38, 'Transferance of a Debt from One Person to Another (Al-Hawaala)', 'Transferance of a Debt from One Person to Another (Al-Hawaala)', 'Transferance of a Debt from One Person to Another (Al-Hawaala)', 2287, 2289)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c39', 'bukhari', 39, 'Kafalah', 'Kafalah', 'Kafalah', 2290, 2298)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c40', 'bukhari', 40, 'Representation, Authorization, Business by Proxy', 'Representation, Authorization, Business by Proxy', 'Representation, Authorization, Business by Proxy', 2299, 2319)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c41', 'bukhari', 41, 'Agriculture', 'Agriculture', 'Agriculture', 2320, 2350)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c42', 'bukhari', 42, 'Distribution of Water', 'Distribution of Water', 'Distribution of Water', 2351, 2383)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c43', 'bukhari', 43, 'Loans, Payment of Loans, Freezing of Property, Bankruptcy', 'Loans, Payment of Loans, Freezing of Property, Bankruptcy', 'Loans, Payment of Loans, Freezing of Property, Bankruptcy', 2385, 2409)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c44', 'bukhari', 44, 'Khusoomaat', 'Khusoomaat', 'Khusoomaat', 2410, 2425)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c45', 'bukhari', 45, 'Lost Things Picked up by Someone (Luqatah)', 'Lost Things Picked up by Someone (Luqatah)', 'Lost Things Picked up by Someone (Luqatah)', 2426, 2439)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c46', 'bukhari', 46, 'Oppressions', 'Oppressions', 'Oppressions', 2440, 2482)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c47', 'bukhari', 47, 'Partnership', 'Partnership', 'Partnership', 2483, 2507)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c48', 'bukhari', 48, 'Mortgaging', 'Mortgaging', 'Mortgaging', 2508, 2515)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c49', 'bukhari', 49, 'Manumission of Slaves', 'Manumission of Slaves', 'Manumission of Slaves', 2517, 2559)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c50', 'bukhari', 50, 'Makaatib', 'Makaatib', 'Makaatib', 2560, 2565)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c51', 'bukhari', 51, 'Gifts', 'Gifts', 'Gifts', 2566, 2636)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c52', 'bukhari', 52, 'Witnesses', 'Witnesses', 'Witnesses', 2637, 2689)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c53', 'bukhari', 53, 'Peacemaking', 'Peacemaking', 'Peacemaking', 2690, 2710)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c54', 'bukhari', 54, 'Conditions', 'Conditions', 'Conditions', 2712, 2737)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c55', 'bukhari', 55, 'Wills and Testaments (Wasaayaa)', 'Wills and Testaments (Wasaayaa)', 'Wills and Testaments (Wasaayaa)', 2738, 2781)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c56', 'bukhari', 56, 'Fighting for the Cause of Allah (Jihaad)', 'Fighting for the Cause of Allah (Jihaad)', 'Fighting for the Cause of Allah (Jihaad)', 2782, 3090)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c57', 'bukhari', 57, 'One-fifth of Booty to the Cause of Allah (Khumus)', 'One-fifth of Booty to the Cause of Allah (Khumus)', 'One-fifth of Booty to the Cause of Allah (Khumus)', 3091, 3155)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c58', 'bukhari', 58, 'Jizyah and Mawaada''ah', 'Jizyah and Mawaada''ah', 'Jizyah and Mawaada''ah', 3157, 3189)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c59', 'bukhari', 59, 'Beginning of Creation', 'Beginning of Creation', 'Beginning of Creation', 3190, 3325)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c60', 'bukhari', 60, 'Prophets', 'Prophets', 'Prophets', 3326, 3488)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c61', 'bukhari', 61, 'Virtues and Merits of the Prophet (pbuh) and his Companions', 'Virtues and Merits of the Prophet (pbuh) and his Companions', 'Virtues and Merits of the Prophet (pbuh) and his Companions', 3489, 3648)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c62', 'bukhari', 62, 'Companions of the Prophet', 'Companions of the Prophet', 'Companions of the Prophet', 3649, 3775)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c63', 'bukhari', 63, 'Merits of the Helpers in Madinah (Ansaar)', 'Merits of the Helpers in Madinah (Ansaar)', 'Merits of the Helpers in Madinah (Ansaar)', 3776, 3948)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c64', 'bukhari', 64, 'Military Expeditions led by the Prophet (pbuh) (Al-Maghaazi)', 'Military Expeditions led by the Prophet (pbuh) (Al-Maghaazi)', 'Military Expeditions led by the Prophet (pbuh) (Al-Maghaazi)', 3949, 4473)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c65', 'bukhari', 65, 'Prophetic Commentary on the Qur''an (Tafseer of the Prophet (pbuh))', 'Prophetic Commentary on the Qur''an (Tafseer of the Prophet (pbuh))', 'Prophetic Commentary on the Qur''an (Tafseer of the Prophet (pbuh))', 4474, 4977)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c66', 'bukhari', 66, 'Virtues of the Qur''an', 'Virtues of the Qur''an', 'Virtues of the Qur''an', 4979, 5062)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c67', 'bukhari', 67, 'Wedlock, Marriage (Nikaah)', 'Wedlock, Marriage (Nikaah)', 'Wedlock, Marriage (Nikaah)', 5063, 5250)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c68', 'bukhari', 68, 'Divorce', 'Divorce', 'Divorce', 5251, 5350)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c69', 'bukhari', 69, 'Supporting the Family', 'Supporting the Family', 'Supporting the Family', 5351, 5372)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c70', 'bukhari', 70, 'Food, Meals', 'Food, Meals', 'Food, Meals', 5373, 5466)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c71', 'bukhari', 71, 'Sacrifice on Occasion of Birth (`Aqiqa)', 'Sacrifice on Occasion of Birth (`Aqiqa)', 'Sacrifice on Occasion of Birth (`Aqiqa)', 5467, 5474)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c72', 'bukhari', 72, 'Hunting, Slaughtering', 'Hunting, Slaughtering', 'Hunting, Slaughtering', 5475, 5544)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c73', 'bukhari', 73, 'Al-Adha Festival Sacrifice (Adaahi)', 'Al-Adha Festival Sacrifice (Adaahi)', 'Al-Adha Festival Sacrifice (Adaahi)', 5545, 5574)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c74', 'bukhari', 74, 'Drinks', 'Drinks', 'Drinks', 5575, 5639)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c75', 'bukhari', 75, 'Patients', 'Patients', 'Patients', 5640, 5677)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c76', 'bukhari', 76, 'Medicine', 'Medicine', 'Medicine', 5678, 5782)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c77', 'bukhari', 77, 'Dress', 'Dress', 'Dress', 5783, 5969)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c78', 'bukhari', 78, 'Good Manners and Form (Al-Adab)', 'Good Manners and Form (Al-Adab)', 'Good Manners and Form (Al-Adab)', 5970, 6226)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c79', 'bukhari', 79, 'Asking Permission', 'Asking Permission', 'Asking Permission', 6227, 6303)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c80', 'bukhari', 80, 'Invocations', 'Invocations', 'Invocations', 6304, 6411)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c81', 'bukhari', 81, 'To make the Heart Tender (Ar-Riqaq)', 'To make the Heart Tender (Ar-Riqaq)', 'To make the Heart Tender (Ar-Riqaq)', 6412, 6593)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c82', 'bukhari', 82, 'Divine Will (Al-Qadar)', 'Divine Will (Al-Qadar)', 'Divine Will (Al-Qadar)', 6594, 6620)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c83', 'bukhari', 83, 'Oaths and Vows', 'Oaths and Vows', 'Oaths and Vows', 6621, 6707)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c84', 'bukhari', 84, 'Expiation for Unfulfilled Oaths', 'Expiation for Unfulfilled Oaths', 'Expiation for Unfulfilled Oaths', 6708, 6722)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c85', 'bukhari', 85, 'Laws of Inheritance (Al-Faraa''id)', 'Laws of Inheritance (Al-Faraa''id)', 'Laws of Inheritance (Al-Faraa''id)', 6723, 6771)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c86', 'bukhari', 86, 'Limits and Punishments set by Allah (Hudood)', 'Limits and Punishments set by Allah (Hudood)', 'Limits and Punishments set by Allah (Hudood)', 6772, 6860)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c87', 'bukhari', 87, 'Blood Money (Ad-Diyat)', 'Blood Money (Ad-Diyat)', 'Blood Money (Ad-Diyat)', 6861, 6917)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c88', 'bukhari', 88, 'Apostates', 'Apostates', 'Apostates', 6918, 6939)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c89', 'bukhari', 89, '(Statements made under) Coercion', '(Statements made under) Coercion', '(Statements made under) Coercion', 6940, 6952)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c90', 'bukhari', 90, 'Tricks', 'Tricks', 'Tricks', 6953, 6981)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c91', 'bukhari', 91, 'Interpretation of Dreams', 'Interpretation of Dreams', 'Interpretation of Dreams', 6982, 7047)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c92', 'bukhari', 92, 'Afflictions and the End of the World', 'Afflictions and the End of the World', 'Afflictions and the End of the World', 7048, 7136)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c93', 'bukhari', 93, 'Judgments (Ahkaam)', 'Judgments (Ahkaam)', 'Judgments (Ahkaam)', 7137, 7225)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c94', 'bukhari', 94, 'Wishes', 'Wishes', 'Wishes', 7226, 7245)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c95', 'bukhari', 95, 'Accepting Information Given by a Truthful Person', 'Accepting Information Given by a Truthful Person', 'Accepting Information Given by a Truthful Person', 7246, 7267)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c96', 'bukhari', 96, 'Holding Fast to the Qur''an and Sunnah', 'Holding Fast to the Qur''an and Sunnah', 'Holding Fast to the Qur''an and Sunnah', 7268, 7370)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('bukhari_c97', 'bukhari', 97, 'Oneness, Uniqueness of Allah (Tawheed)', 'Oneness, Uniqueness of Allah (Tawheed)', 'Oneness, Uniqueness of Allah (Tawheed)', 7371, 7563)
ON CONFLICT (id) DO NOTHING;
INSERT INTO public.chapters (id, book_id, chapter_number, title_ar, title_en, title_id, hadith_start, hadith_end)
VALUES ('nawawi_c1', 'nawawi', 1, 'Forty Hadith of an-Nawawi', 'Forty Hadith of an-Nawawi', 'Forty Hadith of an-Nawawi', 1, 42)
ON CONFLICT (id) DO NOTHING;
