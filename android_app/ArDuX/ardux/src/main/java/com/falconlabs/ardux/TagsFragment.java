package com.falconlabs.ardux;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

/**
 * Created by jorgesalcedo on 2/9/14.
 */

public class TagsFragment extends Fragment {
    private static final String LOG_TAG = "TagsFragment";

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View rootView = inflater.inflate(R.layout.fragment_tags, container, false);
        return rootView;

    }
}
