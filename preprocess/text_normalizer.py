from bs4 import BeautifulSoup
import unicodedata
import re
from nltk.tokenize.punkt import PunktSentenceTokenizer
from punkt_tokenize.sentence_split import get_spliter

def normalize_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)

def strip_html(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def normalize_spacing(text: str) -> str:
    """
    Normalize spacing in Vietnamese text:
    - Remove redundant whitespace
    - Remove space before punctuation
    - Ensure exactly one space after punctuation
    - Fix spacing inside parentheses and quotes
    """

    # Remove space before punctuation
    text = re.sub(r"\s+([.,;:?!])", r"\1", text)

    # Ensure exactly one space after punctuation
    text = re.sub(r"([.,;:?!])\s*", r"\1 ", text)

    # Remove space after opening brackets/quotes
    text = re.sub(r"([\(\[\{“‘])\s+", r"\1", text)

    # Remove space before closing brackets/quotes
    text = re.sub(r"\s+([\)\]\}”’])", r"\1", text)

    # Collapse multiple spaces (including tabs, newlines) into one space
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing spaces
    return text.strip()

def segment_text_to_sentences(text: str, sent_tokenizer: PunktSentenceTokenizer):
    """
    Segment sentences using https://github.com/undertheseanlp/sent_tokenize
    """
    sentences = sent_tokenizer.sentences_from_text(text)
    
    return sentences

text = "Chiều 31/7, Công an tỉnh Thừa Thiên - Huế đã có thông tin ban đầu về vụ nổ súng,cướp tiệm vàng tại chợ Đông Ba nằm trên đường Trần Hưng Đạo (TP Huế, tỉnh Thừa Thiên - Huế). Thông Sài Gòn Giải Phóng, khoảng 12h30' ngày 31/7, một đối tượng sử dụng súng AK bất ngờ xông vào tiệm vàng Hoàng Đức và Thái Lợi (phía trước chợ Đông Ba) rồi nổ súng chỉ thiên liên tiếp uy hiếp chủ tiệm để cướp vàng. Sau đó, đối tượng mang số vàng vừa cướp được vứt ra vỉa hè rồi đi bộ đến khu vực cầu Gia Hội, cách khu vực gây án khoảng 300m. Giám đốc Công an tỉnh Thừa Thiên – Huế lập tức trực tiếp chỉ đạo các lực lượng chức năng gồm Công an tỉnh và Công an TP Huế nhanh chóng có mặt tại hiện trường triển khai đồng bộ các biện pháp nghiệp vụ, khoanh vùng và ngăn không để người dân đi vào hiện trường. Hàng trăm tiểu thương trong chợ Đông Ba và người dân gần cầu Gia Hội được yêu cầu di chuyển khỏi hiện trường, đóng cửa nhà đề phòng đạn lạc. Tuy nhiên, thấy vàng bị ném ra đường, nhiều người đua nhau nhặt, tạo cảnh nhốn nháo trước cổng chợ. Do đây là khu vực trung tâm TP Huế, đông dân nên để đảm bảo an toàn cho người dân, lực lượng công an đã tìm cách hướng đối tượng ra nhà lục giác tại khu vực Công viên Trịnh Công Sơn (cạnh cầu Gia Hội). Lúc này, đối tượng có biểu hiện kích động muốn tự tử nên Đại tá Phạm Văn Toàn, Trưởng Phòng Cảnh sát hình sự Công an tỉnh Thừa Thiên – Huế và một số đồng chí Công an khác trực tiếp tiếp cận, thuyết phục đối tượng. Đối tượng lại yêu cầu được nói chuyện với Đại tá Đặng Ngọc Sơn, Phó Giám đốc Công an tỉnh. Ngay sau đó, khi được Đại tá Đặng Ngọc Sơn gặp gỡ, động viên, thuyết phục, đối tượng đã đồng ý hạ và giao nộp vũ khí. Theo VnExpress cho biết, tên cướp là Ngô Văn Quốc, 38 tuổi, quân hàm đại úy, công tác tại Trại giam Bình Điền, đóng ở xã Bình Tiến, thị xã Hương Trà. Khẩu súng gây án đã bị thu giữ. Hiện trường hai tiệm vàng bị phong tỏa để công an khám nghiệm. Phía trong nhiều mảnh kính bị vỡ văng vãi khắp nơi. Đông Ba là chợ nổi tiếng và sầm uất nhất TP Huế, nằm bên bờ bắc sông Hương, trên đường Trần Hưng Đạo. Nơi đây thu hút nhiều du khách trong và ngoài nước trong hành trình du lịch Huế. Theo MT (2sao/VietNamNet) https://2sao.vn/ten-cuop-tiem-vang-tai-hue-la-dai-uy-cong-an-cong-tac-tai-trai-giam-n-315312.html Trang Thông tin điện tử Docbao.vn Công ty Cổ phần Quang Minh Việt Nam Giấy phép thiết lập Trang thông tin điện tử tổng hợp trên Internet số 2372/GP-STTTT cấp ngày 29/8/2014. SĐT: 024. 666.40816 Địa chỉ: P604, Tầng 6, Tòa nhà Golden Field, Khu đô thị mới Mỹ Đình 1, phường Cầu Diễn, quận Nam Từ Liêm, Hà Nội Chịu trách nhiệm nội dung: Điều Thị Bích; ĐT: 0903.263.198; Email: docbao@kib.vn Đọc báo trực tuyến hiện tại chỉ sử dụng tên miền duy nhất là docbao.vn; độc giả lưu ý tránh nhầm lẫn. Chính sách bảo mật RSS"

sent_tokenizer = get_spliter()
sentences = segment_text_to_sentences(text, sent_tokenizer)
print(sentences)