package com.renzo.idscanner;

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
