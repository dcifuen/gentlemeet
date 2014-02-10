package com.falconlabs.ardux;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.appspot.www_ardux.devices.Devices;
import com.appspot.www_ardux.devices.model.ResourceDevice;
import com.appspot.www_ardux.devices.model.ResourceDeviceCollection;
import com.falconlabs.ardux.widget.PullToRefreshListView;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Set;

/**
 * Created by jorgesalcedo on 2/9/14.
 */

public class DevicesFragment extends Fragment {
    private static final String LOG_TAG = "DevicesFragment";

    private DevicesDataAdapter listAdapter;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View rootView = inflater.inflate(R.layout.fragment_devices, container, false);
        ListView listView = (ListView)rootView.findViewById(R.id.devices_list_view);
        listAdapter = new DevicesDataAdapter((Application)getActivity().getApplication());
        listView.setAdapter(listAdapter);

        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                Intent deviceActivity = new Intent(getActivity(), DeviceActivity.class);
                deviceActivity.putExtra(AppConstants.DEVICE_UUID, ((ResourceDevice)listAdapter.getItem(i)).getUuid());
                startActivity(deviceActivity);
            }
        });


        getDevices();

        return rootView;

    }

    @Override
    public void onStart() {
        super.onStart();
        getDevices();
    }

    public void getDevices(){
        // Use of an anonymous class is done for sample code simplicity. {@code AsyncTasks} should be
        // static-inner or top-level classes to prevent memory leak issues.
        // @see http://goo.gl/fN1fuE @26:00 for an great explanation.
        Activity activity = getActivity();
        if(activity != null){
            getActivity().setProgressBarIndeterminateVisibility(Boolean.TRUE);
        }
        AsyncTask<Void, Void, ResourceDeviceCollection> getAndDisplayDevices =
                new AsyncTask<Void, Void, ResourceDeviceCollection> () {
                    @Override
                    protected ResourceDeviceCollection doInBackground(Void... unused) {
                        // Retrieve service handle using null credential since this is an unauthenticated call.
                        Devices apiServiceHandle = AppConstants.getApiServiceHandle();

                        try {
                            Devices.DevicesOperations.List getDevicesCommand = apiServiceHandle.devices().list();
                            ResourceDeviceCollection devices = getDevicesCommand.execute();
                            return devices;
                        } catch (IOException e) {
                            Log.e(LOG_TAG, "Exception during API call", e);
                        }
                        return null;
                    }

                    @Override
                    protected void onPostExecute(ResourceDeviceCollection devices) {
                        if (devices!=null && devices.getItems()!=null) {
                            displayDevices(devices.getItems().toArray(new ResourceDevice[]{}));
                            Activity activity = getActivity();
                            if(activity != null){
                                getActivity().setProgressBarIndeterminateVisibility(Boolean.FALSE);
                            }
                        } else {
                            Log.e(LOG_TAG, "No devices were returned by the API.");
                        }
                    }
                };

        getAndDisplayDevices.execute((Void)null);
    }



    private void displayDevices(ResourceDevice... devices) {
        String msg;
        if (devices==null || devices.length < 1) {
            msg = "Greeting was not present";
            Toast.makeText(getActivity(), msg, Toast.LENGTH_LONG).show();
        } else {
            if (BuildConfig.DEBUG) {
                Log.d(LOG_TAG, "Displaying " + devices.length + " greetings.");
            }

            List<ResourceDevice> devicesList = Arrays.asList(devices);
            listAdapter.replaceData(devices);
        }
    }

    /**
     * Simple use of an ArrayAdapter but we're using a static class to ensure no references to the
     * Activity exists.
     */
    static class DevicesDataAdapter extends ArrayAdapter {
        private static LayoutInflater inflater=null;
        private static Application app=null;

        DevicesDataAdapter(Application application) {
            super(application.getApplicationContext(), R.layout.device_row,
                    application.devices);
            app = application;
            inflater = (LayoutInflater)application.getApplicationContext().getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        }

        void replaceData(ResourceDevice[] devices) {
            clear();
            for (ResourceDevice device : devices) {
                add(device);
            }
        }

        @Override
        public View getView(int position, View convertView, ViewGroup parent) {
            View vi=convertView;
            if(convertView==null)
                vi = inflater.inflate(R.layout.device_row, null);

            ResourceDevice device = (ResourceDevice)this.getItem(position);

            TextView name = (TextView)vi.findViewById(R.id.device_row_name);
            TextView uuid = (TextView)vi.findViewById(R.id.device_row_uuid);
            TextView state = (TextView)vi.findViewById(R.id.device_row_state);

            name.setText(device.getName());
            uuid.setText(device.getUuid());
            if(device.getOnline()){
                state.setText(app.getString(R.string.online));
                state.setTextColor(0xFF15441B);
            }else{
                state.setText(app.getString(R.string.offline));
                state.setTextColor(0xFF66000E);
            }
            return vi;
        }


    }
}
