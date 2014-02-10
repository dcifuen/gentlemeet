package com.falconlabs.ardux;

import android.app.Activity;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBar;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.appspot.www_ardux.devices.Devices;
import com.appspot.www_ardux.devices.model.ResourceDevice;

import java.io.IOException;
import java.util.Date;

/**
 * Created by jorgesalcedo on 2/9/14.
 */
public class DeviceActivity extends Activity{

    private static final String LOG_TAG = "DeviceActivity";
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_device);
        getActionBar().setDisplayHomeAsUpEnabled(true);
        getDevice(getIntent().getExtras().getString(AppConstants.DEVICE_UUID));

        //Toast.makeText(this, , Toast.LENGTH_LONG).show();
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

    public void displayDevice(ResourceDevice device){
        EditText name = (EditText)this.findViewById(R.id.device_edit_name);
        TextView uuid = (TextView)this.findViewById(R.id.device_edit_uuid);
        TextView last_update = (TextView)this.findViewById(R.id.device_edit_last_update);

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
