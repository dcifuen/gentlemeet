package com.falconlabs.ardux;

import android.app.Activity;
import android.app.Dialog;
import android.content.Context;

import com.google.api.client.extensions.android.http.AndroidHttp;
import com.google.api.client.extensions.android.json.AndroidJsonFactory;
import com.google.api.client.http.HttpTransport;
import com.google.api.client.json.JsonFactory;
import com.appspot.www_ardux.devices.Devices;

import javax.annotation.Nullable;

public class AppConstants {

    public static final String DEVICE_UUID = "DEVICE_UUID";


    /**
     * Class instance of the JSON factory.
     */
    public static final JsonFactory JSON_FACTORY = new AndroidJsonFactory();

    /**
     * Class instance of the HTTP transport.
     */
    public static final HttpTransport HTTP_TRANSPORT = AndroidHttp.newCompatibleTransport();


    /**
     * Retrieve a Helloworld api service handle to access the API.
     */
    public static Devices getApiServiceHandle() {
        // Use a builder to help formulate the API request.
        Devices.Builder devices = new Devices.Builder(AppConstants.HTTP_TRANSPORT,
                AppConstants.JSON_FACTORY,null);
        devices.setRootUrl("http://192.168.1.128:8080/_ah/api/");
        return devices.build();
    }

}