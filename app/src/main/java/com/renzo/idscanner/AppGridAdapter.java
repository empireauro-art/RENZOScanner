package com.renzo.idscanner;

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
