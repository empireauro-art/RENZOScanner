package com.renzo.idscanner;

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
