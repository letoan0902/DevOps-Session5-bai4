# Bài 4: Mô phỏng quy trình Hotfix và Gitflow thực tế

Môn DevOps, Session 05. Toàn bộ lệnh Git trong báo cáo này đã được chạy thật trên máy (Windows 11, Git Bash, git 2.49.0.windows.1, Python 3.13.3). Output được chép nguyên văn từ file `terminal_log.txt` nằm cùng thư mục.

## 1. Mục tiêu

- Áp dụng mô hình phân nhánh Gitflow chuẩn trong quản lý vòng đời phần mềm.
- Thực hành tạo, kiểm thử và tích hợp nhánh `hotfix/v1.0.1` tách trực tiếp từ `main` (đang chạy production).
- Gộp bản vá vào `main`, gắn tag `v1.0.1` để chuẩn bị release.
- Gộp ngược bản vá về `develop` để lỗi không "trôi" sang các phiên bản tương lai.

Các file trong thư mục này:

| File | Nội dung |
|------|----------|
| `README.md` | Báo cáo này |
| `terminal_log.txt` | Toàn bộ lệnh và output thật, theo đúng thứ tự chạy |
| `gitflow_diagram.txt` | Sơ đồ ASCII: Gitflow tổng quát và sơ đồ merge của bài |
| `source/` | Mã nguồn cuối cùng của nhánh `main` (`app/`, `VERSION`, `CHANGELOG.md`) |

Repo thử nghiệm nằm ngoài thư mục nộp bài (`_demo/bai4/gitflow-hotfix-demo`), vì thư mục nộp bài không được `git init`. Phần `source/` là bản sao các file của `main` sau khi hoàn tất.

## 2. Giới thiệu mô hình Gitflow

Gitflow là một quy ước phân nhánh (do Vincent Driessen đề xuất) chia nhánh thành hai nhánh sống lâu dài và ba loại nhánh tạm thời. Mỗi loại nhánh có "điểm tách" và "điểm gộp" cố định, nhờ đó cả nhóm luôn biết code nào đang chạy production, code nào đang phát triển.

### 2.1. Bảng vai trò các nhánh

| Nhánh | Loại | Tách từ | Gộp về | Quy ước đặt tên | Vai trò |
|-------|------|---------|--------|-----------------|---------|
| `main` | Sống lâu | - | - | `main` (cũ: `master`) | Chỉ chứa code đã phát hành, mỗi commit phát hành có tag phiên bản |
| `develop` | Sống lâu | `main` (lúc khởi tạo) | - | `develop` | Tích hợp tính năng cho phiên bản kế tiếp, có thể chưa ổn định |
| `feature/*` | Tạm thời | `develop` | `develop` | `feature/ten-tinh-nang` | Phát triển một tính năng riêng lẻ |
| `release/*` | Tạm thời | `develop` | `main` và `develop` | `release/1.1.0` | Chốt phiên bản: chỉ sửa lỗi nhỏ, cập nhật version, tài liệu |
| `hotfix/*` | Tạm thời | `main` | `main` và `develop` (hoặc `release/*` nếu đang tồn tại) | `hotfix/v1.0.1` | Sửa lỗi khẩn cấp trên production, không chờ chu kỳ release |

Điểm mấu chốt của `hotfix/*`: tách từ `main` chứ không tách từ `develop`, vì `develop` đang chứa tính năng dở dang, không thể đưa lên production.

### 2.2. Sơ đồ ASCII tổng quát

Phần feature và release:

```
 main       o [v1.0.0] ---------------------------------- o [v1.1.0] --------->
            |                                              ^
            |                        release/1.1.0         | (merge --no-ff + tag)
            |                      +---o---o---o-----------+
            |                     /                         \
 develop    o---o---o-------o----+---o-------o---------------+---o---o--------->
                 \         /      \         /
 feature/*        +---o---+        +---o---+
                  (feature A)      (feature B)
```

Phần hotfix:

```
 main       o [v1.1.0] --------------------------+ [v1.1.1] ----------------->
             \                                  /
 hotfix/*     +----o---------o-----------------+
                                                \
 develop    ---o-------------o---------o---------+--------------------------->
```

Bản đầy đủ nằm trong `gitflow_diagram.txt`.

## 3. Kịch bản sự cố

- Hệ thống đang chạy trên `main`, phiên bản stable `v1.0.0`.
- Hàm `get_user_profile` trả về nguyên bản ghi người dùng, bao gồm cả `password_hash` và email đầy đủ. Đây là lỗi lộ dữ liệu nghiêm trọng: bất kỳ client nào gọi API hồ sơ đều nhận được hash mật khẩu.
- Nhánh `develop` đang có 2 commit tính năng dở dang cho phiên bản 1.1.0 (`report_service.py` chưa xong, roadmap trong README). Không thể deploy `develop`.
- Yêu cầu: vá ngay trên nền `main`, phát hành `v1.0.1`, và đảm bảo `develop` cũng có bản vá.

## 4. Thực hiện từng bước

Các khối lệnh dưới đây trình bày dạng `$ lệnh` rồi tới output, trích nguyên văn từ `terminal_log.txt`. Cấu hình trong repo demo: `user.name` là "Lê Toàn", `user.email` là `trinhhanh261293@gmail.com`, `core.autocrlf=false`, khởi tạo bằng `git init -b main`. Thông điệp commit viết tiếng Việt không dấu theo chuẩn `feat:`/`fix:`/`chore:`.

### Bước 1. Dựng hiện trạng

Trên `main` tạo `README.md`, `VERSION` (chứa `1.0.0`) và `app/user_service.py` chứa lỗi; sau đó gắn tag `v1.0.0`:

```
$ git commit -m 'chore: khoi tao du an voi README va VERSION 1.0.0'
[main (root-commit) bb7ec50] chore: khoi tao du an voi README va VERSION 1.0.0
 2 files changed, 8 insertions(+)
 create mode 100644 README.md
 create mode 100644 VERSION

$ git commit -m 'feat: them dich vu nguoi dung get_user_profile'
[main 78569ed] feat: them dich vu nguoi dung get_user_profile
 1 file changed, 27 insertions(+)
 create mode 100644 app/user_service.py

$ git tag -a v1.0.0 -m 'Release 1.0.0'

$ git tag
v1.0.0
```

Đoạn mã lỗi trong `app/user_service.py` (phiên bản 1.0.0):

```python
def get_user_profile(user_id):
    """Tra ve ho so nguoi dung theo id."""
    user = USERS.get(user_id)
    if user is None:
        return None
    # LOI: tra ve nguyen ban ghi, ke ca password_hash va email day du
    return dict(user)
```

Tạo `develop` từ `main` rồi thêm 2 commit tính năng ở file khác (`app/report_service.py` và phần roadmap của `README.md`) để tránh xung đột không cần thiết:

```
$ git switch -c develop
Switched to a new branch 'develop'

$ git commit -m 'feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)'
[develop 1297c15] feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)
 1 file changed, 16 insertions(+)
 create mode 100644 app/report_service.py

$ git commit -m 'feat: bo sung roadmap 1.1.0 vao README'
[develop 20a228e] feat: bo sung roadmap 1.1.0 vao README
 1 file changed, 6 insertions(+)
```

Trạng thái ban đầu:

```
$ git log --graph --oneline --all
* 20a228e feat: bo sung roadmap 1.1.0 vao README
* 1297c15 feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)
* 78569ed feat: them dich vu nguoi dung get_user_profile
* bb7ec50 chore: khoi tao du an voi README va VERSION 1.0.0

$ git branch -a
* develop
  main

$ git tag
v1.0.0
```

### Bước 2. Phát hiện lỗi trên production

Chuyển sang `main` (đại diện cho production) và chạy hàm để xem dữ liệu trả về:

```
$ git switch main
Switched to branch 'main'

$ ls app
user_service.py

$ python -c "import json; from app.user_service import get_user_profile; print(json.dumps(get_user_profile(1), indent=2))"
{
  "id": 1,
  "username": "lan.nguyen",
  "email": "lan.nguyen@example.com",
  "password_hash": "pbkdf2:sha256:600000:s4lt1:9f2c7a1be44d03c5a8e1f6b2d7c9a0e3",
  "role": "admin"
}
```

Trường `password_hash` bị lộ và email hiển thị đầy đủ. Lưu ý trên `main` chưa có `report_service.py`: đúng như bối cảnh, tính năng dở dang chỉ tồn tại ở `develop`.

### Bước 3. Tạo nhánh hotfix trực tiếp từ main và sửa lỗi

```
$ git switch -c hotfix/v1.0.1
Switched to a new branch 'hotfix/v1.0.1'

$ git branch --show-current
hotfix/v1.0.1
```

Bản vá trong `app/user_service.py`: dùng whitelist các trường an toàn, loại bỏ `password_hash`, che bớt email bằng hàm `mask_email`. Diff thực tế:

```
$ git diff -- app/user_service.py
@@ -18,10 +18,21 @@ USERS = {
 }
 
 
+def mask_email(email):
+    """Che bot email: giu 2 ky tu dau cua phan local, an phan con lai."""
+    local, _, domain = email.partition("@")
+    return local[:2] + "***@" + domain
+
+
 def get_user_profile(user_id):
-    """Tra ve ho so nguoi dung theo id."""
+    """Tra ve ho so cong khai cua nguoi dung (whitelist cac truong an toan)."""
     user = USERS.get(user_id)
     if user is None:
         return None
-    # LOI: tra ve nguyen ban ghi, ke ca password_hash va email day du
-    return dict(user)
+    # Chi tra ve cac truong duoc phep. TUYET DOI khong tra ve password_hash.
+    return {
+        "id": user["id"],
+        "username": user["username"],
+        "email": mask_email(user["email"]),
+        "role": user["role"],
+    }
```

(Diff đã lược phần đầu file là dòng docstring đổi phiên bản; bản đầy đủ nằm trong `terminal_log.txt`.)

Commit bản vá, sau đó cập nhật `VERSION` thành `1.0.1` và thêm `CHANGELOG.md` trong một commit `chore:` riêng:

```
$ git commit -m 'fix: khong tra ve password_hash trong ho so nguoi dung'
[hotfix/v1.0.1 01b4647] fix: khong tra ve password_hash trong ho so nguoi dung
 1 file changed, 15 insertions(+), 4 deletions(-)

$ printf '1.0.1\n' > VERSION

$ git commit -m 'chore: nang phien ban len 1.0.1'
[hotfix/v1.0.1 2101781] chore: nang phien ban len 1.0.1
 2 files changed, 15 insertions(+), 1 deletion(-)
 create mode 100644 CHANGELOG.md

$ git log --graph --oneline --all
* 2101781 chore: nang phien ban len 1.0.1
* 01b4647 fix: khong tra ve password_hash trong ho so nguoi dung
| * 20a228e feat: bo sung roadmap 1.1.0 vao README
| * 1297c15 feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)
|/  
* 78569ed feat: them dich vu nguoi dung get_user_profile
* bb7ec50 chore: khoi tao du an voi README va VERSION 1.0.0
```

Đồ thị cho thấy `hotfix/v1.0.1` mọc ra từ `78569ed` (đỉnh của `main`), song song với `develop` và không chứa 2 commit tính năng của `develop`.

Kiểm thử lại trên nhánh hotfix:

```
$ python -c "import json; from app.user_service import get_user_profile; print(json.dumps(get_user_profile(1), indent=2))"
{
  "id": 1,
  "username": "lan.nguyen",
  "email": "la***@example.com",
  "role": "admin"
}

$ python -c "from app.user_service import get_user_profile; print(sorted(get_user_profile(2)))"
['email', 'id', 'role', 'username']

$ python -c "from app.user_service import get_user_profile; print(get_user_profile(999))"
None

$ cat VERSION
1.0.1
```

`password_hash` không còn trong kết quả, email đã được che, user không tồn tại vẫn trả `None`.

### Bước 4. Tích hợp vào main và gắn tag v1.0.1

Trước khi merge, kiểm tra quan hệ giữa `main` và hotfix:

```
$ git switch main
Switched to branch 'main'

$ git merge-base --is-ancestor main hotfix/v1.0.1 && echo 'main la tien than truc tiep cua hotfix/v1.0.1 -> git merge thuong (khong --no-ff) se fast-forward'
main la tien than truc tiep cua hotfix/v1.0.1 -> git merge thuong (khong --no-ff) se fast-forward
```

Vì `main` chưa có commit mới nào kể từ lúc tách nhánh, một lệnh `git merge hotfix/v1.0.1` thông thường (như gợi ý của đề) sẽ chỉ trượt con trỏ `main` lên (fast-forward). Để chứng minh, tôi thử trong một bản sao riêng `ff-test` (clone từ repo demo, không ảnh hưởng repo chính):

```
$ git -C .../ff-test -c user.name=test -c user.email=test@example.com merge origin/hotfix/v1.0.1
Updating 78569ed..2101781
Fast-forward
 CHANGELOG.md        | 14 ++++++++++++++
 VERSION             | 2 +-
 app/user_service.py | 19 +++++++++++++++----
 3 files changed, 30 insertions(+), 5 deletions(-)
 create mode 100644 CHANGELOG.md

$ git -C .../ff-test log --graph --oneline --all
* 2101781 chore: nang phien ban len 1.0.1
* 01b4647 fix: khong tra ve password_hash trong ho so nguoi dung
| * 20a228e feat: bo sung roadmap 1.1.0 vao README
| * 1297c15 feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)
|/  
* 78569ed feat: them dich vu nguoi dung get_user_profile
* bb7ec50 chore: khoi tao du an voi README va VERSION 1.0.0
```

Lịch sử thành một đường thẳng, không còn dấu vết nhánh hotfix. Vì vậy ở repo chính tôi dùng `--no-ff`:

```
$ git merge --no-ff hotfix/v1.0.1 -m "Merge branch 'hotfix/v1.0.1'"
Merge made by the 'ort' strategy.
 CHANGELOG.md        | 14 ++++++++++++++
 VERSION             | 2 +-
 app/user_service.py | 19 +++++++++++++++----
 3 files changed, 30 insertions(+), 5 deletions(-)
 create mode 100644 CHANGELOG.md

$ git tag -a v1.0.1 -m 'Release Hotfix 1.0.1'

$ git tag
v1.0.0
v1.0.1

$ git tag -n
v1.0.0          Release 1.0.0
v1.0.1          Release Hotfix 1.0.1
```

Xem nội dung tag (merge commit mặc định không hiện thống kê file, nên dùng thêm `--first-parent` để Git so với cha thứ nhất):

```
$ git show v1.0.1 --stat --first-parent | head -25
tag v1.0.1
Tagger: Lê Toàn <trinhhanh261293@gmail.com>
Date:   Fri Oct 2 12:49:15 2026 +0700

Release Hotfix 1.0.1

commit 337d9b539d90e20a575a3ec83983e3d7693cd431
Merge: 78569ed 2101781
Author: Lê Toàn <trinhhanh261293@gmail.com>
Date:   Fri Oct 2 12:49:15 2026 +0700

    Merge branch 'hotfix/v1.0.1'

 CHANGELOG.md        | 14 ++++++++++++++
 VERSION             | 2 +-
 app/user_service.py | 19 +++++++++++++++----
 3 files changed, 30 insertions(+), 5 deletions(-)
```

Kiểm tra tag chỉ đúng commit mới nhất của `main`:

```
$ git rev-parse 'v1.0.1^{commit}'
337d9b539d90e20a575a3ec83983e3d7693cd431

$ git rev-parse main
337d9b539d90e20a575a3ec83983e3d7693cd431

$ test "$(git rev-parse 'v1.0.1^{commit}')" = "$(git rev-parse main)" && echo 'v1.0.1 chi dung vao commit moi nhat cua main'
v1.0.1 chi dung vao commit moi nhat cua main

$ git cat-file -t v1.0.1
tag

$ git describe --tags
v1.0.1
```

Cả `v1.0.0` lẫn `v1.0.1` đều là tag annotated (kiểu `tag`). Đồ thị sau khi merge và gắn tag (`git log --graph --oneline --all --decorate`, chép nguyên văn từ log):

```
$ git log --graph --oneline --all --decorate
*   337d9b5 (HEAD -> main, tag: v1.0.1) Merge branch 'hotfix/v1.0.1'
|\  
| * 2101781 (hotfix/v1.0.1) chore: nang phien ban len 1.0.1
| * 01b4647 fix: khong tra ve password_hash trong ho so nguoi dung
|/  
| * 20a228e (develop) feat: bo sung roadmap 1.1.0 vao README
| * 1297c15 feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)
|/  
* 78569ed (tag: v1.0.0) feat: them dich vu nguoi dung get_user_profile
* bb7ec50 chore: khoi tao du an voi README va VERSION 1.0.0
```

Tag `v1.0.1` trỏ vào merge commit `337d9b5`, đúng bằng đỉnh của `main`. Chạy lại `python -c` trên `main` cho kết quả đã được che (không còn `password_hash`), giống bước 3.

### Bước 5. Gộp ngược hotfix về develop

Trước khi gộp, `develop` chưa có commit `fix:` (lệnh `grep` không tìm thấy gì, mã thoát 1). Sau đó merge:

```
$ git switch develop
Switched to branch 'develop'

$ git log --oneline develop | grep 'fix:'
(ma thoat: 1)

$ git merge --no-ff hotfix/v1.0.1 -m "Merge branch 'hotfix/v1.0.1' into develop"
Merge made by the 'ort' strategy.
 CHANGELOG.md        | 14 ++++++++++++++
 VERSION             | 2 +-
 app/user_service.py | 19 +++++++++++++++----
 3 files changed, 30 insertions(+), 5 deletions(-)
 create mode 100644 CHANGELOG.md

$ git status
On branch develop
nothing to commit, working tree clean
```

Không có xung đột. Lý do: `develop` chỉ sửa `README.md` và thêm `app/report_service.py`, còn hotfix chỉ sửa `app/user_service.py`, `VERSION` và thêm `CHANGELOG.md`. Hai bên không chạm vào cùng một file nên Git tự gộp được (chiến lược `ort`). Nếu `develop` cũng sửa `VERSION` hay `app/user_service.py`, sẽ phải giải quyết xung đột thủ công.

Kiểm tra `develop` đã chứa bản vá:

```
$ git log --oneline develop | grep 'fix:'
01b4647 fix: khong tra ve password_hash trong ho so nguoi dung

$ git branch --contains 01b4647
* develop
  hotfix/v1.0.1
  main
```

Commit fix `01b4647` nằm trong cả `develop`, `main` và `hotfix/v1.0.1` (nhánh hotfix lúc này chưa bị xóa). Nội dung file trên `develop` (20 dòng đầu chưa đến phần hàm nên lấy 30 dòng):

```
$ git show develop:app/user_service.py | head -30
"""Dich vu nguoi dung - phien ban 1.0.1 (hotfix: khong lo du lieu nhay cam)."""

USERS = {
    ...
}


def mask_email(email):
    """Che bot email: giu 2 ky tu dau cua phan local, an phan con lai."""
    local, _, domain = email.partition("@")
    return local[:2] + "***@" + domain


def get_user_profile(user_id):
    """Tra ve ho so cong khai cua nguoi dung (whitelist cac truong an toan)."""
    user = USERS.get(user_id)
    if user is None:
```

(Dấu `...` ở trên là phần tôi lược bớt khi trình bày; log đầy đủ ở `terminal_log.txt`.)

Chạy lại trên `develop`, bản vá đã có hiệu lực và tính năng dở dang vẫn nguyên vẹn:

```
$ python -c "import json; from app.user_service import get_user_profile; print(json.dumps(get_user_profile(1), indent=2))"
{
  "id": 1,
  "username": "lan.nguyen",
  "email": "la***@example.com",
  "role": "admin"
}

$ python -c "from app.report_service import count_users_by_role; print(count_users_by_role())"
{'admin': 1, 'member': 1}

$ ls app
report_service.py
user_service.py

$ cat VERSION
1.0.1

$ git diff --stat main develop
 README.md             |  6 ++++++
 app/report_service.py | 16 ++++++++++++++++
 2 files changed, 22 insertions(+)

$ git log --oneline develop..main | wc -l
1

$ git log --oneline main..develop
508c835 Merge branch 'hotfix/v1.0.1' into develop
20a228e feat: bo sung roadmap 1.1.0 vao README
1297c15 feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)
```

Nhận xét:

- `git diff --stat main develop` chỉ còn 2 file là phần tính năng dở dang của `develop`; mọi thứ liên quan đến hotfix đã giống hệt `main`.
- `develop..main` còn đúng 1 commit: đó là merge commit `337d9b5` của chính `main`. Nội dung của nó đã có trong `develop` (qua merge commit `508c835`), chỉ khác là `develop` gộp trực tiếp nhánh hotfix chứ không gộp `main`. Đây là cách làm chuẩn của Gitflow.
- `VERSION` trên `develop` giờ là `1.0.1`: đây là hệ quả bình thường của việc đồng bộ hotfix. Khi làm `release/1.1.0` sẽ nâng lại.

### Bước 6. Dọn dẹp và kiểm tra cuối

```
$ git branch -d hotfix/v1.0.1
Deleted branch hotfix/v1.0.1 (was 2101781).

$ git branch -a
* develop
  main

$ git tag
v1.0.0
v1.0.1

$ git log --graph --oneline --all
*   508c835 Merge branch 'hotfix/v1.0.1' into develop
|\  
* | 20a228e feat: bo sung roadmap 1.1.0 vao README
* | 1297c15 feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)
| | * 337d9b5 Merge branch 'hotfix/v1.0.1'
| |/| 
|/|/  
| * 2101781 chore: nang phien ban len 1.0.1
| * 01b4647 fix: khong tra ve password_hash trong ho so nguoi dung
|/  
* 78569ed feat: them dich vu nguoi dung get_user_profile
* bb7ec50 chore: khoi tao du an voi README va VERSION 1.0.0

$ git log --graph --oneline --all --decorate
*   508c835 (HEAD -> develop) Merge branch 'hotfix/v1.0.1' into develop
|\  
* | 20a228e feat: bo sung roadmap 1.1.0 vao README
* | 1297c15 feat: them report_service thong ke nguoi dung theo vai tro (dang phat trien)
| | * 337d9b5 (tag: v1.0.1, main) Merge branch 'hotfix/v1.0.1'
| |/| 
|/|/  
| * 2101781 chore: nang phien ban len 1.0.1
| * 01b4647 fix: khong tra ve password_hash trong ho so nguoi dung
|/  
* 78569ed (tag: v1.0.0) feat: them dich vu nguoi dung get_user_profile
* bb7ec50 chore: khoi tao du an voi README va VERSION 1.0.0
```

Nhánh `hotfix/v1.0.1` đã biến mất khỏi danh sách nhánh, nhưng 2 commit của nó vẫn còn trong lịch sử vì đã được gộp vào cả `main` lẫn `develop`. `git branch -a` chỉ có `develop` và `main` vì repo demo không có remote (chưa push).

## 5. Sơ đồ merge của bài

Sơ đồ ASCII dựng đúng trên hash thật ở trên (thời gian đi từ trái sang phải):

```
 main            bb7ec50 --- 78569ed ---------------------------------- 337d9b5
                  (init)    [v1.0.0]\                                  /  [v1.0.1]
                           |         \                                /
 hotfix/v1.0.1             |          +--- 01b4647 --- 2101781 ----+
 (xoa sau khi xong)        |                fix:         chore:     \
                           |                                         \
 develop                   +--- 1297c15 --- 20a228e -----------------+--- 508c835
                               feat:        feat:                      merge hotfix
                               report       roadmap                    vao develop
```

Cách đọc:

1. `78569ed` là điểm chung. `main` (tag `v1.0.0`) và `develop` cùng tách ra từ đây.
2. `hotfix/v1.0.1` tách trực tiếp từ `78569ed` trên `main`, không mang theo `1297c15` và `20a228e` (tính năng dở dang của `develop`).
3. `337d9b5` là merge commit trên `main` (cha thứ nhất `78569ed`, cha thứ hai `2101781`), được gắn tag `v1.0.1`.
4. `508c835` là merge commit trên `develop` (cha thứ nhất `20a228e`, cha thứ hai `2101781`). Nhờ nó, `01b4647` và `2101781` có mặt trong `develop`.

Bảng ánh xạ hash:

| Hash | Nhánh / tag | Ý nghĩa |
|------|-------------|---------|
| `bb7ec50` | `main` | Commit khởi tạo |
| `78569ed` | `main`, tag `v1.0.0` | Release 1.0.0 (chứa lỗi) |
| `1297c15`, `20a228e` | `develop` | Hai commit tính năng dở dang |
| `01b4647` | `hotfix/v1.0.1` | Commit sửa lỗi `fix:` |
| `2101781` | `hotfix/v1.0.1` | Nâng phiên bản lên 1.0.1, thêm CHANGELOG |
| `337d9b5` | `main`, tag `v1.0.1` | Merge hotfix vào `main` |
| `508c835` | `develop` | Merge hotfix vào `develop` |

Đồ thị nguyên văn của `git log --graph --oneline --all --decorate` (đặt cạnh sơ đồ) nằm ở Bước 6 phía trên và ở cuối `gitflow_diagram.txt`.

## 6. Giải thích các quyết định kỹ thuật

### 6.1. Vì sao dùng `--no-ff`

Đề gợi ý `git merge hotfix/v1.0.1`. Ở bài này lệnh đó sẽ fast-forward vì `main` chưa có commit mới sau lúc tách nhánh (đã chứng minh ở Bước 4 bằng `git merge-base --is-ancestor` và thử nghiệm trong `ff-test`). Hậu quả:

- Lịch sử `main` thành một đường thẳng, không còn merge commit; nhìn vào đồ thị không biết 2 commit `01b4647`, `2101781` thuộc cùng một đợt hotfix.
- Không có một commit duy nhất đại diện cho "cả đợt sửa lỗi"; muốn hoàn tác (`git revert -m 1 <merge>`) sẽ khó hơn nhiều.
- Tag `v1.0.1` sẽ trỏ vào `2101781` (commit `chore:`) thay vì một điểm tích hợp rõ ràng.

Với `--no-ff`, Git luôn tạo merge commit `337d9b5`, giữ nguyên dấu vết nhánh hotfix trong đồ thị và cho phép hoàn tác cả đợt hotfix bằng một lệnh. Đây cũng là quy ước của Gitflow chuẩn. Kết quả cuối vẫn thỏa yêu cầu đề: tag `v1.0.1` chỉ vào commit mới nhất của `main`.

### 6.2. Vì sao phải gộp ngược hotfix về develop

`develop` được tách ra từ `main` ở lúc `v1.0.0`, tức là nó vẫn mang bản code lỗi (`return dict(user)`). Nếu chỉ vá `main`:

- Khi sau này `develop` được đóng gói thành `release/1.1.0` rồi gộp vào `main`, phiên bản 1.1.0 sẽ mang lại đúng đoạn code lỗi cũ, thậm chí ghi đè bản vá. Lỗi lộ `password_hash` sẽ tái xuất hiện ("trôi lỗi").
- Càng để lâu, `develop` càng phân kỳ khỏi `main`, việc gộp càng dễ xung đột.

Gộp ngay sau khi vá là rẻ nhất: bài này không xung đột và `git diff --stat main develop` chỉ còn phần tính năng dở dang.

### 6.3. Tag annotated và lightweight

| Tiêu chí | Annotated (`git tag -a v1.0.1 -m "..."`) | Lightweight (`git tag v1.0.1`) |
|----------|------------------------------------------|--------------------------------|
| Bản chất | Một object kiểu `tag` riêng trong Git | Chỉ là con trỏ tới commit |
| Metadata | Có người tạo, ngày giờ, thông điệp | Không có |
| `git cat-file -t` | `tag` | `commit` |
| `git tag -n` | Hiện thông điệp tag | Hiện thông điệp của commit |
| Dùng cho | Phát hành chính thức | Đánh dấu tạm, cá nhân |

Chứng cứ thật: trong repo chính, `git cat-file -t v1.0.1` và `git cat-file -t v1.0.0` đều trả về `tag`. Trong bản sao `ff-test`, tôi tạo thêm tag nhẹ `v-nhe-demo` để so sánh:

```
$ git -C .../ff-test tag v-nhe-demo

$ git -C .../ff-test cat-file -t v-nhe-demo
commit

$ git -C .../ff-test tag -n
v-nhe-demo      chore: nang phien ban len 1.0.1
v1.0.0          Release 1.0.0
```

Tag nhẹ chỉ là con trỏ tới commit (kiểu `commit`) và `git tag -n` hiện thông điệp của chính commit đó. Các lệnh `git describe` mặc định và `--follow-tags` cũng chỉ làm việc với tag annotated, nên mọi bản phát hành nên dùng `-a`. Lưu ý: đối tượng tag annotated có hash riêng với hash commit mà nó trỏ tới, vì vậy so sánh phải dùng `v1.0.1^{commit}` như đã làm ở Bước 4.

### 6.4. Semantic Versioning

Định dạng `MAJOR.MINOR.PATCH`:

| Thành phần | Khi nào tăng | Ví dụ |
|------------|--------------|-------|
| MAJOR | Thay đổi phá vỡ tương thích ngược | `1.0.1` -> `2.0.0` |
| MINOR | Thêm tính năng, vẫn tương thích | `1.0.1` -> `1.1.0` (phiên bản của `develop`) |
| PATCH | Sửa lỗi, không đổi hành vi công khai | `1.0.0` -> `1.0.1` (hotfix này) |

Hotfix chỉ sửa lỗi nên chỉ tăng PATCH: `1.0.0` -> `1.0.1`. Điều này khớp với tên nhánh `hotfix/v1.0.1`, file `VERSION`, `CHANGELOG.md` và tag `v1.0.1`.

### 6.5. Đẩy lên remote trong thực tế (chỉ mô tả, không chạy)

Bài này không có remote và không push. Trong dự án thật, sau khi hoàn tất sẽ chạy:

```
git push origin main develop --follow-tags
```

- `main` và `develop` được đẩy cùng lúc để hai nhánh đồng bộ với remote.
- `--follow-tags` đẩy kèm các tag annotated nằm trong lịch sử vừa đẩy (đây là lý do dùng `-a`).
- Có thể đẩy riêng tag bằng `git push origin v1.0.1`.
- Nếu muốn kích hoạt CI/CD, thường pipeline được cấu hình chạy khi có tag dạng `v*.*.*`.
- Xóa nhánh hotfix trên remote (nếu đã từng push): `git push origin --delete hotfix/v1.0.1`.
- Trong thực tế nhóm thường mở Pull Request cho `hotfix/*` vào `main` và vào `develop` để có review; kết quả đồ thị tương đương.

### 6.6. Trường hợp đang có nhánh release

Nếu lúc xảy ra sự cố đang tồn tại `release/1.1.0` (đã tách khỏi `develop`, đang chốt phiên bản), thì hotfix phải được gộp vào `release/1.1.0` thay vì `develop`:

```
hotfix/v1.0.1 -> main (tag v1.0.1)
hotfix/v1.0.1 -> release/1.1.0   (thay cho develop)
```

Lý do: khi `release/1.1.0` hoàn tất, nó sẽ được gộp vào `main` rồi gộp ngược vào `develop`, nên bản vá tự động theo đường đó mà đến `develop`. Nếu cũng gộp thẳng vào `develop` thì dễ tạo thêm xung đột, còn nếu quên gộp vào release thì bản 1.1.0 sẽ phát hành lại đúng lỗi cũ. Bài này tại thời điểm xảy ra sự cố không có nhánh release nên gộp thẳng vào `develop`.

## 7. Bảng đối chiếu yêu cầu đề bài

| Yêu cầu của đề | Thực hiện | Bằng chứng |
|----------------|-----------|------------|
| `main` chạy v1.0.0 có lỗi lộ dữ liệu | Đã dựng; tag `v1.0.0` trỏ `78569ed` | Bước 1, 2 |
| `develop` đang dở dang, không deploy được | 2 commit `feat:` ở file khác | Bước 1 |
| Tạo `hotfix/v1.0.1` tách trực tiếp từ `main` | `git switch main` rồi `git switch -c hotfix/v1.0.1` | Bước 3, đồ thị mọc từ `78569ed` |
| Sửa lỗi và kiểm thử | Commit `01b4647`, chạy `python -c` | Bước 3 |
| Gộp hotfix vào `main` | Merge commit `337d9b5` | Bước 4 |
| Tạo tag `v1.0.1` | `git tag -a v1.0.1 -m "Release Hotfix 1.0.1"` | Bước 4 |
| Tag chỉ vào commit mới trên `main` | `v1.0.1^{commit}` = `main` = `337d9b5` | Bước 4 |
| Bắt buộc gộp ngược vào `develop` | Merge commit `508c835` | Bước 5 |
| Lịch sử `develop` chứa commit sửa lỗi | `git log --oneline develop \| grep "fix:"` ra `01b4647` | Bước 5 |
| Xóa nhánh hotfix cục bộ | `git branch -d hotfix/v1.0.1` | Bước 6 |
| `git branch -a`, `git tag`, `git log --graph --oneline --all` | Đã chạy, chép nguyên văn | Bước 6 |
| README giải thích sơ đồ Gitflow và vẽ sơ đồ merge | Mục 2 và mục 5, thêm `gitflow_diagram.txt` | File này |

Các điểm khác so với gợi ý của đề (đều có lý do):

1. Đề gợi ý `git merge hotfix/v1.0.1`; bài này dùng `git merge --no-ff` để luôn có merge commit (mục 6.1). Có chạy thử merge thường trong bản sao `ff-test` để cho thấy nó fast-forward.
2. Đề chỉ nói "sửa xong"; bài tách thành 2 commit (`fix:` rồi `chore:`) để commit sửa lỗi sạch, dễ cherry-pick hay revert.
3. `git branch -a` chỉ có nhánh cục bộ (`develop`, `main`) vì không có remote; không có dòng `remotes/origin/...`.
4. `git show develop:app/user_service.py | head` dùng 30 dòng thay vì 20 để thấy cả hàm đã sửa.
5. `git show v1.0.1 --stat` được thêm `--first-parent` vì merge commit mặc định không in thống kê file.

## 8. Kết luận

- Hotfix được tách từ `main`, cô lập hoàn toàn khỏi tính năng dở dang của `develop`, nhờ vậy vá nóng mà không phải chờ hoặc đẩy nhầm code chưa sẵn sàng lên production.
- Sau khi gộp bằng `--no-ff`, `main` có merge commit `337d9b5` được gắn tag annotated `v1.0.1`; tag trỏ đúng đỉnh của `main`.
- Gộp ngược vào `develop` (merge commit `508c835`) không xung đột và bảo đảm lỗi `password_hash` không tái xuất hiện ở bản 1.1.0 sắp tới. `develop` vẫn giữ nguyên `report_service.py` và roadmap dở dang.
- Quy tắc cần nhớ: hotfix luôn tách từ `main`, luôn gộp về cả `main` (kèm tag tăng PATCH) và `develop` (hoặc `release/*` nếu đang có), rồi xóa nhánh tạm.
