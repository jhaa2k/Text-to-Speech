[app]
title = VOX STUDIO
package.name = voxstudio
package.domain = com.jhaa2k
source.dir = .
source.include_exts = py,json,png,jpg,kv,ttf
version = 0.1.0
requirements = python3,kivy==2.3.2,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 35
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.private_storage = True
p4a.branch = master
[buildozer]
log_level = 2
warn_on_root = 1
