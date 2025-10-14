import re

def clean_content(preprocessed_content: str) -> str:
  syllables = re.sub(r"[.();:,]", "", preprocessed_content.lower()).split()

  # This pattern is used to match all numeric strings
  numeric_pattern = r"^-?\d+(?:\.\d+)?$"  # Pattern for integers and reals, including negatives

  # Replace all numeric strings with a `[number]` token
  syllables = [("number" if re.fullmatch(numeric_pattern, s) else s) for s in syllables]

  # This regex is used to match all percentage strings.
  percentage_pattern = r"\b\d+(?:\.\d+)?%"

  # Replace all percentage strings with a `[percentage]` token
  syllables = [("percentage" if re.fullmatch(percentage_pattern, s) else s) for s in syllables]

  # This pattern is used to match all date strings.
  date_pattern = r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"

  # Replace all date strings with a `[date]` token.
  syllables = [("date" if re.fullmatch(date_pattern, s) else s) for s in syllables]

  # Process all the Vietnamese words with dashes
  vn_words_with_dashes_pattern = r"^[A-Za-zÀ-ỹ]+(?:-[A-Za-zÀ-ỹ]+)+$"

  syllables = [
      s.replace("-", " ") if re.fullmatch(vn_words_with_dashes_pattern, s) else s
      for s in syllables
  ]

  # Regex: match if contains any special char or number
  special_tokens = ["number", "percentage", "date"]
  pattern = r"[^\w\s]|[0-9]"
  clean_syllables = [s for s in syllables if (not re.search(pattern, s)) or (s in special_tokens)]

  cleaned_content = " ".join(clean_syllables).strip()

  return cleaned_content

def get_vn_media_topics() -> dict:
  """
  This function outputs a dictionary with 5 large topics as 5 keys.
  Each key has an array of small topics.
  """
  
  vietnamese_media_topics = {
      "Tin tức & Thời sự (News & Current Affairs)": [
          "5 phút hôm nay",
          "Bản Tin 46'",
          "Bản tin 113",
          "An ninh hình sự",
          "An sinh",
          "An toàn thực phẩm",
          "Biển Đông 24/7",
          "Biển đảo",
          "Bản tin tiếng Anh",
          "Bản tin tiếng Nga",
          "Bản tin tiếng Pháp",
          "Bản tin tiếng Trung",
          "Bản tin tiếng Việt"
      ],

      "Giải trí & Văn hóa": [
          "3 phút cùng Sao",
          "Bí mật Adam",
          "Bí mật Eva",
          "Bí mật phòng the",
          "Bí quyết của Eva",
          "Bí quyết làm đẹp",
          "Beauty & Fashion",
          "Bật mí bí mật",
          "Bếp Eva"
      ],

      "Thể thao (Sports)": [
          "360 độ thể thao",
          "AFC Cup",
          "Asian Cup",
          "BLV Quang Tùng",
          "Bóng đá",
          "Bóng Đá",
          "Bóng đá & Cuộc sống",
          "Bóng đá Việt Nam",
          "Bóng đá nữ Việt Nam",
          "Bóng đá Anh",
          "Bóng đá Pháp",
          "Bóng đá Đức",
          "Bóng đá Tây Ban Nha",
          "Bóng đá Brazil",
          "Bóng đá Argentina",
          "Bóng đá Châu Âu",
          "Bóng đá Châu Á",
          "Bóng đá Futsal",
          "Bóng đá Phong trào",
          "Bóng rổ",
          "Bundesliga"
      ],

      "Kinh tế & Xã hội": [
          "Bizline",
          "Bất động sản",
          "An Sinh",
          "Bạn trẻ - Cuộc sống",
          "Báo chí toàn cảnh",
          "Bây giờ, ở đây"
      ],

      "Đời sống & Blog": [
          "Blog",
          "Bình luận",
          "Bạn đọc",
          "Bạn đọc làm báo",
          "Bức thư viết tay."
      ]
  }
  
  # --- 1. Tin tức & Thời sự (News & Current Affairs) ---
  vietnamese_media_topics["Tin tức & Thời sự (News & Current Affairs)"] += [
      "CAN", "CDC Đắk Nông", "CHÍNH TRỊ", "Chính trị", "Chính trị - Xã hội", "Chính trị xã hội",
      "Chính sách mới", "Cổng TTĐT Chính phủ", "Cửa sổ ASEAN", "Cải cách hành chính",
      "Cần biết", "CĐ Công an nhân dân", "CĐ Cao su Việt Nam", "CĐ Dầu khí", "CĐ Dệt May Việt Nam",
      "CĐ Ngân hàng", "CĐ ngành Giáo dục", "CĐ ngành NN-PTNT", "CĐ ngành Xây dựng",
      "CĐ ngành Y tế", "CĐ Điện lực", "CĐ Đường sắt", "Công đoàn", "Công đoàn toàn quốc",
      "Chuyển động 24h", "Chuyển động Sài Gòn", "Chuyển động số",
      "Chuyện vụ án", "Chuyên trang Phụ nữ", "Chất", "Chính trị", "Dự báo thời tiết",
      "Daily Biz", "Dòng chảy tài chính", "Góc nhìn", "Góc nhìn thị trường",
      "Góc nhìn nhân quyền", "GÓC NHÌN"
  ]

  # --- 2. Giải trí & Văn hóa ---
  vietnamese_media_topics["Giải trí & Văn hóa"] += [
      "Ca Nhạc", "Ciné", "Clip Eva", "Con đường âm nhạc", "Culture Mosaic",
      "Cuộc hẹn cuối tuần", "Cười 24H", "Cùng hát lên nào", "Cùng lăn vào bếp",
      "Cà phê sáng", "Cà phê cùng quý ông", "Cây táo nở hoa", "Chùm Ảnh", "Chương trình khác",
      "Chọn đâu cho đúng", "Chuyện tình yêu", "Chuyện xưa chép lại", "Chất", "Dám sống",
      "Dáng đẹp", "Dưỡng da", "Giác quan thứ 6", "Giải trí", "Giải mã cuộc sống",
      "Giới tính", "Gia đình vui vẻ", "Giờ thứ 9+", "Giai điệu kết nối",
      "Góc của nàng", "Fine Cuisine", "Cùng bàn luận"
  ]

  # --- 3. Thể thao (Sports) ---
  vietnamese_media_topics["Thể thao (Sports)"] += [
      "Chuyển nhượng", "Các đội tuyển trẻ", "Copa Libertadores",
      "Copa Sudamericana", "Cúp Quốc gia Đức", "Giao hữu Quốc tế", "Golf"
  ]

  # --- 4. Kinh tế & Xã hội ---
  vietnamese_media_topics["Kinh tế & Xã hội"] += [
      "Chuyển đổi số", "Công nghiệp hỗ trợ", "Công nghệ", "Công nghệ - Game",
      "Công nghệ 360", "Công nghệ thông tin", "Cộng đồng", "Doanh nghiệp",
      "Doanh nhân", "Dân tộc - Tôn giáo", "Economy", "Giá vàng hôm nay",
      "Giá vàng hôm nay", "Giá cả hàng hóa", "Giá mà biết trước", "Giáo dục - Khoa học",
      "Giáo dục - du học", "Giáo Dục", "Giáo dục", "Du Lịch", "Du học",
      "Du Học", "Du lịch", "Du lịch xanh", "Cộng đồng", "Family", "Công nghệ"
  ]

  # --- 5. Đời sống & Blog ---
  vietnamese_media_topics["Đời sống & Blog"] += [
      "Cao thủ", "Check in Việt Nam", "Cho ngày hoàn hảo", "Chuyện bốn phương",
      "Chuyện nhà nông", "Chuẩn bị mang thai", "Chuẩn cơm mẹ nấu", "Cơ thể bạn nói gì ?",
      "Các mâm cơm HOT MXH", "Các món chè ngon", "Các món ăn sáng", "Cách làm kem ngon",
      "Cây cảnh - Vườn", "Con đường nông sản", "Cư dân mạng", "Cặp lá yêu thương",
      "Dinh dưỡng", "Diễn viên Bình An", "Diễn đàn", "Dạy con", "Dị", "Dự báo thời tiết",
      "Eva làm", "Eva tám", "Gia đình", "Gia đình - Hôn nhân", "Giới trẻ",
      "Chân dung", "Chân dung cuộc sống"
  ]
  
  # --- 1. Tin tức & Thời sự (News & Current Affairs) ---
  vietnamese_media_topics["Tin tức & Thời sự (News & Current Affairs)"] += [
      "Hai bị cáo tại toà.", "Hồ sơ xét xử", "Hải quan Việt nam", "Hà Nội hôm nay",
      "Học và làm theo Bác", "Hội nông dân", "Hộp thư truyền hình",
      "Infographic", "KINH TẾ", "Khát vọng non sông", "Khởi nghiệp", "Khám Phá",
      "Khám phá", "Ký sự", "Kể chuyện làng", "La Liga", "Lao Động cuối tuần",
      "Lao động - Việc làm", "Lao động công đoàn", "LĐLĐ TP Cần Thơ", "LĐLĐ TP Hải Phòng",
      "LĐLĐ TP. Hà Nội", "LĐLĐ TPHCM", "LĐLĐ tỉnh An Giang", "LĐLĐ tỉnh Bắc Giang",
      "LĐLĐ tỉnh Bắc Kạn", "LĐLĐ tỉnh Bắc Ninh", "LĐLĐ tỉnh Cao Bằng", "LĐLĐ tỉnh Cà Mau",
      "LĐLĐ tỉnh Gia Lai", "LĐLĐ tỉnh Hà Nam", "LĐLĐ tỉnh Hòa Bình", "LĐLĐ tỉnh Hưng Yên",
      "LĐLĐ tỉnh Hải Dương", "LĐLĐ tỉnh Hậu Giang", "LĐLĐ tỉnh Khánh Hòa",
      "LĐLĐ tỉnh Lai Châu", "LĐLĐ tỉnh Lào Cai", "LĐLĐ tỉnh Lâm Đồng", "LĐLĐ tỉnh Lạng Sơn",
      "LĐLĐ tỉnh Nam Định", "LĐLĐ tỉnh Nghệ An", "LĐLĐ tỉnh Phú Thọ", "LĐLĐ tỉnh Quảng Nam",
      "LĐLĐ tỉnh Quảng Trị", "LĐLĐ tỉnh Sóc Trăng", "LĐLĐ tỉnh Thái Bình", "LĐLĐ tỉnh Trà Vinh",
      "LĐLĐ tỉnh Tây Ninh", "LĐLĐ tỉnh Vĩnh Long", "LĐLĐ tỉnh Vĩnh Phúc", "LĐLĐ tỉnh Yên Bái",
      "LĐLĐ tỉnh Điện Biên", "LĐLĐ tỉnh Đắk Lắk", "LĐLĐ tỉnh Đồng Nai", "LĐLĐ tỉnh Đồng Tháp",
      "Miền Tây 24h", "Môi trường", "Nations League", "Ngoại giao", "Nhịp đập Việt Nam",
      "Nét đẹp dân gian", "Nước non ngàn dặm", "Núi sông bờ cõi", "Nẻo về nguồn cội",
      "Người lính", "Nhân đạo", "Nhịp cầu nhân ái", "Nơi xảy ra vụ việc"
  ]

  # --- 2. Giải trí & Văn hóa ---
  vietnamese_media_topics["Giải trí & Văn hóa"] += [
      "Hoa Ngữ - Hàn Quốc", "Hoa hậu", "Hậu Trường", "Hậu trường", "Hậu trường bóng đá",
      "Hành trình di sản", "Hành trình vẻ đẹp", "Hàn Thái Tú.", "House n Home",
      "HOW-TO", "Lifestyle", "Luận và Đàm", "Lưu Hương Giang.", "Lạ - Độc - Vui",
      "MV yêu thích", "MV+", "Media", "Metaverse", "Musik", "Made By Me",
      "MULTIMEDIA", "NSND Trọng Trinh.", "Nghệ sĩ Minh Nhí", "Nhạc", "Nhạc sĩ Hồ Hoài Anh",
      "Nhà sao", "Người đẹp và xe", "Nhân Vật", "Nhân vật đẹp", "Nguyễn Như Nam Anh",
      "Nhâm Hoàng Khang", "Lê Hoàng Phong", "Lý Tử Thất", "Luận và Đàm",
      "Giờ thứ 9+", "Giác quan thứ 6", "Hỏi - Đáp", "Nói thẳng", "Nóng Trên Mạng"
  ]

  # --- 3. Thể thao (Sports) ---
  vietnamese_media_topics["Thể thao (Sports)"] += [
      "Hạng nhất Anh", "Hạng nhất Việt Nam", "Ligue 1", "Ngoại hạng Anh",
      "Lịch bóng đá", "Nhịp đập thể thao", "Cúp Quốc gia Đức"
  ]

  # --- 4. Kinh tế & Xã hội ---
  vietnamese_media_topics["Kinh tế & Xã hội"] += [
      "Học tiếng Anh", "Khoa học", "Khoa giáo", "Khách sạn 5 sao", "Kinh Doanh",
      "Kinh doanh", "Kinh tế", "Kinh tế vĩ mô", "Kinh tế xanh", "Khởi nghiệp",
      "Kỹ năng thoát hiểm", "Ngân hàng", "Nhà đất", "Nhà đẹp", "Nhà nông", "Nhà nông vui vẻ",
      "Nông nghiệp xanh", "Người Việt", "Người Việt 4 phương", "Người Việt tử tế",
      "Nghề nghiệp", "Nhịp sống", "Nhịp sống Thủ đô", "Nhịp sống trẻ", "Nhịp sống ô tô"
  ]

  # --- 5. Đời sống & Blog ---
  vietnamese_media_topics["Đời sống & Blog"] += [
      "Hạnh phúc là gì?", "Hôm nay13/07", "HOW-TO", "Hàng hiệu", "Hành trình vẻ đẹp",
      "Không gian xanh", "Không gian đẹp", "Khỏe đẹp", "Kiến Thức Giới Tính",
      "Làm bánh ngon", "Làm mẹ", "Làm vợ", "Làm Đẹp", "Làm đẹp", "Làm đẹp mỗi ngày",
      "Mẹo hay nhà bếp", "Mẹo vặt gia đình", "Mang thai", "Mùa cưới", "Món ngon",
      "Món ngon cuối tuần", "Món ngon ngày hè", "Món ngon từ cá", "Món ngon từ gà",
      "Món ngon từ thịt bò", "Ngon-bổ-rẻ", "Nhật ký người Việt", "Ngộ nghĩnh trẻ thơ",
      "Nhịp sống trẻ", "Nuôi con", "Gia đình", "Gia đình - Hôn nhân",
      "Lifestyle", "Lời tự sự", "Giới trẻ", "Family", "Hạnh phúc là gì?"
  ]
  
  # --- 1. Tin tức & Thời sự (News & Current Affairs) ---
  vietnamese_media_topics["Tin tức & Thời sự (News & Current Affairs)"] += [
      "PHÁP LUẬT", "Pháp luật", "Pháp Luật", "Pháp luật", "Politics", "Policies", "Opinion",
      "Quân Sự", "Quân khu số 1", "Quân sự", "Quân sự thế giới", "Quốc hội", "Quốc hội với cử tri",
      "Quốc tế", "Society", "Sự kiện", "Sự kiện Bình luận", "Thời sự", "Thời sự - Xã hội",
      "Thời sự quốc tế", "Thời sự trong nước", "Tin tức", "Tin tức - Sự kiện", "Tin tức 24h qua",
      "Tin nóng", "Tin nóng trong ngày", "Tin nhanh 24h", "Tin nổi bật Cổng", "Tin video",
      "Tin ảnh", "Tin độc quyền", "Tin chuyển nhượng", "Tin tức trong ngày", "Tin tức sức khỏe",
      "Tin tức việc làm", "Tin tức thời trang", "Tin tức giải trí", "Tin tức nhà đẹp",
      "Tin tức ẩm thực", "Thế Giới Đó Đây", "THẾ GIỚI", "Thế giới", "Thế giới hôm nay",
      "Toàn cảnh thế giới", "Trong nước", "Tuần Việt Nam", "Tuổi Trẻ Cuối Tuần",
      "Tuổi cao gương sáng", "Tổ quốc trong tim", "Tương lai xanh", "Từ những miền quê",
      "V - Việt Nam", "Vietnam Discovery", "VTV1", "VTV kết nối", "VTC News TV",
      "Việt Nam", "Việt Nam hôm nay", "Việt Nam thức giấc", "Vì an ninh Tổ quốc",
      "Vì trẻ em", "Vì tầm vóc Việt", "Week in Review", "Ý kiến", "Địa phương", "Địa ốc",
      "Đối ngoại", "Điểm tin", "Điểm hẹn năm châu", "Đô thị - Địa ốc", "Đèn giao thông",
      "Đường tới nông trại", "Đánh giá", "Đại dịch Covid-19", "Đầu Tư", "Đầu tư - Tài chính",
      "Đời sống xã hội", "XÃ HỘI", "Xã Hội", "Xã hội", "Xây dựng Đảng", "Vì bạn xứng đáng",
      "Văn hóa - Giải trí", "Đời sống", "Đời sống Showbiz"
  ]

  # --- 2. Giải trí & Văn hóa ---
  vietnamese_media_topics["Giải trí & Văn hóa"] += [
      "Phim", "Phim Chiếu Rạp", "Phim Việt Nam", "Phim tài liệu", "Phim ảnh",
      "Phía sau màn nhung", "Phóng sự", "Phóng sự - Khám phá", "Phóng sự - Điều tra",
      "Phụ nữ là số 1", "Phụ nữ và cuộc sống", "Quizz", "Quà tặng cuộc sống",
      "S - Việt Nam", "Sao", "Sao 360°", "Sao Hàn", "Sao Việt", "Sao quốc tế",
      "Sao thế giới", "Sao đương thời", "Series Truyền Hình", "Showbiz",
      "Star", "Star Style", "TV Show", "Talk Vietnam", "Truyền hình", "Truyện cười",
      "Trời sinh một cặp", "Tác phẩm mới", "Tạp chí tiếng Nhật", "Tuổi Trẻ Cười",
      "Văn nghệ", "Văn hóa", "VĂN HÓA", "Wow", "Đẹp", "Đẹp 24/7", "Độc bản Duo",
      "Đấu trường", "Đọc sách cùng bạn", "Đông Tây - Kim Cổ", "Ông bố hoàn hảo",
      "Ô TÔ - XE MÁY", "Ôtô", "Ôtô - Xe máy", "Ô tô", "Ô tô - Xe máy", "Ô tô+", "Xe", "Xe & Số",
      "Xe +", "Xe+", "Xe cộ", "Xe máy - Xe đạp", "Xem - Đọc", "Xem Mua Luôn", "Xem ăn chơi",
      "Xem-Ăn-Chơi", "Âm nhạc", "Âu-Mỹ", "Thời trang", "Thời trang Hi-tech",
      "Thời trang Sao", "Thời trang công sở", "Thời sự thời trang", "Thư giãn"
  ]

  # --- 3. Thể thao (Sports) ---
  vietnamese_media_topics["Thể thao (Sports)"] += [
      "SEA Games 31", "Serie A", "Sport", "Soi kèo", "Tennis", "Thể thao", "THỂ THAO",
      "Thể thao 24/7", "UEFA Europa League", "U19 Việt Nam", "U23 Châu Á", "V-League",
      "Vô địch châu Phi", "World Cup 2022", "eSport", "eSports", "Đua xe F1",
      "Đội tuyển Anh", "Đội tuyển Italia", "Đội tuyển Pháp", "Đội tuyển Quốc gia",
      "Đội tuyển TBN", "Đội tuyển Đức", "Võ Thuật"
  ]

  # --- 4. Kinh tế & Xã hội ---
  vietnamese_media_topics["Kinh tế & Xã hội"] += [
      "Premium", "Startup", "Số hóa", "Sức mạnh số", "Quốc gia số", "Tek-life",
      "Tiêu điểm kinh tế", "Tiếp thị - Bán hàng", "Tài chính", "Thuế và đời sống",
      "Tiêu dùng", "Tỷ giá ngoại tệ", "Tỷ giá ngoại tệ", "Tiền tiền tiền",
      "Rao vặt", "Shopping", "Săn nhà triệu đô", "Số hóa", "Trí tuệ nhân tạo",
      "Thị trường", "Thị trường 24h", "Đánh giá", "Economy", "Policies",
      "Đầu tư - Tài chính", "Địa điểm du lịch", "Phổ biến kiến thức"
  ]

  # --- 5. Đời sống & Blog ---
  vietnamese_media_topics["Đời sống & Blog"] += [
      "Phẫu thuật thẩm mỹ", "Phụ kiện", "Phong thủy", "Phổ biến kiến thức",
      "Sống", "Sống Xanh", "Sống chậm", "Sống khỏe", "Sống khỏe đời vui",
      "Sống kết nối", "Sống mới", "Sống vui", "Sống đẹp", "Sống ở Hà Nội",
      "Sau sinh", "Sinh con", "SỨC KHỎE", "Sức Khỏe", "Sức khỏe", "Sức khỏe đời sống",
      "Thú nuôi", "Thiết kế nội thất", "Thực đơn hàng ngày", "Trang trí nhà cửa",
      "Trang điểm", "Tâm sự", "Tâm hồn làng Việt", "Tản mạn", "Tấm Lòng Vàng",
      "Tấm lòng Việt", "Tấm lòng nhân ái", "Trạm yêu thương", "Trạng nguyên nhí",
      "Tư vấn", "Tư vấn mặc đẹp", "Tuổi trẻ", "U30 - U40", "Vui - khoẻ - có ích",
      "Vui khỏe 24/7", "Vui sống mỗi ngày", "Y TẾ", "Y tế", "Vaccine",
      "Đánh thức cơ thể", "Độc bản Duo", "Đời sống", "Đời sống Showbiz"
  ]
  
  return vietnamese_media_topics

# Loop over all the dictionary items in the `data` list
def clean_topic_field(topic_field: dict, topics_dictionary: dict) -> str:
    """
    This function will clean the topic field of each item in the dataset.
    
    Return:
        - An item with a clean topic field.
    """
    
    # Loop over keys in the topics_dictionary
    # If the topic_field is inside the list of a key
    # Replace the topic_field by that key
    # Note: A key is a large topic and topic_field, at start, is a small topic.
    found = False
    for key in topics_dictionary.keys():
        if topic_field in topics_dictionary[key]:
            topic_field = key
            found = True
    
    if found == False:
        topic_field = "unknown"
    else:
        topic_field = topic_field.lower()
    
    return topic_field
  
def clean_item(item) -> dict:
    """
    Takes in a news item in Python's dictionary
    and clean the content, topic, and metadata of the item.
    
    Args:
        - item: dict - The Python's dictionary storing data for a news item
         
    Return:
        - A cleaned Python dictionary having only the content and topic for each news item.
    """
    
    item = item.copy()
    
    # Each worker processes one item independently
    
    # Clean content
    item['content'] = clean_content(item['content'])
    
    # Clean topic
    vietnamese_media_topics = get_vn_media_topics()
    if item["topic"] == "":
        item["topic"] = "unknown"
    else:
        item["topic"] = clean_topic_field(item['topic'], vietnamese_media_topics)
        
    # Clean metadata
    metadata = item['metadata']
    if 'topic' in metadata:
        metadata['small_topic'] = metadata.pop('topic')

    result = {}
    result['content'] = item['content']
    result['topic'] = item['topic']
    result['metadata'] = metadata

    return result

def process_segmented_content(segmented_content):
    """
    Expand every occurrence of 'number_number' inside each token list
    into two tokens: ['number', 'number'].

    Parameters
    ----------
    segmented_content : list[list[str]]
        A list of tokenized sentences (each inner list contains tokens).

    Returns
    -------
    list[list[str]]
        A new list where every 'number_number' is expanded into
        two 'number' tokens.
    """
    return [
        [
            subtoken if subtoken != 'number_number' else 'number'
            for token in sentence
            for subtoken in ([token] if token != 'number_number'
                             else ['number', 'number'])
        ]
        for sentence in segmented_content
    ]