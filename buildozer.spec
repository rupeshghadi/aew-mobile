[app]
title = AEW ERP
package.name = aew_erp
package.domain = com.adarsh.erp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db
version = 1.0.0

# Pin python3 to 3.11 to prevent pulling 3.14 alpha headers
requirements = python3==3.11.9,hostpython3==3.11.9,kivy,kivymd==1.2.0,sqlite3,urllib3,certifi

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET

# Target API 33 with matching build tools
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
