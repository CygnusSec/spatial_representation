# Nội dung cần sửa trong báo cáo "Biểu diễn đối tượng không gian"

Tệp đích: `Courses/GIS/contents/content.tex`. Số liệu lấy từ `experiments/results_group`.
Số dòng là vị trí tại thời điểm soát; hãy tìm theo nội dung nếu tệp đã thay đổi.

## Cần kiểm tra trước khi dùng

- [ ] **Chạy lại thực nghiệm.** Các số dưới đây đến từ lần chạy bằng Claude Code trong Docker trên máy này. Câu "thực hiện trên máy của nhóm" chỉ nên giữ khi nhóm tự chạy lại và hiểu mã; nếu chạy lại thì thay số theo kết quả mới. Nếu lớp có quy định về dùng AI, cần khai báo theo quy định đó.
- [ ] **Hệ số nửa mặt phẳng ở mục B.** Mới được thế tay các đỉnh, chưa đưa vào `theory_examples.py`.
- [ ] **Trích dẫn [3] về trường phân loại.** Cần đối chiếu với toàn văn bài của Goodchild, Yuan và Cova.
- [ ] **Bảng ở mục C.** Đây là cách diễn giải của nhóm; cần sẵn sàng giải thích khi bị hỏi.
- [ ] **Thông tin nhóm.** Điền tên thành viên và lớp trên trang bìa.

---

# A. Thay phần môi trường và số liệu

## A1. Thay đoạn ở dòng 297

> Đây là các lần chạy thực tế trên dữ liệu tổng hợp, thực hiện trên máy của nhóm ngày 03/11/2026 trong container Docker. Dữ liệu, mã, cấu hình, nhật ký và kết quả từng lượt được lưu trong gói tái lập. Các số liệu không phải số đo thực địa và không lấy lại từ các bài báo. Phương pháp tham khảo cách xác định đường xử lý của [10] và cách tách tải dữ liệu với hiển thị của [11], [12]; thiết kế ở đây có quy mô và phạm vi riêng.

## A2. Thay đoạn ở dòng 305

> Lần chạy sử dụng Python 3.12.16 trên Linux x86_64, CPU Intel Core i7-9700 (8 lõi), trong container giới hạn 8 CPU và 8 GiB bộ nhớ. Các thư viện chính gồm Shapely 2.2.0, GEOS 3.14.1, GeoPandas 1.2.0, PyArrow 26.0.0, topojson 2.2, mapbox-vector-tile 2.2.0, pyproj 3.8.0 và PROJ 9.8.1. Máy vẫn chạy các ứng dụng khác trong lúc đo nên thời gian có nhiễu. Tệp environment.json ghi đầy đủ phiên bản và thời điểm chạy.

## A3. Thay số trong các bảng

Bảng 5 và Bảng 9 **giữ nguyên** vì E1 và dung lượng E3 trùng khớp giữa hai lần chạy.

**Bảng 6. Dung lượng và thời gian trung vị với 10.000 đa giác**

| Cấu hình | Tệp byte | Gzip6 byte | Ghi ms | Đọc ms |
|---|---:|---:|---:|---:|
| GeoJSON | 4.551.029 | 538.339 | 415,032 | 344,613 |
| TopoJSON | 3.017.111 | 439.887 | 5.951,398 | 357,933 |
| KML | 6.511.224 | 546.117 | 587,172 | 607,346 |
| GeoParquet NONE | 3.023.469 | 536.556 | 35,986 | 44,112 |
| GeoParquet ZSTD | 452.131 | 253.110 | 35,076 | 45,894 |

**Bảng 7. Khoảng Q1 đến Q3 ở 10.000 đa giác**

| Cấu hình | Ghi Q1–Q3 ms | Đọc Q1–Q3 ms |
|---|---:|---:|
| GeoJSON | 405,899–416,604 | 339,022–347,016 |
| TopoJSON | 5.921,509–6.047,245 | 356,452–363,152 |
| KML | 578,769–609,666 | 604,725–607,505 |
| GeoParquet NONE | 35,427–38,294 | 43,787–45,012 |
| GeoParquet ZSTD | 34,567–35,910 | 44,302–47,125 |

**Bảng 8. Thời gian đọc trung vị theo quy mô**

| Cấu hình | 100 ms | 1.000 ms | 10.000 ms |
|---|---:|---:|---:|
| GeoJSON | 3,357 | 31,381 | 344,613 |
| TopoJSON | 3,248 | 30,565 | 357,933 |
| KML | 6,754 | 63,047 | 607,346 |
| GeoParquet NONE | 26,510 | 28,351 | 44,112 |
| GeoParquet ZSTD | 26,756 | 28,134 | 45,894 |

**Bảng 10. Sai số toàn miền và thời gian giải mã vùng nhìn của MVT**

| Zoom | Bước lưới m | Hausdorff lớn nhất m | Sai khác diện tích % | Giải mã trung vị ms |
|---:|---:|---:|---:|---:|
| 11 | 4,777314 | 3,371148 | 2,711787 | 628,323 |
| 13 | 1,194329 | 0,837874 | 0,699537 | 355,564 |
| 15 | 0,298582 | 0,209441 | 0,174150 | 92,307 |

## A4. Thay các đoạn nhận xét

**Sau Bảng 7, đoạn "Dung lượng nhỏ hơn...":**

> Dung lượng nhỏ hơn không đi cùng thời gian ghi ngắn hơn. Dựng và ghi TopoJSON mất trung vị 5.951,398 ms, gấp khoảng 14 lần GeoJSON (415,032 ms). Điều này phù hợp với nhận xét của sách rằng mô hình topo phải tính trước một phần đồ thị phẳng khi nhập đối tượng [1, tr. 51]. Tệp KML gốc lớn hơn GeoJSON, nhưng sau gzip hai kích thước gần nhau: 546.117 và 538.339 byte.

**Sau Bảng 8, đoạn "GeoParquet ZSTD đọc...":**

> GeoParquet ZSTD đọc 10.000 đối tượng trong 45,894 ms, thấp hơn nhiều so với 344,613 ms của GeoJSON. Với 100 đối tượng, thứ tự đảo lại: GeoJSON cần 3,357 ms, còn GeoParquet ZSTD cần 26,756 ms. Điều này phù hợp với giả thuyết chi phí mở tệp và diễn giải metadata chi phối bộ nhỏ, nhưng thực nghiệm chưa đo tách riêng các chi phí đó. Ở 1.000 đối tượng, hai cấu hình gần nhau (31,381 và 28,134 ms) và khoảng Q1–Q3 chồng lấn, nên không thể suy ra một ngưỡng chuyển đổi chính xác.

**Câu sai số diện tích của TopoJSON:**

> Sai lệch diện tích tương đối lớn nhất của TopoJSON xấp xỉ 2,25 × 10⁻¹⁶, phù hợp với ảnh hưởng của phép tính số thực.

**Câu Q1–Q3 của MVT:**

> Thời gian giải mã vùng nhìn có Q1–Q3 lần lượt là 628,046–628,585 ms tại zoom 11; 352,924–355,657 ms tại zoom 13; và 91,964–92,793 ms tại zoom 15.

## A5. Thêm mục cuối Mục 6: "So sánh với lần chạy trên môi trường khác"

> Để kiểm tra khả năng tái lập, nhóm so sánh với một lần chạy trước trên môi trường khác (AMD EPYC 9V74, Python 3.12.14) dùng cùng mã và cùng phiên bản thư viện đã ghim. Các phần xác định cho kết quả giống nhau: cả 15 tệp E2 trùng mã băm SHA-256, kết quả E1 trùng khớp, dung lượng gzip và Hausdorff của E3 không đổi. Thời gian thì khác: ghi TopoJSON ở N = 10.000 là 5.313 ms so với 5.951 ms; đọc GeoParquet ZSTD là 51 ms so với 46 ms. Ở N = 1.000, thứ tự đọc giữa GeoJSON và GeoParquet ZSTD đảo chiều (23,1 và 32,6 ms ở lần trước; 31,4 và 28,1 ms ở lần này). Vì vậy, số byte và sai số hình học có thể xem là ổn định, còn thứ hạng thời gian ở vùng giao nhau phụ thuộc môi trường.

## A6. Thêm vào cuối Kết luận

> Lần chạy trên máy của nhóm và lần chạy trên môi trường khác cho cùng dữ liệu đầu ra đến từng byte, trong khi thời gian thay đổi theo môi trường. Vì vậy, kết luận về dung lượng và sai số có độ tin cậy cao hơn so với thứ hạng thời gian ở các quy mô mà các đường cong giao nhau.

---

# B. Bổ sung lý thuyết còn thiếu

## B1. Thêm vào đầu mục mô hình thực thể

> Sách phân đối tượng không gian theo số chiều [1, tr. 31–34]. **Đối tượng 0 chiều** là điểm, dùng khi hình dạng không quan trọng. **Đối tượng 1 chiều** dùng đường gấp khúc (polyline): một tập hữu hạn các đoạn thẳng, trong đó mỗi đầu mút được dùng chung bởi đúng hai đoạn, trừ hai điểm cực trị chỉ thuộc một đoạn. Polyline là *đóng* nếu hai điểm cực trị trùng nhau; là *đơn* nếu các cạnh không liên tiếp không cắt nhau; là *đơn điệu* theo đường L nếu mọi đường vuông góc với L cắt polyline tại nhiều nhất một điểm.
>
> **Đối tượng 2 chiều** dùng đa giác, là vùng được bao bởi một polyline đóng. Đa giác là *đơn* nếu biên là polyline đơn; là *lồi* nếu đoạn nối hai điểm bất kỳ trong đa giác nằm trọn trong đa giác; là *đơn điệu* nếu là đa giác đơn và biên tách được thành đúng hai polyline đơn điệu. **Vùng (region)** là một tập đa giác, nên có thể không liên thông, như một quốc gia và các đảo. Việc chọn kiểu hình học phụ thuộc mục đích và tỉ lệ: một sân bay có thể là điểm hoặc vùng.

## B2. Mô hình trường: thay câu "không nhất thiết là hàm liên tục"

> Sách mô tả thuộc tính của trường là các hàm liên tục theo x và y [1, tr. 34]. Báo cáo dùng cách hiểu rộng hơn, cho phép cả giá trị nhãn như loại đất [3]; khi đó trường không còn là hàm liên tục theo nghĩa của sách.

## B3. Thêm vào mục raster

> Chia ô gồm chia đều và không đều [1, tr. 35–38]. Chia đều dùng các ô cùng kích thước, như raster vuông hoặc lưới lục giác; chia không đều dùng các ô khác kích thước, như vùng địa chính hoặc đa giác Thiessen (biểu đồ Voronoi), trong đó mỗi đa giác gồm các điểm gần một điểm mẫu nhất. Với dữ liệu trường, miền của hàm chuyển từ tập điểm vô hạn thành tập pixel hữu hạn. Với dữ liệu thực thể, đối tượng được biểu diễn bằng tập pixel nhỏ nhất chứa nó. Độ phân giải càng cao thì xấp xỉ càng tốt nhưng càng tốn bộ nhớ và thời gian xử lý.

## B4. Thêm vào mục vector

> Sách dùng ký hiệu [ ] cho bộ, < > cho danh sách và { } cho tập [1, tr. 38]:

```text
point   : [x: real, y: real]
polyline: < point >
polygon : < point >
region  : { polygon }
```

> Ví dụ, đa giác P ở Hình 2.6 của sách là < [4,4], [6,1], [3,0], [0,2], [2,2] >. Đa giác n đỉnh có 2n cách biểu diễn: n cách chọn đỉnh đầu và 2 chiều duyệt. Cấu trúc này không phân biệt polyline với đa giác và không bảo đảm tính đơn hay tính lồi, nên phần mềm phải tự kiểm tra [1, tr. 39]. Với TIN, ngoài tập điểm mẫu còn lưu tập cạnh và tập tam giác: mỗi cạnh trỏ đến hai đầu mút và hai tam giác kề (4 con trỏ), mỗi tam giác trỏ đến ba cạnh (3 con trỏ) [1, tr. 42].

## B5. Thêm vào mục nửa mặt phẳng

> Một nửa không gian trong ℝᵈ được biểu diễn bằng vectơ [a₁, …, a_d, a_{d+1}]. *Đa diện lồi (polytope)* là giao của hữu hạn nửa không gian đóng; *khối đa diện (polyhedron)* là hợp của hữu hạn polytope, không nhất thiết lồi hay liên thông [1, tr. 42]. Đa giác lồi n cạnh là giao của n nửa mặt phẳng, còn đa giác không lồi phải tách thành các mảnh lồi. Đa giác P ở trên được tách theo đường qua (2,2) và (3,0) thành hai mảnh, mỗi mảnh viết dưới dạng ax + by + c ≤ 0:
>
> - P₁, tam giác (0,2), (2,2), (3,0): [0, 1, −2], [−2, −3, 6], [2, 1, −6].
> - P₂, tứ giác (2,2), (4,4), (6,1), (3,0): [−1, 1, 0], [3, 2, −20], [1, −3, −3], [−2, −1, 6].
>
> Cách tách không duy nhất: P cũng có thể tách theo đường qua (0,2) và (2,2) [1, tr. 46]. Cùng một dạng ràng buộc còn biểu diễn được đối tượng không bị chặn và mở rộng sang nhiều chiều, đây là động lực của mô hình dữ liệu ràng buộc.

## B6. Thêm vào mục spaghetti, mạng, topo

> Spaghetti đơn giản và dễ nhập đối tượng mới, nhưng không lưu topo: mọi quan hệ phải tính khi cần, và biên chung bị lưu hai lần nên có nguy cơ không nhất quán [1, tr. 47]. Mô hình mạng thêm nút và cung, hỗ trợ kiểm tra nối thông và tìm đường ngắn nhất, nhưng không lưu quan hệ giữa các đối tượng 2 chiều [1, tr. 48–49]:

```text
node: [point, < arc >]
arc : [node-start, node-end, < point >]
```

> Mạng phẳng ghi mỗi giao điểm thành một nút; mạng không phẳng cho phép cạnh cắt nhau mà không tạo giao điểm, như đường hầm hay cầu vượt. Ví dụ tự xây dựng trong `theory_examples.py` gồm hai đường cắt nhau tại (1,1): khi không có nút tại giao điểm, không tồn tại đường đi từ S đến E; khi ghi giao điểm thành nút X, có đường S → X → E dài 2.
>
> Mô hình topo yêu cầu mạng phẳng và thêm hai đa giác kề vào mỗi cung [1, tr. 49–50]:

```text
arc    : [node-start, node-end, left-poly, right-poly, < point >]
polygon: < arc >
```

> Ở Hình 2.14 của sách: P₁ = <a, b, f>, P₂ = <c, d, e, f>, f = [N₁, N₂, P₁, P₂, <>], N₁ = [[3,0], <a, f, e>]. Tìm đa giác kề chỉ cần duyệt các cung của đa giác, và mỗi cạnh chỉ cập nhật một lần. Đổi lại, cấu trúc có thể sinh đối tượng không có ý nghĩa thực tế, làm chậm việc quét để hiển thị, phải xoá biên chung khi vẽ một vùng, và phải tính trước một phần đồ thị phẳng khi nhập đối tượng mới [1, tr. 51].

## B7. Thay mục TIGER/Line

> TIGER/Line là một cài đặt thực tế của mô hình topo, mô tả qua ví dụ bộ dữ liệu năm 1998 trong sách [1, tr. 54–61]. Các đối tượng gồm: *nút*; *điểm thực thể* (landmark, record 7); *chuỗi (chain)*, tương ứng với cung; và *GT-polygon*, các đa giác rời nhau phân hoạch toàn bộ không gian. *Complete chain* tham chiếu đa giác trái và phải; *network chain* thì không và không thuộc biên đa giác, như đường cụt.
>
> Dữ liệu nằm rải trong 17 loại tệp và được ghép qua khoá:

| Bản ghi | Nội dung | Ví dụ chain 8086 trong sách |
|---|---|---|
| Record 1 | TLID, nút đầu, nút cuối | (−72156546; 41957498) → (−72161936; 41958117) |
| Record 2 | Tối đa 10 điểm hình dạng mỗi bản ghi, theo RTSQ; 0 là NULL | RTSQ 1 và 2; bảng trong sách lược bớt phần giữa |
| Record I | Đa giác trái và phải | (PO123, 1) và (PO1987, 1) |

> Dựng biên đa giác gồm hai bước, ở đây viết lại thành Thuật toán 3. Nút không có định danh nên phải so toạ độ.

**Thuật toán 3. Dựng biên GT-polygon từ các chain**

```text
GT_POLYGON_BOUNDARY(polygon, chains)
    L <- empty list
    for each chain c in chains
        if c.left = polygon and c.right = polygon: skip c
        if c.left = polygon:  append (start, shape points, end) to L
        if c.right = polygon: append (end, reversed shape points, start) to L
    ring <- remove first line of L
    while L is not empty
        next <- line in L whose first point equals last point of ring
        if next does not exist: reject disconnected boundary
        append next to ring, skipping its first point
        remove next from L
    if first point of ring <> last point of ring: reject open boundary
    return ring
```

> Chạy thuật toán trên Hình 2.14 thu được vòng của P₁ và P₂ với diện tích 2 và 8,5, có tổng đúng bằng 10,5 là diện tích đa giác P; đồng thời V − E + F = 5 − 6 + 3 = 2. Sách chỉ cho hướng của cung f; hướng các cung khác do nhóm chọn. Thuật toán chỉ xử lý một vòng khép kín, chưa xử lý lỗ. TIGER cũng cho thấy giới hạn của việc thiếu định danh đối tượng: cùng tên và loại sông không bảo đảm xác định duy nhất một con sông [1, tr. 60–61].

---

# C. Mục mới trong Mục 4: "Đối chiếu mô hình trong sách với định dạng hiện đại"

| Định dạng | Gần với mô hình | Giống | Khác |
|---|---|---|---|
| GeoJSON | Spaghetti | Mỗi đối tượng giữ hình học riêng | Có chuẩn hoá CRS và cú pháp trao đổi |
| TopoJSON | Topo một phần | Cung dùng chung, mỗi cạnh lưu một lần | Không lưu đa giác trái/phải như TIGER |
| KML | Spaghetti | Hình học lưu độc lập | Thêm kiểu trình bày và ngữ nghĩa cao độ |
| Vector Tiles | Chia ô kết hợp vector | Không gian được chia theo ô | Có cắt và lượng tử hoá, không phải bản gốc đầy đủ |
| GeoParquet | Spaghetti theo cột | Hình học từng hàng độc lập | Lưu theo cột, có nén và metadata địa lý |

> Bảng trên là cách diễn giải của nhóm dựa trên sách và đặc tả, không phải phân loại do các đặc tả công bố.

---

# D. Mục mới trong Mục 7: "Nhận xét phản biện về tài liệu gốc"

> Khi đọc Chương 2, nhóm ghi nhận một số điểm cần lưu ý. Thứ nhất, Bảng 2.4 ghi LALAT = −7216159 và LALONG = +4195811, trong khi Bảng 2.1 và 2.2 cho thấy kinh độ mang giá trị âm cỡ −72 và vĩ độ dương cỡ +41; hai cột có vẻ bị đảo. Thứ hai, trang 57–58 mô tả "10 cặp (latitude, longitude)" nhưng Bảng 2.2 đặt LONG trước LAT. Thứ ba, sách coi trường là hàm liên tục, trong khi các trường phân loại được dùng phổ biến [3]. Thứ tư, sách xem việc quét mô hình topo chậm hơn nhiều so với spaghetti [1, tr. 51]. Thực nghiệm E2 không kiểm chứng trực tiếp nhận định này, vì chỉ đo đọc toàn bộ tệp: TopoJSON đọc chậm hơn GeoJSON khoảng 4% ở N = 10.000 nhưng nhỉnh hơn ở N = 100; chi phí lớn nhất của TopoJSON quan sát được là ở khâu dựng, gấp khoảng 14 lần. Thứ năm, phần chuẩn hoá ở mục 2.4 phản ánh giai đoạn xuất bản, nên báo cáo cập nhật bằng các định dạng ở Mục 4.

---

# E. Sửa nhỏ

| Vị trí | Sửa thành |
|---|---|
| Dòng 739, "đạt 60 phép đối chiếu bất biến" | "đạt 36 phép đối chiếu bất biến khác nhau" |
| Dòng 739, phần liệt kê nội dung | Thêm: "ví dụ mạng phẳng và không phẳng, ghép bản ghi TIGER và dựng biên đa giác từ Hình 2.14" |
| Spaghetti, `tr. 47–48` | `tr. 47` |
| Mục 2.1.1, `tr. 31–33` | `tr. 31–34` |
| Chia ô, `tr. 35–37` | `tr. 35–38` |
| Phụ lục B và đoạn ở dòng 776 | **Xoá toàn bộ** để không tự đối chiếu thang điểm hay để lại ghi chú nội bộ trong bài nộp |
| Hình 4 và Hình 5 | Dùng PDF trong `experiments/results_group/figures`; Hình 4b đã có Q1–Q3 ở cả ba quy mô |
| Trang bìa | Điền tên thành viên, lớp |
