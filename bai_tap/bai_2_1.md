# BÀI 2.1: LỰA CHỌN GIẤY PHÉP PHẦN MỀM CHO DỰ ÁN

**Dự án lựa chọn:** Nền tảng thương mại điện tử có bán bản doanh nghiệp.

---

## 1. Xác định giấy phép phù hợp
Đối với nền tảng thương mại điện tử có định hướng bán phiên bản Doanh nghiệp (Enterprise), giải pháp tối ưu nhất là áp dụng mô hình **Dual-Licensing (Giấy phép kép)**:
* **Phiên bản Cộng đồng (Community Edition):** Phát hành dưới giấy phép **GNU AGPLv3 (Affero General Public License version 3)**.
* **Phiên bản Doanh nghiệp (Enterprise Edition):** Phát hành dưới **Giấy phép Thương mại (Commercial License)** do chính nhà phát triển sở hữu.

## 2. Bài lập luận 

### Đặt vấn đề
Một nền tảng thương mại điện tử khi phát triển cần cân bằng hai mục tiêu: vừa tận dụng sức mạnh cộng đồng để nhanh chóng mở rộng thị phần, vừa đảm bảo mô hình tài chính bền vững thông qua việc bán các bản trả phí cho doanh nghiệp lớn. 

### Phân tích

#### a. Ràng buộc bảo vệ mã nguồn mở với AGPLv3
Khác với các giấy phép rành buộc yếu hay GPL thông thường, **AGPLv3** mở rộng điều khoản Copyleft áp dụng cho cả các mô hình triển khai trên điện toán đám mây hay máy chủ (SaaS). Bất kỳ cá nhân hay tổ chức nào chỉnh sửa, nâng cấp nền tảng và vận hành trên máy chủ cho người dùng cuối truy cập đều **bắt buộc phải công khai toàn bộ mã nguồn cải tiến** cho cộng đồng. Điều này giúp ngăn chặn các đối thủ lấy miễn phí mã nguồn mở để kinh doanh dịch vụ đóng độc quyền mà không đóng góp lại cho dự án.

#### b. Động lực thúc đẩy thương mại với Commercial License
Các doanh nghiệp lớn khi triển khai thương mại điện tử luôn có nhu cầu bảo mật quy trình kinh doanh, tích hợp hệ thống nội bộ độc quyền (ERP, CRM) và yêu cầu cam kết chất lượng dịch vụ (SLA) kèm hỗ trợ kỹ thuật chuyên sâu. Điều khoản buộc mở mã nguồn của AGPLv3 sẽ khiến nhóm khách hàng này không thể dùng bản miễn phí. Do đó, họ sẽ sẵn sàng chi trả để **mua Giấy phép Thương mại (Commercial License)** nhằm được miễn trừ nghĩa vụ công khai mã nguồn và nhận được các quyền lợi ưu tiên.

#### c. Hiệu quả thực tiễn
Mô hình Dual-Licensing đã chứng minh tính hiệu quả vượt trội ở nhiều dự án mã nguồn mở thành công trên thế giới như Odoo, Magento hay MongoDB. Mô hình này vừa duy trì được lực lượng đóng góp đông đảo từ cộng đồng lập trình viên, vừa tạo ra nguồn doanh thu thương mại ổn định để tái đầu tư phát triển sản phẩm.

Chiến lược **Dual-Licensing (AGPLv3 kết hợp Commercial License)** là sự lựa chọn hài hòa nhất, giúp bảo vệ tính mở của sản phẩm cộng đồng, đồng thời tạo tiền đề tài chính vững chắc cho sự phát triển lâu dài của dự án.