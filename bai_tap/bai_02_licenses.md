| Name               | Version     | License                                            |
|--------------------|-------------|----------------------------------------------------|
| Django             | 6.1.1       | BSD-3-Clause                                       |
| Flask              | 3.1.3       | BSD-3-Clause                                       |
| Jinja2             | 3.1.6       | BSD License                                        |
| MarkupSafe         | 3.0.3       | BSD-3-Clause                                       |
| Werkzeug           | 3.1.8       | BSD-3-Clause                                       |
| asgiref            | 3.12.1      | BSD License                                        |
| blinker            | 1.9.0       | MIT License                                        |
| certifi            | 2026.7.22   | Mozilla Public License 2.0 (MPL 2.0)               |
| charset-normalizer | 3.5.1       | MIT                                                |
| click              | 8.5.0       | BSD-3-Clause                                       |
| contourpy          | 1.4.0       | BSD-3-Clause                                       |
| cycler             | 0.12.1      | BSD License                                        |
| fonttools          | 4.65.0      | MIT                                                |
| idna               | 3.20        | BSD-3-Clause                                       |
| itsdangerous       | 2.2.0       | BSD License                                        |
| kiwisolver         | 1.5.1       | BSD License                                        |
| matplotlib         | 3.11.2      | Python Software Foundation License                 |
| numpy              | 2.5.3       | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| packaging          | 26.3        | Apache-2.0 OR BSD-2-Clause                         |
| pandas             | 3.0.6       | BSD License                                        |
| pillow             | 12.3.0      | MIT-CMU                                            |
| pyparsing          | 3.3.3       | MIT                                                |
| python-dateutil    | 2.9.0.post0 | Apache Software License; BSD License               |
| requests           | 2.34.2      | Apache Software License                            |
| six                | 1.17.0      | MIT License                                        |
| sqlparse           | 0.6.0       | BSD License                                        |
| tzdata             | 2026.4      | Apache-2.0                                         |
| urllib3            | 2.8.0       | MIT                                                |

## Phân tích gói thuộc nhóm Copyleft mạnh
Dựa trên bảng thống kê danh sách các gói phụ thuộc, **không có gói nào thuộc nhóm Copyleft mạnh** (như GNU GPLv2, GNU GPLv3, hay GNU AGPLv3). 

Hầu hết các gói sử dụng giấy phép dạng **Permissive** (MIT, BSD, Apache 2.0) và có một gói thuộc nhóm **Weak Copyleft** (certifi - MPL 2.0).

## Nghĩa vụ phát sinh đối với dự án phần mềm thương mại đóng nguồn
Vì dự án không sử dụng các thư viện có giấy phép Copyleft mạnh, sản phẩm hoàn toàn có thể **đóng nguồn và thương mại hóa độc quyền** mà không bị buộc phải công khai toàn bộ mã nguồn ứng dụng.

Tuy nhiên, nhà phát triển phải tuân thủ các nghĩa vụ pháp lý sau:
1. **Thông báo bản quyền (Copyright Notices):** Giữ nguyên và công khai nội dung giấy phép cùng thông báo bản quyền gốc của tất cả các thư viện phụ thuộc (MIT, BSD, Apache 2.0, MPL 2.0) trong phần tài liệu hướng dẫn hoặc giao diện ứng dụng.
2. **Quy định đối với MPL 2.0 (Gói certifi):** Giữ nguyên mã nguồn của gói `certifi`. Nếu có thực hiện chỉnh sửa trực tiếp vào mã nguồn của `certifi`, phần chỉnh sửa đó phải được mở mã nguồn theo điều khoản của MPL 2.0.
3. **Miễn trừ trách nhiệm:** Giữ nguyên các tuyên bố miễn trừ trách nhiệm pháp lý đối với lỗi phát sinh từ các thư viện bên thứ ba.