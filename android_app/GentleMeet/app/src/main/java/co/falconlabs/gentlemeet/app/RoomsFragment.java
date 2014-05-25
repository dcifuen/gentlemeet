package co.falconlabs.gentlemeet.app;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.appspot.www_ardux.gentlemeet.Gentlemeet;
import com.appspot.www_ardux.gentlemeet.model.ResourceCalendar;
import com.appspot.www_ardux.gentlemeet.model.ResourceCalendarCollection;
import com.appspot.www_ardux.gentlemeet.model.ResourceDevice;
import com.appspot.www_ardux.gentlemeet.model.ResourceDeviceCollection;
import com.google.api.client.googleapis.extensions.android.gms.auth.GoogleAccountCredential;
import com.google.api.client.repackaged.com.google.common.base.Strings;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

/**
 * Created by jorgesalcedo on 2/9/14.
 */

public class RoomsFragment extends Fragment {
    private static final String LOG_TAG = "DevicesFragment";

    private RoomsDataAdapter listAdapter;

    String mEmailAccount;

    SharedPreferences prefs;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View rootView = inflater.inflate(R.layout.fragment_rooms, container, false);
        ListView listView = (ListView)rootView.findViewById(R.id.rooms_list_view);
        listAdapter = new RoomsDataAdapter((Application)getActivity().getApplication());
        listView.setAdapter(listAdapter);

        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
//                Intent deviceActivity = new Intent(getActivity(), DeviceActivity.class);
//                deviceActivity.putExtra(AppConstants.DEVICE_UUID, ((ResourceDevice)listAdapter.getItem(i)).getUuid());
//                deviceActivity.putExtra(AppConstants.DEVICE_NAME, ((ResourceDevice)listAdapter.getItem(i)).getName());
//                deviceActivity.putExtra(AppConstants.DEVICE_LAST_SYNC, ((ResourceDevice)listAdapter.getItem(i)).getLastSync());
//                startActivity(deviceActivity);
            }
        });

        prefs = PreferenceManager.getDefaultSharedPreferences(this.getActivity());
        mEmailAccount = prefs.getString("pref_email", "");

        getRooms();

        return rootView;

    }

    @Override
    public void onStart() {
        super.onStart();
        getRooms();
    }

    public void getRooms(){
        // Use of an anonymous class is done for sample code simplicity. {@code AsyncTasks} should be
        // static-inner or top-level classes to prevent memory leak issues.
        // @see http://goo.gl/fN1fuE @26:00 for an great explanation.
        Activity activity = getActivity();
        if(activity != null){
            getActivity().setProgressBarIndeterminateVisibility(Boolean.TRUE);
        }
        AsyncTask<Void, Void, ResourceCalendarCollection> getAndDisplayRooms =
                new AsyncTask<Void, Void, ResourceCalendarCollection> () {
                    @Override
                    protected ResourceCalendarCollection doInBackground(Void... unused) {
                        if (Strings.isNullOrEmpty(mEmailAccount)) {
                            return null;
                        }

                        if (!AppConstants.checkGooglePlayServicesAvailable(RoomsFragment.this.getActivity())) {
                            return null;
                        }

                        GoogleAccountCredential credential = GoogleAccountCredential.usingAudience(
                                RoomsFragment.this.getActivity(), AppConstants.AUDIENCE);

                        credential.setSelectedAccountName(mEmailAccount);
                        // Retrieve service handle using null credential since this is an unauthenticated call.
                        Gentlemeet apiServiceHandle = AppConstants.getApiServiceHandle(credential);

                        try {
                            Gentlemeet.Resources.List getRoomsCommand = apiServiceHandle.resources().list();
                            ResourceCalendarCollection rooms = getRoomsCommand.execute();
                            return rooms;
                        } catch (IOException e) {
                            Log.e(LOG_TAG, "Exception during API call", e);
                        }
                        return null;
                    }

                    @Override
                    protected void onPostExecute(ResourceCalendarCollection devices) {
                        if (devices!=null && devices.getItems()!=null) {
                            displayRooms(devices.getItems().toArray(new ResourceCalendar[]{}));
                            Activity activity = getActivity();
                            if(activity != null){
                                getActivity().setProgressBarIndeterminateVisibility(Boolean.FALSE);
                            }
                        } else {
                            Log.w(LOG_TAG, "No rooms were returned by the API.");
                        }
                    }
                };

        getAndDisplayRooms.execute((Void)null);
    }



    private void displayRooms(ResourceCalendar... rooms) {
        String msg;
        if (rooms==null || rooms.length < 1) {
            msg = "No rooms to display";
            Toast.makeText(getActivity(), msg, Toast.LENGTH_LONG).show();
        } else {
            if (BuildConfig.DEBUG) {
                Log.d(LOG_TAG, "Displaying " + rooms.length + " rooms.");
            }

            List<ResourceCalendar> roomsList = Arrays.asList(rooms);
            listAdapter.replaceData(rooms);
        }
    }

    /**
     * Simple use of an ArrayAdapter but we're using a static class to ensure no references to the
     * Activity exists.
     */
    static class RoomsDataAdapter extends ArrayAdapter {
        private static LayoutInflater inflater=null;
        private static Application app=null;

        RoomsDataAdapter(Application application) {
            super(application.getApplicationContext(), R.layout.room_row, application.rooms);
            app = application;
            inflater = (LayoutInflater)application.getApplicationContext().getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        }

        void replaceData(ResourceCalendar[] devices) {
            clear();
            for (ResourceCalendar device : devices) {
                add(device);
            }
        }

        @Override
        public View getView(int position, View convertView, ViewGroup parent) {
            View vi=convertView;
            if(convertView==null)
                vi = inflater.inflate(R.layout.room_row, null);
            ResourceCalendar room = (ResourceCalendar)this.getItem(position);
            TextView name = (TextView)vi.findViewById(R.id.room_row_name);
            name.setText(room.getName());
            return vi;
        }


    }
}
