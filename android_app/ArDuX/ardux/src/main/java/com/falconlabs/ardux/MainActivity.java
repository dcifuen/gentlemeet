package com.falconlabs.ardux;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

import android.app.Activity;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.IntentFilter;
import android.nfc.NdefMessage;
import android.nfc.NdefRecord;
import android.nfc.NfcAdapter;
import android.nfc.NfcAdapter.CreateNdefMessageCallback;
import android.nfc.NfcAdapter.OnNdefPushCompleteCallback;
import android.nfc.NfcEvent;
import android.nfc.Tag;
import android.nfc.tech.Ndef;
import android.os.AsyncTask;
import android.os.Handler;
import android.os.Parcelable;
import android.support.v7.app.ActionBarActivity;
import android.support.v7.app.ActionBar;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.app.FragmentPagerAdapter;
import android.os.Bundle;
import android.support.v4.view.ViewPager;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.TextView;
import android.widget.Toast;

import com.appspot.www_ardux.devices.model.ResourceDevice;

import org.ndeftools.Message;
import org.ndeftools.Record;
import org.ndeftools.externaltype.AndroidApplicationRecord;
import org.ndeftools.wellknown.TextRecord;

public class MainActivity extends ActionBarActivity implements ActionBar.TabListener, CreateNdefMessageCallback, OnNdefPushCompleteCallback {

    private static final String LOG_TAG = "MainActivity";
    private static final int MESSAGE_SENT = 1;

    /**
     * The {@link android.support.v4.view.PagerAdapter} that will provide
     * fragments for each of the sections. We use a
     * {@link FragmentPagerAdapter} derivative, which will keep every
     * loaded fragment in memory. If this becomes too memory intensive, it
     * may be best to switch to a
     * {@link android.support.v4.app.FragmentStatePagerAdapter}.
     */
    SectionsPagerAdapter mSectionsPagerAdapter;

    /**
     * The {@link ViewPager} that will host the section contents.
     */
    ViewPager mViewPager;

    private NfcAdapter nfcAdapter;
    private PendingIntent nfcPendingIntent;


    private Activity activity;

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        activity = this;
        requestWindowFeature(Window.FEATURE_INDETERMINATE_PROGRESS);
        setContentView(R.layout.activity_main);
        // Set up the action bar.
        final ActionBar actionBar = getSupportActionBar();
        actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_TABS);

        nfcAdapter = NfcAdapter.getDefaultAdapter(this);

        if (nfcAdapter == null) {
            // Stop here, we definitely need NFC
            Toast.makeText(this, R.string.nfc_error, Toast.LENGTH_LONG).show();
        }

        if (!nfcAdapter.isEnabled()) {
            Toast toast = Toast.makeText(this, R.string.nfc_disabled, Toast.LENGTH_LONG);
            toast.setGravity(Gravity.CENTER_VERTICAL | Gravity.CENTER_HORIZONTAL, 0, 0);
            toast.show();
        }


        // Create the adapter that will return a fragment for each of the three
        // primary sections of the activity.
        mSectionsPagerAdapter = new SectionsPagerAdapter(getSupportFragmentManager());

        // Set up the ViewPager with the sections adapter.
        mViewPager = (ViewPager) findViewById(R.id.pager);
        mViewPager.setAdapter(mSectionsPagerAdapter);

        // When swiping between different sections, select the corresponding
        // tab. We can also use ActionBar.Tab#select() to do this if we have
        // a reference to the Tab.
        mViewPager.setOnPageChangeListener(new ViewPager.SimpleOnPageChangeListener() {
            @Override
            public void onPageSelected(int position) {
                actionBar.setSelectedNavigationItem(position);
            }
        });

        // For each of the sections in the app, add a tab to the action bar.
        for (int i = 0; i < mSectionsPagerAdapter.getCount(); i++) {
            // Create a tab with text corresponding to the page title defined by
            // the adapter. Also specify this Activity object, which implements
            // the TabListener interface, as the callback (listener) for when
            // this tab is selected.
            actionBar.addTab(
                    actionBar.newTab()
                            .setText(mSectionsPagerAdapter.getPageTitle(i))
                            .setTabListener(this));
        }

        nfcPendingIntent = PendingIntent.getActivity(this, 0, new Intent(this, this.getClass()).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), 0);
        // Register Android Beam callback
        nfcAdapter.setNdefPushMessageCallback(this, this);
        // Register callback to listen for message-sent success
        nfcAdapter.setOnNdefPushCompleteCallback(this, this);

        if (getIntent().hasExtra(NfcAdapter.EXTRA_TAG)) {
            //mViewPager.setCurrentItem(1);
        }

    }

    public void enableForegroundMode() {
        Log.d(LOG_TAG, "enableForegroundMode");

        // foreground mode gives the current active application priority for reading scanned tags
        IntentFilter tagDetected = new IntentFilter(NfcAdapter.ACTION_TAG_DISCOVERED); // filter for tags
        IntentFilter[] writeTagFilters = new IntentFilter[]{tagDetected};
        nfcAdapter.enableForegroundDispatch(this, nfcPendingIntent, writeTagFilters, null);
    }

    public void disableForegroundMode() {
        Log.d(LOG_TAG, "disableForegroundMode");

        nfcAdapter.disableForegroundDispatch(this);
    }

    @Override
    protected void onResume() {
        super.onResume();

        /**
         * It's important, that the activity is in the foreground (resumed). Otherwise
         * an IllegalStateException is thrown.
         */
        enableForegroundMode();
    }

    @Override
    protected void onPause() {
        /**
         * Call this before onPause, otherwise an IllegalArgumentException is thrown as well.
         */
        super.onPause();
        disableForegroundMode();

    }

    @Override
    public void onNewIntent(Intent intent) {
        Log.d(LOG_TAG, "onNewIntent");
        if (mSectionsPagerAdapter.tabs.size() >= 2) {

            TagsFragment tags_fragmet = (TagsFragment) mSectionsPagerAdapter.getItem(1);
            if (NfcAdapter.ACTION_TAG_DISCOVERED.equals(intent.getAction())) {

                if (tags_fragmet.savingTag) {
                    Message composedMessage = tags_fragmet.composeMessage();
                    NdefMessage composedMessageNdefMessage = composedMessage.getNdefMessage();
                    if (write(composedMessageNdefMessage, intent)) {
                        Log.d(LOG_TAG, "Write success!");
                        TextView textView = (TextView) findViewById(R.id.tag_message);
                        textView.setText(getString(R.string.tag_message_success));
                    } else {
                        Log.d(LOG_TAG, "Write failure!");
                        TextView textView = (TextView) findViewById(R.id.tag_message);
                        textView.setText(getString(R.string.tag_message_error));
                    }
                    tags_fragmet.savingTag = false;

                } else {
                    Parcelable[] messages = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES);
                    if (messages != null) {

                        Log.d(LOG_TAG, "Found " + messages.length + " NDEF messages"); // is almost always just one

                        // parse to records
                        for (int i = 0; i < messages.length; i++) {
                            try {
                                List<Record> records = new Message((NdefMessage) messages[i]);

                                Log.d(LOG_TAG, "Found " + records.size() + " records in message " + i);

                                for (int k = 0; k < records.size(); k++) {
                                    Log.d(LOG_TAG, " Record #" + k + " is of class " + records.get(k).getClass().getSimpleName());
                                    Record record = records.get(k);
                                    if (record instanceof TextRecord) {
                                        TextRecord txr = (TextRecord) record;
                                        String message = txr.getText();
                                        Log.d(LOG_TAG, "Package is " + message);
                                        Toast toast = Toast.makeText(activity, message, Toast.LENGTH_LONG);
                                        toast.setGravity(Gravity.CENTER_VERTICAL | Gravity.CENTER_HORIZONTAL, 0, 0);
                                        toast.show();
                                        if(message.startsWith("uuid:")){
                                            String[] strs = message.split(":");
                                            Intent deviceActivity = new Intent(this, DeviceActivity.class);
                                            deviceActivity.putExtra(AppConstants.DEVICE_UUID, (strs[1]));
                                            startActivity(deviceActivity);
                                        }else{
                                            mViewPager.setCurrentItem(1);
                                        }
                                    }
                                }
                            } catch (Exception e) {
                                Log.e(LOG_TAG, "Problem parsing message", e);
                            }

                        }
                    } else {

                        Toast toast = Toast.makeText(activity, activity.getString(R.string.nfc_empty_tag), Toast.LENGTH_LONG);
                        toast.setGravity(Gravity.CENTER_VERTICAL | Gravity.CENTER_HORIZONTAL, 0, 0);
                        toast.show();
                    }

                }
            }
        }
    }

    public void onClickSave(View v) {
        TagsFragment tags_fragmet = (TagsFragment) mSectionsPagerAdapter.getItem(1);
        tags_fragmet.savingTag = true;
        tags_fragmet.tagMessage.setVisibility(View.VISIBLE);
        tags_fragmet.tagMessage.setText(R.string.tag_message_scan);
    }

    public boolean write(NdefMessage rawMessage, Intent intent) {
        Tag tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG);
        Ndef ndef = Ndef.get(tag);
        if (ndef != null) {
            try {
                Log.d(LOG_TAG, "Write formatted tag");
                ndef.connect();
                if (!ndef.isWritable()) {
                    Log.d(LOG_TAG, "Tag is not writeable");
                    return false;
                }
                if (ndef.getMaxSize() < rawMessage.toByteArray().length) {
                    Log.d(LOG_TAG, "Tag size is too small, have " + ndef.getMaxSize() + ", need " + rawMessage.toByteArray().length);
                    return false;
                }
                ndef.writeNdefMessage(rawMessage);
                return true;
            } catch (Exception e) {
                Log.d(LOG_TAG, "Problem writing to tag", e);
            } finally {
                try {
                    ndef.close();
                } catch (IOException e) {
                    // ignore
                }
            }
        } else {
            Log.d(LOG_TAG, "Write to an unformatted tag not implemented");
        }
        return false;
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {

        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        switch (item.getItemId()) {
            // Handle presses on the action bar items
            case R.id.action_refresh:
                ((DevicesFragment) mSectionsPagerAdapter.getItem(0)).getDevices();
                return true;
            case R.id.action_settings:
                return true;
            default:
                return super.onOptionsItemSelected(item);

        }
    }

    @Override
    public void onTabSelected(ActionBar.Tab tab, FragmentTransaction fragmentTransaction) {
        // When the given tab is selected, switch to the corresponding page in
        // the ViewPager.
        mViewPager.setCurrentItem(tab.getPosition());
    }

    @Override
    public void onTabUnselected(ActionBar.Tab tab, FragmentTransaction fragmentTransaction) {

    }

    @Override
    public void onTabReselected(ActionBar.Tab tab, FragmentTransaction fragmentTransaction) {

    }

    @Override
    public NdefMessage createNdefMessage(NfcEvent event) {
        Log.d(LOG_TAG, "createNdefMessage");

        // create record to be pushed
        TextRecord record = new TextRecord("This is my text record");

        // encode one or more record to NdefMessage
        return new NdefMessage(record.getNdefRecord());
    }

    @Override
    public void onNdefPushComplete(NfcEvent arg0) {
        Log.d(LOG_TAG, "onNdefPushComplete");

        // A handler is needed to send messages to the activity when this
        // callback occurs, because it happens from a binder thread
        mHandler.obtainMessage(MESSAGE_SENT).sendToTarget();
    }

    /**
     * This handler receives a message from onNdefPushComplete
     */
    private final Handler mHandler = new Handler() {
        @Override
        public void handleMessage(android.os.Message msg) {
            switch (msg.what) {
                case MESSAGE_SENT:
                    Toast.makeText(getApplicationContext(), "Message beamed!", Toast.LENGTH_LONG).show();
                    break;
            }
        }
    };


    /**
     * A {@link FragmentPagerAdapter} that returns a fragment corresponding to
     * one of the sections/tabs/pages.
     */
    public class SectionsPagerAdapter extends FragmentPagerAdapter {

        ArrayList<Fragment> tabs = new ArrayList<Fragment>();

        public SectionsPagerAdapter(FragmentManager fm) {
            super(fm);
        }

        @Override
        public Fragment getItem(int position) {
            // getItem is called to instantiate the fragment for the given page.
            // Return a PlaceholderFragment (defined as a static inner class below).

            if (tabs.size() <= position) {
                switch (position) {
                    case 0:
                        tabs.add(position, new DevicesFragment());
                        break;
                    case 1:
                        tabs.add(position, new TagsFragment());
                        break;
                }
            }
            return tabs.get(position);

        }

        @Override
        public int getCount() {
            // Show 2 total pages.
            return 2;
        }

        @Override
        public CharSequence getPageTitle(int position) {
            Locale l = Locale.getDefault();
            switch (position) {
                case 0:
                    return getString(R.string.devices_section).toUpperCase(l);
                case 1:
                    return getString(R.string.tags_section).toUpperCase(l);
            }
            return null;
        }
    }
}
