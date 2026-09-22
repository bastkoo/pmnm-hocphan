# BÀI 2.4: NGHIÊN CỨU VIỆC HASHICORP CHUYỂN ĐỔI GIẤY PHÉP TERRAFORM SANG BSL-1.1 VÀ SỰ RA ĐỜI CỦA OPENTOFU

## 1. Mở đầu
Tháng 8 năm 2023, cộng đồng công nghệ thông tin toàn cầu chứng kiến một bước ngoặt lớn trong hệ sinh thái mã nguồn mở: HashiCorp thông báo thay đổi giấy phép bản quyền của Terraform — công cụ Quản lý Hạ tầng dưới dạng Mã nguồn (Infrastructure as Code - IaC) hàng đầu thế giới — từ Mozilla Public License 2.0 (MPL-2.0) sang Business Source License v1.1 (BSL-1.1 hay BUSL-1.1). Quyết định này ngay lập tức thổi bùng lên các tranh cãi dữ dội về ranh giới giữa mã nguồn mở và kinh doanh thương mại, đồng thời dẫn đến sự ra đời của OpenTofu — một bản fork mã nguồn mở hoàn toàn nhằm duy trì các giá trị cốt lõi của cộng đồng.

---

## 2. Bối cảnh và Nguyên nhân HashiCorp chuyển đổi giấy phép

### a. Sự khác biệt giữa MPL-2.0 và BSL-1.1
* **MPL-2.0 (Mozilla Public License 2.0):** Là một giấy phép mã nguồn mở thuộc nhóm Weak Copyleft. MPL-2.0 cho phép bất kỳ ai tự do sử dụng, chỉnh sửa, tích hợp và thương mại hóa mã nguồn, miễn là phần mã nguồn thuộc về các file gốc của MPL được giữ nguyên hoặc đóng góp lại nếu có sửa đổi.
* **BSL-1.1 (Business Source License 1.1):** Không được tổ chức Open Source Initiative (OSI) công nhận là giấy phép "mã nguồn mở" chuẩn nghĩa (Source-Available). BSL-1.1 cho phép người dùng xem, chỉnh sửa và sử dụng mã nguồn cho mục đích phi thương mại hoặc nội bộ. Tuy nhiên, giấy phép này cấm việc sử dụng mã nguồn để cung cấp các sản phẩm/dịch vụ cạnh tranh trực tiếp với sản phẩm thương mại của HashiCorp (ví dụ: cung cấp dịch vụ quản lý Terraform dưới dạng Managed Service/SaaS). Đặc biệt, sau một thời hạn nhất định (thường là 4 năm), mã nguồn BSL sẽ tự động chuyển về một giấy phép mở chuẩn (như Change License).

### b. Động cơ kinh doanh của HashiCorp
Nguyên nhân cốt lõi khiến HashiCorp đưa ra quyết định này xuất phát từ xung đột lợi ích thương mại. Trong nhiều năm, HashiCorp đã đầu tư nguồn lực khổng lồ để phát triển và hoàn thiện Terraform. Tuy nhiên, các nhà cung cấp dịch vụ đám mây lớn và các công ty khởi nghiệp (như Spacelift, env0, Scalr) đã tận dụng miễn phí mã nguồn mở Terraform theo giấy phép MPL-2.0 để xây dựng các nền tảng thương mại cạnh tranh trực tiếp với dự án trả phí Terraform Cloud / Enterprise của HashiCorp.

HashiCorp cho rằng mô hình mã nguồn mở truyền thống không còn bảo vệ được giá trị đầu tư của họ khi các đối thủ "dùng miễn phí" công sức của họ mà không đóng góp tương xứng. Việc chuyển sang BSL-1.1 nhằm thiết lập rào cản pháp lý, buộc các nhà cung cấp dịch vụ thương mại cạnh tranh phải mua giấy phép kinh doanh thương mại từ HashiCorp.

---

## 3. Phản ứng của cộng đồng và Sự ra đời của OpenTofu

### a. Sự phẫn nộ từ cộng đồng và doanh nghiệp
Quyết định của HashiCorp tạo ra làn sóng bất bình mạnh mẽ. Nhiều công ty lo ngại sự mơ hồ trong khái niệm "sản phẩm cạnh tranh" của BSL-1.1 sẽ tạo ra rủi ro pháp lý lớn cho hệ thống hạ tầng của họ. Các nhà phát triển từng đóng góp công sức cho Terraform cảm thấy bị phản bội khi đóng góp của họ bị chuyển đổi thành một phần của giấy phép thương mại đóng.

### b. Hành động của Linux Foundation và sự thành lập OpenTofu
Chỉ ít tuần sau thông báo của HashiCorp, vào tháng 8 năm 2023, một liên minh gồm hàng chục công ty công nghệ và hàng trăm lập trình viên đã thành lập dự án **OpenTF**. 

Đến tháng 9 năm 2023, dự án chính thức đổi tên thành **OpenTofu** và được bảo trợ dưới sự quản lý của **Linux Foundation** — tổ chức phi lợi nhuận uy tín hàng đầu về mã nguồn mở. OpenTofu được fork ra từ phiên bản cuối cùng của Terraform trước khi đổi giấy phép (phiên bản 1.5.x, vẫn mang giấy phép MPL-2.0).

Mục tiêu của OpenTofu là:
* Duy trì một công cụ IaC mã nguồn mở hoàn toàn, trung lập và thuộc về cộng đồng.
* Sử dụng giấy phép mở chuẩn **MPL-2.0**.
* Đảm bảo khả năng tương thích ngược 100% với các phiên bản Terraform cũ.

---

## 4. Tác động và Ý nghĩa pháp lý - Kinh tế

### a. Tác động đối với hệ sinh thái IaC
Sự kiện này chia rẽ hệ sinh thái quản lý hạ tầng thành hai ngả:
* **Hệ sinh thái Terraform (HashiCorp):** Tiếp tục phát triển theo định hướng bảo hộ thương mại dưới BSL-1.1, tập trung vào khách hàng doanh nghiệp sử dụng hệ sinh thái khép kín của HashiCorp.
* **Hệ sinh thái OpenTofu (Linux Foundation):** Nhận được sự ủng hộ mạnh mẽ từ cộng đồng, các công ty Cloud Native và các nhà cung cấp dịch vụ độc lập nhờ tính minh bạch và sự bảo trợ trung lập của Linux Foundation.

### b. Bài học pháp lý cho ngành phần mềm mã nguồn mở
1. **Xu hướng thương mại hóa mã nguồn mở:** Sự việc của HashiCorp không phải duy nhất (trước đó có MongoDB chuyển sang SSPL, ElasticSearch chuyển sang SSPL/BSL). Điều này phản ánh cuộc khủng hoảng mô hình kinh doanh của các công ty mã nguồn mở trước sự lấn lướt của các gã khổng lồ điện toán đám mây (Cloud Providers).
2. **Sức mạnh phản kháng của cộng đồng:** Sự ra đời thần tốc của OpenTofu chứng minh cơ chế Copyleft và quyền Fork của mã nguồn mở vẫn là "vũ khí" hiệu quả nhất để cộng đồng tự bảo vệ mình trước các quyết định đơn phương từ doanh nghiệp.
3. **Rủi ro phụ thuộc vào một vendor (Vendor Lock-in):** Các doanh nghiệp khi lựa chọn công cụ công nghệ ngày càng cẩn trọng hơn với các dự án mã nguồn mở do duy nhất một công ty nắm giữ toàn bộ bản quyền (Single-vendor Open Source).

---

## 5. Kết luận
Cuộc chuyển đổi giấy phép của HashiCorp và sự trỗi dậy của OpenTofu là một bài học đắt giá về sự cân bằng giữa lợi ích kinh doanh của doanh nghiệp và giá trị cốt lõi của cộng đồng mã nguồn mở. Nó đánh dấu bước chuyển mình của ngành phần mềm, nơi các tiêu chuẩn giấy phép không chỉ là văn bản pháp lý mà còn quyết định sự sống còn của cả một hệ sinh thái công nghệ.