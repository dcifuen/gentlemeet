package com.falconlabs.ardux;

import android.app.Activity;
import android.content.Context;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBar;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.SpinnerAdapter;
import android.widget.TextView;
import android.widget.Toast;

import com.appspot.www_ardux.devices.Devices;
import com.appspot.www_ardux.devices.model.ResourceCalendar;
import com.appspot.www_ardux.devices.model.ResourceCalendarCollection;
import com.appspot.www_ardux.devices.model.ResourceDevice;
import com.appspot.www_ardux.devices.model.ResourceDeviceCollection;
import com.appspot.www_ardux.devices.model.ResourceDeviceProtoNameResourceId;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;

/**
 * Created by jorgesalcedo on 2/9/14.
 */
public class DeviceActivity extends Activity {

    private static final String LOG_TAG = "DeviceActivity";
    EditText name;
    TextView uuid;
    TextView last_update;
    Activity activity;
    Spinner resources;
    ResourcesDataAdapter resourcesAdapter;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        activity = this;
        setContentView(R.layout.activity_device);
        getActionBar().setDisplayHomeAsUpEnabled(true);

        name = (EditText) this.findViewById(R.id.device_edit_name);
        uuid = (TextView) this.findViewById(R.id.device_edit_uuid);
        last_update = (TextView) this.findViewById(R.id.device_edit_last_update);
        resources = (Spinner) this.findViewById(R.id.resources);
        resourcesAdapter = new ResourcesDataAdapter(this.getApplicationContext(), android.R.layout.simple_spinner_dropdown_item);
        resources.setAdapter(resourcesAdapter);

        getResourcesList();

        if (getIntent().getExtras().getString(AppConstants.DEVICE_LAST_SYNC) == null) {
            getDevice(getIntent().getExtras().getString(AppConstants.DEVICE_UUID));
        } else {
            name.setText(getIntent().getExtras().getString(AppConstants.DEVICE_NAME));
            uuid.setText(getIntent().getExtras().getString(AppConstants.DEVICE_UUID));
            last_update.setText(getIntent().getExtras().getString(AppConstants.DEVICE_LAST_SYNC));
        }
    }

    public void onClickSave(View v) {
        updateDevice(uuid.getText().toString(), name.getText().toString());

    }

    private void getResourcesList() {
        AsyncTask<Void, Void, ResourceCalendarCollection> getAndDisplayResources =
                new AsyncTask<Void, Void, ResourceCalendarCollection>() {
                    @Override
                    protected ResourceCalendarCollection doInBackground(Void... unused) {
                        // Retrieve service handle using null credential since this is an unauthenticated call.
                        Devices apiServiceHandle = AppConstants.getApiServiceHandle();

                        try {
                            Devices.Resources.List getResourcesCommand = apiServiceHandle.resources().list();
                            ResourceCalendarCollection resources = getResourcesCommand.execute();
                            return resources;
                        } catch (IOException e) {
                            Log.e(LOG_TAG, "Exception during API call", e);
                        }
                        return null;
                    }

                    @Override
                    protected void onPostExecute(ResourceCalendarCollection resources) {
                        if (resources != null && resources.getItems() != null) {

                            displayResources(resources.getItems().toArray(new ResourceCalendar[]{}));
                            activity.setProgressBarIndeterminateVisibility(Boolean.FALSE);

                        } else {
                            Log.e(LOG_TAG, "No devices were returned by the API.");
                        }
                    }
                };

        getAndDisplayResources.execute((Void) null);
    }

    public void displayResources(ResourceCalendar... resources) {
        resourcesAdapter.replaceData(resources);
    }


    private void getDevice(final String uuid) {
        // Use of an anonymous class is done for sample code simplicity. {@code AsyncTasks} should be
        // static-inner or top-level classes to prevent memory leak issues.
        // @see http://goo.gl/fN1fuE @26:00 for an great explanation.
        AsyncTask<String, Void, ResourceDevice> getAndDisplayGreeting =
                new AsyncTask<String, Void, ResourceDevice>() {
                    @Override
                    protected ResourceDevice doInBackground(String... strings) {
                        // Retrieve service handle.
                        Devices apiServiceHandle = AppConstants.getApiServiceHandle();

                        try {
                            ResourceDevice device = apiServiceHandle.device().get(strings[0]).execute();
                            return device;
                        } catch (IOException e) {
                            Log.e(LOG_TAG, "Exception during API call", e);
                        }
                        return null;
                    }

                    @Override
                    protected void onPostExecute(ResourceDevice device) {
                        if (device != null) {
                            displayDevice(device);
                        } else {
                            Log.e(LOG_TAG, "No greetings were returned by the API.");
                        }
                    }
                };

        getAndDisplayGreeting.execute(uuid);
    }

    public void updateDevice(String uuid_str, String name_str) {
        AsyncTask<String, Void, ResourceDevice> sendGreetings = new AsyncTask<String, Void, ResourceDevice>() {
            @Override
            protected ResourceDevice doInBackground(String... strings) {
                // Retrieve service handle.
                Devices apiServiceHandle = AppConstants.getApiServiceHandle();
                Log.d(LOG_TAG, strings[0] + strings[1]);
                try {
                    ResourceDeviceProtoNameResourceId name = new ResourceDeviceProtoNameResourceId();

                    name.setName(strings[1]);
                    ResourceDevice device = apiServiceHandle.device().update(strings[0], name).execute();
                    return device;
                } catch (IOException e) {
                    Log.e(LOG_TAG, "Exception during API call", e);
                }
                return null;
            }

            @Override
            protected void onPostExecute(ResourceDevice device) {
                if (device != null) {
                    displayDevice(device);
                    Toast toast = Toast.makeText(activity, activity.getString(R.string.devices_updated), Toast.LENGTH_LONG);
                    toast.setGravity(Gravity.CENTER_VERTICAL | Gravity.CENTER_HORIZONTAL, 0, 0);
                    toast.show();

                } else {
                    Log.e(LOG_TAG, "No greetings were returned by the API.");
                    Toast toast = Toast.makeText(activity, activity.getString(R.string.error_updating), Toast.LENGTH_LONG);
                    toast.setGravity(Gravity.CENTER_VERTICAL | Gravity.CENTER_HORIZONTAL, 0, 0);
                    toast.show();
                }
            }
        };

        sendGreetings.execute(uuid_str, name_str);
    }

    public void displayDevice(ResourceDevice device) {
        name.setText(device.getName());
        uuid.setText(device.getUuid());
        last_update.setText(device.getLastSync());
        resources.setSelection(resourcesAdapter.getPosition(device.getResource()));
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {

        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                finish();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }


    static class ResourcesDataAdapter extends ArrayAdapter{
        private Context context;
        private int resource_id;
        private LayoutInflater inflater;
        ResourcesDataAdapter(Context context, int resource) {
            super(context, resource);
            this.context = context;
            this.resource_id = resource;
            inflater = (LayoutInflater)context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        }

        void replaceData(ResourceCalendar[] resources) {
            clear();
            for (ResourceCalendar resource : resources) {
                add(resource);
            }
        }

        @Override
        public View getView(int position, View convertView, ViewGroup parent) {
            View view=convertView;
            if(convertView==null)
                view = inflater.inflate(android.R.layout.simple_spinner_item, parent, false);

            ResourceCalendar resource = (ResourceCalendar)getItem(position);
            ((TextView)view).setTextColor(0xff000000);
            ((TextView)view).setText(resource.getName());
            return view;
        }

        @Override
        public View getDropDownView(int position, View convertView, ViewGroup parent) {
            View view=convertView;
            if(convertView==null)
                view = inflater.inflate(android.R.layout.simple_spinner_dropdown_item, parent, false);

            ResourceCalendar resource = (ResourceCalendar)getItem(position);
            ((TextView)view).setTextColor(0xff000000);
            ((TextView)view).setText(resource.getName());
            return view;
        }
    }
}
