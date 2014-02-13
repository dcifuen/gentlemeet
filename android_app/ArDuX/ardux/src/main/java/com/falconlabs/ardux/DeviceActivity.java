package com.falconlabs.ardux;

import android.app.Activity;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBar;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.appspot.www_ardux.devices.Devices;
import com.appspot.www_ardux.devices.model.ResourceDevice;
import com.appspot.www_ardux.devices.model.ResourceDeviceProtoName;

import java.io.IOException;
import java.util.Date;

/**
 * Created by jorgesalcedo on 2/9/14.
 */
public class DeviceActivity extends Activity{

    private static final String LOG_TAG = "DeviceActivity";
    EditText name;
    TextView uuid;
    TextView last_update;
    Activity activity;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        activity = this;
        setContentView(R.layout.activity_device);
        getActionBar().setDisplayHomeAsUpEnabled(true);

        name = (EditText)this.findViewById(R.id.device_edit_name);
        uuid = (TextView)this.findViewById(R.id.device_edit_uuid);
        last_update = (TextView)this.findViewById(R.id.device_edit_last_update);


        if (getIntent().getExtras().getString(AppConstants.DEVICE_LAST_SYNC) == null){
            getDevice(getIntent().getExtras().getString(AppConstants.DEVICE_UUID));
        }else{
            name.setText(getIntent().getExtras().getString(AppConstants.DEVICE_NAME));
            uuid.setText(getIntent().getExtras().getString(AppConstants.DEVICE_UUID));
            last_update.setText(getIntent().getExtras().getString(AppConstants.DEVICE_LAST_SYNC));
        }


    }

    public void onClickSave(View v){
        updateDevice(uuid.getText().toString(), name.getText().toString());

    }


    private void getDevice(final String uuid){
        // Use of an anonymous class is done for sample code simplicity. {@code AsyncTasks} should be
        // static-inner or top-level classes to prevent memory leak issues.
        // @see http://goo.gl/fN1fuE @26:00 for an great explanation.
        AsyncTask<String, Void, ResourceDevice> getAndDisplayGreeting =
                new AsyncTask<String, Void, ResourceDevice> () {
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
                        if (device!=null) {
                            displayDevice(device);
                        } else {
                            Log.e(LOG_TAG, "No greetings were returned by the API.");
                        }
                    }
                };

        getAndDisplayGreeting.execute(uuid);
    }

    public void updateDevice(String uuid_str, String name_str){
        AsyncTask<String, Void, ResourceDevice> sendGreetings = new AsyncTask<String, Void, ResourceDevice> () {
            @Override
            protected ResourceDevice doInBackground(String... strings) {
                // Retrieve service handle.
                Devices apiServiceHandle = AppConstants.getApiServiceHandle();
                Log.d(LOG_TAG, strings[0] + strings[1]);
                try {
                    ResourceDeviceProtoName name = new ResourceDeviceProtoName();

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
                if (device!=null) {
                    displayDevice(device);
                    Toast toast = Toast.makeText(activity, activity.getString(R.string.devices_updated), Toast.LENGTH_LONG);
                    toast.setGravity(Gravity.CENTER_VERTICAL|Gravity.CENTER_HORIZONTAL, 0, 0);
                    toast.show();

                } else {
                    Log.e(LOG_TAG, "No greetings were returned by the API.");
                    Toast toast = Toast.makeText(activity, activity.getString(R.string.error_updating), Toast.LENGTH_LONG);
                    toast.setGravity(Gravity.CENTER_VERTICAL|Gravity.CENTER_HORIZONTAL, 0, 0);
                    toast.show();
                }
            }
        };

        sendGreetings.execute(uuid_str, name_str);
    }

    public void displayDevice(ResourceDevice device){
        name.setText(device.getName());
        uuid.setText(device.getUuid());
        last_update.setText(device.getLastSync());

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {

        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()){
            case android.R.id.home:
                finish();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }
}
