package co.falconlabs.gentlemeet.app;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
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
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.appspot.www_ardux.gentlemeet.Gentlemeet;
import com.appspot.www_ardux.gentlemeet.model.ArduxApiMessagesEventMessage;
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
    private static final String LOG_TAG = RoomsFragment.class.getName();

    private RoomsDataAdapter listAdapter;

    String mEmailAccount;

    SharedPreferences prefs;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View rootView = inflater.inflate(R.layout.fragment_rooms, container, false);
        ListView listView = (ListView)rootView.findViewById(R.id.rooms_list_view);
        listAdapter = new RoomsDataAdapter(getActivity());
        listView.setAdapter(listAdapter);

        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
               Intent roomActivity = new Intent(getActivity(), RoomActivity.class);
               roomActivity.putExtra(AppConstants.RESOURCE_ID, ((ResourceCalendar)listAdapter.getItem(i)).getId());
               roomActivity.putExtra(AppConstants.RESOURCE_NAME, ((ResourceCalendar)listAdapter.getItem(i)).getName());
               startActivity(roomActivity);
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
        private static Activity activity=null;

        RoomsDataAdapter(Activity activity) {
            super(activity.getApplication().getApplicationContext(), R.layout.room_row, ((Application)activity.getApplication()).rooms);
            inflater = (LayoutInflater)activity.getApplication().getApplicationContext().getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            this.activity = activity;
        }

        void replaceData(ResourceCalendar[] resources) {
            clear();
            for (ResourceCalendar resource : resources) {
                add(resource);
            }
        }

        @Override
        public View getView(int position, View convertView, ViewGroup parent) {
            View vi=convertView;
            if(convertView==null)
                vi = inflater.inflate(R.layout.room_row, parent, false);

            final View vi2 = vi;
            ResourceCalendar room = (ResourceCalendar)this.getItem(position);
            TextView name = (TextView)vi.findViewById(R.id.room_row_name);
            name.setText(room.getName());
            SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(activity);
            final String mEmailAccount = prefs.getString("pref_email", "");
            AsyncTask<ResourceCalendar, Void, ArduxApiMessagesEventMessage> getCalendarEvent =
                    new AsyncTask<ResourceCalendar, Void, ArduxApiMessagesEventMessage>() {
                        @Override
                        protected ArduxApiMessagesEventMessage doInBackground(ResourceCalendar... resourceCalendars) {
                            ResourceCalendar resource = null;
                            if(resourceCalendars.length > 0){
                                resource = resourceCalendars[0];
                            }else{
                                return null;
                            }
                            if (Strings.isNullOrEmpty(mEmailAccount)) {
                                return null;
                            }

                            if (!AppConstants.checkGooglePlayServicesAvailable(activity)) {
                                return null;
                            }

                            GoogleAccountCredential credential = GoogleAccountCredential.usingAudience(
                                    activity, AppConstants.AUDIENCE);

                            credential.setSelectedAccountName(mEmailAccount);
                            // Retrieve service handle using null credential since this is an unauthenticated call.
                            Gentlemeet apiServiceHandle = AppConstants.getApiServiceHandle(credential);
                            try {
                                Gentlemeet.Resource.EventCurrent getResourceCommand = apiServiceHandle.resource().eventCurrent(resource.getId());
                                ArduxApiMessagesEventMessage event = getResourceCommand.execute();
                                Log.i(LOG_TAG, "Event found");
                                return event;
                            } catch (Exception e) {
                                Log.e(LOG_TAG, "Exception during API call", e);
                                return null;
                            }
                        }

                        @Override
                        protected void onPostExecute(ArduxApiMessagesEventMessage resource) {
                            if (resource!=null ) {
                                TimerView tview = (TimerView)vi2.findViewById(R.id.rowTimer);
                                tview.setEndTime(resource.getEndDateTime());
                            } else {
                                Log.w(LOG_TAG, "No resource was returned by the API.");
                            }
                        }
                    };
            getCalendarEvent.execute((ResourceCalendar) this.getItem(position));
            return vi;
        }


    }
}
