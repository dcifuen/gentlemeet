package com.falconlabs.ardux;

import android.nfc.NdefRecord;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.nfc.NfcAdapter;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;


import org.ndeftools.Message;
import org.ndeftools.wellknown.TextRecord;

import java.io.UnsupportedEncodingException;


/**
 * Created by jorgesalcedo on 2/9/14.
 */

public class TagsFragment extends Fragment {

    private static final String LOG_TAG = "TagsFragment";
    private NfcAdapter mNfcAdapter;
    public Boolean savingTag = false;

    public EditText emailView;
    public TextView tagMessage;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {



        View rootView = inflater.inflate(R.layout.fragment_tags, container, false);
        emailView = (EditText)rootView.findViewById(R.id.email);
        tagMessage = (TextView)rootView.findViewById(R.id.tag_message);
        tagMessage.setVisibility(View.INVISIBLE);
        return rootView;

    }

    public Message composeMessage() {
        Log.d(LOG_TAG, "createMessage");

        Message message = new Message(); // ndeftools ndef message

        // add an android application record
        TextRecord txr = new TextRecord(emailView.getText().toString());
        message.add(txr);

        return message;
    }




    public void onFocusChange(View v, boolean hasFocus){
        if(!hasFocus){
            tagMessage.setVisibility(View.INVISIBLE);
        }
    }
}
