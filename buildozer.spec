[app]
title = 规划土地执法依据查询
package.name = lawquery
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,csv,html

version = 1.0
requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
