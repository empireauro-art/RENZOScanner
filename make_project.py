import os

files = {
    "settings.gradle": """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "RenzoIdScanner"
include ':app'
""",

    "build.gradle": """plugins {
    id 'com.android.application' version '8.2.2' apply false
}
""",

    "gradle.properties": """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=false
""",

    "app/build.gradle": """plugins {
    id 'com.android.application'
}

android {
    namespace 'com.renzo.idscanner'
    compileSdk 34

    defaultConfig {
        applicationId "com.renzo.idscanner"
        minSdk 23
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt')
            signingConfig signingConfigs.debug
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
}
""",

    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>
    </queries>

    <application
        android:allowBackup="false"
        android:icon="@android:drawable/sym_def_app_icon"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.Material.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".ReceiveDiagnosticActivity"
            android:exported="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar">
            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="text/plain" />
            </intent-filter>
        </activity>

    </application>
</manifest>
""",

    "app/src/main/res/values/strings.xml": """<resources>
    <string name="app_name">RENZO ID Scanner</string>
</resources>
""",

    "app/src/main/res/layout/activity_main.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#0D0D0D"
    android:orientation="vertical"
    android:padding="8dp">

    <GridView
        android:id="@+id/appGridView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:numColumns="4"
        android:verticalSpacing="12dp"
        android:horizontalSpacing="8dp"
        android:stretchMode="columnWidth"
        android:gravity="center" />

</LinearLayout>
""",

    "app/src/main/res/layout/item_app.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:gravity="center"
    android:orientation="vertical"
    android:padding="4dp">

    <ImageView
        android:id="@+id/appIcon"
        android:layout_width="52dp"
        android:layout_height="52dp"
        android:scaleType="fitCenter" />

    <TextView
        android:id="@+id/appName"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
        android:ellipsize="end"
        android:gravity="center"
        android:maxLines="1"
        android:textColor="#E0E0E0"
        android:textSize="11sp" />

</LinearLayout>
""",

    "app/src/main/java/com/renzo/idscanner/DiagnosticStorage.java": r"""package com.renzo.idscanner;

import android.content.Context;
import android.content.SharedPreferences;

public final class DiagnosticStorage {
    private static final String PREFS_NAME = "renzo_diagnostic_records";

    private DiagnosticStorage() {}

    public static boolean isValidFourFieldFormat(String payload) {
        if (payload == null) return false;
        if (payload.contains("\n") || payload.contains("\r")) return false;
        String[] parts = payload.split("\\|", -1);
        if (parts.length != 4) return false;
        for (String part : parts) {
            if (part.isEmpty()) return false;
        }
        return true;
    }

    public static void saveRecord(Context context, String packageName, String exactPayload) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        prefs.edit().putString(packageName, exactPayload).apply();
    }

    public static String getRecord(Context context, String packageName) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getString(packageName, null);
    }
}
""",

    "app/src/main/java/com/renzo/idscanner/ReceiveDiagnosticActivity.java": """package com.renzo.idscanner;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Toast;

public class ReceiveDiagnosticActivity extends Activity {

    public static final String EXTRA_SENDER_PACKAGE = "com.renzo.idscanner.EXTRA_SENDER_PACKAGE";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent intent = getIntent();
        if (intent != null && Intent.ACTION_SEND.equals(intent.getAction()) && "text/plain".equals(intent.getType())) {
            handleIncomingDiagnostic(intent);
        }
        finish();
    }

    private void handleIncomingDiagnostic(Intent intent) {
        String payload = intent.getStringExtra(Intent.EXTRA_TEXT);
        String senderPackage = resolveSenderPackage(intent);

        if (senderPackage == null || senderPackage.isEmpty()) {
            Toast.makeText(this, "Rejected: Unknown sender package", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!DiagnosticStorage.isValidFourFieldFormat(payload)) {
            Toast.makeText(this, "Rejected: Invalid 4-field format", Toast.LENGTH_SHORT).show();
            return;
        }

        DiagnosticStorage.saveRecord(this, senderPackage, payload);
        Toast.makeText(this, "Diagnostic ID saved for " + senderPackage, Toast.LENGTH_SHORT).show();
    }

    private String resolveSenderPackage(Intent intent) {
        Uri referrer = getReferrer();
        if (referrer != null && "android-app".equals(referrer.getScheme())) {
            return referrer.getHost();
        }
        return intent.getStringExtra(EXTRA_SENDER_PACKAGE);
    }
}
""",

    "app/src/main/java/com/renzo/idscanner/AppGridAdapter.java": """package com.renzo.idscanner;

import android.content.Context;
import android.graphics.drawable.Drawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;
import java.util.List;

public class AppGridAdapter extends BaseAdapter {

    public static class AppItem {
        public final String label;
        public final String packageName;
        public final Drawable icon;

        public AppItem(String label, String packageName, Drawable icon) {
            this.label = label;
            this.packageName = packageName;
            this.icon = icon;
        }
    }

    private final LayoutInflater inflater;
    private final List<AppItem> apps;

    public AppGridAdapter(Context context, List<AppItem> apps) {
        this.inflater = LayoutInflater.from(context);
        this.apps = apps;
    }

    @Override
    public int getCount() { return apps.size(); }

    @Override
    public AppItem getItem(int position) { return apps.get(position); }

    @Override
    public long getItemId(int position) { return position; }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;
        if (convertView == null) {
            convertView = inflater.inflate(R.layout.item_app, parent, false);
            holder = new ViewHolder();
            holder.icon = convertView.findViewById(R.id.appIcon);
            holder.name = convertView.findViewById(R.id.appName);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        AppItem item = apps.get(position);
        holder.icon.setImageDrawable(item.icon);
        holder.name.setText(item.label);
        return convertView;
    }

    private static class ViewHolder {
        ImageView icon;
        TextView name;
    }
}
""",

    "app/src/main/java/com/renzo/idscanner/MainActivity.java": """package com.renzo.idscanner;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.os.Bundle;
import android.widget.GridView;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        GridView gridView = findViewById(R.id.appGridView);
        List<AppGridAdapter.AppItem> installedApps = loadLaunchableApps();

        AppGridAdapter adapter = new AppGridAdapter(this, installedApps);
        gridView.setAdapter(adapter);

        gridView.setOnItemClickListener((parent, view, position, id) -> {
            AppGridAdapter.AppItem selected = adapter.getItem(position);
            copyDiagnosticData(selected);
        });
    }

    private List<AppGridAdapter.AppItem> loadLaunchableApps() {
        PackageManager pm = getPackageManager();
        Intent mainIntent = new Intent(Intent.ACTION_MAIN, null);
        mainIntent.addCategory(Intent.CATEGORY_LAUNCHER);

        List<ResolveInfo> resolveInfos = pm.queryIntentActivities(mainIntent, 0);
        List<AppGridAdapter.AppItem> items = new ArrayList<>();
        String selfPackage = getPackageName();

        for (ResolveInfo info : resolveInfos) {
            String pkg = info.activityInfo.packageName;
            if (pkg.equals(selfPackage)) continue;

            String label = info.loadLabel(pm).toString();
            items.add(new AppGridAdapter.AppItem(label, pkg, info.loadIcon(pm)));
        }

        Collections.sort(items, new Comparator<AppGridAdapter.AppItem>() {
            @Override
            public int compare(AppGridAdapter.AppItem a, AppGridAdapter.AppItem b) {
                return a.label.compareToIgnoreCase(b.label);
            }
        });

        return items;
    }

    private void copyDiagnosticData(AppGridAdapter.AppItem app) {
        String record = DiagnosticStorage.getRecord(this, app.packageName);
        if (record == null || record.isEmpty()) {
            Toast.makeText(this, "Diagnostic information unavailable for " + app.label, Toast.LENGTH_SHORT).show();
            return;
        }

        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (clipboard != null) {
            ClipData clip = ClipData.newPlainText("RENZO_ID", record);
            clipboard.setPrimaryClip(clip);
            Toast.makeText(this, "Copied", Toast.LENGTH_SHORT).show();
        }
    }
}
""",

    ".github/workflows/build.yml": """name: Build Android APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          gradle-version: '8.4'
      - name: Build Release APK
        run: gradle assembleRelease
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: RENZO-ID-Scanner-APK
          path: app/build/outputs/apk/release/app-release.apk
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Done! All project files created successfully.")
