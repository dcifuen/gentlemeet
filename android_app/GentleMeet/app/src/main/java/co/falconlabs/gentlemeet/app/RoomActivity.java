package co.falconlabs.gentlemeet.app;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.appspot.www_ardux.gentlemeet.Gentlemeet;
import com.appspot.www_ardux.gentlemeet.model.ArduxApiMessagesEventMessage;
import com.appspot.www_ardux.gentlemeet.model.ArduxApiMessagesEventsResponseMessage;
import com.appspot.www_ardux.gentlemeet.model.ResourceCalendar;
import com.appspot.www_ardux.gentlemeet.model.ResourceCalendarCollection;
import com.google.api.client.googleapis.extensions.android.gms.auth.GoogleAccountCredential;
import com.google.api.client.repackaged.com.google.common.base.Strings;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;


public class RoomActivity extends Activity {
    private static final String LOG_TAG = RoomActivity.class.getName();
    private String resourceId = "";
    String mEmailAccount;
    SharedPreferences prefs;
    TextView title;
    TextView range;
    TimerView tview;
    Button button;
    ArduxApiMessagesEventMessage event;

    private EventsDataAdapter listAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_room);
        resourceId = getIntent().getExtras().getString(AppConstants.RESOURCE_ID, "");
        getActionBar().setTitle(getIntent().getExtras().getString(AppConstants.RESOURCE_NAME, ""));

        prefs = PreferenceManager.getDefaultSharedPreferences(this);
        mEmailAccount = prefs.getString("pref_email", "");


        ListView listView = (ListView)findViewById(R.id.eventsList);
        listAdapter = new EventsDataAdapter(this);
        listView.setAdapter(listAdapter);


        title =(TextView)findViewById(R.id.eventTitle);
        range =(TextView)findViewById(R.id.rangeTitle);
        tview = (TimerView)findViewById(R.id.eventTimer);
        button = (Button)findViewById(R.id.eventButton);


        setProgressBarIndeterminateVisibility(Boolean.TRUE);

        AsyncTask<String, Void, ArduxApiMessagesEventMessage> getCalendarEvent =
                new AsyncTask<String, Void, ArduxApiMessagesEventMessage>() {
                    @Override
                    protected ArduxApiMessagesEventMessage doInBackground(String... resourceCalendarsIds) {
                        String resource_id = null;
                        if(resourceCalendarsIds.length > 0){
                            resource_id = resourceCalendarsIds[0];
                        }else{
                            return null;
                        }
                        if (Strings.isNullOrEmpty(mEmailAccount)) {
                            return null;
                        }

                        if (!AppConstants.checkGooglePlayServicesAvailable(RoomActivity.this)) {
                            return null;
                        }

                        GoogleAccountCredential credential = GoogleAccountCredential.usingAudience(
                                RoomActivity.this, AppConstants.AUDIENCE);

                        credential.setSelectedAccountName(mEmailAccount);
                        // Retrieve service handle using null credential since this is an unauthenticated call.
                        Gentlemeet apiServiceHandle = AppConstants.getApiServiceHandle(credential);
                        try {
                            Gentlemeet.Resource.EventCurrent getResourceCommand = apiServiceHandle.resource().eventCurrent(resource_id);
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
                        setupCurrentEvent(resource);
                    }
                };

        AsyncTask<String, Void, ArduxApiMessagesEventsResponseMessage> getAndDisplayEvents =
                new AsyncTask<String, Void, ArduxApiMessagesEventsResponseMessage> () {
                    @Override
                    protected ArduxApiMessagesEventsResponseMessage doInBackground(String... resourceCalendarsIds) {
                        String resource_id = null;
                        if(resourceCalendarsIds.length > 0){
                            resource_id = resourceCalendarsIds[0];
                        }else{
                            return null;
                        }

                        if (Strings.isNullOrEmpty(mEmailAccount)) {
                            return null;
                        }

                        if (!AppConstants.checkGooglePlayServicesAvailable(RoomActivity.this)) {
                            return null;
                        }

                        GoogleAccountCredential credential = GoogleAccountCredential.usingAudience(
                                RoomActivity.this, AppConstants.AUDIENCE);

                        credential.setSelectedAccountName(mEmailAccount);
                        // Retrieve service handle using null credential since this is an unauthenticated call.
                        Gentlemeet apiServiceHandle = AppConstants.getApiServiceHandle(credential);

                        try {
                            Gentlemeet.Resource.NextEventsToday getEventsCommand = apiServiceHandle.resource().nextEventsToday(resource_id);
                            ArduxApiMessagesEventsResponseMessage events = getEventsCommand.execute();
                            return events;
                        } catch (IOException e) {
                            Log.e(LOG_TAG, "Exception during API call", e);
                        }
                        return null;
                    }

                    @Override
                    protected void onPostExecute(ArduxApiMessagesEventsResponseMessage events) {
                        if (events!=null && events.getItems()!=null) {
                            displayEvents(events.getItems().toArray(new ArduxApiMessagesEventMessage[]{}));
                        } else {
                            Log.w(LOG_TAG, "No events were returned by the API.");
                        }
                    }
                };

        getAndDisplayEvents.execute(resourceId);


        getCalendarEvent.execute(resourceId);
    }

    private void displayEvents(ArduxApiMessagesEventMessage... events) {
        String msg;
        if (events==null || events.length < 1) {
            msg = "No rooms to display";
            Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
        } else {
            if (BuildConfig.DEBUG) {
                Log.d(LOG_TAG, "Displaying " + events.length + " rooms.");
            }
            listAdapter.replaceData(events);
        }
    }


    public void setupCurrentEvent(ArduxApiMessagesEventMessage resource){
        setProgressBarIndeterminateVisibility(Boolean.FALSE);
        event = resource;
        if (resource!=null ) {
            title.setText(resource.getTitle());
            tview.setEndTime(resource.getEndDateTime());
            button.setText("Finalizar");
            String start = new SimpleDateFormat("H:mm a").format(new Date(resource.getStartDateTime().getValue()));
            String end = new SimpleDateFormat("H:mm a").format(new Date(resource.getEndDateTime().getValue()));
            range.setText(start + " - "+end);

        } else {
            title.setText("");
            range.setText("");
            button.setText("Aparta Sala");
        }
    }


    public void buttonAction(View view) {
        if(event ==  null){
            AsyncTask<String, Void, ArduxApiMessagesEventMessage> quickAdd =
                    new AsyncTask<String, Void, ArduxApiMessagesEventMessage>() {
                        @Override
                        protected ArduxApiMessagesEventMessage doInBackground(String... resourceCalendarsIds) {
                            String resource_id = null;
                            if(resourceCalendarsIds.length > 0){
                                resource_id = resourceCalendarsIds[0];
                            }else{
                                return null;
                            }
                            if (Strings.isNullOrEmpty(mEmailAccount)) {
                                return null;
                            }

                            if (!AppConstants.checkGooglePlayServicesAvailable(RoomActivity.this)) {
                                return null;
                            }

                            GoogleAccountCredential credential = GoogleAccountCredential.usingAudience(
                                    RoomActivity.this, AppConstants.AUDIENCE);

                            credential.setSelectedAccountName(mEmailAccount);
                            // Retrieve service handle using null credential since this is an unauthenticated call.
                            Gentlemeet apiServiceHandle = AppConstants.getApiServiceHandle(credential);
                            try {
                                Gentlemeet.Resource.QuickAdd quickAdd = apiServiceHandle.resource().quickAdd(resource_id);
                                ArduxApiMessagesEventMessage event = quickAdd.execute();
                                return event;
                            } catch (Exception e) {
                                Log.e(LOG_TAG, "Exception during API call", e);
                                return null;
                            }
                        }

                        @Override
                        protected void onPostExecute(ArduxApiMessagesEventMessage resource) {
                            setupCurrentEvent(resource);
                        }
                    };
            quickAdd.execute(resourceId);
        }else{

        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.room, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            return true;
        }
        return super.onOptionsItemSelected(item);
    }


    static class EventsDataAdapter extends ArrayAdapter {
        private static LayoutInflater inflater=null;
        private static Activity activity=null;

        EventsDataAdapter(Activity activity) {
            super(activity.getApplication().getApplicationContext(), R.layout.event_row, new ArrayList<ArduxApiMessagesEventMessage>());
            inflater = (LayoutInflater)activity.getApplication().getApplicationContext().getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            this.activity = activity;
        }

        void replaceData(ArduxApiMessagesEventMessage[] events) {
            clear();
            for (ArduxApiMessagesEventMessage event : events) {
                add(event);
            }
        }

        @Override
        public View getView(int position, View convertView, ViewGroup parent) {
            View vi=convertView;
            if(convertView==null)
                vi = inflater.inflate(R.layout.event_row, parent, false);
            ArduxApiMessagesEventMessage event = (ArduxApiMessagesEventMessage)this.getItem(position);
            String start = new SimpleDateFormat("H:mm a").format(new Date(event.getStartDateTime().getValue()));
            String end = new SimpleDateFormat("H:mm a").format(new Date(event.getEndDateTime().getValue()));
            TextView subname = (TextView)vi.findViewById(R.id.eventSubname);
            TextView name = (TextView)vi.findViewById(R.id.eventName);
            subname.setText(start + " - "+end);
            name.setText(event.getSummary());
            return  vi;

        }


    }

}
