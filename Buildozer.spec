[app]
title = AEW ERP
package.name = aew_erp
package.domain = com.adarsh.erp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db
version = 1.0.0

# Dependencies to package inside APK
requirements = python3,kivy==2.3.0,kivymd==2.0.1.dev0,sqlite3,urllib3,certifi

orientation = portrait
fullscreen = 0

# Android permissions for storage, camera/receipt scanning, and network
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET

# API levels
android.api = 34
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1