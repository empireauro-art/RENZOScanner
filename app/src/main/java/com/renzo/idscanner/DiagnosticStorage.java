package com.renzo.idscanner;

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
